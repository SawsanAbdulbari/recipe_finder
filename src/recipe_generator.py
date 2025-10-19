"""
Recipe Generator Module using FLAN-T5
"""
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional
import config


class RecipeGenerator:
    """
    Generates recipes using FLAN-T5 language model
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize FLAN-T5 model
        
        Args:
            model_name: Hugging Face model name
        """
        self.model_name = model_name or config.LLM_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading LLM '{self.model_name}' on {self.device}...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=config.CACHE_DIR
        )
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            cache_dir=config.CACHE_DIR,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        
        self.model.to(self.device)
        self.model.eval()
        
        print("Recipe generator model loaded successfully!")
    
    def generate_recipe(
        self,
        ingredients: str,
        recipe_type: str = "Any",
        dietary: str = "None",
        max_length: int = None
    ) -> str:
        """
        Generate recipe based on ingredients and preferences
        
        Args:
            ingredients: Comma-separated list of ingredients
            recipe_type: Sweet, Savory, or Any
            dietary: Dietary restriction
            max_length: Maximum length of generated recipe
        
        Returns:
            Generated recipe text
        """
        max_length = max_length or config.MAX_RECIPE_LENGTH
        
        # Construct prompt
        prompt = self._build_prompt(ingredients, recipe_type, dietary)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # Generate recipe with proper FLAN-T5 settings
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=400,  # Generate more tokens
                    min_length=100,  # Ensure minimum output length
                    num_beams=6,  # More beams for better quality
                    length_penalty=1.5,  # Encourage longer outputs
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    do_sample=False  # Use beam search, not sampling
                )
            
            # Decode output
            recipe = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"[DEBUG] Raw recipe output: {recipe[:200]}...")  # First 200 chars
            print(f"[DEBUG] Recipe length: {len(recipe)} characters")

            # Format recipe
            formatted_recipe = self._format_recipe(recipe, ingredients, recipe_type, dietary)

            return formatted_recipe
        
        except Exception as e:
            print(f"Error during recipe generation: {e}")
            return f"Error generating recipe: {str(e)}\n\nPlease try again with different ingredients."
    
    def _build_prompt(self, ingredients: str, recipe_type: str, dietary: str) -> str:
        """
        Build prompt using best practices: few-shot examples + chain-of-thought
        """
        # Clean ingredients
        ingredients = ingredients.strip()

        # Few-shot example with clear structure
        example_prompt = """Create a recipe from ingredients.

Example:
Ingredients: pasta, tomatoes, basil, garlic
Recipe Name: Classic Tomato Basil Pasta
Ingredients List:
- 12 oz pasta
- 4 large tomatoes, diced
- 3 cloves garlic, minced
- 1/4 cup fresh basil, chopped
- 2 tbsp olive oil
- Salt and pepper to taste

Instructions:
1. Bring a large pot of salted water to boil. Cook pasta according to package directions (8-10 minutes).
2. While pasta cooks, heat olive oil in a large skillet over medium heat.
3. Add minced garlic and sauté for 1 minute until fragrant.
4. Add diced tomatoes, cook for 5-7 minutes until soft. Season with salt and pepper.
5. Drain pasta and add to the tomato sauce. Toss to combine.
6. Remove from heat, stir in fresh basil, and serve immediately.

Now create a recipe using these ingredients: """

        # Add user's ingredients
        prompt = example_prompt + ingredients

        # Add preferences
        if recipe_type != "Any":
            prompt += f". Make it {recipe_type.lower()}"

        if dietary != "None":
            prompt += f". Must be {dietary.lower()}"

        prompt += """.
Recipe Name:"""

        print(f"[DEBUG] Prompt length: {len(prompt)} chars")

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
        
        # Format the recipe text
        formatted_recipe = recipe.strip()
        
        # Add some structure if missing
        if "ingredients:" not in formatted_recipe.lower() and "instructions:" not in formatted_recipe.lower():
            formatted_recipe = self._add_structure(formatted_recipe)
        
        return header + formatted_recipe
    
    def _add_structure(self, recipe: str) -> str:
        """
        Add basic structure to recipe if it's missing
        """
        lines = recipe.split('. ')
        
        if len(lines) < 2:
            return recipe
        
        # Try to identify recipe name (usually first sentence)
        recipe_name = lines[0] if len(lines[0]) < 50 else "Delicious Recipe"
        
        structured = f"**{recipe_name}**\n\n"
        structured += "**Instructions:**\n"
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                structured += f"{i}. {line.strip()}\n"
        
        return structured


# Global instance (lazy loading)
_generator_instance: Optional[RecipeGenerator] = None


def get_generator_instance() -> RecipeGenerator:
    """
    Get or create global RecipeGenerator instance
    """
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = RecipeGenerator()
    return _generator_instance
