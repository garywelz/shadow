#!/usr/bin/env python3
"""
Convert PDF files to Markdown format
Supports multiple PDF extraction methods
"""

import os
import sys
import subprocess
from pathlib import Path
import re

def convert_pdf_with_pdftotext(pdf_path, output_path):
    """Convert PDF to text using pdftotext command"""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_pdf_with_pymupdf(pdf_path, output_path):
    """Convert PDF to text using PyMuPDF (fitz)"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content.append(text)
        
        doc.close()
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with PyMuPDF: {e}")
        return False

def convert_pdf_with_pypdf2(pdf_path, output_path):
    """Convert PDF to text using PyPDF2"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_content.append(text)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with PyPDF2: {e}")
        return False

def convert_pdf_with_pdfplumber(pdf_path, output_path):
    """Convert PDF to text using pdfplumber"""
    try:
        import pdfplumber
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
        return False

def text_to_markdown(text_content):
    """Convert plain text to basic markdown format"""
    # Clean up the text
    text = text_content.strip()
    
    # Remove excessive blank lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Try to detect and format headers (lines that are all caps or have specific patterns)
    lines = text.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue
        
        # Detect potential headers (short lines, all caps, or lines followed by blank line)
        if len(stripped) < 100 and stripped.isupper() and len(stripped.split()) < 10:
            # Check if next line is blank or different
            if i + 1 < len(lines) and (not lines[i+1].strip() or lines[i+1].strip()[0].islower()):
                formatted_lines.append(f"## {stripped.title()}")
                continue
        
        formatted_lines.append(stripped)
    
    return '\n'.join(formatted_lines)

def convert_pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to Markdown using available method"""
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    # Try different conversion methods in order of preference
    methods = [
        ("pdftotext", convert_pdf_with_pdftotext),
        ("PyMuPDF", convert_pdf_with_pymupdf),
        ("pdfplumber", convert_pdf_with_pdfplumber),
        ("PyPDF2", convert_pdf_with_pypdf2),
    ]
    
    temp_text_path = output_path.with_suffix('.txt')
    
    for method_name, method_func in methods:
        print(f"  Trying {method_name}...", end=' ')
        if method_func(str(pdf_path), str(temp_text_path)):
            print("✓ Success")
            break
        else:
            print("✗ Not available")
    else:
        print(f"❌ No PDF conversion method available for {pdf_path.name}")
        print("   Please install one of: pdftotext, PyMuPDF, pdfplumber, or PyPDF2")
        return False
    
    # Read the extracted text and convert to markdown
    try:
        with open(temp_text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        markdown_content = text_to_markdown(text_content)
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Clean up temp file
        if temp_text_path.exists():
            temp_text_path.unlink()
        
        return True
    except Exception as e:
        print(f"❌ Error processing text: {e}")
        return False

def process_directory(directory, output_base='manuscripts'):
    """Process all PDFs in a directory structure"""
    directory = Path(directory)
    pdf_files = list(directory.rglob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF file(s) to convert:\n")
    
    success_count = 0
    for pdf_file in pdf_files:
        # Create output path maintaining directory structure
        relative_path = pdf_file.relative_to(directory)
        output_dir = Path(output_base) / relative_path.parent
        output_file = output_dir / f"{pdf_file.stem}.md"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting: {pdf_file.name}")
        if convert_pdf_to_markdown(pdf_file, output_file):
            print(f"  ✓ Created: {output_file}\n")
            success_count += 1
        else:
            print(f"  ✗ Failed: {pdf_file.name}\n")
    
    print(f"✅ Successfully converted {success_count}/{len(pdf_files)} files")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert PDF files to Markdown')
    parser.add_argument('input', nargs='?', default='manuscripts',
                       help='Input directory (default: manuscripts)')
    parser.add_argument('-o', '--output', default='manuscripts',
                       help='Output directory (default: manuscripts)')
    
    args = parser.parse_args()
    
    process_directory(args.input, args.output)

if __name__ == '__main__':
    main()

