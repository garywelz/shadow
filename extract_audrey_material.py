#!/usr/bin/env python3
"""
Extract and Organize Audrey Berger Welz's Original Material
Prioritizes her original writing and identifies what's truly hers
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json
from datetime import datetime

class AudreyMaterialExtractor:
    """Extract and organize Audrey's original material"""
    
    def __init__(self):
        self.manuscripts_dir = Path("manuscripts")
        self.audrey_material_dir = Path("manuscripts/Shadow_of_Lillya/audrey_original")
        self.audrey_material_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_versions(self) -> Dict[str, Dict]:
        """Load all versions of the manuscript"""
        versions = {}
        
        # Load edited version (sent to Tyson - most likely to be Audrey's)
        edited_dir = self.manuscripts_dir / "Shadow_of_Lillya" / "edited_version"
        for md_file in edited_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                versions['edited_tyson'] = {
                    'content': content,
                    'source': str(md_file),
                    'priority': 1,  # Highest priority - sent to editor
                    'date': '2020-03-12',  # From filename
                    'description': 'Rough Draft sent to Tyson Cornell at Rare Bird Books'
                }
        
        # Load unedited material (earlier versions - likely more of Audrey's work)
        unedited_dir = self.manuscripts_dir / "Shadow_of_Lillya" / "unedited_material"
        version_num = 2
        
        for md_file in sorted(unedited_dir.glob("*.md")):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = md_file.stem
                
                # Extract date from filename if possible
                date_match = re.search(r'(\d{2}_\d{2}_\d{2,4})|(\d{4}-\d{2}-\d{2})', filename)
                date = date_match.group() if date_match else None
                
                # Determine if this is likely Audrey's work
                is_audrey = True
                if 'v69' in filename or 'v73' in filename:
                    # Later versions might have ghost writer material
                    is_audrey = False
                    description = f"Later version - may contain ghost writer material"
                elif 'GW' in filename or 'gw' in filename:
                    # Explicitly marked as ghost writer
                    is_audrey = False
                    description = f"Ghost writer version"
                else:
                    description = f"Earlier version - likely Audrey's original work"
                
                versions[f'version_{version_num}'] = {
                    'content': content,
                    'source': str(md_file),
                    'priority': version_num if is_audrey else 100,  # Lower priority for non-Audrey
                    'date': date,
                    'is_audrey': is_audrey,
                    'description': description
                }
                version_num += 1
        
        return versions
    
    def extract_unique_paragraphs(self, versions: Dict[str, Dict]) -> Dict[str, List]:
        """Extract unique paragraphs from each version, prioritizing Audrey's work"""
        paragraph_sets = {}
        paragraph_to_version = defaultdict(list)
        
        # First, extract all paragraphs from highest priority (Audrey's) versions
        for version_id, version_data in sorted(versions.items(), key=lambda x: x[1]['priority']):
            content = version_data['content']
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
            
            paragraph_sets[version_id] = set()
            for para in paragraphs:
                # Normalize paragraph (remove extra whitespace, normalize quotes)
                normalized = re.sub(r'\s+', ' ', para).strip()
                if len(normalized) > 50:  # Only meaningful paragraphs
                    paragraph_sets[version_id].add(normalized)
                    paragraph_to_version[normalized].append(version_id)
        
        return paragraph_sets, paragraph_to_version
    
    def identify_audrey_core_material(self, versions: Dict[str, Dict]) -> Dict:
        """Identify core material that's most likely Audrey's original work"""
        paragraph_sets, paragraph_to_version = self.extract_unique_paragraphs(versions)
        
        # Material that appears in high-priority (Audrey's) versions
        audrey_versions = [v for v, d in versions.items() if d.get('is_audrey', True) and d['priority'] < 10]
        
        audrey_paragraphs = set()
        for version_id in audrey_versions:
            audrey_paragraphs.update(paragraph_sets.get(version_id, set()))
        
        # Remove paragraphs that only appear in low-priority (ghost writer) versions
        ghost_versions = [v for v, d in versions.items() if not d.get('is_audrey', True) or d['priority'] >= 10]
        ghost_paragraphs = set()
        for version_id in ghost_versions:
            ghost_paragraphs.update(paragraph_sets.get(version_id, set()))
        
        # Core Audrey material: appears in her versions but not exclusively in ghost writer versions
        core_material = audrey_paragraphs - (ghost_paragraphs - audrey_paragraphs)
        
        # Organize by source version
        organized_material = defaultdict(list)
        for para in core_material:
            sources = paragraph_to_version.get(para, [])
            # Find the highest priority source
            best_source = min(sources, key=lambda s: versions[s]['priority']) if sources else None
            if best_source:
                organized_material[best_source].append(para)
        
        return {
            'core_paragraphs': list(core_material),
            'organized_by_source': {k: v for k, v in organized_material.items()},
            'total_paragraphs': len(core_material),
            'sources': {k: versions[k]['description'] for k in organized_material.keys()}
        }
    
    def create_audrey_original_manuscript(self, core_material: Dict, versions: Dict = None) -> str:
        """Create a clean manuscript from Audrey's original material"""
        # Organize paragraphs in a logical order
        # Start with highest priority source
        all_paragraphs = []
        if versions:
            source_order = sorted(core_material['organized_by_source'].items(), 
                                key=lambda x: versions[x[0]]['priority'])
        else:
            source_order = list(core_material['organized_by_source'].items())
        
        for source_id, paragraphs in core_material['organized_by_source'].items():
            all_paragraphs.extend(paragraphs)
        
        # Create manuscript
        manuscript = f"""# The Shadow of Lillya
## Original Material by Audrey Berger Welz

**Compiled from:** {', '.join(core_material['sources'].values())}
**Total Paragraphs:** {core_material['total_paragraphs']}
**Compilation Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## Note on Material

This manuscript contains only material identified as Audrey Berger Welz's original work, extracted from her draft versions. Material from later ghost writer versions or other sources has been excluded to preserve the authenticity of her voice and vision.

---

{chr(10).join(all_paragraphs)}
"""
        return manuscript
    
    def save_audrey_material(self, core_material: Dict, manuscript: str):
        """Save Audrey's original material"""
        # Save the compiled manuscript
        manuscript_file = self.audrey_material_dir / "audrey_original_compiled.md"
        with open(manuscript_file, 'w', encoding='utf-8') as f:
            f.write(manuscript)
        
        # Save metadata
        metadata = {
            'compilation_date': datetime.now().isoformat(),
            'total_paragraphs': core_material['total_paragraphs'],
            'sources': core_material['sources'],
            'paragraph_count_by_source': {k: len(v) for k, v in core_material['organized_by_source'].items()}
        }
        
        metadata_file = self.audrey_material_dir / "compilation_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Save individual source files
        for source_id, paragraphs in core_material['organized_by_source'].items():
            source_file = self.audrey_material_dir / f"source_{source_id}.md"
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(f"# Material from {source_id}\n\n")
                f.write(f"{chr(10).join(paragraphs)}\n")
        
        return manuscript_file, metadata_file

