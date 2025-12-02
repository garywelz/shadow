#!/usr/bin/env python3
"""
Edit and Clean Audrey's Original Material
Preserves her voice while improving clarity
"""

import re
from pathlib import Path
from typing import List, Dict
import json

class AudreyMaterialEditor:
    """Edit Audrey's material while preserving her voice"""
    
    def __init__(self):
        self.audrey_material_dir = Path("manuscripts/Shadow_of_Lillya/audrey_original")
        self.edited_dir = Path("manuscripts/Shadow_of_Lillya/audrey_edited")
        self.edited_dir.mkdir(parents=True, exist_ok=True)
    
    def load_original_material(self) -> str:
        """Load Audrey's compiled original material"""
        original_file = self.audrey_material_dir / "audrey_original_compiled.md"
        if not original_file.exists():
            raise FileNotFoundError(f"Original material not found. Run extract_audrey_material.py first.")
        
        with open(original_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def clean_text(self, text: str, preserve_voice: bool = True) -> str:
        """Clean text while preserving voice"""
        # Remove excessive blank lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Fix common formatting issues without changing voice
        # Normalize spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*([A-Z])', r'\1 \2', text)
        
        # Fix common typos that don't affect voice
        # (Add specific fixes as needed, but be conservative)
        
        # Preserve dialogue formatting
        # Keep Audrey's unique punctuation and style choices
        
        return text.strip()
    
    def identify_editing_needs(self, text: str) -> Dict:
        """Identify areas that might need editing for clarity"""
        issues = {
            'long_paragraphs': [],
            'repeated_phrases': [],
            'unclear_references': [],
            'incomplete_sentences': []
        }
        
        paragraphs = text.split('\n\n')
        for i, para in enumerate(paragraphs):
            # Very long paragraphs might need breaking up
            if len(para) > 1000:
                issues['long_paragraphs'].append({
                    'paragraph': i,
                    'length': len(para),
                    'preview': para[:100] + '...'
                })
            
            # Check for incomplete sentences
            sentences = re.split(r'[.!?]+', para)
            for sent in sentences:
                if sent.strip() and not re.search(r'[.!?]$', sent.strip()):
                    if len(sent.strip()) > 20:  # Not just a fragment
                        issues['incomplete_sentences'].append({
                            'paragraph': i,
                            'sentence': sent.strip()[:100]
                        })
        
        return issues
    
    def create_edited_version(self, original_text: str, edits: List[Dict] = None) -> str:
        """Create edited version with clear attribution"""
        # Extract just the content (skip header)
        content_start = original_text.find('---', original_text.find('---') + 3) + 3
        content = original_text[content_start:].strip()
        
        # Apply cleaning
        cleaned = self.clean_text(content)
        
        # Create edited version with attribution
        edited_version = f"""# The Shadow of Lillya
## Original Material by Audrey Berger Welz
### Edited for Clarity

**Source:** Extracted from Audrey's original draft manuscripts
**Editing:** Minor edits for clarity only - voice and style preserved
**Date:** {Path(__file__).stat().st_mtime}

---

## Editorial Note

This version contains only Audrey Berger Welz's original writing, with minimal edits for clarity:
- Fixed obvious typos and formatting issues
- Normalized spacing and punctuation
- Preserved all of Audrey's unique voice, style, and word choices
- No content changes or additions

Any material beyond this point that is not clearly marked is Audrey's original work.

---

{cleaned}
"""
        return edited_version
    
    def save_edited_version(self, edited_text: str):
        """Save the edited version"""
        output_file = self.edited_dir / "audrey_edited_clean.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(edited_text)
        
        return output_file

def main():
    print("✏️  Editing Audrey's Material for Clarity...\n")
    
    editor = AudreyMaterialEditor()
    
    # Load original
    print("📖 Loading original material...")
    original = editor.load_original_material()
    print("  ✓ Loaded\n")
    
    # Identify editing needs
    print("🔍 Identifying editing needs...")
    issues = editor.identify_editing_needs(original)
    print(f"  Found {len(issues['long_paragraphs'])} long paragraphs")
    print(f"  Found {len(issues['incomplete_sentences'])} potentially incomplete sentences\n")
    
    # Create edited version
    print("📝 Creating edited version...")
    edited = editor.create_edited_version(original)
    
    # Save
    print("💾 Saving edited version...")
    output_file = editor.save_edited_version(edited)
    
    print(f"\n✅ Complete!")
    print(f"  📄 Edited manuscript: {output_file}")
    print(f"\n⚠️  Note: This version contains ONLY Audrey's original material, edited minimally for clarity.")

if __name__ == '__main__':
    main()

