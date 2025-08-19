#!/usr/bin/env python3
"""
Reverse Prompt Tool - Generate descriptive prompts from images using vision models.
"""

import argparse
import json
import os
import sys
import time
import threading
import atexit
from pathlib import Path
from typing import Optional

try:
    import google.generativeai as genai
    from PIL import Image
    from dotenv import load_dotenv
    import webbrowser
    from urllib.parse import quote
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install google-generativeai pillow python-dotenv")
    sys.exit(1)


# Spinner implementation
_SPINNERS = {
    "dots": ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'],
    "line": ['-', '\\', '|', '/'],
    "triangle": ['◢','◣','◤','◥'],
    "arrow": ['←','↖','↑','↗','→','↘','↓','↙']
}

_GREEN = "\033[92m"
_RED   = "\033[91m"
_RESET = "\033[0m"

class Spinner:
    def __init__(self, text="Loading...", spinner="dots", interval=0.08, stream=sys.stdout):
        self.text = text
        self.spinner = spinner
        self.interval = interval
        self.stream = stream

        self._frames = self._get_frames(spinner)
        self._stop = threading.Event()
        self._thread = None
        self._cursor_hidden = False
        self._render_lock = threading.Lock()
        self._last_len = 0

    def _get_frames(self, name):
        if isinstance(name, (list, tuple)) and name:
            return list(name)
        return _SPINNERS.get(str(name), _SPINNERS["dots"])

    def _hide_cursor(self):
        if not self._cursor_hidden:
            self.stream.write("\x1b[?25l")
            self.stream.flush()
            self._cursor_hidden = True

    def _show_cursor(self):
        if self._cursor_hidden:
            self.stream.write("\x1b[?25h")
            self.stream.flush()
            self._cursor_hidden = False

    def _render(self, s: str):
        pad = max(0, self._last_len - len(s))
        self.stream.write("\r" + s + (" " * pad))
        self.stream.flush()
        self._last_len = len(s)

    def _loop(self):
        i = 0
        self._hide_cursor()
        while not self._stop.is_set():
            frame = self._frames[i % len(self._frames)]
            line = f"{frame} {self.text}"
            with self._render_lock:
                self._render(line)
            i += 1
            end = time.time() + self.interval
            while time.time() < end:
                if self._stop.is_set():
                    break
                time.sleep(0.01)

    def _clear_line(self):
        self._render("")
        self.stream.write("\r")
        self.stream.flush()
        self._last_len = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return self
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        with self._render_lock:
            self._clear_line()
        self._show_cursor()

    def succeed(self, text="Done."):
        self.stop()
        self.stream.write(f"{_GREEN}✔{_RESET} {text}\n\n")
        self.stream.flush()

    def fail(self, text="Failed."):
        self.stop()
        self.stream.write(f"{_RED}✖{_RESET} {text}\n")
        self.stream.flush()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.fail(str(exc) if str(exc) else "Failed.")
        else:
            self.succeed("Done.")

_instances = []
def _restore_all():
    for sp in _instances:
        try:
            sp._show_cursor()
        except Exception:
            pass
atexit.register(_restore_all)

def open_browser_with_prompt(prompt_text: str):
    """Open Google AI Studio and copy prompt to clipboard for easy pasting."""
    try:
        import subprocess
        # Copy to clipboard (macOS)
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(prompt_text.encode('utf-8'))
        
        webbrowser.open("https://aistudio.google.com/prompts/new_image")
        print(f"\nPrompt copied to clipboard! At Google AI Studio:")
        print("1. Paste the prompt (Cmd+V)")
        print("2. Check 'Run settings' for Aspect Ratio and other options")
        print("3. Click 'Run' to generate")
        print("\nhttps://aistudio.google.com/prompts/new_image")
        print()
        
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")
        webbrowser.open("https://aistudio.google.com/prompts/new_image")
        print(f"\nPlease copy and paste this prompt:\n\n{prompt_text}")
        print("Then go to: https://aistudio.google.com/prompts/new_image")
        print()


class ReversePrompter:
    def __init__(self, model: str = "gemini-2.5-flash"):
        """Initialize the reverse prompter with API configuration."""
        # Load environment variables from ~/.env
        load_dotenv(os.path.expanduser("~/.env"))
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in ~/.env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    def validate_image(self, image_path: str) -> bool:
        """Validate that the file is a supported image format."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            raise ValueError(f"Invalid image file {image_path}: {e}")

    def load_image(self, image_path: str) -> Image.Image:
        """Load and return PIL Image object."""
        try:
            return Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")

    def generate_prompt(self, image_path: str) -> str:
        """Generate a descriptive prompt from an image."""
        self.validate_image(image_path)
        image = self.load_image(image_path)
        
        prompt_text = "Generate a single paragraph prompt that could be used to recreate this image. Include the main subject, artistic style, composition, colors, lighting, and mood in a flowing descriptive paragraph. Focus on being comprehensive but concise."
        
        try:
            # Generate content with Gemini - try simple approach first
            with Spinner("Analyzing image with Gemini", spinner="dots") as spinner:
                response = self.client.generate_content([prompt_text, image])
            
            # Handle response parts properly
            if not response.candidates:
                raise RuntimeError("No response candidates from Gemini API")
            
            candidate = response.candidates[0]
            
            # Check for blocked content
            if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                if candidate.finish_reason in [3, 4]:  # SAFETY or RECITATION
                    raise RuntimeError(f"Content was blocked by safety filters")
            
            # Try simple text accessor first
            try:
                if response.text and response.text.strip():
                    return response.text.strip()
            except:
                pass  # Fall back to parts method
            
            # Fallback to parts method
            if candidate.content and candidate.content.parts:
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                
                if text_parts:
                    return ' '.join(text_parts).strip()
            
            raise RuntimeError("No text content found in Gemini API response")
            
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        usage="%(prog)s image [--open]",
        description="Generate descriptive prompts from images using Google Gemini 2.5 Flash",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "image",
        help="Path to the image file"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Copy prompt to clipboard and open Google AI Studio in browser"
    )
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        print()
        sys.exit(0)
    
    args = parser.parse_args()
    
    try:
        prompter = ReversePrompter()
        prompt = prompter.generate_prompt(args.image)
        
        
        if args.open:
            print(f"Prompt:\n{prompt}")
            open_browser_with_prompt(prompt)
        else:
            print(f"Prompt:\n{prompt}")
            print("\nYou can use the prompt at: https://aistudio.google.com/prompts/new_image")
            print("Or run with --open to automatically open it in your browser.")
            print()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()