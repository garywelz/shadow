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
import re

def _normalize_openai_key(value: str) -> str:
    v = value.strip().strip('"').strip("'")
    for prefix in ("export ", "OPENAI_API_KEY="):
        if v.startswith(prefix):
            v = v[len(prefix):].strip().strip('"').strip("'")
    m = re.search(r"(sk-(?:proj-)?[A-Za-z0-9_-]{10,})", v)
    return (m.group(1) if m else v).strip()

def _approx_tokens_from_chars(char_count: int) -> int:
    # Rough rule of thumb for English prose.
    return max(1, int(char_count / 4))

def _infer_openai_context_limit_tokens(model_name: str) -> int:
    m = (model_name or "").lower().strip()
    # Heuristic defaults; we intentionally avoid overconfidence.
    if "128k" in m or m.startswith("gpt-4o") or m.startswith("gpt-4.1") or m.startswith("gpt-4o-mini"):
        return 128_000
    if m.startswith("gpt-4"):
        return 32_768
    if m.startswith("gpt-3.5"):
        return 16_385
    return 32_768

def _extract_generated_continuation(markdown: str) -> str:
    # The completion files saved by this project contain a "## Generated Continuation" section.
    marker = "## Generated Continuation"
    if marker in markdown:
        after = markdown.split(marker, 1)[1]
        # Cut off at next horizontal rule block if present.
        if "\n---" in after:
            after = after.split("\n---", 1)[0]
        return after.strip()
    return markdown.strip()

