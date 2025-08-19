# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a reverse prompt tool for generating descriptive text prompts from images using Google Gemini Vision API. The main components are:
- `rprompt.py` - Main Python script with ReversePrompter class and spinner UI
- `requirements.txt` - Python dependencies (google-generativeai, pillow, python-dotenv, requests)
- `sample.png` - Sample image for testing
- `.gitignore` - Prevents committing sensitive files like .env and cache files

## Development Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up Gemini API key in ~/.env file:
```bash
echo "GEMINI_API_KEY=your-api-key-here" >> ~/.env
```

## Common Commands

Run reverse prompting on an image:
```bash
python rprompt.py sample.png          # Generate prompt from image
python rprompt.py sample.png --open   # Generate prompt and open Google AI Studio
```

## Architecture

The `ReversePrompter` class handles:
- Image validation and PIL Image loading
- Google Gemini Vision API integration (gemini-2.5-flash by default)
- Environment variable loading from ~/.env file
- Error handling for blocked content and API failures

The script includes:
- Animated spinner for visual feedback during API calls
- Clipboard integration (macOS) for easy prompt copying
- Google AI Studio browser integration
- Comprehensive error handling and validation

The tool generates single paragraph prompts suitable for recreating images, focusing on subject, style, composition, colors, lighting, and mood.
