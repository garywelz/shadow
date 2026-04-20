# The Shadow of Lillya - Novel Completion Project

## About This Project

This Hugging Face Space is dedicated to completing **The Shadow of Lillya**, a novel by the late **Audrey Berger Welz**. This work serves as both a sequel and prequel to her previous novel, **Circus of the Queens**.

This is an ongoing **research + craft** project: build tooling that helps preserve Audrey’s authentic voice, organize source material, and (optionally) use LLMs to propose clearly-attributed continuations.

## Project Mission

**Our primary goal is to use as much of Audrey Berger Welz's original material and original intent as possible.**

This project prioritizes Audrey's authentic writing above all else. Her original material is extracted, edited minimally for clarity, and preserved as the core of the manuscript. Any AI-generated or suggested additions are clearly marked and attributed, ensuring readers can distinguish between Audrey's original work and supplementary material.

We are committed to remaining as faithful as possible to her work, honoring her voice, style, and vision.

## Background

Audrey Berger Welz was a gifted storyteller whose novel *Circus of the Queens* captivated readers with its rich characters and imaginative world-building. *The Shadow of Lillya* represents her vision for expanding this universe, exploring the deeper mysteries and connections within her literary world.

## Project Structure

This space contains:

1. **Original Manuscripts**: Audrey's draft of *The Shadow of Lillya*
2. **Reference Material**: Complete text of *Circus of the Queens* for context and voice analysis
3. **Completion Attempts**: Various LLM-generated continuations and completions
4. **Analysis Tools**: Methods for evaluating authenticity and voice consistency

## Methodology

Our approach prioritizes Audrey's original material:

1. **Extract Original Material**: Identify and extract only Audrey's authentic writing from all available drafts, excluding ghost writer versions
2. **Edit for Clarity**: Make minimal edits to improve clarity while preserving her voice, style, and word choices
3. **Clear Attribution**: All material is clearly labeled:
   - **Audrey's Original Material**: Her authentic writing, edited minimally for clarity
   - **AI-Generated Material**: Clearly marked continuations inspired by her work
   - **Suggested Additions**: Material suggested by editors/contributors, clearly attributed
4. **Voice Preservation**: No changes to Audrey's voice, style, or word choices
5. **Transparency**: Readers can see exactly what is Audrey's and what is supplementary

See `WORKFLOW_AUDREY_FIRST.md` for detailed workflow instructions.

## How the Space works

The Streamlit app (`app.py`) provides:

- **Manuscript browser**: view and download the markdown manuscript files under `manuscripts/`
- **Search**: keyword/phrase search across manuscripts with contextual snippets
- **Audrey-first tools**: buttons to run:
  - `extract_audrey_material.py`
  - `edit_audrey_material.py`
  - `compile_final_manuscript.py`
- **LLM completion generator** (optional): runs `llm_completion.py` with adjustable context sizes

## LLM keys (optional)

If you want to generate completions inside the Space, configure Space secrets:

- `OPENAI_API_KEY` for OpenAI models
- `ANTHROPIC_API_KEY` for Anthropic models

You can also paste a key into the UI for a single run, but Space secrets are preferred.

## Contributing

This is a deeply personal project honoring Audrey's literary legacy. While this space serves as a memorial and completion effort, we welcome respectful engagement with the material.

## Key Files and Tools

### Material Organization
- `manuscripts/Shadow_of_Lillya/edited_version/` - Draft sent to editor (reference)
- `manuscripts/Shadow_of_Lillya/unedited_material/` - Other draft material (reference)
- `manuscripts/Shadow_of_Lillya/audrey_original/` - Extracted original material (generated)
- `manuscripts/Shadow_of_Lillya/audrey_edited/` - Edited for clarity (generated)
- `manuscripts/Shadow_of_Lillya/final_compilation/` - Final manuscript with attribution (generated)

### Workflow Tools
- `extract_audrey_material.py` - Extract only Audrey's original writing
- `edit_audrey_material.py` - Edit for clarity while preserving voice
- `compile_final_manuscript.py` - Compile final version with clear attribution
- `llm_completion.py` - Generate AI continuations (clearly marked)
- `voice_analysis.py` - Analyze writing style and authenticity

### Reference Material
- `Circus_of_the_Queens/` - Complete original novel
- `completion_attempts/` - AI-generated completions (clearly attributed)
- `analysis/` - Voice analysis and style comparison tools

## Acknowledgments

We remember and honor **Audrey Berger Welz** for her creative vision and the beautiful worlds she created. This project is a labor of love dedicated to bringing her final story to completion.

---

*"The shadow knows what the light cannot see."* - Audrey Berger Welz



