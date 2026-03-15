#!/usr/bin/env python3
"""
Fix ASCII art alignment in Markdown files for better Word/PDF rendering.

Usage:
    python3 fix-ascii-art.py input.md
    python3 fix-ascii-art.py input.md --output=fixed.md
    python3 fix-ascii-art.py input.md --check  # Just check, don't modify

This script pads lines in ASCII box diagrams to equal width,
ensuring clean right borders when converted to Word or PDF.
"""

import re
import argparse
from pathlib import Path


def fix_ascii_box(match):
    """Fix alignment in a single code block containing ASCII art."""
    lang = match.group(1) or 'text'
    block = match.group(2)
    lines = block.split('\n')
    
    # Check if this block contains ASCII box characters
    box_chars = set('┌┐└┘─│├┤┬┴┼')
    box_lines_indices = []
    max_width = 0
    
    for i, line in enumerate(lines):
        if any(c in line for c in box_chars):
            box_lines_indices.append(i)
            max_width = max(max_width, len(line))
    
    if max_width < 10 or not box_lines_indices:
        return match.group(0)  # Not a valid box
    
    # Pad all box lines to max_width
    fixed_lines = list(lines)
    for i in box_lines_indices:
        if len(fixed_lines[i]) < max_width:
            fixed_lines[i] = fixed_lines[i] + ' ' * (max_width - len(fixed_lines[i]))
    
    return f'```{lang}\n' + '\n'.join(fixed_lines) + '```'


def check_file(content):
    """Check ASCII art alignment without modifying."""
    pattern = r'```(\w*)\n(.*?)```'
    blocks = re.findall(pattern, content, re.DOTALL)
    
    box_chars = set('┌┐└┘─│├┤┬┴┼')
    issues = []
    
    for i, (lang, block) in enumerate(blocks):
        lines = block.split('\n')
        box_lines = [l for l in lines if any(c in l for c in box_chars)]
        
        if len(box_lines) < 2:
            continue
        
        widths = [len(l) for l in box_lines]
        if max(widths) - min(widths) > 0:
            issues.append({
                'block': i + 1,
                'lang': lang or 'text',
                'min_width': min(widths),
                'max_width': max(widths),
                'line_count': len(box_lines)
            })
    
    return issues


def fix_file(input_path, output_path=None, check_only=False):
    """Fix ASCII art alignment in a Markdown file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if check_only:
        issues = check_file(content)
        if issues:
            print(f"Found {len(issues)} misaligned ASCII blocks:\n")
            for issue in issues:
                print(f"  Block {issue['block']} (```{issue['lang']}): " +
                      f"width {issue['min_width']}-{issue['max_width']}, " +
                      f"{issue['line_count']} box lines")
            return 1
        else:
            print("✓ All ASCII art blocks are properly aligned")
            return 0
    
    # Fix all code blocks with ASCII art
    pattern = r'```(\w*)\n(.*?)```'
    fixed_content = re.sub(pattern, fix_ascii_box, content, flags=re.DOTALL)
    
    # Count fixes
    original_issues = check_file(content)
    
    # Save
    if output_path is None:
        output_path = input_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✓ Fixed {len(original_issues)} ASCII box blocks")
    print(f"  Output: {output_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Fix ASCII art alignment in Markdown for Word/PDF conversion'
    )
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('--output', '-o', help='Output file (default: overwrite input)')
    parser.add_argument('--check', action='store_true', help='Check only, don\'t modify')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        return 1
    
    return fix_file(input_path, output_path, args.check)


if __name__ == '__main__':
    exit(main())
