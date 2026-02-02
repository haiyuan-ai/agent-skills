#!/usr/bin/env python3
"""
Mermaid to PNG Converter
Convert Mermaid diagrams in Markdown files to PNG images.

GitHub Repository: https://github.com/haiyuan-ai/agent-skills
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple


def extract_mermaid_diagrams(content: str) -> List[Tuple[str, str, int]]:
    """Extract Mermaid diagrams from Markdown content."""
    pattern = r'```mermaid\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)

    diagrams = []
    for idx, match in enumerate(matches):
        code = match.group(1).strip()
        lines = code.split('\n')
        title = lines[0] if lines else f"diagram_{idx}"
        diagrams.append((code, title, idx))

    return diagrams


def generate_diagram_hash(code: str) -> str:
    """Generate hash for diagram code."""
    return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]


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

    try:
        cmd = [
            'npx', '@mermaid-js/mermaid-cli',
            '-i', temp_mmd_path,
            '-o', output_path,
            '-b', background,
            '-w', str(width)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
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


def replace_mermaid_with_images(content: str, image_mapping: dict) -> str:
    """Replace Mermaid code blocks with image references."""
    pattern = r'```mermaid\n(.*?)```'

    idx_counter = [0]
    def replace_func(match):
        current_idx = idx_counter[0]
        idx_counter[0] += 1

        if current_idx in image_mapping:
            image_path = image_mapping[current_idx]
            alt_text = f"Diagram {current_idx + 1}"
            return f"![{alt_text}]({image_path})"
        return match.group(0)

    return re.sub(pattern, replace_func, content, flags=re.DOTALL)


def main():
    parser = argparse.ArgumentParser(description='Convert Mermaid to PNG')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output-dir', default='./output', help='Output directory')
    parser.add_argument('-w', '--width', type=int, default=1200, help='Image width')
    parser.add_argument('-b', '--background', default='white', help='Background color')
    parser.add_argument('-f', '--format', default='png', choices=['png', 'svg'], help='Output format')
    parser.add_argument('--replace', action='store_true', help='Replace code blocks with images')

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

    image_mapping = {}
    for idx, (code, title, _) in enumerate(diagrams):
        hash_str = generate_diagram_hash(code)
        filename = f"diagram_{idx + 1}_{hash_str}.{args.format}"
        output_path = os.path.join(args.output_dir, filename)

        print(f"\nConverting diagram {idx + 1}: {title}")
        print(f"  Output: {output_path}")

        success = convert_mermaid_to_image(
            code=code,
            output_path=output_path,
            width=args.width,
            background=args.background,
            fmt=args.format
        )

        if success:
            image_mapping[idx] = output_path
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
