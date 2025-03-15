#!/usr/bin/env python
"""
AutoReader - Text to Speech Application

This application converts text files to speech using the Kokoro-82M text-to-speech model.
"""

import os
import sys
import argparse
from text_to_speech_app import text_to_speech

def main():
    """Main entry point for the application"""
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="AutoReader - Convert text files to speech using Kokoro-82M",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file", 
        help="Path to the input .txt file"
    )
    
    parser.add_argument(
        "-o", "--output", 
        default="output.wav", 
        help="Output audio file name"
    )
    
    parser.add_argument(
        "-v", "--voice", 
        default="af_bella",
        help="Voice to use. Options: af_bella, af_nicole, af_sarah, af_sky, "
             "am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis"
    )
    
    parser.add_argument(
        "-p", "--play", 
        action="store_true",
        default=True,
        help="Play audio out loud during generation"
    )
    
    parser.add_argument(
        "--no-play", 
        action="store_false",
        dest="play",
        help="Don't play audio out loud during generation"
    )
    
    parser.add_argument(
        "-s", "--save", 
        action="store_true",
        default=True,
        help="Save audio files to disk"
    )
    
    parser.add_argument(
        "--no-save", 
        action="store_false",
        dest="save",
        help="Don't save audio files to disk, just play them"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1
    
    if not args.input_file.endswith('.txt'):
        print(f"Warning: Input file '{args.input_file}' does not have a .txt extension.")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            return 0
    
    # Clean up voice parameter
    args.voice = args.voice.strip()
    
    # List of valid voices
    valid_voices = ["af_bella", "af_nicole", "af_sarah", "af_sky", 
                    "am_adam", "am_michael", 
                    "bf_emma", "bf_isabella", 
                    "bm_george", "bm_lewis"]
    
    # Validate voice parameter
    if args.voice not in valid_voices:
        print(f"Warning: '{args.voice}' may not be a valid voice.")
        print(f"Valid voices are: {', '.join(valid_voices)}")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            return 0
    
    # Ensure at least one of save or play is enabled
    if not args.save and not args.play:
        print("Error: You've disabled both saving and playing audio.")
        print("At least one of these options must be enabled.")
        return 1
    
    # Run the text-to-speech conversion
    try:
        text_to_speech(args.input_file, args.output, args.voice, args.play, args.save)
        if args.save:
            print(f"\nSuccess! Audio saved to {args.output}")
        else:
            print(f"\nSuccess! Audio played without saving to disk.")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 