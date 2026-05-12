from flask import Flask, request, jsonify, render_template
import os
import io
import base64
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize the InferenceClient
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    client = InferenceClient(provider="auto", api_key=hf_token)
else:
    client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not client:
        return jsonify({'error': 'Hugging Face Token is not configured. Please add HF_TOKEN to your .env file.'}), 500

    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({'error': 'No prompt provided.'}), 400

    prompt = data['prompt']
    model = data.get('model', 'stabilityai/stable-diffusion-xl-base-1.0')
    style = data.get('style', 'none')
    aspect_ratio = data.get('aspect_ratio', '1:1')
    negative_prompt = data.get('negative_prompt', '')
    guidance_scale = data.get('guidance_scale', 7.5)

    # Apply style modifiers
    style_modifiers = {
        'photorealistic': ', highly detailed, photorealistic, 8k resolution, cinematic lighting, ultra-realistic',
        'cinematic': ', cinematic shot, dramatic lighting, IMAX, 35mm lens, highly detailed',
        'anime': ', anime style, studio ghibli, makoto shinkai, highly detailed, vibrant colors',
        'digital_art': ', trending on artstation, digital art, highly detailed, vivid',
        'cyberpunk': ', cyberpunk, neon lights, dystopian, futuristic, highly detailed'
    }

    if style in style_modifiers:
        prompt += style_modifiers[style]

    # Handle aspect ratio
    width, height = 1024, 1024 # Default SDXL
    if aspect_ratio == '16:9':
        width, height = 1024, 576
    elif aspect_ratio == '9:16':
        width, height = 576, 1024

    try:
        # Build kwargs for the API call
        kwargs = {}
        if negative_prompt:
            kwargs['negative_prompt'] = negative_prompt
        kwargs['width'] = width
        kwargs['height'] = height
        try:
            kwargs['guidance_scale'] = float(guidance_scale)
        except (ValueError, TypeError):
            kwargs['guidance_scale'] = 7.5

        # Generate image
        # output is a PIL.Image object
        image = client.text_to_image(
            prompt,
            model=model,
            **kwargs
        )

        # Convert PIL Image to Base64 string
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({
            'success': True,
            'image_data': f"data:image/png;base64,{img_str}"
        })

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
