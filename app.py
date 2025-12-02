import streamlit as st
import pandas as pd
from pathlib import Path
import os

# Page configuration
st.set_page_config(
    page_title="The Shadow of Lillya - Novel Completion Project",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .section-header {
        font-size: 2rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .quote {
        font-style: italic;
        color: #7f8c8d;
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">The Shadow of Lillya</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Novel Completion Project</p>', unsafe_allow_html=True)
    
    # Quote
    st.markdown('<div class="quote">"The shadow knows what the light cannot see."<br>— Audrey Berger Welz</div>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    ## About This Project
    
    This space is dedicated to completing **The Shadow of Lillya**, a novel by the late **Audrey Berger Welz**. 
    This work serves as both a sequel and prequel to her previous novel, **Circus of the Queens**.
    
    Our mission is to use multiple Large Language Models to complete the novel as authentically as possible, 
    staying true to Audrey's original intentions and preserving her unique voice and storytelling style.
    """)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Home", "Original Manuscripts", "Generate Completion", "Completion Attempts", "Voice Analysis", "About Audrey"]
    )
    
    if page == "Home":
        show_home_page()
    elif page == "Original Manuscripts":
        show_manuscripts_page()
    elif page == "Generate Completion":
        show_generate_page()
    elif page == "Completion Attempts":
        show_completions_page()
    elif page == "Voice Analysis":
        show_analysis_page()
    elif page == "About Audrey":
        show_about_page()

def show_home_page():
    st.markdown('<h2 class="section-header">Project Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Background
        
        Audrey Berger Welz was a gifted storyteller whose novel *Circus of the Queens* 
        captivated readers with its rich characters and imaginative world-building. 
        *The Shadow of Lillya* represents her vision for expanding this universe, 
        exploring the deeper mysteries and connections within her literary world.
        """)
        
        st.markdown("""
        ### Methodology
        
        We employ multiple approaches to ensure the completion remains faithful to Audrey's vision:
        
        1. **Voice Analysis**: Studying Audrey's writing style, vocabulary, and narrative patterns
        2. **Character Consistency**: Maintaining the depth and complexity of established characters
        3. **Plot Continuity**: Ensuring seamless integration with *Circus of the Queens*
        4. **Multiple LLM Approach**: Using different models to generate and compare completions
        5. **Human Oversight**: Reviewing and selecting the most authentic continuations
        """)
    
    with col2:
        st.markdown("""
        ### Project Structure
        
        This space contains:
        
        - **Original Manuscripts**: Audrey's draft of *The Shadow of Lillya*
        - **Reference Material**: Complete text of *Circus of the Queens* for context
        - **Completion Attempts**: Various LLM-generated continuations
        - **Analysis Tools**: Methods for evaluating authenticity and voice consistency
        """)
        
        st.markdown("""
        ### Current Status
        
        - ✅ Project setup and documentation
        - 📚 Manuscript upload and processing
        - 🔄 LLM completion generation
        - 📊 Voice analysis and comparison
        - 📖 Final manuscript compilation
        """)

def show_manuscripts_page():
    st.markdown('<h2 class="section-header">Original Manuscripts</h2>', unsafe_allow_html=True)
    
    st.info("📚 Manuscript files will be uploaded here. Please check back soon for the complete texts.")
    
    # Placeholder for manuscript display
    st.markdown("""
    ### Available Documents
    
    Once uploaded, this section will contain:
    
    - **Circus of the Queens** - The complete original novel
    - **The Shadow of Lillya Draft** - Audrey's manuscript draft
    - **Character Notes** - Any additional character development materials
    - **Plot Outlines** - Story structure and planned developments
    """)

def show_generate_page():
    st.markdown('<h2 class="section-header">Generate Completion</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Generate a new completion of *The Shadow of Lillya* using LLM technology.
    The system will use Audrey's manuscripts as context to maintain her voice and style.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic"])
        model_name = st.text_input("Model Name", value="gpt-4" if provider == "OpenAI" else "claude-3-opus-20240229")
        api_key = st.text_input("API Key", type="password", help="Or set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        max_tokens = st.slider("Max Tokens", 500, 4000, 2000)
    
    with col2:
        continuation_point = st.text_area("Continuation Point", 
                                         placeholder="Optional: Specify where to continue from. Leave blank to continue from end of manuscript.",
                                         height=100)
        st.info("💡 The system will automatically load all manuscripts as context for the completion.")
    
    if st.button("Generate Completion", type="primary"):
        with st.spinner("Generating completion..."):
            try:
                import subprocess
                import sys
                
                # Build command
                cmd = [sys.executable, "llm_completion.py", 
                       "--model", provider.lower(),
                       "--model-name", model_name,
                       "--max-tokens", str(max_tokens)]
                
                if api_key:
                    cmd.extend(["--api-key", api_key])
                if continuation_point:
                    cmd.extend(["--continuation-point", continuation_point])
                
                # Set environment variables
                env = os.environ.copy()
                if provider == "OpenAI" and api_key:
                    env["OPENAI_API_KEY"] = api_key
                elif provider == "Anthropic" and api_key:
                    env["ANTHROPIC_API_KEY"] = api_key
                
                result = subprocess.run(cmd, capture_output=True, text=True, env=env)
                
                if result.returncode == 0:
                    st.success("✅ Completion generated successfully!")
                    st.code(result.stdout)
                else:
                    st.error(f"❌ Error generating completion:\n{result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.markdown("### Recent Completions")
    
    # List recent completions
    completion_dir = Path("completion_attempts")
    if completion_dir.exists():
        completion_files = list(completion_dir.rglob("*.md"))
        completion_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if completion_files:
            for comp_file in completion_files[:5]:
                with st.expander(f"📄 {comp_file.name}"):
                    with open(comp_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    st.markdown(content[:1000] + "..." if len(content) > 1000 else content)
        else:
            st.info("No completions generated yet. Use the form above to generate your first completion.")

def show_completions_page():
    st.markdown('<h2 class="section-header">Completion Attempts</h2>', unsafe_allow_html=True)
    
    # List all completions
    completion_dir = Path("completion_attempts")
    if completion_dir.exists():
        completion_files = list(completion_dir.rglob("*.md"))
        completion_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if completion_files:
            st.success(f"Found {len(completion_files)} completion attempt(s)")
            
            # Group by model
            by_model = {}
            for comp_file in completion_files:
                model = comp_file.parent.name
                if model not in by_model:
                    by_model[model] = []
                by_model[model].append(comp_file)
            
            for model, files in by_model.items():
                with st.expander(f"📚 {model.replace('_', ' ').title()} ({len(files)} files)"):
                    for comp_file in files:
                        st.markdown(f"**{comp_file.name}**")
                        with open(comp_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        st.text_area("Preview", content[:500] + "..." if len(content) > 500 else content, 
                                   key=str(comp_file), height=200)
        else:
            st.info("🔄 No completion attempts found. Go to 'Generate Completion' to create your first attempt.")
    else:
        st.info("🔄 LLM completion attempts will be generated and displayed here.")

def show_analysis_page():
    st.markdown('<h2 class="section-header">Voice Analysis</h2>', unsafe_allow_html=True)
    
    st.info("📊 Voice analysis tools and comparisons will be available here.")
    
    # Placeholder for analysis tools
    st.markdown("""
    ### Analysis Tools
    
    This section will provide tools for:
    
    - **Style Comparison** - Analyzing Audrey's writing patterns
    - **Vocabulary Analysis** - Word choice and frequency analysis
    - **Character Voice Consistency** - Ensuring character authenticity
    - **Plot Coherence** - Story structure and flow analysis
    """)

def show_about_page():
    st.markdown('<h2 class="section-header">About Audrey Berger Welz</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Remembering Audrey
    
    Audrey Berger Welz was a talented author whose creative vision brought *Circus of the Queens* 
    to life. Her storytelling captured the imagination of readers with its unique blend of 
    fantasy, mystery, and human emotion.
    
    *The Shadow of Lillya* represents her final creative project, a continuation of the 
    world she so beautifully crafted. This project honors her memory by bringing her 
    vision to completion.
    
    ### Acknowledgments
    
    We remember and honor **Audrey Berger Welz** for her creative vision and the beautiful 
    worlds she created. This project is a labor of love dedicated to bringing her final 
    story to completion.
    """)
    
    st.markdown("""
    ### Contact
    
    This is a deeply personal project honoring Audrey's literary legacy. While this space 
    serves as a memorial and completion effort, we welcome respectful engagement with the material.
    """)

if __name__ == "__main__":
    main()



