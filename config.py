import os
from pathlib import Path
from dotenv import load_dotenv

# Base project paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
INPUTS_DIR = BASE_DIR / "inputs"

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH)

# Configurable output directory (default: project's outputs folder)
custom_output = os.getenv("OUTPUT_DIR")
if custom_output:
    OUTPUTS_DIR = Path(custom_output).expanduser().resolve()
else:
    OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure runtime directories exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
INPUTS_DIR.mkdir(parents=True, exist_ok=True)


raw_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
PLACEHOLDER_KEYS = {"your_key_here", "your_free_google_ai_studio_api_key_here", "your_free_ai_studio_api_key_here", "AIzaSy..."}

if not raw_key or raw_key in PLACEHOLDER_KEYS or raw_key.startswith("your_"):
    GEMINI_API_KEY = None
else:
    GEMINI_API_KEY = raw_key


# Supported models for the pipeline
DEFAULT_GENERATION_MODEL = os.getenv("GENERATION_MODEL", "imagen-3.0-generate-002")
DEFAULT_UPSCALER_MODEL = os.getenv("UPSCALER_MODEL", "imagen-3.0-generate-002")

# Resolution presets
RESOLUTION_PRESETS = {
    "16:9": {"width": 3840, "height": 2160, "aspect_ratio": "16:9", "name": "4K UHD (3840x2160)"},
    "1:1": {"width": 4096, "height": 4096, "aspect_ratio": "1:1", "name": "4K Square (4096x4096)"},
    "4:3": {"width": 3840, "height": 2880, "aspect_ratio": "4:3", "name": "4K Standard (3840x2880)"},
    "9:16": {"width": 2160, "height": 3840, "aspect_ratio": "9:16", "name": "4K Vertical (2160x3840)"},
}
