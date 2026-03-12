#!/usr/bin/env python3
"""
ModelScope Image Generation Script
Generates images using ModelScope API with async polling
"""

import requests
import time
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict
from io import BytesIO

from PIL import Image

# Check if we can use getpass for secure input
try:
    from getpass import getpass
    HAS_GETPASS = True
except ImportError:
    HAS_GETPASS = False

# Configuration
BASE_URL = 'https://api-inference.modelscope.cn/'
REQUEST_TIMEOUT = 30
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 60

def get_config_path() -> Path:
    """Get the config file path (~/.config/modelscope/config.json)"""
    # Use XDG config directory if set, otherwise ~/.config/modelscope/
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        config_dir = Path(xdg_config) / 'modelscope'
    else:
        config_dir = Path.home() / '.config' / 'modelscope'

    return config_dir / 'config.json'

def save_api_key(api_key: str, config_path: Path) -> None:
    """Save API key to config file with restricted permissions"""
    try:
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config file
        with open(config_path, 'w') as f:
            json.dump({"api_key": api_key}, f)

        # Set restrictive permissions on Unix-like systems
        try:
            os.chmod(config_path, 0o600)
        except OSError:
            pass  # Ignore permission setting failures on some systems

        print(f"API key saved to: {config_path}")
    except Exception as e:
        print(f"Warning: Could not save API key to config file: {e}")

def get_api_key() -> str:
    """Get API key from config file, environment variable, or interactive input"""
    # Environment variable should override local config for CI and one-off runs.
    api_key = os.environ.get('MODELSCOPE_API_KEY')
    if api_key:
        return api_key

    # Check config file first
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'api_key' in config:
                    return config['api_key']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to read config file: {e}")

    # Interactive prompt for API key
    print("ModelScope API key not found.")
    print(f"Get your API key from: https://modelscope.cn/my/myaccesstoken")
    print()

    # Try to use secure input, fallback to regular input
    if HAS_GETPASS:
        try:
            api_key = getpass("Enter your Model ModelScope API key (input will be hidden): ")
        except EOFError:
            # Non-interactive environment
            print()
            print("Error: No API key found.")
            print(f"\nPlease set your API key:")
            print(f"1. Create config file at: {config_path}")
            print(f"2. Or set environment variable: MODELSCOPE_API_KEY")
            sys.exit(1)
    else:
        api_key = input("Enter your Model ModelScope API key: ")

    # Validate API key format (Model ModelScope API keys start with 'ms-')
    if not api_key or not api_key.startswith('ms-'):
        print("Warning: API key format looks incorrect (should start with 'ms-')")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            sys.exit(1)

    # Ask to save API key
    print()
    save_option = input("Save API key to config file for future use? (Y/n): ").strip().lower()
    if save_option in ('', 'y', 'yes'):
        save_api_key(api_key, config_path)

    return api_key

def generate_image(
    prompt: str,
    model: str = "Tongyi-MAI/Z-Image-Turbo",
    loras: Optional[str | Dict[str, float]] = None,
    output_path: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Generate an image using Model ModelScope API

    Args:
        prompt: Text prompt for image generation
        model: Model ID to use (default: Tongyi-MAI/Z-Image-Turbo)
        loras: Optional LoRA config - either string (single) or dict (multiple)
        output_path: Optional output file path (default: result_image.jpg)
        api_key: Optional API key (default: from env or config)

    Returns:
        Path to generated image
    """
    if api_key is None:
        api_key = get_api_key()

    if output_path is None:
        output_path = "result_image.jpg"

    common_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build request payload
    payload = {
        "model": model,
        "prompt": prompt
    }

    if loras is not None:
        payload["loras"] = loras

    # Submit generation task
    try:
        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"Error submitting task: {exc}")
        sys.exit(1)

    if response.status_code != 200:
        print(f"Error submitting task: {response.status_code}")
        print(response.text)
        sys.exit(1)

    task_id = response.json()["task_id"]
    print(f"Task submitted: {task_id}")

    # Poll for completion
    for _ in range(MAX_POLL_ATTEMPTS):
        try:
            result = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            print(f"Error checking status: {exc}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if result.status_code != 200:
            print(f"Error checking status: {result.status_code}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        data = result.json()
        status = data.get("task_status", "UNKNOWN")
        print(f"Status: {status}")

        if status == "SUCCEED":
            image_url = data["output_images"][0]
            print(f"Downloading from: {image_url}")

            try:
                img_response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
                img_response.raise_for_status()
                image = Image.open(BytesIO(img_response.content))
                image.save(output_path)
            except (requests.RequestException, OSError) as exc:
                print(f"Error downloading or saving image: {exc}")
                sys.exit(1)

            print(f"Image saved to: {output_path}")
            return output_path

        elif status == "FAILED":
            print("Image Generation Failed.")
            if "error" in data:
                print(f"Error: {data['error']}")
            sys.exit(1)

        time.sleep(POLL_INTERVAL_SECONDS)

    print("Timeout: Image generation took too long")
    sys.exit(1)


def parse_loras(single_lora: Optional[str], multiple_loras: Optional[str]) -> Optional[str | Dict[str, float]]:
    """Parse mutually exclusive LoRA CLI options into API payload format."""
    if single_lora and multiple_loras:
        raise ValueError("Use either --lora or --loras, not both.")

    if single_lora:
        return single_lora

    if multiple_loras:
        try:
            parsed = json.loads(multiple_loras)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON for --loras: {exc}") from exc

        if not isinstance(parsed, dict) or not parsed:
            raise ValueError("--loras must be a non-empty JSON object.")

        total_weight = 0.0
        normalized: Dict[str, float] = {}
        for lora_id, weight in parsed.items():
            if not isinstance(lora_id, str) or not lora_id:
                raise ValueError("Each LoRA id must be a non-empty string.")
            if not isinstance(weight, (int, float)):
                raise ValueError(f"Weight for '{lora_id}' must be a number.")
            if weight <= 0:
                raise ValueError(f"Weight for '{lora_id}' must be positive.")
            normalized[lora_id] = float(weight)
            total_weight += float(weight)

        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(f"LoRA weights must sum to 1.0, got {total_weight:.6f}.")

        return normalized

    return None

def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate images using ModelScope Z-Image models")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("output_path", nargs="?", default=None, help="Output file path (default: result_image.jpg)")
    parser.add_argument("--model", default="Tongyi-MAI/Z-Image-Turbo", help="Model ID to use (default: Tongyi-MAI/Z-Image-Turbo)")
    parser.add_argument("--lora", help="Single LoRA model ID")
    parser.add_argument("--loras", help="JSON object of multiple LoRA IDs to weights, e.g. '{\"foo\": 0.6, \"bar\": 0.4}'")

    args = parser.parse_args()

    try:
        loras = parse_loras(args.lora, args.loras)
    except ValueError as exc:
        parser.error(str(exc))

    generate_image(
        args.prompt,
        model=args.model,
        loras=loras,
        output_path=args.output_path
    )

if __name__ == "__main__":
    main()
