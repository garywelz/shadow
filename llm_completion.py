#!/usr/bin/env python3
"""
LLM Completion Workflow for The Shadow of Lillya
Supports multiple LLMs for generating novel completions
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse

class LLMCompletion:
    """Base class for LLM completion"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.completions_dir = Path("completion_attempts")
        self.completions_dir.mkdir(exist_ok=True)
    
    def load_manuscripts(self) -> Dict[str, str]:
        """Load all manuscript files"""
        manuscripts = {}
        manuscripts_dir = Path("manuscripts")
        
        # Load Circus of the Queens
        circus_dir = manuscripts_dir / "Circus_of_the_Queens"
        for md_file in circus_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                manuscripts['circus_of_the_queens'] = f.read()
        
        # Load edited version of Shadow of Lillya
        edited_dir = manuscripts_dir / "Shadow_of_Lillya" / "edited_version"
        for md_file in edited_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                manuscripts['shadow_edited'] = f.read()
        
        # Load unedited material
        unedited_dir = manuscripts_dir / "Shadow_of_Lillya" / "unedited_material"
        unedited_texts = []
        for md_file in unedited_dir.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                unedited_texts.append(f.read())
        manuscripts['shadow_unedited'] = '\n\n---\n\n'.join(unedited_texts)
        
        # Load notes and outlines
        shadow_dir = manuscripts_dir / "Shadow_of_Lillya"
        notes = []
        for md_file in shadow_dir.glob("*.md"):
            if 'notes' in md_file.name.lower() or 'outline' in md_file.name.lower():
                with open(md_file, 'r', encoding='utf-8') as f:
                    notes.append(f.read())
        manuscripts['notes'] = '\n\n---\n\n'.join(notes)
        
        return manuscripts
    
    def create_prompt(self, manuscripts: Dict[str, str], continuation_point: Optional[str] = None) -> str:
        """Create a prompt for LLM completion"""
        prompt = f"""You are completing the novel "The Shadow of Lillya" by Audrey Berger Welz. This is a sequel/prequel to her novel "Circus of the Queens."

CONTEXT - CIRCUS OF THE QUEENS:
{manuscripts.get('circus_of_the_queens', '')[:5000]}...

CURRENT MANUSCRIPT - THE SHADOW OF LILLYA (Edited Version):
{manuscripts.get('shadow_edited', '')}

ADDITIONAL MATERIAL - UNEDITED VERSIONS:
{manuscripts.get('shadow_unedited', '')[:3000]}...

NOTES AND OUTLINES:
{manuscripts.get('notes', '')}

INSTRUCTIONS:
1. Continue the story from where Audrey left off, maintaining her unique voice and writing style
2. Stay true to the characters and world established in "Circus of the Queens"
3. Preserve the thematic elements and narrative style of Audrey's work
4. Ensure character consistency and plot coherence
5. Write in a style that matches Audrey's voice as closely as possible

CONTINUATION POINT:
{continuation_point if continuation_point else 'Continue from the end of the edited manuscript.'}

Please continue the novel, writing approximately 1000-2000 words that seamlessly continue from where Audrey's manuscript ends."""
        
        return prompt
    
    def generate_completion(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate completion using the LLM (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement generate_completion")
    
    def save_completion(self, completion: str, metadata: Dict) -> Path:
        """Save completion to file"""
        model_dir = self.completions_dir / self.model_name.lower().replace(' ', '_')
        model_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"completion_{timestamp}.md"
        filepath = model_dir / filename
        
        # Create markdown file with metadata
        content = f"""# Completion Attempt - {self.model_name}

**Generated:** {metadata.get('timestamp', datetime.now().isoformat())}
**Model:** {self.model_name}
**Version:** {metadata.get('version', '1.0')}
**Continuation Point:** {metadata.get('continuation_point', 'End of edited manuscript')}

---

## Generated Continuation

{completion}

---

## Metadata

```json
{json.dumps(metadata, indent=2)}
```
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Also save metadata separately
        metadata_file = model_dir / f"metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return filepath

class OpenAICompletion(LLMCompletion):
    """OpenAI GPT completion"""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        super().__init__(f"OpenAI-{model_name}")
        self.model_name_full = model_name
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
    
    def generate_completion(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate completion using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model_name_full,
                messages=[
                    {"role": "system", "content": "You are a literary assistant helping to complete a novel in the author's voice and style."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

class AnthropicCompletion(LLMCompletion):
    """Anthropic Claude completion"""
    
    def __init__(self, model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None):
        super().__init__(f"Anthropic-{model_name}")
        self.model_name_full = model_name
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
    
    def generate_completion(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate completion using Anthropic API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model_name_full,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate LLM completions for The Shadow of Lillya')
    parser.add_argument('--model', choices=['openai', 'anthropic'], default='openai',
                       help='LLM provider to use')
    parser.add_argument('--model-name', type=str,
                       help='Specific model name (e.g., gpt-4, claude-3-opus-20240229)')
    parser.add_argument('--api-key', type=str,
                       help='API key (or set environment variable)')
    parser.add_argument('--max-tokens', type=int, default=2000,
                       help='Maximum tokens to generate')
    parser.add_argument('--continuation-point', type=str,
                       help='Specific point in text to continue from')
    
    args = parser.parse_args()
    
    # Load manuscripts
    print("📚 Loading manuscripts...")
    base_completion = LLMCompletion("base")
    manuscripts = base_completion.load_manuscripts()
    print(f"  ✓ Loaded {len(manuscripts)} manuscript sections")
    
    # Create prompt
    print("📝 Creating prompt...")
    prompt = base_completion.create_prompt(manuscripts, args.continuation_point)
    print(f"  ✓ Prompt created ({len(prompt)} characters)")
    
    # Initialize LLM
    print(f"🤖 Initializing {args.model}...")
    if args.model == 'openai':
        model_name = args.model_name or "gpt-4"
        llm = OpenAICompletion(model_name, args.api_key)
    elif args.model == 'anthropic':
        model_name = args.model_name or "claude-3-opus-20240229"
        llm = AnthropicCompletion(model_name, args.api_key)
    
    # Generate completion
    print("✨ Generating completion...")
    try:
        completion = llm.generate_completion(prompt, args.max_tokens)
        print(f"  ✓ Generated {len(completion)} characters")
        
        # Save completion
        metadata = {
            'model': llm.model_name,
            'model_full': model_name,
            'timestamp': datetime.now().isoformat(),
            'continuation_point': args.continuation_point or 'End of edited manuscript',
            'max_tokens': args.max_tokens,
            'completion_length': len(completion)
        }
        
        filepath = llm.save_completion(completion, metadata)
        print(f"  ✓ Saved to: {filepath}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

