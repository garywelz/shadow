#!/usr/bin/env python3
"""
Organize and identify duplicate manuscript files
Helps organize The Shadow of Lillya PDF files and identify duplicates
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil

def get_file_hash(filepath):
    """Calculate MD5 hash of file to identify duplicates"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_info(filepath):
    """Get file information"""
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'hash': get_file_hash(filepath),
        'name': os.path.basename(filepath),
        'path': filepath
    }

def find_duplicates(directory='.'):
    """Find duplicate files based on content hash"""
    files_by_hash = defaultdict(list)
    pdf_files = []
    
    # Find all PDF files
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and certain folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['manuscripts', 'analysis', 'completion_attempts']]
        
        for file in files:
            if file.lower().endswith('.pdf'):
                filepath = os.path.join(root, file)
                try:
                    info = get_file_info(filepath)
                    files_by_hash[info['hash']].append(info)
                    pdf_files.append(info)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return files_by_hash, pdf_files

def analyze_files():
    """Analyze and organize the manuscript files"""
    print("🔍 Analyzing manuscript files...\n")
    
    files_by_hash, pdf_files = find_duplicates()
    
    # Find duplicates
    duplicates = {h: files for h, files in files_by_hash.items() if len(files) > 1}
    
    if duplicates:
        print("⚠️  DUPLICATE FILES FOUND (same content):\n")
        for hash_val, files in duplicates.items():
            print(f"  Hash: {hash_val[:16]}...")
            for f in files:
                print(f"    - {f['name']} ({f['size']:,} bytes)")
            print()
    else:
        print("✅ No exact duplicates found (files with identical content)\n")
    
    # Group by similar names
    print("📚 FILES FOUND:\n")
    
    # Identify likely edited version (sent to Tyson)
    edited_candidates = []
    unedited_candidates = []
    notes_files = []
    
    for info in pdf_files:
        name_lower = info['name'].lower()
        if 'tyson' in name_lower or 'rough draft' in name_lower:
            edited_candidates.append(info)
        elif 'notes' in name_lower or 'outline' in name_lower:
            notes_files.append(info)
        else:
            unedited_candidates.append(info)
    
    print("📝 LIKELY EDITED VERSION (sent to Tyson Cornell):")
    if edited_candidates:
        for f in edited_candidates:
            print(f"  ✓ {f['name']}")
            print(f"    Size: {f['size']:,} bytes")
            print(f"    Path: {f['path']}\n")
    else:
        print("  (None identified - check manually)\n")
    
    print("📄 OTHER VERSIONS / UNEDITED MATERIAL:")
    if unedited_candidates:
        for f in unedited_candidates:
            print(f"  • {f['name']}")
            print(f"    Size: {f['size']:,} bytes")
            print(f"    Path: {f['path']}\n")
    else:
        print("  (None found)\n")
    
    print("📋 NOTES & OUTLINES:")
    if notes_files:
        for f in notes_files:
            print(f"  • {f['name']}")
            print(f"    Size: {f['size']:,} bytes")
            print(f"    Path: {f['path']}\n")
    else:
        print("  (None found)\n")
    
    return {
        'duplicates': duplicates,
        'edited_candidates': edited_candidates,
        'unedited_candidates': unedited_candidates,
        'notes_files': notes_files,
        'all_files': pdf_files
    }

def organize_files(analysis, auto_organize=False):
    """Organize files into appropriate directories"""
    if not auto_organize:
        print("\n💡 SUGGESTED ORGANIZATION:\n")
        print("To organize files, run with --organize flag")
        print("Or manually move files to:")
        print("  - manuscripts/Shadow_of_Lillya/edited_version/")
        print("  - manuscripts/Shadow_of_Lillya/unedited_material/")
        return
    
    print("\n📁 Organizing files...\n")
    
    # Organize edited version
    edited_dir = Path("manuscripts/Shadow_of_Lillya/edited_version")
    edited_dir.mkdir(parents=True, exist_ok=True)
    
    for f in analysis['edited_candidates']:
        dest = edited_dir / f['name']
        if not dest.exists():
            shutil.move(f['path'], dest)
            print(f"  ✓ Moved to edited_version: {f['name']}")
        else:
            print(f"  ⚠️  Skipped (already exists): {f['name']}")
    
    # Organize unedited material
    unedited_dir = Path("manuscripts/Shadow_of_Lillya/unedited_material")
    unedited_dir.mkdir(parents=True, exist_ok=True)
    
    for f in analysis['unedited_candidates']:
        dest = unedited_dir / f['name']
        if not dest.exists():
            shutil.move(f['path'], dest)
            print(f"  ✓ Moved to unedited_material: {f['name']}")
        else:
            print(f"  ⚠️  Skipped (already exists): {f['name']}")
    
    # Organize notes
    notes_dir = Path("manuscripts/Shadow_of_Lillya")
    for f in analysis['notes_files']:
        dest = notes_dir / f['name']
        if not dest.exists():
            shutil.move(f['path'], dest)
            print(f"  ✓ Moved to Shadow_of_Lillya: {f['name']}")
        else:
            print(f"  ⚠️  Skipped (already exists): {f['name']}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Organize manuscript files and identify duplicates')
    parser.add_argument('--organize', action='store_true', 
                       help='Automatically organize files into directories')
    
    args = parser.parse_args()
    
    analysis = analyze_files()
    
    if args.organize:
        organize_files(analysis, auto_organize=True)
        print("\n✅ Organization complete!")
    else:
        organize_files(analysis, auto_organize=False)

if __name__ == '__main__':
    main()

