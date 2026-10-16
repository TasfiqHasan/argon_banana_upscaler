"""
Batch Upscaler for D:\4k images
Takes a list of generated images, upscales them to 4K Ultra HD (3840x2160)
with edge sharpening and contrast enhancement, and writes them directly to D:\4k images.
"""

import sys
import time
from pathlib import Path
from PIL import Image, ImageEnhance

# Configure console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DESTINATION_DIR = Path(r"D:\4k images")
DESTINATION_DIR.mkdir(parents=True, exist_ok=True)

TARGET_WIDTH = 3840
TARGET_HEIGHT = 2160


def upscale_image_to_4k(input_path: Path | str, output_name: str | None = None) -> Path:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    if output_name is None:
        output_name = src.stem + "_4k.png"
    elif not output_name.endswith(".png"):
        output_name += ".png"

    dest = DESTINATION_DIR / output_name

    print(f">> Upscaling {src.name} to 4K ({TARGET_WIDTH}x{TARGET_HEIGHT})...")
    with Image.open(src) as img:
        # High quality Lanczos resampling
        upscaled = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        
        # Micro-contrast and clarity enhancement
        sharpener = ImageEnhance.Sharpness(upscaled)
        crisp = sharpener.enhance(1.15)
        
        # Save lossless PNG
        crisp.save(dest, "PNG", compress_level=1)

    file_size_mb = round(dest.stat().st_size / (1024 * 1024), 2)
    print(f"   [DONE] Saved to: {dest} ({TARGET_WIDTH}x{TARGET_HEIGHT}, {file_size_mb} MB)")
    return dest


def batch_upscale(image_paths: list[str | Path]) -> list[Path]:
    results = []
    print(f"\n=======================================================")
    print(f"  BATCH 4K UPSCALING -> {DESTINATION_DIR}")
    print(f"=======================================================")
    total = len(image_paths)
    for idx, path in enumerate(image_paths, 1):
        print(f"\n[{idx}/{total}] Processing: {Path(path).name}")
        out = upscale_image_to_4k(path)
        results.append(out)
    
    print(f"\n=======================================================")
    print(f"  [SUCCESS] All {len(results)} images upscaled to 4K Ultra HD!")
    print(f"=======================================================\n")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", help="Image paths to upscale")
    args = parser.parse_args()
    batch_upscale(args.images)
