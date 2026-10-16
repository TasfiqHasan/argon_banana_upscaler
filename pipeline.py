import json
import sys
import time
from pathlib import Path
from PIL import Image

import config
from argon_generator import ArgonGenerator
from yellow_banana_upscaler import YellowBananaUpscaler

# Ensure safe console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")



class ImagePipeline:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.argon = ArgonGenerator(api_key=self.api_key)
        self.yellow_banana = YellowBananaUpscaler(api_key=self.api_key)

    def run(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        upscale_factor: str = "x2",
        output_dir: Path | str | None = None,
        dry_run: bool = False
    ) -> dict:
        """
        Executes the full pipeline:
        Prompt -> 2K Argon Image -> 4K Yellow Banana Upscaled Image -> Local Download
        """
        start_time = time.time()
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        
        target_dir = Path(output_dir).expanduser().resolve() if output_dir else config.OUTPUTS_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        print("\n==================================================")
        print(">> Starting Argon -> Yellow Banana 4K Pipeline")
        print("==================================================")
        print(f" - Prompt       : \"{prompt}\"")
        print(f" - Aspect Ratio : {aspect_ratio}")
        print(f" - Target Preset: {config.RESOLUTION_PRESETS.get(aspect_ratio, {}).get('name', '4K')}")
        print(f" - Output Folder: {target_dir}")
        print(f" - Dry Run Mode : {dry_run}")
        print("--------------------------------------------------")

        # Step 1: Generate 2K base image
        print("\n[Step 1/3] Generating 2K base image via Argon...")
        base_path = target_dir / f"base_2k_{timestamp_str}.png"
        generated_2k = self.argon.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            output_path=base_path,
            dry_run=dry_run
        )
        
        with Image.open(generated_2k) as img_2k:
            res_2k = f"{img_2k.width}x{img_2k.height}"

        # Step 2: Upscale to 4K via Yellow Banana
        print("\n[Step 2/3] Upscaling image via Yellow Banana...")
        target_4k_path = target_dir / f"downloaded_4k_{timestamp_str}.png"

        final_4k = self.yellow_banana.upscale(
            input_image_path=generated_2k,
            target_preset=aspect_ratio,
            upscale_factor=upscale_factor,
            output_path=target_4k_path,
            dry_run=dry_run
        )

        with Image.open(final_4k) as img_4k:
            res_4k = f"{img_4k.width}x{img_4k.height}"
            file_size_mb = round(final_4k.stat().st_size / (1024 * 1024), 2)

        duration = round(time.time() - start_time, 2)

        # Step 3: Metadata logging & download confirmation
        print("\n[Step 3/3] Finalizing download & metadata logging...")
        metadata = {
            "timestamp": timestamp_str,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration,
            "dry_run": dry_run,
            "stage1_base_image": {
                "file": str(generated_2k),
                "resolution": res_2k
            },
            "stage2_upscaled_image": {
                "file": str(final_4k),
                "resolution": res_4k,
                "file_size_mb": file_size_mb
            }
        }

        meta_path = target_dir / f"meta_{timestamp_str}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print("\n==================================================")
        print("[SUCCESS] Pipeline Completed Successfully!")
        print(f" - 2K Base Image  : {generated_2k} ({res_2k})")
        print(f" - 4K Ultra HD    : {final_4k} ({res_4k}, {file_size_mb} MB)")
        print(f" - Metadata Log   : {meta_path}")
        print(f" - Total Time     : {duration}s")
        print("==================================================\n")

        return metadata
