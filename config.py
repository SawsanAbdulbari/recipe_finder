"""
Configuration settings for AI Recipe Finder
Loads settings from environment variables with sensible defaults
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API Configuration (RECOMMENDED - Fast & Free)
# Get your free API key from: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
USE_GROQ = os.getenv("USE_GROQ", "true").lower() == "true"

# Model Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # Options: tiny, base, small, medium, large
LLM_MODEL = os.getenv("LLM_MODEL", "google/flan-t5-large")  # Options: base, large, xl

# Generation Parameters
MAX_RECIPE_LENGTH = int(os.getenv("MAX_RECIPE_LENGTH", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
TOP_K = int(os.getenv("TOP_K", "50"))

# Preferences
RECIPE_TYPES = ["Sweet", "Savory", "Any"]
DIETARY_OPTIONS = [
    "None",
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
    "Nut-Free",
    "Keto",
    "Paleo"
]

# Default preferences
DEFAULT_SERVINGS = int(os.getenv("DEFAULT_SERVINGS", "4"))
DEFAULT_RECIPE_TYPE = os.getenv("DEFAULT_RECIPE_TYPE", "Any")
DEFAULT_DIETARY = os.getenv("DEFAULT_DIETARY", "None")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
CACHE_DIR = os.path.join(MODELS_DIR, "cache")

# Gradio Configuration
GRADIO_THEME = os.getenv("GRADIO_THEME", "default")
SHARE_LINK = os.getenv("SHARE_LINK", "false").lower() == "true"
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))

# Device Configuration
DEVICE = os.getenv("DEVICE", "cuda")  # Will fallback to CPU if CUDA not available

# Validate critical settings
if USE_GROQ and (not GROQ_API_KEY or GROQ_API_KEY == "your-groq-api-key-here"):
    print("\n" + "="*60)
    print("WARNING: Groq API key not configured!")
    print("="*60)
    print("Please set GROQ_API_KEY in your .env file")
    print("Get a free API key from: https://console.groq.com")
    print("="*60 + "\n")
