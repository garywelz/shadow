#!/usr/bin/env python3
"""
Word Document to Markdown Converter
Converts .doc and .docx files to Markdown format for The Shadow of Lillya project.
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import re

def convert_with_pandoc(input_file, output_file):
    """Convert document using pandoc (preferred method)"""
    try:
        cmd = [
            'pandoc',
            input_file,
            '-f', 'docx' if input_file.endswith('.docx') else 'doc',
            '-t', 'markdown',
            '--wrap=none',
            '--markdown-headings=atx',
            '-o', output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully converted {input_file} to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Pandoc conversion failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Pandoc not found. Please install pandoc first.")
        return False

def clean_markdown_content(content):
    """Clean up the markdown content for better formatting"""
    # Remove excessive blank lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Fix common formatting issues
    content = re.sub(r'\\\*', '*', content)  # Fix escaped asterisks
    content = re.sub(r'\\_', '_', content)   # Fix escaped underscores
    
    # Ensure proper spacing around headers
    content = re.sub(r'([^\n])\n(#+\s)', r'\1\n\n\2', content)
    
    # Clean up list formatting
    content = re.sub(r'\n\s*(\d+\.|\*|\-)\s*\n', r'\n\1 ', content)
    
    return content.strip()

def process_file(input_path, output_dir):
    """Process a single file"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return False
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    output_file = output_dir / f"{input_file.stem}.md"
    
    # Convert using pandoc
    if convert_with_pandoc(str(input_file), str(output_file)):
        # Clean up the content
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            cleaned_content = clean_markdown_content(content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"📝 Cleaned and formatted: {output_file}")
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not clean content: {e}")
            return True  # Still successful even if cleaning failed
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Convert Word documents to Markdown')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', default='manuscripts', 
                       help='Output directory (default: manuscripts)')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Process directories recursively')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        if input_path.suffix.lower() in ['.doc', '.docx']:
            success = process_file(input_path, args.output)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unsupported file type: {input_path.suffix}")
            sys.exit(1)
    
    elif input_path.is_dir():
        # Directory
        pattern = '**/*' if args.recursive else '*'
        word_files = list(input_path.glob(pattern))
        word_files = [f for f in word_files if f.suffix.lower() in ['.doc', '.docx']]
        
        if not word_files:
            print(f"❌ No Word documents found in {input_path}")
            sys.exit(1)
        
        print(f"📚 Found {len(word_files)} Word document(s) to convert:")
        for f in word_files:
            print(f"  - {f}")
        
        success_count = 0
        for word_file in word_files:
            if process_file(word_file, args.output):
                success_count += 1
        
        print(f"\n✅ Successfully converted {success_count}/{len(word_files)} files")
        sys.exit(0 if success_count == len(word_files) else 1)
    
    else:
        print(f"❌ File or directory not found: {input_path}")
        sys.exit(1)

if __name__ == '__main__':
    main()



