# AI Recipe Finder 🍳🎤

An intelligent voice-powered recipe generator that creates delicious recipes from your ingredients using AI. Features beautiful dark theme UI, PDF export, and lightning-fast generation with Groq API.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- 🎙️ **Voice Input**: Speak your ingredients naturally using OpenAI Whisper
- ⚡ **Lightning Fast**: 1-2 second recipe generation with Groq API (247x faster than FLAN-T5)
- 🎨 **Modern Dark Theme**: Beautiful, professional interface with smooth animations
- 🍽️ **Serving Size Control**: Adjust recipes for 1-12 people
- 📄 **PDF Export**: Download recipes as beautifully formatted PDFs
- 🎯 **Smart Preferences**: Choose recipe type (Sweet/Savory) and dietary restrictions
- 🔒 **Secure**: Environment variable configuration for API keys
- 📱 **Responsive**: Clean, intuitive Gradio interface

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/recipe_finder.git
cd recipe_finder

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Groq API key
# Get free API key from: https://console.groq.com
```

Edit `.env`:
```env
GROQ_API_KEY=your-groq-api-key-here
USE_GROQ=true
WHISPER_MODEL=small
```

### 3. Run the Application

```bash
python app.py
```

Access the app at: **http://127.0.0.1:7860**

## 📦 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Speech-to-Text** | OpenAI Whisper (Small) | Voice recognition |
| **Recipe Generation** | Groq API (Llama 3.3 70B) | Fast AI recipe creation |
| **Alternative LLM** | FLAN-T5 | Local fallback option |
| **UI Framework** | Gradio | Web interface |
| **PDF Generation** | ReportLab | Recipe export |
| **Configuration** | python-dotenv | Environment management |

## 📁 Project Structure

```
recipe_finder/
├── src/
│   ├── __init__.py
│   ├── speech_to_text.py      # Whisper integration
│   ├── recipe_generator.py    # FLAN-T5 (local) generator
│   ├── groq_recipe_generator.py  # Groq API (fast) generator
│   └── utils.py               # Helper functions
├── helper/
│   └── test_groq.py           # Test suite
├── models/                     # Model cache (auto-created)
├── app.py                      # Main Gradio application
├── config.py                   # Configuration (uses .env)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .env                        # Your environment (DO NOT COMMIT)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

All configuration is done via `.env` file:

```env
# Required
GROQ_API_KEY=your-groq-api-key-here

# Optional (defaults shown)
USE_GROQ=true                    # Use Groq (fast) vs FLAN-T5 (slow)
WHISPER_MODEL=small              # tiny, base, small, medium, large
DEVICE=cuda                      # cuda or cpu
SHARE_LINK=false                 # Create public URL
SERVER_HOST=127.0.0.1
SERVER_PORT=7860
```

### Getting Groq API Key (Free)

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up (no credit card required)
3. Create API key
4. Add to `.env` file
5. Free tier: **30 requests/minute**, **14,400 requests/day**

## 💡 Usage

### Voice Method

1. Click the microphone button
2. Speak your ingredients: *"chicken, tomatoes, garlic, onions"*
3. Recording auto-generates recipe when stopped
4. Or click "Transcribe Audio" first to review

### Text Method

1. Type ingredients in the text box
2. Select preferences (type, dietary, servings)
3. Click "Generate Recipe"

### PDF Export

1. Generate a recipe
2. Click "Download as PDF" button
3. Save formatted PDF file

## 📊 Performance

### Groq API (Recommended) ⚡
- **Speed**: 1-2 seconds
- **Quality**: Excellent (Llama 3.3 70B)
- **VRAM**: 0GB (cloud-based)
- **Cost**: FREE
- **Rate Limit**: 30/min, 14,400/day

### FLAN-T5 (Local Alternative) 🐌
- **Speed**: 247 seconds
- **Quality**: Poor
- **VRAM**: 3GB
- **Not Recommended**: 247x slower than Groq

### Whisper (Speech Recognition)
- **Model Size**: ~500MB (small)
- **Processing**: 2-4 seconds
- **Accuracy**: Excellent

## 🎯 Features in Detail

### Serving Size Control
- Adjust recipes for 1-12 people
- Automatically scales ingredients
- Updates instructions accordingly

### PDF Export
- Professional formatting
- Purple-themed design
- Includes all recipe details
- Timestamp footer
- Easy sharing

### Dietary Options
- None
- Vegetarian
- Vegan
- Gluten-Free
- Dairy-Free
- Nut-Free
- Keto
- Paleo

## 🧪 Testing

Run the comprehensive test suite:

```bash
python helper/test_groq.py
```

Tests include:
- Groq client initialization
- Recipe generation
- Input validation
- Dietary restrictions
- Serving size control
- PDF export

## 🐛 Troubleshooting

### "Groq API key not configured"
- **Solution**: Add your API key to `.env` file
- Get key from: https://console.groq.com

### Slow recipe generation
- **Solution**: Ensure `USE_GROQ=true` in `.env`
- Verify API key is correct

### Out of memory
- **Solution**: Use smaller Whisper model (tiny/base)
- Or use CPU: `DEVICE=cpu` in `.env`

### Audio not detected
- **Solution**: Check browser microphone permissions
- Allow microphone access when prompted

### Module not found
- **Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt
```

## 🚢 Deployment

### Local Deployment

```bash
python app.py
```

### Public Deployment (Gradio)

Set in `.env`:
```env
SHARE_LINK=true
```

Creates public URL valid for 72 hours.

### Production Deployment

For platforms like Hugging Face Spaces, Railway, or AWS:

1. Set environment variables in platform settings
2. Don't commit `.env` file
3. Use platform's secret management
4. Configure GROQ_API_KEY as secret

## 📝 Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for models
- **Internet**: Required for Groq API and initial model download
- **Optional GPU**: CUDA for faster Whisper transcription

## 🔒 Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ Environment variable configuration
- ✅ No hardcoded secrets
- ✅ Secure defaults
- ⚠️ Never commit `.env` to version control
- ⚠️ Keep API keys private

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📜 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **OpenAI Whisper** for speech recognition
- **Groq** for lightning-fast LLM inference
- **Gradio** for beautiful UI framework
- **Hugging Face** for model hosting

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/recipe_finder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/recipe_finder/discussions)

## 🗺️ Roadmap

- [x] Voice input with Whisper
- [x] Groq API integration
- [x] Serving size control
- [x] PDF export
- [x] Dark theme UI
- [ ] Recipe ratings
- [ ] Nutritional information
- [ ] Multi-language support
- [ ] Recipe image generation
- [ ] Save favorites
- [ ] Shopping list generation

---

**Made with ❤️ and AI**
