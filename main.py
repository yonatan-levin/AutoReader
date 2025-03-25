#!/usr/bin/env python
"""
AutoReader - Text to Speech Application

This application converts text files to speech using the Kokoro-82M text-to-speech model.
"""

import os
import sys
import argparse
import glob
import asyncio
from text_to_speech_app import TextToSpeechProcessor

def process_file(input_file, output_file, voice, play_aloud, save_audio, speed):
    """Process a single text file"""
    try:
        print(f"Processing file: {input_file}")
        
        tts = TextToSpeechProcessor(input_file, output_file, voice, play_aloud, save_audio, speed)
        
        asyncio.run(tts.process())
        if save_audio:
            print(f"Success! Audio saved to {output_file}")
        else:
            print(f"Success! Audio played without saving to disk.")
        return 0
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return 1

def parse_arguments():
    """Parse and validate command line arguments"""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="AutoReader - Convert text files to speech using Kokoro-82M",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file", 
        nargs='?',  # Make input_file optional
        help="Path to the input .txt file (if not specified, all .txt files in the input folder will be processed)"
    )
    
    parser.add_argument(
        "-o", "--output", 
        default=None,  # We'll determine the default based on input file
        help="Output audio file name (default: input_filename.wav in the output folder)"
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
        help="Play audio during generation"
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

    parser.add_argument(
        "-sp", "--speed", 
        type=float,
        default=1.0,
        help="Speed of the speech. Default is 1.0 (normal speed)."
    )
    
    # Parse arguments
    args = parser.parse_args()
    
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
            sys.exit(0)
    
    # Ensure at least one of save or play is enabled
    if not args.save and not args.play:
        print("Error: You've disabled both saving and playing audio.")
        print("At least one of these options must be enabled.")
        sys.exit(1)
        
    return args

def main():
    """Main entry point for the application"""
    
    # Ensure input and output directories exist
    input_dir = os.path.join(os.getcwd(), "input")
    output_dir = os.path.join(os.getcwd(), "output")
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created input directory: {input_dir}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Determine which file(s) to process
    if args.input_file:
        args.input_file = input_dir+"\\"+args.input_file
        # User specified a specific file
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' does not exist.")
            return 1
        
        if not args.input_file.endswith('.txt'):
            print(f"Warning: Input file '{args.input_file}' does not have a .txt extension.")
            user_input = input("Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                return 0
        
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            # Use the input filename but in the output directory
            input_basename = os.path.basename(args.input_file)
            output_basename = os.path.splitext(input_basename)[0] + ".wav"
            output_file = os.path.join(output_dir, output_basename)
        
        # Process the single file
        return process_file(args.input_file, output_file, args.voice, args.play, args.save, args.speed)
       
    else:
        # Process all .txt files in the input directory
        input_files = glob.glob(os.path.join(input_dir, "*.txt"))
        
        if not input_files:
            print(f"No .txt files found in the input directory: {input_dir}")
            print("Please add .txt files to the input directory or specify an input file.")
            return 1
        
        print(f"Found {len(input_files)} .txt files in the input directory.")
        
        # Process each file
        result = 0
        for input_file in input_files:
            input_basename = os.path.basename(input_file)
            output_basename = os.path.splitext(input_basename)[0] + ".wav"
            output_file = os.path.join(output_dir, output_basename)
            
            file_result = process_file(input_file, output_file, args.voice, args.play, args.save,args.speed)
            if file_result != 0:
                result = file_result
        
        return result

if __name__ == "__main__":
    sys.exit(main()) 