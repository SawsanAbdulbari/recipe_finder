"""
AI Recipe Finder - Main Application
Voice-powered recipe generation using Whisper and FLAN-T5
"""
import gradio as gr
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import from src modules (without src prefix since it's in path)
from speech_to_text import get_stt_instance
from recipe_generator import get_generator_instance
from groq_recipe_generator import get_groq_generator_instance
from utils import (
    clean_ingredients_text,
    validate_audio_input,
    create_recipe_card,
    ensure_directories,
    get_example_ingredients
)
import config


# Global model instances (lazy loaded)
stt_model = None
recipe_model = None


def initialize_models():
    """Initialize AI models (called on first use)"""
    global stt_model, recipe_model

    if stt_model is None:
        print("\n" + "="*50)
        print("Initializing AI Models...")
        print("="*50)
        stt_model = get_stt_instance()

    if recipe_model is None:
        # Choose between Groq (fast) or FLAN-T5 (slow)
        if config.USE_GROQ:
            print("Using Groq API (fast & high quality)...")
            recipe_model = get_groq_generator_instance()
        else:
            print("Using FLAN-T5 (slow, local model)...")
            recipe_model = get_generator_instance()

    return stt_model, recipe_model


def transcribe_audio(audio):
    """
    Transcribe audio input to text
    
    Args:
        audio: Audio data from Gradio microphone
    
    Returns:
        Transcribed text
    """
    try:
        # Validate audio
        is_valid, error_msg = validate_audio_input(audio)
        if not is_valid:
            return error_msg
        
        # Initialize models
        stt, _ = initialize_models()
        
        # Extract audio data
        sample_rate, audio_array = audio
        
        # Transcribe
        text = stt.transcribe_array(audio_array, sample_rate)
        
        # Clean the text
        cleaned_text = clean_ingredients_text(text)
        
        return cleaned_text
    
    except Exception as e:
        return f"[ERROR] Error transcribing audio: {str(e)}"


def generate_recipe_from_voice(audio, recipe_type, dietary, servings):
    """
    Complete pipeline: transcribe audio and generate recipe

    Args:
        audio: Audio data from Gradio microphone
        recipe_type: Type of recipe (Sweet/Savory/Any)
        dietary: Dietary restriction
        servings: Number of servings

    Returns:
        Tuple of (transcribed_text, generated_recipe, recipe_state, pdf_btn_visible, pdf_file_visible)
    """
    # Transcribe audio
    ingredients_text = transcribe_audio(audio)

    # Check if transcription failed
    if ingredients_text.startswith("Error") or ingredients_text.startswith("No speech"):
        error_msg = "[ERROR] Could not generate recipe. Please record your ingredients again."
        return ingredients_text, error_msg, "", gr.update(visible=False), gr.update(visible=False)

    # Generate recipe
    recipe, recipe_text, pdf_visible, file_visible = generate_recipe_from_text(ingredients_text, recipe_type, dietary, servings)

    return ingredients_text, recipe, recipe_text, pdf_visible, file_visible


def generate_recipe_from_text(ingredients_text, recipe_type, dietary, servings):
    """
    Generate recipe from text ingredients

    Args:
        ingredients_text: Text containing ingredients
        recipe_type: Type of recipe (Sweet/Savory/Any)
        dietary: Dietary restriction
        servings: Number of servings

    Returns:
        Tuple of (formatted_recipe, raw_recipe_text, pdf_btn_visible, pdf_file_visible)
    """
    if not ingredients_text or not ingredients_text.strip():
        error_msg = "[ERROR] Please provide ingredients first."
        return error_msg, "", gr.update(visible=False), gr.update(visible=False)

    # Initialize models
    _, recipe_gen = initialize_models()

    # Generate recipe
    print(f"\nGenerating recipe...")
    print(f"Ingredients: {ingredients_text}")
    print(f"Type: {recipe_type}, Dietary: {dietary}, Servings: {servings}")

    recipe = recipe_gen.generate_recipe(
        ingredients=ingredients_text,
        recipe_type=recipe_type,
        dietary=dietary,
        servings=int(servings)
    )

    # Format recipe card
    formatted_recipe = create_recipe_card(recipe)

    # Return formatted recipe, raw text for PDF, and show PDF button
    return formatted_recipe, recipe, gr.update(visible=True), gr.update(visible=False)


def export_recipe_as_pdf(recipe_text):
    """
    Export recipe as PDF file

    Args:
        recipe_text: Recipe text to export

    Returns:
        Tuple of (pdf_file_path, file_component_update)
    """
    if not recipe_text or recipe_text.strip() == "":
        return None, gr.update(visible=False)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        import tempfile
        from datetime import datetime

        # Create temporary PDF file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(tempfile.gettempdir(), f"recipe_{timestamp}.pdf")

        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#667eea',
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#667eea',
            spaceAfter=12,
            spaceBefore=12
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        )

        # Parse and format the recipe text
        lines = recipe_text.strip().split('\n')

        # Add title
        story.append(Paragraph("AI-Generated Recipe", title_style))
        story.append(Spacer(1, 12))

        # Process recipe content
        for line in lines:
            line = line.strip()
            if not line or line == "=" * 50:
                continue

            # Check for headings (lines with ** or starting with Recipe Name, Ingredients, Instructions)
            if line.startswith('**') and line.endswith('**'):
                # Bold heading
                heading_text = line.replace('**', '')
                story.append(Paragraph(heading_text, heading_style))
            elif any(line.startswith(prefix) for prefix in ['Recipe Name:', 'Ingredients:', 'Instructions:']):
                story.append(Paragraph(line, heading_style))
            elif line.startswith('-') or line[0].isdigit() and '. ' in line[:4]:
                # List item
                story.append(Paragraph(line, body_style))
            else:
                # Regular text
                if line:
                    story.append(Paragraph(line, body_style))

        # Add footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor='gray',
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"Generated by AI Recipe Finder • {datetime.now().strftime('%B %d, %Y')}",
            footer_style
        ))

        # Build PDF
        doc.build(story)

        print(f"[INFO] PDF generated: {pdf_path}")
        return pdf_path, gr.update(visible=True, value=pdf_path)

    except ImportError:
        error_msg = "[ERROR] PDF library not installed. Run: pip install reportlab"
        print(error_msg)
        return None, gr.update(visible=False)
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {e}")
        return None, gr.update(visible=False)


