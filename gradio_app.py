# Import required libraries
import gradio as gr
import numpy as np
from PIL import Image
import torch 
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from rembg import remove  # for background removal

# Define the base Stable Diffusion XL checkpoint and fix random seed
base_ckpt_id = "stabilityai/stable-diffusion-xl-base-1.0"
generator = torch.manual_seed(0)

def center_crop(image, size=(912, 912)):
    """
    Crop an image to the center with the given size.
    """
    width, height = image.size
    new_width, new_height = size
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = (width + new_width) // 2
    bottom = (height + new_height) // 2
    return image.crop((left, top, right, bottom))

def load_model(controlnet_path):
    """
    Load ControlNet and attach it to the Stable Diffusion XL pipeline.
    """
    controlnet = ControlNetModel.from_pretrained(
        controlnet_path, torch_dtype=torch.float16
    ).to("cuda")

    pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
        base_ckpt_id, controlnet=controlnet, torch_dtype=torch.float16
    ).to("cuda")

    return pipeline

# Load the model once on startup
pipeline_ = load_model('controlnet_model')

def inference(input_img: np.array, mask: bool, prompt: str, num_images: int, model: str = "", history=[str]):
    """
    Run inference on the input image with ControlNet, generating multiple images.

    Args:
        input_img: The input image as a NumPy array
        mask: Whether to apply background removal to outputs
        prompt: Text prompt for generation
        num_images: Number of images to generate
        model, history: (Unused) Placeholder arguments for future extension

    Returns:
        A list of images, starting with the control image, followed by generated outputs
    """
    input_img = Image.fromarray(input_img)

    # Crop to square if needed
    if input_img.size[0] != input_img.size[1]:
        input_img = center_crop(input_img, size=(input_img.size[1], input_img.size[1]))

    # Resize to the expected ControlNet input size
    control_image = input_img.resize((512, 512))

    # Generate multiple images using the pipeline
    generated_images = pipeline_(
        prompt,
        num_inference_steps=20,
        generator=generator,
        image=control_image,
        num_images_per_prompt=num_images  # user-selected number of images
    ).images

    # Optionally remove background from each image
    if mask:
        return [control_image] + [remove(x) for x in generated_images]
    else:
        return [control_image] + generated_images

# Create Gradio interface
demo = gr.Interface(
    fn=inference,
    inputs=[
        gr.Image(value="imgs/skull.jpg"),                         # Input image with default value
        gr.Checkbox(value=True, label='Apply Mask'),              # Option to remove background
        gr.Textbox(label="Enter prompt", value="A glossy skull in orange soft crayon"),  # Text prompt
        gr.Slider(minimum=1, maximum=8, step=1, value=5, label="Number of Painterly Depictions")  # Option to select the number of generated painterly depictions
    ],
    outputs=[gr.Gallery(format="png")],                          # Output shown in a gallery format
    theme=gr.themes.Default(),
    title='Artist-Inator: Text-based, Gloss-aware Non-photorealistic Stylization'
)

# Launch the web app with public sharing and open to all interfaces
demo.launch(share=True, server_name="0.0.0.0")
