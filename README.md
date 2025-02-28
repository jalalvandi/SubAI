# SubAI

SubAI is a subtitle translation application that leverages the power of AI to translate subtitles into various languages. The application is built using Python and PyQt5 for the GUI, and it integrates with Google's Generative AI for translation.

## Features

- Load and translate subtitle files (.srt)
- Save translated subtitles
- Cache translations for faster processing
- Configurable settings for translation parameters
- User-friendly GUI

## Requirements

- Python 3.10
- PyQt5
- pysrt
- requests
- google-generativeai

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jalalvandi/SubAI.git
    cd SubAI
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python SubAI.py
    ```

2. Use the GUI to load a subtitle file, configure settings, and start the translation process.

## Configuration

The application uses a SQLite database (`subtitle_translator.db`) to store settings and translation cache.

## License

This project is licensed under the MIT License. See the LICENSE file for details.