def main():
    print("📚 Extracting Audrey Berger Welz's Original Material...\n")
    
    extractor = AudreyMaterialExtractor()
    
    # Load all versions
    print("📖 Loading all manuscript versions...")
    versions = extractor.load_all_versions()
    print(f"  ✓ Loaded {len(versions)} versions\n")
    
    # Identify core material
    print("🔍 Identifying Audrey's original material...")
    core_material = extractor.identify_audrey_core_material(versions)
    print(f"  ✓ Identified {core_material['total_paragraphs']} paragraphs of original material")
    print(f"  ✓ From {len(core_material['sources'])} source versions\n")
    
    # Create compiled manuscript
    print("📝 Compiling original manuscript...")
    manuscript = extractor.create_audrey_original_manuscript(core_material, versions)
    
    # Save files
    print("💾 Saving files...")
    manuscript_file, metadata_file = extractor.save_audrey_material(core_material, manuscript)
    
    print(f"\n✅ Complete!")
    print(f"  📄 Compiled manuscript: {manuscript_file}")
    print(f"  📊 Metadata: {metadata_file}")
    print(f"\n📋 Material organized by source:")
    for source, count in core_material['paragraph_count_by_source'].items():
        print(f"  - {source}: {count} paragraphs")

if __name__ == '__main__':
    main()

