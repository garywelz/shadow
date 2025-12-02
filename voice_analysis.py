#!/usr/bin/env python3
"""
Voice Analysis Tools for The Shadow of Lillya
Analyzes writing style and compares completions with Audrey's voice
"""

import re
from pathlib import Path
from collections import Counter
from typing import Dict, List
import json

class VoiceAnalyzer:
    """Analyze writing style and voice"""
    
    def __init__(self):
        self.manuscripts_dir = Path("manuscripts")
    
    def load_reference_text(self) -> str:
        """Load reference text from Audrey's manuscripts"""
        texts = []
        
        # Load Circus of the Queens
        circus_dir = self.manuscripts_dir / "Circus_of_the_Queens"
        for md_file in circus_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                texts.append(f.read())
        
        # Load edited version
        edited_dir = self.manuscripts_dir / "Shadow_of_Lillya" / "edited_version"
        for md_file in edited_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                texts.append(f.read())
        
        return '\n\n'.join(texts)
    
    def analyze_style(self, text: str) -> Dict:
        """Analyze writing style metrics"""
        # Basic statistics
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Word frequency
        word_freq = Counter(words)
        most_common_words = word_freq.most_common(50)
        
        # Sentence length
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Paragraph length
        paragraph_lengths = [len(re.findall(r'\b\w+\b', p)) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Vocabulary diversity
        unique_words = len(set(words))
        total_words = len(words)
        vocabulary_diversity = unique_words / total_words if total_words > 0 else 0
        
        # Dialogue analysis
        dialogue_lines = re.findall(r'["\']([^"\']+)["\']', text)
        dialogue_percentage = len(dialogue_lines) / len(sentences) if sentences else 0
        
        # Descriptive language (adjectives and adverbs)
        descriptive_pattern = r'\b\w+ly\b|\b\w+ing\b'
        descriptive_words = len(re.findall(descriptive_pattern, text.lower()))
        descriptive_ratio = descriptive_words / total_words if total_words > 0 else 0
        
        return {
            'total_words': total_words,
            'total_sentences': len(sentences),
            'total_paragraphs': len(paragraphs),
            'unique_words': unique_words,
            'vocabulary_diversity': vocabulary_diversity,
            'avg_sentence_length': avg_sentence_length,
            'avg_paragraph_length': avg_paragraph_length,
            'dialogue_percentage': dialogue_percentage,
            'descriptive_ratio': descriptive_ratio,
            'most_common_words': most_common_words[:20],
            'sentence_length_distribution': {
                'min': min(sentence_lengths) if sentence_lengths else 0,
                'max': max(sentence_lengths) if sentence_lengths else 0,
                'median': sorted(sentence_lengths)[len(sentence_lengths)//2] if sentence_lengths else 0
            }
        }
    
    def compare_voices(self, reference_text: str, completion_text: str) -> Dict:
        """Compare completion text with reference voice"""
        ref_style = self.analyze_style(reference_text)
        comp_style = self.analyze_style(completion_text)
        
        # Calculate similarity scores
        sentence_length_diff = abs(ref_style['avg_sentence_length'] - comp_style['avg_sentence_length'])
        sentence_length_similarity = 1 - (sentence_length_diff / max(ref_style['avg_sentence_length'], 1))
        
        paragraph_length_diff = abs(ref_style['avg_paragraph_length'] - comp_style['avg_paragraph_length'])
        paragraph_length_similarity = 1 - (paragraph_length_diff / max(ref_style['avg_paragraph_length'], 1))
        
        dialogue_diff = abs(ref_style['dialogue_percentage'] - comp_style['dialogue_percentage'])
        dialogue_similarity = 1 - dialogue_diff
        
        # Word overlap
        ref_words = set(re.findall(r'\b\w+\b', reference_text.lower()))
        comp_words = set(re.findall(r'\b\w+\b', completion_text.lower()))
        word_overlap = len(ref_words & comp_words) / len(ref_words) if ref_words else 0
        
        # Overall similarity score
        overall_similarity = (
            sentence_length_similarity * 0.3 +
            paragraph_length_similarity * 0.2 +
            dialogue_similarity * 0.2 +
            word_overlap * 0.3
        )
        
        return {
            'overall_similarity': overall_similarity,
            'sentence_length_similarity': sentence_length_similarity,
            'paragraph_length_similarity': paragraph_length_similarity,
            'dialogue_similarity': dialogue_similarity,
            'word_overlap': word_overlap,
            'reference_style': ref_style,
            'completion_style': comp_style,
            'differences': {
                'sentence_length': comp_style['avg_sentence_length'] - ref_style['avg_sentence_length'],
                'paragraph_length': comp_style['avg_paragraph_length'] - ref_style['avg_paragraph_length'],
                'dialogue_percentage': comp_style['dialogue_percentage'] - ref_style['dialogue_percentage'],
                'vocabulary_diversity': comp_style['vocabulary_diversity'] - ref_style['vocabulary_diversity']
            }
        }
    
    def analyze_completion(self, completion_file: Path) -> Dict:
        """Analyze a completion file"""
        with open(completion_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract just the completion text (after metadata)
        completion_text = content.split('## Generated Continuation')[1].split('---')[0].strip() if '## Generated Continuation' in content else content
        
        reference_text = self.load_reference_text()
        comparison = self.compare_voices(reference_text, completion_text)
        
        return {
            'file': str(completion_file),
            'comparison': comparison,
            'completion_stats': self.analyze_style(completion_text)
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze voice and style')
    parser.add_argument('completion_file', type=Path, nargs='?',
                       help='Completion file to analyze')
    parser.add_argument('--all', action='store_true',
                       help='Analyze all completion files')
    parser.add_argument('--output', type=Path,
                       help='Output file for results')
    
    args = parser.parse_args()
    
    analyzer = VoiceAnalyzer()
    
    if args.all:
        # Analyze all completions
        completion_dir = Path("completion_attempts")
        results = []
        
        for completion_file in completion_dir.rglob("*.md"):
            print(f"Analyzing: {completion_file}")
            try:
                result = analyzer.analyze_completion(completion_file)
                results.append(result)
                print(f"  Similarity: {result['comparison']['overall_similarity']:.2%}")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Save results
        output_file = args.output or Path("analysis/completion_analysis.json")
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Analyzed {len(results)} completions")
        print(f"📊 Results saved to: {output_file}")
        
    elif args.completion_file:
        # Analyze single file
        result = analyzer.analyze_completion(args.completion_file)
        
        print(f"\n📊 Voice Analysis Results")
        print(f"File: {result['file']}")
        print(f"\nOverall Similarity: {result['comparison']['overall_similarity']:.2%}")
        print(f"Sentence Length Similarity: {result['comparison']['sentence_length_similarity']:.2%}")
        print(f"Paragraph Length Similarity: {result['comparison']['paragraph_length_similarity']:.2%}")
        print(f"Dialogue Similarity: {result['comparison']['dialogue_similarity']:.2%}")
        print(f"Word Overlap: {result['comparison']['word_overlap']:.2%}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"\n📄 Results saved to: {args.output}")
    else:
        # Analyze reference text
        print("📚 Analyzing reference text (Audrey's manuscripts)...")
        reference_text = analyzer.load_reference_text()
        style = analyzer.analyze_style(reference_text)
        
        print(f"\n📊 Reference Style Analysis")
        print(f"Total Words: {style['total_words']:,}")
        print(f"Unique Words: {style['unique_words']:,}")
        print(f"Vocabulary Diversity: {style['vocabulary_diversity']:.2%}")
        print(f"Avg Sentence Length: {style['avg_sentence_length']:.1f} words")
        print(f"Avg Paragraph Length: {style['avg_paragraph_length']:.1f} words")
        print(f"Dialogue Percentage: {style['dialogue_percentage']:.2%}")
        print(f"\nMost Common Words:")
        for word, count in style['most_common_words'][:10]:
            print(f"  {word}: {count}")

if __name__ == '__main__':
    main()

