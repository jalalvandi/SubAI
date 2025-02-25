# Subtitle Translator

A PyQt5-based application for translating subtitle files (`.srt`) using Google's Generative AI (Gemini). This tool allows you to load subtitle files, translate them into various languages, and save the translated subtitles to a new file.

---

## Features

- **Load Subtitle Files**: Open `.srt` files and display the subtitles in a table.
- **Translate Subtitles**: Translate subtitles into multiple languages using Google's Gemini API.
- **Save Translated Subtitles**: Save the translated subtitles to a new `.srt` file.
- **Settings Management**: Configure your Google API key and proxy settings (HTTP/HTTPS).
- **User-Friendly Interface**: Simple and intuitive GUI for easy navigation.

---

## Requirements

- Python 3.7 or higher
- Required Python libraries:
  - `PyQt5`
  - `pysrt`
  - `google-generativeai`

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jalalvandi/subtitle-translator.git
   cd subtitle-translator
   ```
2. **Install Dependencies:**:   
   ```bash
    pip install PyQt5 pysrt google-generativeai
   ``` 
3. **Run the Application:**:
   ```bash
   python subtitle_translator.py
   ```
      