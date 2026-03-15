#!/bin/bash
# Optimized PDF conversion for Markdown with CJK support
# Usage: ./convert-to-pdf.sh input.md [output.pdf]

set -e

INPUT="${1:-input.md}"
OUTPUT="${2:-${1%.md}.pdf}"

echo "Converting $INPUT to $OUTPUT..."

# Create temporary header file
HEADER=$(mktemp)
cat > "$HEADER" << 'TEXEOF'
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\setCJKmonofont{Sarasa Fixed SC}
\setmonofont{Sarasa Fixed SC}
\usepackage{geometry}
\geometry{margin=1.5cm,a4paper}

% Force all code tokens to use monospace font (fix ASCII alignment)
\def\NormalTok#1{{\ttfamily#1}}
\def\DataTypeTok#1{{\ttfamily#1}}
\def\DecValTok#1{{\ttfamily#1}}
\def\BaseNTok#1{{\ttfamily#1}}
\def\FloatTok#1{{\ttfamily#1}}
\def\CharTok#1{{\ttfamily#1}}
\def\StringTok#1{{\ttfamily#1}}
\def\CommentTok#1{{\ttfamily#1}}
\def\OtherTok#1{{\ttfamily#1}}
\def\AlertTok#1{{\ttfamily#1}}
\def\FunctionTok#1{{\ttfamily#1}}
\def\KeywordTok#1{{\ttfamily#1}}
\def\OperatorTok#1{{\ttfamily#1}}
\def\ConstantTok#1{{\ttfamily#1}}
\def\SpecialCharTok#1{{\ttfamily#1}}
\def\VerbatimStringTok#1{{\ttfamily#1}}
TEXEOF

pandoc "$INPUT" -o "$OUTPUT" \
  --pdf-engine=xelatex \
  -V fontsize=11pt \
  -H "$HEADER" \
  2>&1 | grep -v "Missing character" | grep -v "xeCJK Warning" || true

rm -f "$HEADER"

if [ -f "$OUTPUT" ]; then
  echo "✓ Created: $OUTPUT ($(ls -lh "$OUTPUT" | awk '{print $5}'))"
  echo "  Font: CJK=PingFang SC, Code=Sarasa Fixed SC (ttfamily)"
  echo "  Margins: 1.5cm, Font size: 11pt"
else
  echo "✗ Failed"
  exit 1
fi