def create_interface():
    """Create Gradio interface"""
    
    # Ensure directories exist
    ensure_directories()
    
    # Custom CSS for modern dark theme
    custom_css = """
    /* Global dark theme */
    body {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .gradio-container {
        max-width: 1400px !important;
        margin: auto;
    }

    /* Header styling */
    .header {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }

    .header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        font-weight: 700;
    }

    .header p {
        font-size: 1.1em;
        opacity: 0.95;
    }

    /* Section headers */
    .section-header {
        background: rgba(102, 126, 234, 0.1);
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 15px;
        color: #e0e0e0 !important;
    }

    /* Card containers */
    .control-card {
        background-color: #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #4a5568;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Input components dark theme */
    .input-box, textarea, input, select {
        background-color: #2d3748 !important;
        border: 1px solid #4a5568 !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
    }

    label {
        color: #e0e0e0 !important;
        font-weight: 500 !important;
    }

    /* Buttons */
    button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        padding: 12px 24px !important;
    }

    .primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }

    .primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }

    .secondary {
        background-color: #4a5568 !important;
        border: none !important;
        color: white !important;
    }

    .secondary:hover {
        background-color: #667eea !important;
        transform: translateY(-2px);
    }

    /* Recipe output card */
    .recipe-output {
        background-color: #ffffff !important;
        padding: 30px;
        border-radius: 15px;
        border: none !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        color: #2d3748 !important;
        min-height: 400px;
    }

    .recipe-output * {
        color: #2d3748 !important;
    }

    .recipe-output h1, .recipe-output h2, .recipe-output h3 {
        color: #1a202c !important;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .recipe-output strong {
        color: #667eea !important;
        font-weight: 700;
    }

    .recipe-output p, .recipe-output li {
        color: #2d3748 !important;
        line-height: 1.8;
    }

    .recipe-output ul, .recipe-output ol {
        margin-left: 20px;
    }

    /* Examples table */
    .examples-table {
        background-color: #2d3748;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }

    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 15px;
    }

    thead {
        background-color: #667eea;
        color: white;
    }

    thead th {
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        color: white !important;
    }

    thead th:first-child {
        border-top-left-radius: 8px;
    }

    thead th:last-child {
        border-top-right-radius: 8px;
    }

    tbody tr {
        background-color: #2d3748;
        border-bottom: 1px solid #4a5568;
        transition: background-color 0.2s ease;
    }

    tbody tr:hover {
        background-color: #3d4758;
        cursor: pointer;
    }

    tbody tr:last-child {
        border-bottom: none;
    }

    tbody td {
        padding: 12px 16px;
        color: #e0e0e0 !important;
    }

    tbody tr:last-child td:first-child {
        border-bottom-left-radius: 8px;
    }

    tbody tr:last-child td:last-child {
        border-bottom-right-radius: 8px;
    }

    /* Loading state */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* Info boxes */
    .info-box {
        background-color: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        color: #cbd5e0 !important;
    }

    .success-box {
        background-color: rgba(72, 187, 120, 0.1);
        border-left: 4px solid #48bb78;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        color: #9ae6b4 !important;
    }

    .warning-box {
        background-color: rgba(237, 137, 54, 0.1);
        border-left: 4px solid #ed8936;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        color: #fbd38d !important;
    }

    /* Markdown content */
    .markdown {
        color: #e0e0e0 !important;
    }

    .markdown h3 {
        color: #ffffff !important;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .markdown p {
        color: #cbd5e0 !important;
        line-height: 1.6;
    }

    .markdown li {
        color: #cbd5e0 !important;
        line-height: 1.8;
    }

    /* Audio component */
    .audio-container {
        background-color: #2d3748 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }

    /* Slider styling */
    input[type="range"] {
        accent-color: #667eea !important;
    }

    /* Radio and dropdown */
    .radio-group, .dropdown {
        background-color: #2d3748 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* File component */
    .file {
        background-color: #2d3748 !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
    }

    /* Divider */
    hr {
        border-color: #4a5568 !important;
        margin: 30px 0;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1a202c;
    }

    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }

    /* Accordion styling */
    .accordion {
        background-color: #2d3748 !important;
        border-radius: 10px !important;
        border: 1px solid #4a5568 !important;
        margin-top: 20px;
    }

    .accordion summary {
        padding: 15px 20px !important;
        font-weight: 600 !important;
        color: #e0e0e0 !important;
        cursor: pointer !important;
        border-radius: 10px !important;
        transition: background-color 0.2s ease !important;
    }

    .accordion summary:hover {
        background-color: rgba(102, 126, 234, 0.1) !important;
    }

    .accordion[open] summary {
        border-bottom: 1px solid #4a5568 !important;
        border-radius: 10px 10px 0 0 !important;
        background-color: rgba(102, 126, 234, 0.15) !important;
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    .status-success {
        background-color: #48bb78;
    }

    .status-warning {
        background-color: #ed8936;
    }

    .status-info {
        background-color: #667eea;
    }

    /* Better spacing for button groups */
    .button-group {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    /* Subtle hover effects on cards */
    .hover-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .hover-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
    """
    
    # Use dark theme
    dark_theme = gr.themes.Base(
        primary_hue="purple",
        secondary_hue="blue",
        neutral_hue="slate",
    ).set(
        body_background_fill="#1a1a2e",
        body_background_fill_dark="#1a1a2e",
        block_background_fill="#2d3748",
        block_background_fill_dark="#2d3748",
        input_background_fill="#2d3748",
        input_background_fill_dark="#2d3748",
        button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        button_primary_background_fill_dark="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    )

    with gr.Blocks(css=custom_css, theme=dark_theme) as app:
        
        gr.Markdown(
            """
            <div class="header">
                <h1>🍳 AI Recipe Finder 🎤</h1>
                <p style="font-size: 18px; margin-top: 10px;">
                    Speak your ingredients and let AI create delicious recipes!
                </p>
            </div>
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                
                gr.Markdown("### 🎙️ Step 1: Record Your Ingredients")
                gr.Markdown("*Click the microphone and speak naturally*")
                
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="Voice Input",
                    format="wav",
                    show_download_button=False,
                    show_share_button=False
                )
                
                transcribe_btn = gr.Button("🎯 Transcribe Audio", variant="secondary")
                
                generate_from_audio_btn = gr.Button("🎤 Generate Recipe from Audio", variant="primary")
                
                ingredients_output = gr.Textbox(
                    label="Detected Ingredients",
                    placeholder="Your spoken ingredients will appear here...",
                    lines=3
                )
                
                gr.Markdown("### 🎨 Step 2: Choose Your Preferences")
                
                recipe_type = gr.Radio(
                    choices=config.RECIPE_TYPES,
                    value="Any",
                    label="Recipe Type"
                )
                
                dietary = gr.Dropdown(
                    choices=config.DIETARY_OPTIONS,
                    value="None",
                    label="Dietary Restrictions"
                )

                servings = gr.Slider(
                    minimum=1,
                    maximum=12,
                    value=4,
                    step=1,
                    label="Number of Servings",
                    info="Adjust recipe quantity for desired servings"
                )

                generate_btn = gr.Button("✨ Generate Recipe", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📖 Your AI-Generated Recipe")

                recipe_output = gr.Markdown(
                    value="*Your recipe will appear here...*",
                    elem_classes=["recipe-output"]
                )

                # Hidden state to store raw recipe text for PDF export
                recipe_state = gr.State(value="")

                # PDF Download button
                pdf_btn = gr.Button("📄 Download as PDF", variant="secondary", size="lg", visible=False)
                pdf_file = gr.File(label="Download Recipe PDF", visible=False)
        
        gr.Markdown("---")

        with gr.Accordion("💡 Try These Example Recipes", open=False):
            gr.Markdown("""
            <div class="info-box">
            Click any example below to automatically fill in the ingredients and preferences
            </div>
            """)
            # Example inputs
            gr.Examples(
                examples=[
                    ["chicken, tomatoes, garlic, onions", "Savory", "None"],
                    ["eggs, flour, milk, sugar", "Sweet", "None"],
                    ["chickpeas, tahini, lemon, olive oil", "Savory", "Vegan"],
                    ["bananas, oats, honey, cinnamon", "Sweet", "Gluten-Free"],
                ],
                inputs=[ingredients_output, recipe_type, dietary],
                label="Example Recipes"
            )
        
        # Event handlers
        transcribe_btn.click(
            fn=transcribe_audio,
            inputs=[audio_input],
            outputs=[ingredients_output]
        )

        # Generate recipe from text (when using text input)
        generate_btn.click(
            fn=generate_recipe_from_text,
            inputs=[ingredients_output, recipe_type, dietary, servings],
            outputs=[recipe_output, recipe_state, pdf_btn, pdf_file]
        )

        # Generate recipe directly from audio (manual button)
        generate_from_audio_btn.click(
            fn=generate_recipe_from_voice,
            inputs=[audio_input, recipe_type, dietary, servings],
            outputs=[ingredients_output, recipe_output, recipe_state, pdf_btn, pdf_file]
        )

        # Generate recipe directly from audio (when audio recording stops)
        audio_input.stop_recording(
            fn=generate_recipe_from_voice,
            inputs=[audio_input, recipe_type, dietary, servings],
            outputs=[ingredients_output, recipe_output, recipe_state, pdf_btn, pdf_file]
        )

        # PDF export handler
        pdf_btn.click(
            fn=export_recipe_as_pdf,
            inputs=[recipe_state],
            outputs=[pdf_file, pdf_file]
        )
        
        
        # Dynamic "Powered by" section with improved styling
        gr.Markdown("---")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 📝 Usage Tips
                <div class="info-box">
                <strong>For Best Results:</strong><br>
                • Speak clearly when recording ingredients<br>
                • You can edit transcribed text before generating<br>
                • Try different combinations of preferences<br>
                • Models load on first use (may take a moment)<br>
                • Download recipes as PDF for easy access
                </div>
                """)

            with gr.Column(scale=1):
                powered_by_text = f"""
                ### ⚡ Powered By
                <div class="success-box">
                <strong>AI Technology Stack:</strong><br>
                • **Speech Recognition:** OpenAI Whisper (Small)<br>
                • **Recipe Generation:** {"Groq API (Llama 3.3 70B)" if config.USE_GROQ else "FLAN-T5 (Local Model)"}<br>
                • **Speed:** {"~1-2 seconds ⚡" if config.USE_GROQ else "~10-15 seconds"}<br>
                • **Interface:** Gradio + Custom Dark Theme
                </div>
                """
                gr.Markdown(powered_by_text)
    
    return app


def main():
    """Main application entry point"""
    print("\n" + "="*50)
    print("AI Recipe Finder")
    print("="*50)
    print(f"Whisper Model: {config.WHISPER_MODEL}")
    if config.USE_GROQ:
        print(f"Recipe Generator: Groq API (Llama 3.3 70B)")
        print(f"Speed: ~1-2 seconds")
    else:
        print(f"Recipe Generator: {config.LLM_MODEL}")
        print(f"Speed: ~10-15 seconds (local)")
    print(f"Device: {config.DEVICE}")
    print("="*50 + "\n")
    
    # Create and launch interface
    app = create_interface()
    
    app.launch(
        share=config.SHARE_LINK,
        server_name=config.SERVER_HOST,  # Use config for flexibility (0.0.0.0 for HF, 127.0.0.1 for local)
        server_port=config.SERVER_PORT,
        show_error=True,
        max_file_size="50MB",  # 50MB max file size
        allowed_paths=["./"]  # Allow current directory
    )


if __name__ == "__main__":
    main()
