"""
Main CLI entrypoint for Argon -> Yellow Banana 4K Automation.
Supports CLI arguments and interactive terminal mode.
"""

import argparse
import sys
from pathlib import Path

# Ensure safe console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import config
from pipeline import ImagePipeline
from yellow_banana_upscaler import YellowBananaUpscaler


def print_banner():
    print("""
===========================================================
  ARGON -> YELLOW BANANA 4K AUTOMATION PIPELINE
===========================================================
  1. Base 2K Image Generation via Argon (Google AI Studio)
  2. 4K Ultra HD AI Upscaling via Yellow Banana
  3. Automatic Local Download & Metadata Logging
===========================================================
""")


def check_api_key(allow_dry_run: bool = False) -> bool:
    if not config.GEMINI_API_KEY:
        print("\n[!] NOTICE: GEMINI_API_KEY is not set.")
        print("To run with live AI Studio generation, get a FREE key:")

        print("1. Visit https://aistudio.google.com/app/apikey")
        print("2. Copy your free key and paste it into `.env` file:")
        print("   GEMINI_API_KEY=AIzaSy...")
        print("-----------------------------------------------------------")
        if allow_dry_run:
            print("💡 Running in DRY-RUN mode to test pipeline end-to-end without an API key.\n")
            return False
        else:
            choice = input("Would you like to run in simulated Dry-Run mode now? (Y/n): ").strip().lower()
            return choice in ("", "y", "yes")
    return True


def interactive_mode():
    print_banner()
    has_key = bool(config.GEMINI_API_KEY)
    dry_run = False
    
    if not has_key:
        proceed = check_api_key(allow_dry_run=False)
        if not proceed:
            print("Exiting. Add your free key to .env and run again.")
            sys.exit(0)
        dry_run = True

    print("\nSelect an option:")
    print(" [1] Generate & Upscale to 4K from Prompt")
    print(" [2] Upscale an Existing Local Image to 4K directly")
    print(" [3] Run Pipeline Dry-Run Test")
    print(" [4] Exit")

    choice = input("\nEnter choice [1-4] (default: 1): ").strip() or "1"

    if choice == "1":
        prompt = input("\nEnter prompt for Argon (e.g. 'A futuristic cyberpunk neon city at dusk, 8k'): ").strip()
        if not prompt:
            prompt = "A futuristic cyberpunk neon city at dusk, cinematic lighting, ultra-detailed"
            print(f"Using default prompt: \"{prompt}\"")

        print("\nChoose Aspect Ratio:")
        print(" [1] 16:9 - 4K Ultra HD (3840x2160)")
        print(" [2] 1:1  - 4K Square (4096x4096)")
        print(" [3] 4:3  - 4K Standard (3840x2880)")
        print(" [4] 9:16 - 4K Vertical / Mobile (2160x3840)")
        aspect_choice = input("Choice [1-4] (default: 1): ").strip() or "1"
        aspect_map = {"1": "16:9", "2": "1:1", "3": "4:3", "4": "9:16"}
        aspect_ratio = aspect_map.get(aspect_choice, "16:9")

        custom_out = input(f"\nSave images to folder (Press Enter for '{config.OUTPUTS_DIR}'): ").strip().strip('"').strip("'")
        out_dir = custom_out if custom_out else None

        pipe = ImagePipeline()
        pipe.run(prompt=prompt, aspect_ratio=aspect_ratio, output_dir=out_dir, dry_run=dry_run)

    elif choice == "2":
        img_path_str = input("\nEnter path to local 2K image: ").strip().strip('"').strip("'")
        img_path = Path(img_path_str)
        if not img_path.exists():
            print(f"Error: File does not exist at {img_path}")
            return
        
        custom_out = input(f"\nSave upscaled image to folder (Press Enter for '{config.OUTPUTS_DIR}'): ").strip().strip('"').strip("'")
        out_dir = custom_out if custom_out else None

        upscaler = YellowBananaUpscaler()
        upscaler.upscale(input_image_path=img_path, output_path=out_dir, dry_run=dry_run)

    elif choice == "3":
        pipe = ImagePipeline()
        pipe.run(
            prompt="Futuristic quantum laboratory with holographic displays and glowing neon aesthetic",
            aspect_ratio="16:9",
            dry_run=True
        )

    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Argon -> Yellow Banana 4K Automation Pipeline")
    parser.add_argument("--prompt", type=str, help="Text prompt to generate 2K base image")
    parser.add_argument("--aspect", type=str, default="16:9", choices=["16:9", "1:1", "4:3", "9:16"], help="Aspect ratio")
    parser.add_argument("-o", "--output", type=str, help="Custom folder path to download and save images")
    parser.add_argument("--upscale-only", type=str, help="Path to local image to directly upscale to 4K")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pipeline without calling external APIs")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive menu")

    args = parser.parse_args()

    # If no flags provided or --interactive specified, launch interactive mode
    if len(sys.argv) == 1 or args.interactive:
        interactive_mode()
        return

    is_dry_run = args.dry_run or not bool(config.GEMINI_API_KEY)
    if not config.GEMINI_API_KEY and not args.dry_run:
        check_api_key(allow_dry_run=True)
        is_dry_run = True

    if args.upscale_only:
        upscaler = YellowBananaUpscaler()
        upscaler.upscale(input_image_path=args.upscale_only, target_preset=args.aspect, output_path=args.output, dry_run=is_dry_run)
    elif args.prompt:
        pipe = ImagePipeline()
        pipe.run(prompt=args.prompt, aspect_ratio=args.aspect, output_dir=args.output, dry_run=is_dry_run)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

