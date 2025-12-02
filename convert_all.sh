#!/bin/bash

# Convert All Word Documents to Markdown
# Usage: ./convert_all.sh [input_directory] [output_directory]

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-manuscripts}"

echo "📚 Converting Word documents to Markdown..."
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Convert all .doc and .docx files
python3 convert_docs.py "$INPUT_DIR" -o "$OUTPUT_DIR" -r

echo ""
echo "✅ Conversion complete!"
echo "📁 Check the '$OUTPUT_DIR' directory for your Markdown files."



