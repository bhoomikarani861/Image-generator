import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

client = InferenceClient(
    provider="auto",
    api_key=os.environ["HF_TOKEN"],
)

# output is a PIL.Image object
image = client.text_to_image(
    "Bollywood actor rashmika mandana with Vijay deverakonda",
    
    model="stabilityai/stable-diffusion-xl-base-1.0",
)
image.save("Rashmika_Vijay.png")
print("Image saved succefully")