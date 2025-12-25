from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import torch

print("Loading local Captioning model (Salesforce/blip-image-captioning-large)...")

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ GPU not found. Using CPU.")

# Load Model & Processor
try:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
except Exception as e:
    print(f"Error loading model: {e}")
    processor = None
    model = None

def analyze_image(image_bytes):
    """
    Analyzes an image to list ingredients using conditional captioning.
    """
    if not model or not processor:
        return "Error: Model not loaded correctly."

    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # We use a prompt that encourages listing items
        text_prompt = "fresh food ingredients on a table including "
        
        # Prepare inputs
        inputs = processor(image, text_prompt, return_tensors="pt").to(device)
        
        # Generate answer with Nucleus Sampling (Top-p) 
        # This helps getting specific items like 'pineapple' instead of generic 'fruit'
        out = model.generate(
            **inputs, 
            max_new_tokens=100,
            min_new_tokens=20,
            do_sample=True,        # Enable sampling for variety
            top_p=0.9,             # Nucleus sampling
            temperature=0.7,       # Slightly creative but focused
            repetition_penalty=1.5 # High penalty to force listing distinct items
        )
        
        description = processor.decode(out[0], skip_special_tokens=True)
        
        # Clean up the output (remove the prompt if it's repeated)
        return description
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"
