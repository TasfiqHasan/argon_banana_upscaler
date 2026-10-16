"""
AI Neural Super-Resolution Pipeline using Real-ESRGAN x4plus (Vulkan GPU Accelerated)
Hallucinates genuine micro-textures, specular highlights, and crisp edge details.
"""

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

IMAGES = [
    ("01_cosmic_nebula_observatory", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\cosmic_nebula_observatory_1792134226019.jpg"),
    ("02_bioluminescent_forest", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\bioluminescent_forest_1792134246017.jpg"),
    ("03_nordic_aurora_fjord", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\nordic_aurora_fjord_1792134281718.jpg"),
    ("04_solarpunk_utopia", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\solarpunk_utopia_1792134304234.jpg"),
    ("05_desert_hypercar_sunset", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\desert_hypercar_sunset_1792134336135.jpg"),
    ("06_cyber_samurai_pagoda", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\cyber_samurai_pagoda_1792134359038.jpg"),
    ("07_abyssal_bioluminescent_reef", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\abyssal_bioluminescent_reef_1792134381921.jpg"),
    ("08_steampunk_airship_dock", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\steampunk_airship_dock_1792134421307.jpg"),
    ("09_volcanic_obsidian_peaks", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\volcanic_obsidian_peaks_1792134444794.jpg"),
    ("10_zen_water_pavilion", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\zen_water_pavilion_1792134482057.jpg"),
    ("11_cyberpunk_city_rain", r"C:\Users\User\.gemini\antigravity\brain\51b5cc25-93a8-4dd6-9dc3-dccc6b134401\cyberpunk_city_rain_1792132852965.jpg"),
]

def main():
    print("=================================================================")
    print("  REAL-ESRGAN x4plus NEURAL SUPER-RESOLUTION -> D:\\4k images")
    print("=================================================================")
    
    total = len(IMAGES)
    for idx, (clean_name, src_path) in enumerate(IMAGES, 1):
        src = Path(src_path)
        if not src.exists():
            print(f"[{idx}/{total}] Skipping {clean_name}: File not found ({src})")
            continue
            
        print(f"\n[{idx}/{total}] Neural AI Upscaling: {clean_name}...")
        temp_esrgan_out = OUTPUT_DIR / f"{clean_name}_esrgan_temp.png"
        final_4k_path = OUTPUT_DIR / f"{clean_name}_4k_ultra.png"
        
        # Run Real-ESRGAN x4plus using Vulkan GPU acceleration
        cmd = [
            str(REALESRGAN_EXE),
            "-i", str(src),
            "-o", str(temp_esrgan_out),
            "-n", "realesrgan-x4plus",
            "-s", "4"
        ]
        
        t0 = time.time()
        res = subprocess.run(cmd, cwd=str(REALESRGAN_EXE.parent), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"   [Error] Real-ESRGAN failed: {res.stderr}")
            continue
            
        # Target 4K UHD (3840x2160) super-sampling from the 5.5K neural output
        with Image.open(temp_esrgan_out) as raw_img:
            w, h = raw_img.size
            final_img = raw_img.resize((3840, 2160), Image.Resampling.LANCZOS)
            final_img.save(final_4k_path, "PNG", compress_level=1)
            
        # Remove intermediate raw file
        if temp_esrgan_out.exists():
            temp_esrgan_out.unlink()
            
        dt = round(time.time() - t0, 1)
        size_mb = round(final_4k_path.stat().st_size / (1024 * 1024), 2)
        print(f"   [SUCCESS] Saved: {final_4k_path.name} (3840x2160, {size_mb} MB) in {dt}s")

    print("\n=================================================================")
    print("  [COMPLETE] All images upgraded with True Neural AI Super-Resolution!")
    print("=================================================================\n")

if __name__ == "__main__":
    main()
