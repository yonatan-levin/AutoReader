# AutoReader - Text to Speech Application

AutoReader is a Python application that converts text files to speech using the Kokoro-82M text-to-speech model.

## Features

- Convert text files to high-quality speech
- Simple command-line interface
- Support for various text formats
- Uses Kokoro-82M, a lightweight but powerful TTS model (82 million parameters)
- Multiple voice options (American/British, male/female)
- Real-time audio playback during generation
- Option to play audio without saving files to disk
- Cross-platform audio playback support (Windows, macOS, Linux)
- Efficient handling of long texts by processing in segments

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/AutoReader.git
cd AutoReader
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install espeak-ng (required for some languages):
   - Windows: Download from [espeak-ng GitHub releases](https://github.com/espeak-ng/espeak-ng/releases)
   - Linux (Ubuntu): `sudo apt-get install espeak-ng`
   - macOS: `brew install espeak-ng`

## Usage

### Basic Usage

```bash
python main.py input.txt
```

This will convert the text in `input.txt` to speech, save it as `output.wav`, and play it during generation.

### Command-line Options

```bash
python main.py input.txt -o output.wav -v af_bella
```

#### Available Parameters:

- `-o, --output`: Specify output filename (default: output.wav)
- `-v, --voice`: Specify voice to use (default: af_bella)
- `-p, --play`: Play audio during generation (default: enabled)
- `--no-play`: Disable audio playback
- `-s, --save`: Save audio files to disk (default: enabled)
- `--no-save`: Don't save audio files, just play them

### Usage Examples

#### Convert text and save audio without playback:
```bash
python main.py input.txt --no-play
```

#### Play text without saving files:
```bash
python main.py input.txt --no-save
```

#### Specify custom voice and output filename:
```bash
python main.py input.txt -v am_michael -o michael_voice.wav
```

## Available Voices

Kokoro-82M supports multiple voices. Here are the available options:

### American English Voices:
- `af_bella`: Female voice (Bella)
- `af_nicole`: Female voice (Nicole) 
- `af_sarah`: Female voice (Sarah)
- `af_sky`: Female voice (Sky)
- `am_adam`: Male voice (Adam)
- `am_michael`: Male voice (Michael)

### British English Voices:
- `bf_emma`: Female voice (Emma)
- `bf_isabella`: Female voice (Isabella)
- `bm_george`: Male voice (George)
- `bm_lewis`: Male voice (Lewis)

## Technical Details

AutoReader uses the following technologies:

- **Kokoro-82M**: A lightweight TTS model with 82 million parameters
- **Platform-specific audio playback**:
  - Windows: Uses `winsound` for audio playback
  - macOS: Uses `afplay` command
  - Linux: Uses `playsound` library
- **Segment processing**: Handles long texts by breaking them into logical segments
- **Temporary file management**: Can operate in memory-only mode without saving files

## Requirements

- Python 3.8 or higher
- kokoro >= 0.7.11
- soundfile >= 0.12.1
- numpy >= 1.24.0
- espeak-ng (for text processing)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) - The text-to-speech model
- [Kokoro GitHub Repository](https://github.com/hexgrad/kokoro) - Implementation library 