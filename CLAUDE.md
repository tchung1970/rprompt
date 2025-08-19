# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a reverse prompt tool for generating descriptive text prompts from images using vision models. The main components are:
- `rprompt.py` - Main Python script for reverse prompting functionality
- `requirements.txt` - Python dependencies
- `000.jpg` - Sample anime-style landscape image for testing

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
python rprompt.py                    # Uses default 000.jpg
python rprompt.py --style artistic   # Uses default 000.jpg with artistic style
python rprompt.py 000.jpg --output prompt.txt
python rprompt.py custom.jpg --json --output result.json
```

## Architecture

The `ReversePrompter` class handles:
- Image validation and PIL Image loading
- Google Gemini Vision API integration (gemini-2.5-flash by default)
- Multiple prompt styles (detailed, concise, artistic, technical)
- Environment variable loading from ~/.env file
- Error handling and response parsing

The script supports various output formats and prompt styles to suit different use cases for image analysis and description generation using Google's Gemini models.