import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REALESRGAN_EXE = Path(r"C:\Users\User\.gemini\antigravity\scratch\argon-banana-upscaler\realesrgan\realesrgan-ncnn-vulkan.exe")
OUTPUT_DIR = Path(r"D:\4k images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def upscale_image(src_path: str | Path, clean_name: str | None = None) -> Path:
    src = Path(src_path).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    name = clean_name or src.stem
    temp_out = OUTPUT_DIR / f"{name}_temp.png"
    final_4k_path = OUTPUT_DIR / f"{name}_4k.png"

    print(f">> Neural AI Upscaling: {name}...")
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
        raise RuntimeError(f"Real-ESRGAN error: {res.stderr}")

    with Image.open(temp_out) as raw:
        final_img = raw.resize((3840, 2160), Image.Resampling.LANCZOS)
        final_img.save(final_4k_path, "PNG", compress_level=1)

    if temp_out.exists():
        temp_out.unlink()

    dt = round(time.time() - t0, 1)
    size_mb = round(final_4k_path.stat().st_size / (1024 * 1024), 2)
    print(f"   [DONE] {final_4k_path.name} (3840x2160, {size_mb} MB) in {dt}s")
    return final_4k_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            upscale_image(p)
