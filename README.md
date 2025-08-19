# Reverse Prompt Tool

Generate descriptive text prompts from images using Google Gemini Vision API. Perfect for creating prompts that can recreate or describe images in detail.

## Features

- 🖼️ Analyze any image format supported by PIL
- 🤖 Powered by Google Gemini 2.5 Flash Vision model
- ✨ Animated spinner for visual feedback
- 📋 Automatic clipboard copying (macOS)
- 🌐 Direct integration with Google AI Studio
- 🛡️ Comprehensive error handling and validation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rprompt.git
cd rprompt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
```bash
echo "GEMINI_API_KEY=your-api-key-here" >> ~/.env
```

Get your API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

### Basic Usage
```bash
python rprompt.py image.jpg
```

### With Browser Integration
```bash
python rprompt.py image.jpg --open
```

This will:
- Generate a descriptive prompt from your image
- Copy the prompt to your clipboard (macOS)
- Open Google AI Studio in your browser for immediate use

### Examples

```bash
# Analyze a photo
python rprompt.py sample.png

# Generate prompt and open AI Studio
python rprompt.py sample.png --open

# Works with various formats
python rprompt.py image.jpeg --open
```

## How It Works

The tool uses Google's Gemini 2.5 Flash model to analyze images and generate comprehensive prompts that describe:

- Main subject and composition
- Artistic style and technique
- Colors and lighting
- Mood and atmosphere
- Visual elements and details

The generated prompts are designed to be comprehensive yet concise, perfect for:
- AI image generation
- Image cataloging and description
- Accessibility alt-text creation
- Creative writing inspiration

## Requirements

- Python 3.7+
- Google Gemini API key
- macOS (for clipboard integration)

## Dependencies

- `google-generativeai` - Google Gemini API client
- `pillow` - Image processing
- `python-dotenv` - Environment variable loading
- `requests` - HTTP requests

## Error Handling

The tool includes robust error handling for:
- Invalid image formats
- Missing API keys
- Network connectivity issues
- Content safety filters
- API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section in the code
- Verify your API key is correctly set in `~/.env`