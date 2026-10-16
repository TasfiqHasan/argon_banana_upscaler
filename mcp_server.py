"""
Nano Banana 2.1 & Real-ESRGAN 4K MCP Server
Provides MCP tools for Antigravity to generate and upscale images directly to D:\4k images.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

REALESRGAN_EXE = BASE_DIR / "realesrgan" / "realesrgan-ncnn-vulkan.exe"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", r"D:\4k images"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from mcp.server.mcpserver import MCPServer

server = MCPServer("nano-banana")


@server.tool()
def upscale_to_4k(image_path: str) -> str:
    """
    Upscale an image to true 4K Ultra HD (3840x2160) using Real-ESRGAN x4plus neural super-resolution on GPU.
    Args:
        image_path: Absolute or relative path to the image to upscale.
    Returns:
        Path to the upscaled 4K image in D:\\4k images.
    """
    src = Path(image_path).expanduser().resolve()
    if not src.exists():
        return f"Error: Source image not found at {src}"

    timestamp = int(time.time())
    name = f"{src.stem}_4k_{timestamp}.png"
    temp_out = OUTPUT_DIR / f"temp_{timestamp}.png"
    final_out = OUTPUT_DIR / name

    if not REALESRGAN_EXE.exists():
        return f"Error: Real-ESRGAN engine not found at {REALESRGAN_EXE}"

    cmd = [
        str(REALESRGAN_EXE),
        "-i", str(src),
        "-o", str(temp_out),
        "-n", "realesrgan-x4plus",
        "-s", "4"
    ]

    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(REALESRGAN_EXE.parent), capture_output=True, text=True)
    if res.returncode != 0:
        return f"Error running Real-ESRGAN: {res.stderr}"

    with Image.open(temp_out) as raw:
        final_img = raw.resize((3840, 2160), Image.Resampling.LANCZOS)
        final_img.save(final_out, "PNG", compress_level=1)

    if temp_out.exists():
        temp_out.unlink()

    duration = round(time.time() - t0, 1)
    size_mb = round(final_out.stat().st_size / (1024 * 1024), 2)
    return f"Successfully upscaled to 4K Ultra HD (3840x2160, {size_mb} MB) in {duration}s.\nFile saved to: {final_out}"


@server.tool()
def generate_and_upscale(prompt: str, aspect_ratio: str = "16:9") -> str:
    """
    Generate an image using the Nano Banana / Google AI Studio pipeline and upscale to 4K Ultra HD.
    Args:
        prompt: Description of the scene or subject to generate.
        aspect_ratio: Aspect ratio ('16:9', '1:1', '4:3', '9:16').
    Returns:
        Status and destination path of the generated 4K image.
    """
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.startswith("your_"):
            return "Error: GEMINI_API_KEY is not configured in .env file."

        client = genai.Client(api_key=api_key)
        timestamp = int(time.time())
        base_out = OUTPUT_DIR / f"base_{timestamp}.png"

        # Call Gemini image endpoint
        response = client.models.generate_content(
            model="gemini-3.1-flash-image",
            contents=[prompt],
        )

        saved = False
        for part in response.parts:
            if getattr(part, "inline_data", None) is not None:
                img = part.as_image()
                img.save(str(base_out))
                saved = True
                break

        if not saved:
            return "Error: Model did not return an image part."

        # Pass to 4K GPU upscaler
        upscale_result = upscale_to_4k(str(base_out))
        return f"Image generated via Nano Banana.\n{upscale_result}"

    except Exception as e:
        return f"Error during generation: {e}"


if __name__ == "__main__":
    server.run("stdio")
