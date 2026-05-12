"""
This module provides a Flask web application for generating images
using the Hugging Face Inference API.
"""
import os
import io
import base64
from typing import Optional

from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize InferenceClient (will attempt to load dynamically if missing)
_client = None
INITIAL_HF_TOKEN = os.environ.get("HF_TOKEN")
if INITIAL_HF_TOKEN:
    _client = InferenceClient(provider="auto", api_key=INITIAL_HF_TOKEN)


def get_hf_client() -> Optional[InferenceClient]:
    """
    Retrieve or initialize the Hugging Face InferenceClient.
    Returns the client or None if no token is found.
    """
    global _client  # pylint: disable=global-statement
    if _client:
        return _client

    load_dotenv(override=True)
    hf_token = os.environ.get("HF_TOKEN")

    # Bulletproof fallback for local testing: read .env file directly
    if not hf_token and os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Strip potential BOM and whitespace
                clean_line = line.strip('\ufeff').strip()
                if clean_line.startswith('HF_TOKEN='):
                    hf_token = clean_line.split('=', 1)[1].strip()
                    # Remove potential quotes around the token
                    hf_token = hf_token.strip('\'"')
                    break

    if hf_token:
        _client = InferenceClient(provider="auto", api_key=hf_token)

    return _client


def apply_style(prompt: str, style: str) -> str:
    """Apply specific artistic styles to the prompt."""
    style_modifiers = {
        'photorealistic': (
            ', highly detailed, photorealistic, '
            '8k resolution, cinematic lighting, ultra-realistic'
        ),
        'cinematic': (
            ', cinematic shot, dramatic lighting, '
            'IMAX, 35mm lens, highly detailed'
        ),
        'anime': (
            ', anime style, studio ghibli, '
            'makoto shinkai, highly detailed, vibrant colors'
        ),
        'digital_art': (
            ', trending on artstation, digital art, '
            'highly detailed, vivid'
        ),
        'cyberpunk': (
            ', cyberpunk, neon lights, dystopian, '
            'futuristic, highly detailed'
        )
    }
    if style in style_modifiers:
        prompt += style_modifiers[style]
    return prompt


def get_dimensions(aspect_ratio: str) -> tuple[int, int]:
    """Return width and height based on aspect ratio."""
    width, height = 1024, 1024  # Default SDXL
    if aspect_ratio == '16:9':
        width, height = 1024, 576
    elif aspect_ratio == '9:16':
        width, height = 576, 1024
    return width, height


@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Handle POST requests to generate images from text prompts.
    """
    client = get_hf_client()
    if not client:
        error_msg = (
            "Hugging Face Token is missing! If you are on VERCEL, "
            "add HF_TOKEN to your Vercel Dashboard -> Settings -> "
            "Environment Variables. If local, check your .env file."
        )
        return jsonify({'error': error_msg}), 500

    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({'error': 'No prompt provided.'}), 400

    prompt = apply_style(data['prompt'], data.get('style', 'none'))
    width, height = get_dimensions(data.get('aspect_ratio', '1:1'))

    model = data.get('model', 'stabilityai/stable-diffusion-xl-base-1.0')
    negative_prompt = data.get('negative_prompt', '')

    try:
        guidance_scale = float(data.get('guidance_scale', 7.5))
    except (ValueError, TypeError):
        guidance_scale = 7.5

    try:
        kwargs = {
            'width': width,
            'height': height,
            'guidance_scale': guidance_scale
        }
        if negative_prompt:
            kwargs['negative_prompt'] = negative_prompt

        # Generate image (output is a PIL.Image object)
        image = client.text_to_image(prompt, model=model, **kwargs)

        # Convert PIL Image to Base64 string
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({
            'success': True,
            'image_data': f"data:image/png;base64,{img_str}"
        })

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
