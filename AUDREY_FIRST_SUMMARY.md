# Summary: Prioritizing Audrey's Original Material

## What's Changed

The project has been restructured to **prioritize Audrey Berger Welz's original material** above all else. This ensures that readers of *Circus of the Queens* receive as much of her authentic writing as possible.

## New Tools Created

### 1. `extract_audrey_material.py`
**Purpose:** Identify and extract only Audrey's original writing

**What it does:**
- Analyzes all manuscript versions
- Prioritizes the version sent to Tyson Cornell (March 2020)
- Includes earlier unedited versions
- **Excludes** ghost writer versions (v69, v73, GW versions)
- Compiles a clean version of only her original work

**Run:** `python3 extract_audrey_material.py`

### 2. `edit_audrey_material.py`
**Purpose:** Make minimal edits for clarity while preserving voice

**What it does:**
- Loads Audrey's extracted original material
- Fixes obvious typos and formatting
- Normalizes spacing and punctuation
- **Preserves** all voice, style, and word choices
- Creates a clean, readable version

**Run:** `python3 edit_audrey_material.py`

### 3. `compile_final_manuscript.py`
**Purpose:** Create final manuscript with clear attribution

**What it does:**
- Combines Audrey's edited material (Part I)
- Adds AI-generated sections (Part II) with clear labels
- Includes suggested additions (Part III) if any
- Creates clear section breaks and attribution notes

**Run:** `python3 compile_final_manuscript.py`

## Workflow

1. **Extract** → Get only Audrey's original material
2. **Edit** → Minimal clarity edits, preserve voice
3. **Generate** (optional) → AI completions, clearly marked
4. **Compile** → Final manuscript with full attribution

See `WORKFLOW_AUDREY_FIRST.md` for detailed instructions.

## Key Principles

✅ **Audrey's Material First** - Her writing takes absolute priority  
✅ **Clear Attribution** - Every section labeled with its source  
✅ **Voice Preservation** - No changes to her style or word choices  
✅ **Transparency** - Readers can see what's Audrey's and what's not  
✅ **Minimal Editing** - Only clarity, no content changes  
✅ **Respect Original Intent** - Honor her vision above all else

## File Structure

```
manuscripts/Shadow_of_Lillya/
├── audrey_original/          # Step 1: Extracted original
│   └── audrey_original_compiled.md
├── audrey_edited/            # Step 2: Edited for clarity
│   └── audrey_edited_clean.md
└── final_compilation/         # Step 4: Final with attribution
    ├── shadow_of_lillya_final.md
    └── shadow_of_lillya_audrey_only.md
```

## Next Steps

1. Run `extract_audrey_material.py` to identify Audrey's core material
2. Review the extracted material
3. Run `edit_audrey_material.py` for clarity edits
4. Generate AI completions if needed (they'll be clearly marked)
5. Compile final manuscript with `compile_final_manuscript.py`

## Result

The final manuscript will have:
- **Part I:** All of Audrey's original material (edited minimally for clarity)
- **Part II:** AI-generated continuations (clearly marked and attributed)
- **Part III:** Suggested additions (if any, clearly marked)

This ensures readers get maximum exposure to Audrey's authentic voice while maintaining complete transparency about any supplementary material.

---

*"The shadow knows what the light cannot see."* - Audrey Berger Welz