def _load_all_markdown_texts(folder: Path) -> str:
    if not folder.exists():
        return ""
    parts: list[str] = []
    for p in sorted(folder.glob("*.md")):
        try:
            parts.append(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
    return "\n\n---\n\n".join([x for x in parts if x.strip()])

def _load_completion_attempts_text(completions_dir: Path) -> str:
    if not completions_dir.exists():
        return ""
    files = sorted(completions_dir.rglob("completion_*.md"), key=lambda p: p.stat().st_mtime)
    parts: list[str] = []
    for p in files:
        try:
            md = p.read_text(encoding="utf-8", errors="ignore")
            txt = _extract_generated_continuation(md)
            if txt:
                parts.append(f"\n\n[AI continuation from {p.as_posix()}]\n\n{txt}".strip())
        except Exception:
            continue
    return "\n\n---\n\n".join(parts)

def _sandwich(text: str, head_chars: int, tail_chars: int, label: str) -> str:
    t = text or ""
    if head_chars <= 0 and tail_chars <= 0:
        return ""
    if len(t) <= head_chars + tail_chars + 200:
        return t
    head = t[: max(0, head_chars)].rstrip()
    tail = t[-max(0, tail_chars) :].lstrip() if tail_chars > 0 else ""
    omitted = len(t) - len(head) - len(tail)
    return (
        f"{head}\n\n"
        f"[... omitted {omitted} characters from {label} to fit context window ...]\n\n"
        f"{tail}"
    )

def pack_context_for_completion(
    *,
    circus_full: str,
    shadow_working_full: str,
    notes_full: str,
    model_name: str,
    max_output_tokens: int,
    overhead_tokens: int = 1200,
) -> tuple[dict[str, str], dict[str, int]]:
    """
    Try to include as much real text as possible within an estimated context window.
    Priority: Shadow (working draft) > Circus > Notes.
    Returns (packed_sections, report).
    """
    context_limit = _infer_openai_context_limit_tokens(model_name)
    budget_input_tokens = max(2_000, context_limit - max_output_tokens - overhead_tokens)
    budget_chars = budget_input_tokens * 4

    circus = circus_full or ""
    shadow = shadow_working_full or ""
    notes = notes_full or ""

    raw_total = len(circus) + len(shadow) + len(notes)
    if raw_total <= budget_chars:
        packed = {"circus": circus, "shadow": shadow, "notes": notes}
        report = {
            "context_limit_tokens": context_limit,
            "budget_input_tokens": budget_input_tokens,
            "budget_chars": budget_chars,
            "circus_total_chars": len(circus),
            "shadow_total_chars": len(shadow),
            "notes_total_chars": len(notes),
            "circus_included_chars": len(circus),
            "shadow_included_chars": len(shadow),
            "notes_included_chars": len(notes),
            "truncated": 0,
        }
        return packed, report

    # Allocate budget across sections. Shadow gets the biggest share.
    shadow_budget = int(budget_chars * 0.60)
    circus_budget = int(budget_chars * 0.35)
    notes_budget = budget_chars - shadow_budget - circus_budget

    # Shadow: keep both beginning and end (recency matters, but opening anchors names/setting).
    shadow_head = int(shadow_budget * 0.25)
    shadow_tail = shadow_budget - shadow_head
    shadow_packed = _sandwich(shadow, shadow_head, shadow_tail, "Shadow (working draft)")

    # Circus: keep beginning + end if it’s long; otherwise full.
    circus_head = int(circus_budget * 0.70)
    circus_tail = max(0, circus_budget - circus_head)
    circus_packed = _sandwich(circus, circus_head, circus_tail, "Circus of the Queens")

    # Notes: beginning only (usually outlines / short).
    notes_packed = (notes[: max(0, notes_budget)]).strip()
    if notes and len(notes) > len(notes_packed) + 200:
        notes_packed = f"{notes_packed}\n\n[... notes truncated to fit context window ...]".strip()

    packed = {"circus": circus_packed, "shadow": shadow_packed, "notes": notes_packed}
    report = {
        "context_limit_tokens": context_limit,
        "budget_input_tokens": budget_input_tokens,
        "budget_chars": budget_chars,
        "circus_total_chars": len(circus),
        "shadow_total_chars": len(shadow),
        "notes_total_chars": len(notes),
        "circus_included_chars": len(circus_packed),
        "shadow_included_chars": len(shadow_packed),
        "notes_included_chars": len(notes_packed),
        "truncated": 1,
    }
    return packed, report

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

        # Prefer Audrey-first edited material if it exists (generated by edit_audrey_material.py)
        audrey_first_path = Path("manuscripts/Shadow_of_Lillya/audrey_edited/audrey_edited_clean.md")
        if audrey_first_path.exists():
            with open(audrey_first_path, "r", encoding="utf-8") as f:
                manuscripts["shadow_edited"] = f.read()
        
        # Load Circus of the Queens
        circus_dir = manuscripts_dir / "Circus_of_the_Queens"
        manuscripts["circus_of_the_queens"] = _load_all_markdown_texts(circus_dir)
        
        # Load edited version of Shadow of Lillya (fallback if Audrey-first not present)
        if "shadow_edited" not in manuscripts:
            edited_dir = manuscripts_dir / "Shadow_of_Lillya" / "edited_version"
            manuscripts["shadow_edited"] = _load_all_markdown_texts(edited_dir)
        
        # Load unedited material
        unedited_dir = manuscripts_dir / "Shadow_of_Lillya" / "unedited_material"
        manuscripts["shadow_unedited"] = _load_all_markdown_texts(unedited_dir)
        
        # Load notes and outlines
        shadow_dir = manuscripts_dir / "Shadow_of_Lillya"
        notes = []
        for md_file in shadow_dir.glob("*.md"):
            if 'notes' in md_file.name.lower() or 'outline' in md_file.name.lower():
                with open(md_file, 'r', encoding='utf-8') as f:
                    notes.append(f.read())
        manuscripts['notes'] = '\n\n---\n\n'.join(notes)

        # Build a working Shadow draft by appending prior completion attempts (chronological).
        completions_text = _load_completion_attempts_text(self.completions_dir)
        base_shadow = manuscripts.get("shadow_edited", "")
        if completions_text.strip():
            manuscripts["shadow_working"] = f"{base_shadow}\n\n---\n\n{completions_text}".strip()
        else:
            manuscripts["shadow_working"] = base_shadow
        
        return manuscripts
    
    def create_prompt(
        self,
        manuscripts: Dict[str, str],
        writing_request: Optional[str] = None,
        *,
        target_words: int = 1400,
        max_output_tokens: int = 2000,
        model_name: str = "gpt-4",
    ) -> str:
        """Create a prompt for LLM completion using an auto-packed context window."""
        circus = manuscripts.get("circus_of_the_queens", "")
        shadow_working = manuscripts.get("shadow_working", manuscripts.get("shadow_edited", ""))
        notes = manuscripts.get("notes", "")

        packed, report = pack_context_for_completion(
            circus_full=circus,
            shadow_working_full=shadow_working,
            notes_full=notes,
            model_name=model_name,
            max_output_tokens=max_output_tokens,
        )

        packing_report = (
            f"PACKING REPORT (estimated):\n"
            f"- Model context limit (tokens): {report['context_limit_tokens']}\n"
            f"- Input budget (tokens): {report['budget_input_tokens']}\n"
            f"- Input budget (chars): {report['budget_chars']}\n"
            f"- Circus included/total (chars): {report['circus_included_chars']}/{report['circus_total_chars']}\n"
            f"- Shadow included/total (chars): {report['shadow_included_chars']}/{report['shadow_total_chars']}\n"
            f"- Notes included/total (chars): {report['notes_included_chars']}/{report['notes_total_chars']}\n"
            f"- Truncated: {'yes' if report['truncated'] else 'no'}\n"
        )

        prompt = f"""You are completing the novel "The Shadow of Lillya" by Audrey Berger Welz. This is a sequel/prequel to her novel "Circus of the Queens."

{packing_report}

CONTEXT - CIRCUS OF THE QUEENS:
{packed['circus']}

WORKING MANUSCRIPT - THE SHADOW OF LILLYA (Audrey draft + your appended continuations):
{packed['shadow']}

NOTES AND OUTLINES (if any):
{packed['notes']}

INSTRUCTIONS:
1. Continue the story from where Audrey left off, maintaining her unique voice and writing style
2. Stay true to the characters and world established in "Circus of the Queens"
3. Preserve the thematic elements and narrative style of Audrey's work
4. Ensure character consistency and plot coherence
5. Write in a style that matches Audrey's voice as closely as possible

WRITING REQUEST (optional):
{writing_request if writing_request else 'Continue naturally from the end of the working Shadow draft.'}

OUTPUT:
- Write approximately {target_words} words (flexible).
- Keep continuity with the final paragraphs of the Shadow excerpt above.
- Do not include analysis or meta commentary—just the next section of the novel text.
"""
        
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
        self.api_key = _normalize_openai_key(self.api_key)
        if self.api_key.strip() in {"OPENAI_API_KEY", "OPENAI_API_KEY="} or self.api_key.strip().startswith("OPENAI_"):
            raise ValueError("OpenAI API key looks invalid. Set OPENAI_API_KEY to your actual key that starts with 'sk-'.")
        if not (self.api_key.startswith("sk-") or self.api_key.startswith("sk-proj-")):
            raise ValueError("OpenAI API key looks invalid. It should start with 'sk-' (or 'sk-proj-').")
    
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
    parser.add_argument('--writing-request', type=str,
                       help='Optional instruction/request for what to write next (e.g., a specific scene or chapter)')
    parser.add_argument('--use-audrey-first', action='store_true',
                        help='Prefer Audrey-first edited material if present (default behavior). Included for clarity in logs/UI.')
    parser.add_argument('--target-words', type=int, default=1400,
                        help='Approximate word target for the continuation')
    
    args = parser.parse_args()

    # Resolve model name early (used for context packing + API call)
    if args.model == 'openai':
        model_name = args.model_name or "gpt-4"
    elif args.model == 'anthropic':
        model_name = args.model_name or "claude-3-opus-20240229"
    else:
        model_name = args.model_name or "gpt-4"
    
    # Load manuscripts
    print("📚 Loading manuscripts...")
    base_completion = LLMCompletion("base")
    manuscripts = base_completion.load_manuscripts()
    print(f"  ✓ Loaded {len(manuscripts)} manuscript sections")
    
    # Create prompt
    print("📝 Creating prompt...")
    prompt = base_completion.create_prompt(
        manuscripts,
        args.writing_request,
        target_words=args.target_words,
        max_output_tokens=args.max_tokens,
        model_name=model_name,
    )
    print(f"  ✓ Prompt created ({len(prompt)} characters)")
    
    # Initialize LLM
    print(f"🤖 Initializing {args.model}...")
    if args.model == 'openai':
        llm = OpenAICompletion(model_name, args.api_key)
    elif args.model == 'anthropic':
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
            'writing_request': args.writing_request or '',
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
