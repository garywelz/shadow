# Setting Up GitHub and Hugging Face

## Step 1: Initialize Git Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Shadow of Lillya completion project"
```

## Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Repository name: `shadow-of-lillya` (or your preferred name)
4. Description: "Completing The Shadow of Lillya by Audrey Berger Welz"
5. Choose Public or Private (your preference)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 3: Connect Local Repository to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/shadow-of-lillya.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 4: Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in:
   - **Space name:** `shadow` (or your preferred name)
   - **SDK:** Streamlit
   - **Hardware:** CPU Basic (free tier is fine)
   - **Visibility:** Public or Private
4. Click "Create Space"

## Step 5: Connect Hugging Face to GitHub

### Option A: Connect Existing GitHub Repository

1. In your Hugging Face Space, go to "Settings"
2. Scroll to "Repository" section
3. Click "Connect to GitHub"
4. Authorize Hugging Face to access your GitHub
5. Select your repository: `YOUR_USERNAME/shadow-of-lillya`
6. Click "Connect"

### Option B: Push Directly to Hugging Face

```bash
# Add Hugging Face as a remote
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/shadow.git

# Push to Hugging Face
git push huggingface main
```

## Step 6: Configure Hugging Face Space

### Set Environment Variables (for API keys)

1. In your Hugging Face Space, go to "Settings"
2. Scroll to "Repository secrets"
3. Add secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key (if using OpenAI)
   - `ANTHROPIC_API_KEY` - Your Anthropic API key (if using Anthropic)

### Verify Space Configuration

Make sure these files exist in your repository:
- ✅ `app.py` - Streamlit application
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Project description
- ✅ `config.yaml` or `.hfignore` - Space configuration (optional)

## Step 7: Deploy and Test

1. Hugging Face will automatically build and deploy your space
2. Wait for the build to complete (usually 2-5 minutes)
3. Visit your space URL: `https://huggingface.co/spaces/YOUR_USERNAME/shadow`
4. Test the application

## Important Notes

### What Gets Committed

✅ **DO Commit:**
- All Python scripts
- Configuration files (requirements.txt, config.yaml)
- Documentation (README, workflow guides)
- Manuscript structure (directories, READMEs)
- Small to medium manuscript files (PDFs, Markdown)

❌ **DON'T Commit:**
- API keys or secrets (use Hugging Face secrets)
- Virtual environment (`venv/`)
- Large generated files (if they exceed GitHub's limits)
- Personal notes or temporary files

### File Size Considerations

GitHub has file size limits:
- Files over 50MB require Git LFS
- Files over 100MB are blocked

If your manuscript PDFs are very large, consider:
- Using Git LFS for large files
- Or storing large files elsewhere and referencing them

### Updating Your Space

After making changes:

```bash
# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# If connected, Hugging Face will auto-update
# Or push directly to Hugging Face:
git push huggingface main
```

## Troubleshooting

### Build Fails on Hugging Face

1. Check `requirements.txt` - all dependencies listed?
2. Check `app.py` - any import errors?
3. Check build logs in Hugging Face Space settings

### API Keys Not Working

1. Verify secrets are set in Hugging Face Space settings
2. Check that environment variable names match in your code
3. Restart the space after adding secrets

### Large Files

If you get errors about large files:
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pdf"
git lfs track "*.docx"

# Add and commit
git add .gitattributes
git add .
git commit -m "Add large files with Git LFS"
```

## Next Steps After Deployment

1. ✅ Test the web interface
2. ✅ Verify manuscript files are accessible
3. ✅ Test LLM completion generation (if API keys are set)
4. ✅ Share the space with others who want to contribute

---

Your project is now on GitHub and Hugging Face! 🎉

