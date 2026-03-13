#!/usr/bin/env python3
"""
Mermaid to PNG Converter
Convert Mermaid diagrams in Markdown files to styled PNG images.

GitHub Repository: https://github.com/haiyuan-ai/agent-skills
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from styles import (
    get_available_styles,
    inject_style_into_diagram,
    get_style_info
)


MERMAID_BLOCK_PATTERN = re.compile(
    r"```mermaid[^\n\r]*\r?\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)

CHART_TYPE_PATTERNS = (
    ("sequence", re.compile(r"^\s*sequenceDiagram\b", re.MULTILINE)),
    ("gantt", re.compile(r"^\s*gantt\b", re.MULTILINE)),
    ("class", re.compile(r"^\s*classDiagram\b", re.MULTILINE)),
    ("state", re.compile(r"^\s*stateDiagram(?:-v2)?\b", re.MULTILINE)),
    ("flowchart", re.compile(r"^\s*(?:graph|flowchart)\b", re.MULTILINE)),
)


def extract_mermaid_diagrams(content: str) -> List[Tuple[str, str, int]]:
    """Extract Mermaid diagrams from Markdown content."""
    diagrams = []
    for idx, match in enumerate(MERMAID_BLOCK_PATTERN.finditer(content)):
        code = match.group(1).strip()
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        title = lines[0] if lines else f"diagram_{idx + 1}"
        diagrams.append((code, title, idx))

    return diagrams


def generate_diagram_hash(code: str) -> str:
    """Generate hash for diagram code."""
    return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]


def detect_chart_type(code: str) -> str:
    """Infer Mermaid chart type from diagram source."""
    for chart_type, pattern in CHART_TYPE_PATTERNS:
        if pattern.search(code):
            return chart_type
    return "flowchart"


def resolve_mmdc_command() -> List[str]:
    """Prefer a locally installed mermaid CLI and fall back to npx."""
    for binary in ("mmdc", "@mermaid-js/mermaid-cli"):
        resolved = shutil.which(binary)
        if resolved:
            return [resolved]
    return ["npx", "@mermaid-js/mermaid-cli"]


def convert_mermaid_to_image(
    code: str,
    output_path: str,
    width: int = 1200,
    background: str = "white",
    fmt: str = "png"
) -> bool:
    """Convert Mermaid code to image using mermaid-cli."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(code)
        temp_mmd_path = f.name
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"args":["--no-sandbox","--disable-setuid-sandbox"]}')
        temp_puppeteer_config = f.name

    try:
        cmd = resolve_mmdc_command() + [
            '-i', temp_mmd_path,
            '-o', output_path,
            '-b', background,
            '-w', str(width),
            '-p', temp_puppeteer_config,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            if "Failed to launch the browser process" in result.stderr:
                print(
                    "Hint: Mermaid CLI needs Chromium via Puppeteer. "
                    "If you are in a restricted sandbox/CI environment, run this outside the sandbox "
                    "or provide a Chrome/Puppeteer setup that can launch locally."
                )
            return False

        return True

    except subprocess.TimeoutExpired:
        print("Error: Conversion timed out")
        return False
    except FileNotFoundError:
        print("Error: mermaid-cli not found")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return False
    finally:
        if os.path.exists(temp_mmd_path):
            os.unlink(temp_mmd_path)
        if os.path.exists(temp_puppeteer_config):
            os.unlink(temp_puppeteer_config)


def replace_mermaid_with_images(content: str, image_mapping: dict) -> str:
    """Replace Mermaid code blocks with image references."""
    idx_counter = [0]
    def replace_func(match):
        current_idx = idx_counter[0]
        idx_counter[0] += 1

        if current_idx in image_mapping:
            image_path = image_mapping[current_idx]
            alt_text = f"Diagram {current_idx + 1}"
            return f"![{alt_text}]({image_path})"
        return match.group(0)

    return MERMAID_BLOCK_PATTERN.sub(replace_func, content)


def main():
    parser = argparse.ArgumentParser(description='Convert Mermaid to PNG with style themes')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output-dir', default='./output', help='Output directory')
    parser.add_argument('-w', '--width', type=int, default=1200, help='Image width')
    parser.add_argument('-b', '--background', default='white', help='Background color')
    parser.add_argument('-f', '--format', default='png', choices=['png', 'svg'], help='Output format')
    parser.add_argument('--replace', action='store_true', help='Replace code blocks with images')
    parser.add_argument('--style', choices=get_available_styles(), help='Apply a built-in style theme')
    parser.add_argument(
        '--chart-type',
        default='auto',
        choices=['auto', 'flowchart', 'sequence', 'gantt', 'class', 'state'],
        help='Optimize for specific chart type, or auto-detect from each diagram',
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()

    diagrams = extract_mermaid_diagrams(content)

    if not diagrams:
        print("No Mermaid diagrams found.")
        sys.exit(0)

    print(f"Found {len(diagrams)} diagram(s)")

    # Get style info for display
    if args.style:
        style_info = get_style_info(args.style)
        if style_info:
            print(f"Using style: {style_info['name']} - {style_info['description']}")

    image_mapping: Dict[int, str] = {}
    output_dir = Path(args.output_dir)
    for idx, (code, title, _) in enumerate(diagrams):
        chart_type = detect_chart_type(code) if args.chart_type == 'auto' else args.chart_type

        # Inject style if specified
        if args.style:
            code = inject_style_into_diagram(code, args.style, chart_type)

        hash_str = generate_diagram_hash(code)
        filename = f"diagram_{idx + 1}_{hash_str}.{args.format}"
        output_path = output_dir / filename

        print(f"\nConverting diagram {idx + 1}: {title}")
        print(f"  Chart type: {chart_type}")
        print(f"  Output: {output_path}")

        # Use style background if available, otherwise use args.background
        background = args.background
        if args.style:
            from styles import STYLES
            background = STYLES.get(args.style, {}).get("background", args.background)

        success = convert_mermaid_to_image(
            code=code,
            output_path=str(output_path),
            width=args.width,
            background=background,
            fmt=args.format
        )

        if success:
            image_mapping[idx] = output_path.name
            print(f"  Success")
        else:
            print(f"  Failed")

    if args.replace and image_mapping:
        output_md_path = os.path.join(
            args.output_dir,
            f"{os.path.splitext(os.path.basename(args.input))[0]}_converted.md"
        )

        new_content = replace_mermaid_with_images(content, image_mapping)

        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"\nConverted Markdown: {output_md_path}")

    print(f"\nDone! {len(image_mapping)}/{len(diagrams)} diagrams converted.")


if __name__ == '__main__':
    main()
