"""
Argon Image Generator Module
Generates high-fidelity base images (2K class) using Google AI Studio's API.
"""

import io
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types

import config


class ArgonGenerator:
    def __init__(self, api_key: str | None = None, model: str = config.DEFAULT_GENERATION_MODEL):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model
        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        output_path: Path | str | None = None,
        dry_run: bool = False
    ) -> Path:
        """
        Generates a 2K base image from the specified text prompt.
        
        Args:
            prompt: Text prompt describing the image to generate.
            aspect_ratio: Aspect ratio ('16:9', '1:1', '4:3', '9:16').
            output_path: Optional explicit file path to save the generated image.
            dry_run: When True, simulates image generation without calling external API.
        
        Returns:
            Path to the saved 2K base image.
        """
        timestamp = int(time.time())
        if output_path is None:
            output_path = config.OUTPUTS_DIR / f"argon_2k_{timestamp}.png"
        else:
            output_path = Path(output_path)

        if dry_run:
            print(f"[Argon] (Dry-Run) Simulating 2K generation for prompt: '{prompt}'...")
            dims = (2560, 1440) if aspect_ratio == "16:9" else (2048, 2048)
            img = Image.new("RGB", dims, color=(30, 41, 59))
            draw = ImageDraw.Draw(img)
            draw.text((dims[0] // 4, dims[1] // 2), f"Argon 2K Base Image\nPrompt: {prompt}\nAspect: {aspect_ratio}", fill=(248, 250, 252))
            img.save(output_path, "PNG")
            print(f"[Argon] (Dry-Run) Base 2K image saved: {output_path} ({dims[0]}x{dims[1]})")
            return output_path

        if not self.client:
            raise ValueError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file. "
                "You can get a free key at https://aistudio.google.com/app/apikey"
            )

        print(f"[Argon] Generating base 2K image with model '{self.model}' (Aspect: {aspect_ratio})...")
        print(f"[Argon] Prompt: \"{prompt}\"")

        config_options = types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            output_mime_type="image/png",
            person_generation="ALLOW_ADULT",
            safety_filter_level="BLOCK_MEDIUM_AND_ABOVE",
        )

        try:
            response = self.client.models.generate_images(
                model=self.model,
                prompt=prompt,
                config=config_options
            )
            
            if not response.generated_images:
                raise RuntimeError("No image was returned by the generation model.")

            raw_bytes = response.generated_images[0].image.image_bytes
            pil_image = Image.open(io.BytesIO(raw_bytes))
            pil_image.save(output_path, "PNG", quality=95)
            
            print(f"[Argon] Generated successfully: {output_path} ({pil_image.width}x{pil_image.height})")
            return output_path

        except Exception as e:
            err_msg = str(e)
            if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg:
                raise ValueError(
                    "\n[!] API Key Error: Your GEMINI_API_KEY in .env is not valid.\n"
                    "Make sure you replaced 'your_key_here' with your real API key from Google AI Studio.\n"
                    "Get a free key here: https://aistudio.google.com/app/apikey"
                )

            # Fallback to multimodal generate_content if standard generate_images is unavailable for this key/tier
            print(f"[Argon] Note: Standard generate_images endpoint responded: {e}")
            print("[Argon] Attempting multimodal image synthesis fallback...")
            
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[f"Generate a high-detail cinematic 2K image: {prompt}"],
                )
                
                # Check for inline image parts
                saved = False
                for part in response.parts:
                    if getattr(part, "inline_data", None) is not None:
                        image_obj = part.as_image()
                        image_obj.save(str(output_path))
                        saved = True
                        break
                
                if not saved:
                    raise RuntimeError(f"Could not generate image via model. Error details: {e}")
                
                return output_path
            except Exception as fallback_err:
                if "API_KEY_INVALID" in str(fallback_err) or "API key not valid" in str(fallback_err):
                    raise ValueError(
                        "\n[!] API Key Error: Your GEMINI_API_KEY in .env is not valid.\n"
                        "Make sure you replaced 'your_key_here' with your real API key from Google AI Studio.\n"
                        "Get a free key here: https://aistudio.google.com/app/apikey"
                    )
                raise fallback_err

            return output_path
