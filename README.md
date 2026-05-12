# ImaginAI Pro Studio

A highly customizable, professional-grade Text-to-Image web application built with Python (Flask) and powered by the Hugging Face Inference API (Stable Diffusion XL).

## ✨ Features

- **Pro Studio Interface**: A sleek, dark-mode glassmorphic UI designed for creative workflows.
- **Art Style Injector**: Instantly force your prompts into specific styles like *Photorealistic*, *Cinematic*, *Anime*, *Cyberpunk*, and *Digital Art*.
- **Aspect Ratio Control**: Generate images in standard formats including Square (1:1), Landscape (16:9), and Portrait (9:16).
- **Advanced AI Controls**: Adjust the **Guidance Scale** to control how strictly the AI adheres to your prompt.
- **Negative Prompts**: Explicitly tell the AI what elements to exclude from your generation.
- **"Magic Dice" Prompt Generator**: Stuck for ideas? Click the dice icon to auto-generate a highly detailed, complex prompt engineered for spectacular results.
- **Local History Gallery**: Your generated images are automatically saved locally in your browser's history, allowing you to reload past creations and prompts with a single click.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- A [Hugging Face](https://huggingface.co/) account and an Access Token.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bhoomikarani861/Image-generator.git
   cd Image-generator
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On Mac/Linux:
   source env/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Create a `.env` file in the root directory and add your Hugging Face API token:
   ```env
   HF_TOKEN=your_hugging_face_token_here
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://127.0.0.1:5000`.

## 🛠️ Built With

- **Backend**: Python, Flask, HuggingFace Hub API
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript
- **AI Engine**: Stable Diffusion XL Base 1.0
