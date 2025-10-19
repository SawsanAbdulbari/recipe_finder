"""
Utility functions for AI Recipe Finder
"""
import os
import re
from typing import List, Tuple


def clean_ingredients_text(text: str) -> str:
    """
    Clean and format ingredients text from speech recognition
    
    Args:
        text: Raw transcribed text
    
    Returns:
        Cleaned ingredients text
    """
    # Remove common filler words
    filler_words = ["um", "uh", "like", "you know", "i have", "i've got"]
    
    text_lower = text.lower()
    for filler in filler_words:
        text_lower = text_lower.replace(filler, "")
    
    # Clean up extra spaces
    text_lower = " ".join(text_lower.split())
    
    # Remove "and" at the beginning if present
    text_lower = text_lower.strip()
    if text_lower.startswith("and "):
        text_lower = text_lower[4:]
    
    return text_lower.strip()


def parse_ingredients(text: str) -> List[str]:
    """
    Parse ingredients from text into a list
    
    Args:
        text: Text containing ingredients
    
    Returns:
        List of ingredients
    """
    # Split by common separators
    separators = [",", " and ", " & ", ";"]
    
    ingredients = [text]
    for sep in separators:
        new_ingredients = []
        for ing in ingredients:
            new_ingredients.extend(ing.split(sep))
        ingredients = new_ingredients
    
    # Clean each ingredient
    ingredients = [ing.strip() for ing in ingredients if ing.strip()]
    
    return ingredients


def format_ingredients_list(ingredients: List[str]) -> str:
    """
    Format list of ingredients as a readable string
    
    Args:
        ingredients: List of ingredient strings
    
    Returns:
        Formatted string
    """
    if not ingredients:
        return ""
    
    if len(ingredients) == 1:
        return ingredients[0]
    
    if len(ingredients) == 2:
        return f"{ingredients[0]} and {ingredients[1]}"
    
    return ", ".join(ingredients[:-1]) + f", and {ingredients[-1]}"


def validate_audio_input(audio_data) -> Tuple[bool, str]:
    """
    Validate audio input from Gradio
    
    Args:
        audio_data: Audio data from Gradio (tuple or None)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if audio_data is None:
        return False, "No audio recorded. Please record your voice."
    
    # Gradio returns tuple of (sample_rate, audio_array)
    if isinstance(audio_data, tuple) and len(audio_data) == 2:
        sample_rate, audio_array = audio_data
        
        if audio_array is None or len(audio_array) == 0:
            return False, "Audio is empty. Please try recording again."
        
        # Check if audio is too short (less than 0.5 seconds)
        duration = len(audio_array) / sample_rate
        if duration < 0.5:
            return False, "Audio is too short. Please speak for at least 1 second."
        
        return True, ""
    
    return False, "Invalid audio format."


def create_recipe_card(recipe_text: str) -> str:
    """
    Create a nicely formatted recipe card
    
    Args:
        recipe_text: Generated recipe text
    
    Returns:
        Formatted recipe card
    """
    # Add some styling hints for Gradio markdown
    lines = recipe_text.split("\n")
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Make headers bold
        if stripped and not stripped.startswith("*") and not stripped.startswith("-"):
            if any(keyword in stripped.lower() for keyword in ["recipe", "ingredients:", "instructions:", "directions:", "steps:"]):
                if not stripped.startswith("**"):
                    line = f"**{stripped}**"
        
        formatted_lines.append(line)
    
    return "\n".join(formatted_lines)


def ensure_directories():
    """
    Ensure all necessary directories exist
    """
    import config
    
    directories = [
        config.MODELS_DIR,
        config.CACHE_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"[OK] Directory ensured: {directory}")


def get_example_ingredients() -> List[List[str]]:
    """
    Get example ingredients for the interface
    
    Returns:
        List of example ingredient combinations
    """
    examples = [
        ["chicken, tomatoes, onions, garlic"],
        ["eggs, milk, flour, sugar"],
        ["pasta, olive oil, basil, parmesan"],
        ["rice, beans, bell peppers, cumin"],
        ["salmon, lemon, dill, butter"]
    ]
    
    return examples
