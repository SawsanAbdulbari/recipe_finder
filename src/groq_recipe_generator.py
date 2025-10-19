"""
Recipe Generator Module using Groq API (Llama 3.3 70B)
Fast, high-quality recipe generation (1-2 seconds vs 247 seconds)
"""
from groq import Groq
from typing import Optional
import config
import time


class GroqRecipeGenerator:
    """
    Generates recipes using Groq API with Llama 3.3 70B model
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key (get free from https://console.groq.com)

        Raises:
            ValueError: If API key is not configured or invalid
        """
        self.api_key = api_key or config.GROQ_API_KEY

        # Validate API key exists
        if not self.api_key or self.api_key == "your-groq-api-key-here":
            raise ValueError(
                "\n\n[ERROR] Groq API key not configured!\n"
                "Please:\n"
                "1. Get a free API key from: https://console.groq.com\n"
                "2. Add it to config.py: GROQ_API_KEY = 'your-key-here'\n"
            )

        # Validate API key format (should start with 'gsk_')
        if not self.api_key.startswith('gsk_'):
            print("[WARNING] API key may be invalid (should start with 'gsk_')")

        print("Initializing Groq client...")
        try:
            self.client = Groq(api_key=self.api_key)
            print("Groq client ready! (Llama 3.3 70B)")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Groq client: {str(e)}")

    def generate_recipe(
        self,
        ingredients: str,
        recipe_type: str = "Any",
        dietary: str = "None",
        servings: int = 4,
        max_length: int = None,
        max_retries: int = 2
    ) -> str:
        """
        Generate recipe based on ingredients and preferences

        Args:
            ingredients: Comma-separated list of ingredients
            recipe_type: Sweet, Savory, or Any
            dietary: Dietary restriction
            servings: Number of servings (default 4)
            max_length: Maximum tokens (default 800)
            max_retries: Maximum number of retry attempts (default 2)

        Returns:
            Generated recipe text
        """
        max_length = max_length or 800

        # Validate inputs
        if not ingredients or not ingredients.strip():
            return "[ERROR] No ingredients provided. Please enter some ingredients."

        # Build prompt
        prompt = self._build_prompt(ingredients, recipe_type, dietary, servings)

        # Retry logic for handling transient network issues
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"[INFO] Retry attempt {attempt}/{max_retries}...")
                    time.sleep(1)  # Brief delay before retry

                print(f"[DEBUG] Sending request to Groq API...")
                start_time = time.time()

                # Generate recipe with Groq API
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # Fast & high quality
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7,
                    max_tokens=max_length,
                    top_p=0.9
                )

                elapsed_time = time.time() - start_time
                recipe = response.choices[0].message.content
                print(f"[DEBUG] Received recipe ({len(recipe)} chars) in {elapsed_time:.2f}s")

                # Validate response
                if not recipe or len(recipe) < 50:
                    print("[WARNING] Recipe seems too short, may be incomplete")

                # Format recipe
                formatted_recipe = self._format_recipe(recipe, ingredients, recipe_type, dietary)

                return formatted_recipe

            except AttributeError as e:
                # Groq API response structure issue
                print(f"[ERROR] Invalid API response structure: {e}")
                return f"[ERROR] Invalid response from Groq API.\n\nPlease try again."

            except ConnectionError as e:
                # Network connectivity issues
                print(f"[ERROR] Network connection error: {e}")
                if attempt < max_retries:
                    continue
                return f"[ERROR] Network connection failed.\n\nPlease check your internet connection and try again."

            except TimeoutError as e:
                # API timeout
                print(f"[ERROR] Request timeout: {e}")
                if attempt < max_retries:
                    continue
                return f"[ERROR] Request timed out.\n\nPlease try again."

            except Exception as e:
                # Catch-all for other errors
                error_msg = str(e).lower()

                # Check for common error types
                if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                    print(f"[ERROR] Authentication failed: {e}")
                    return (
                        f"[ERROR] Invalid API key.\n\n"
                        f"Please check your Groq API key in config.py.\n"
                        f"Get a free key from: https://console.groq.com"
                    )
                elif "rate limit" in error_msg or "429" in error_msg:
                    print(f"[ERROR] Rate limit exceeded: {e}")
                    return (
                        f"[ERROR] Rate limit exceeded.\n\n"
                        f"Please wait a moment and try again.\n"
                        f"Free tier: 30 requests per minute"
                    )
                elif "model" in error_msg:
                    print(f"[ERROR] Model error: {e}")
                    return f"[ERROR] Model unavailable.\n\nThe Groq API may be experiencing issues. Please try again later."
                else:
                    print(f"[ERROR] Unexpected error during recipe generation: {e}")
                    if attempt < max_retries:
                        continue
                    return f"[ERROR] Error generating recipe: {str(e)}\n\nPlease try again."

        # Should not reach here, but just in case
        return "[ERROR] Failed to generate recipe after multiple attempts.\n\nPlease try again later."

    def _build_prompt(self, ingredients: str, recipe_type: str, dietary: str, servings: int) -> str:
        """
        Build prompt for recipe generation
        """
        ingredients = ingredients.strip()

        prompt = f"""Create a detailed recipe using these ingredients: {ingredients}

Please provide:
1. A creative recipe name
2. Complete ingredients list with measurements for {servings} servings
3. Step-by-step cooking instructions

Requirements:
- Servings: {servings} people"""

        if recipe_type != "Any":
            prompt += f"\n- Type: {recipe_type}"

        if dietary != "None":
            prompt += f"\n- Dietary: {dietary}"

        prompt += """

Format:
Recipe Name: [name]
Servings: [number]

Ingredients:
- [ingredient with measurement]
- [ingredient with measurement]
...

Instructions:
1. [step]
2. [step]
...
"""

        return prompt

    def _format_recipe(self, recipe: str, ingredients: str, recipe_type: str, dietary: str) -> str:
        """
        Format the generated recipe for better readability
        """
        # Add header with preferences
        header = "**AI-Generated Recipe**\n\n"

        if recipe_type != "Any":
            header += f"**Type:** {recipe_type}\n"
        if dietary != "None":
            header += f"**Dietary:** {dietary}\n"

        header += f"**Your Ingredients:** {ingredients}\n"
        header += "\n" + "="*50 + "\n\n"

        return header + recipe.strip()


# Global instance (lazy loading)
_groq_generator_instance: Optional[GroqRecipeGenerator] = None


def get_groq_generator_instance() -> GroqRecipeGenerator:
    """
    Get or create global GroqRecipeGenerator instance
    """
    global _groq_generator_instance
    if _groq_generator_instance is None:
        _groq_generator_instance = GroqRecipeGenerator()
    return _groq_generator_instance
