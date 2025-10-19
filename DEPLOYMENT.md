# Deployment Guide

Complete guide for deploying AI Recipe Finder to GitHub and various platforms.

## Table of Contents

- [GitHub Deployment](#github-deployment)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Git Commands](#git-commands)
- [Platform-Specific Deployments](#platform-specific-deployments)

---

## Pre-Deployment Checklist

###  Files Created

- [x] `.gitignore` - Prevents sensitive files from being committed
- [x] `.env.example` - Template for environment variables
- [x] `.env` - Your local environment (NEVER commit this!)
- [x] `config.py` - Updated to use environment variables
- [x] `README.md` - Comprehensive documentation
- [x] `LICENSE` - MIT License
- [x] `requirements.txt` - All Python dependencies
- [x] `DEPLOYMENT.md` - This file

###   Security Check

**CRITICAL: Before pushing to GitHub**

```bash
# Verify .env is in .gitignore
grep ".env" .gitignore

# Check for hardcoded secrets (should return nothing sensitive)
grep -r "gsk_" --exclude-dir=.git --exclude=.env --exclude=.env.example .

# Verify config.py uses environment variables
grep "os.getenv" config.py
```

### = API Key Protection

 **What's Safe**:
- `.env.example` (template with placeholder keys)
- `config.py` (uses `os.getenv()`)
- `README.md` (no actual keys)

L **Never Commit**:
- `.env` (contains your actual API key)
- Any file with actual `GROQ_API_KEY` value

---

## GitHub Deployment

### Step 1: Initialize Git Repository

```bash
cd D:\ai\recipe_finder

# Initialize git (if not already)
git init

# Add all files (respects .gitignore)
git add .

# Verify what will be committed (should NOT include .env)
git status

# Check .env is not staged
git ls-files | grep "^\.env$"  # Should return nothing
```

### Step 2: Create Initial Commit

```bash
# Create first commit
git commit -m "Initial commit: AI Recipe Finder v1.1.0

Features:
- Voice-powered recipe generation with Whisper
- Groq API integration (1-2 second generation)
- Modern dark theme UI with smooth animations
- Serving size control (1-12 servings)
- PDF export functionality
- Environment variable configuration
- Comprehensive test suite"
```

### Step 3: Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to https://github.com/new
2. Repository name: `recipe_finder` or `ai-recipe-finder`
3. Description: `Voice-powered AI recipe generator with Groq API and Whisper`
4. Visibility: Public or Private
5. **DO NOT** initialize with README (we have one)
6. Click "Create repository"

**Option B: Via GitHub CLI**
```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Create repository
gh repo create recipe_finder --public --description "Voice-powered AI recipe generator"

# Or private
gh repo create recipe_finder --private --description "Voice-powered AI recipe generator"
```

### Step 4: Push to GitHub

```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/recipe_finder.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 5: Verify Deployment

Visit your repository and verify:

 `.env` is NOT in the repository
 `.env.example` IS in the repository
 `.gitignore` is working
 README.md displays correctly
 All source files are present

---

## Platform-Specific Deployments

### Hugging Face Spaces

Perfect for sharing your app publicly!

**1. Create Space**
```bash
# Install huggingface-hub
pip install huggingface-hub

# Login
huggingface-cli login
```

**2. Create `app.py` wrapper** (if needed)

Already have `app.py` - no changes needed!

**3. Set Secrets**
- Go to Space Settings ’ Variables and secrets
- Add: `GROQ_API_KEY` = your-key-here
- Add: `USE_GROQ` = true

**4. Push to Space**
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/recipe-finder
git push hf main
```

**Files needed**:
- `app.py`  (already exists)
- `requirements.txt`  (already exists)
- `README.md`  (already exists)

---

### Railway

**1. Install Railway CLI**
```bash
npm install -g @railway/cli

# Login
railway login
```

**2. Initialize Project**
```bash
railway init
```

**3. Set Environment Variables**
```bash
railway variables set GROQ_API_KEY=your-key-here
railway variables set USE_GROQ=true
railway variables set WHISPER_MODEL=small
```

**4. Deploy**
```bash
railway up
```

---

### Render

**1. Create `render.yaml`**
```yaml
services:
  - type: web
    name: ai-recipe-finder
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python app.py"
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: USE_GROQ
        value: "true"
```

**2. Connect Repository**
- Go to https://render.com
- New ’ Web Service
- Connect your GitHub repository
- Add environment variables in dashboard

---

### Docker Deployment

**Create `Dockerfile`**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 7860

# Run application
CMD ["python", "app.py"]
```

**Build and Run**:
```bash
# Build image
docker build -t ai-recipe-finder .

# Run container
docker run -p 7860:7860 \
  -e GROQ_API_KEY=your-key-here \
  -e USE_GROQ=true \
  ai-recipe-finder
```

---

## Environment Variables for Production

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | `gsk_...` |
| `USE_GROQ` | Use Groq API | `true` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model size | `small` |
| `DEVICE` | Compute device | `cuda` |
| `SHARE_LINK` | Create public Gradio link | `false` |
| `SERVER_HOST` | Server host | `127.0.0.1` |
| `SERVER_PORT` | Server port | `7860` |

---

## Post-Deployment Testing

### 1. Test Locally First

```bash
# Run app
python app.py

# Run tests
python helper/test_groq.py

# Verify:
# - Voice input works
# - Recipe generation works
# - PDF export works
# - All features functional
```

### 2. Test Production Deployment

- Test voice recording
- Generate multiple recipes
- Test PDF export
- Verify error handling
- Check response times
- Test rate limits

---

## Troubleshooting

### Git Issues

**Problem**: `.env` was committed
```bash
# Remove from Git (keeps local file)
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

**Problem**: Large files in history
```bash
# Use BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/
```

### Deployment Issues

**Problem**: Environment variables not loading
- Check platform's environment variable syntax
- Verify variable names match exactly
- Check for typos in variable values

**Problem**: Out of memory
- Use smaller Whisper model: `WHISPER_MODEL=tiny`
- Use CPU: `DEVICE=cpu`
- Upgrade server resources

**Problem**: Slow performance
- Ensure `USE_GROQ=true`
- Check internet connection to Groq API
- Verify API key is valid

---

## Maintenance

### Regular Updates

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
python helper/test_groq.py

# Commit and push
git add .
git commit -m "Update dependencies"
git push
```

### Monitoring

- Check Groq API usage: https://console.groq.com
- Monitor error rates
- Track response times
- Review user feedback

---

## Security Best Practices

1.  **Never commit `.env`** - Add to `.gitignore`
2.  **Rotate API keys** - If exposed, generate new one
3.  **Use secrets management** - Platform-specific secret storage
4.  **Limit API keys** - Use read-only keys when possible
5.  **Monitor usage** - Check for unusual activity
6.  **Keep dependencies updated** - Regular security updates

---

## Support

- **Issues**: https://github.com/YOUR_USERNAME/recipe_finder/issues
- **Groq Support**: https://console.groq.com/docs
- **Gradio Docs**: https://www.gradio.app/docs

---

**Ready to deploy!** =€
