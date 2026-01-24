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
from typing import Optional, Dict, Any
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

def get_config_path() -> Path:
    """Get the config file path (prefer XDG config dir, otherwise ~/.config/modelscope/)"""
    # Try XDG config directory
    xdg_config = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config:
        config_dir = Path(xdg_config) / 'modelscope'
    else:
        config_dir = Path.home() / '.config' / 'modelscope'

    # Fallback to ~/.modelscope if it exists
    legacy_dir = Path.home() / '.modelscope'
    if legacy_dir.exists():
        return legacy_dir / 'config.json'
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

    # Check environment variable
    api_key = os.environ.get('MODELSCOPE_API_KEY')
    if api_key:
        return api_key

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
    response = requests.post(
        f"{BASE_URL}v1/images/generations",
        headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
    )

    if response.status_code != 200:
        print(f"Error submitting task: {response.status_code}")
        print(response.text)
        sys.exit(1)

    task_id = response.json()["task_id"]
    print(f"Task submitted: {task_id}")

    # Poll for completion
    max_attempts = 60  # 5 minutes max
    for attempt in range(max_attempts):
        result = requests.get(
            f"{BASE_URL}v1/tasks/{task_id}",
            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
        )

        if result.status_code != 200:
            print(f"Error checking status: {result.status_code}")
            time.sleep(5)
            continue

        data = result.json()
        status = data.get("task_status", "UNKNOWN")
        print(f"Status: {status}")

        if status == "SUCCEED":
            image_url = data["output_images"][0]
            print(f"Downloading from: {image_url}")

            img_response = requests.get(image_url)
            image = Image.open(BytesIO(img_response.content))
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            return output_path

        elif status == "FAILED":
            print("Image Generation Failed.")
            if "error" in data:
                print(f"Error: {data['error']}")
            sys.exit(1)

        time.sleep(5)

    print("Timeout: Image generation took too long")
    sys.exit(1)

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <prompt> [output_path] [model]")
        print("Example: python generate_image.py 'A golden cat' output.jpg")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else "Tongyi-MAI/Z-Image-Turbo"

    generate_image(prompt, model=model, output_path=output_path)

if __name__ == "__main__":
    main()
