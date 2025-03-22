from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import argparse
import os
import numpy as np
import sys
import tempfile
import platform

# Function to play audio out loud
def play_audio(audio_file):
    """Play audio file out loud"""
    try:
        # Use different methods depending on the platform
        system = platform.system()
        
        if system == 'Windows':
            # On Windows, use winsound
            import winsound
            winsound.PlaySound(audio_file, winsound.SND_FILENAME)
            return True
        elif system == 'Darwin':  # macOS
            # Use afplay on macOS
            import subprocess
            subprocess.run(['afplay', audio_file], check=True)
            return True
        else:  # Linux and others
            # Try playsound for other platforms
            from playsound import playsound
            playsound(audio_file)
            return True
            
    except ImportError:
        print("Could not find a suitable audio playback library.")
        print("On Windows, winsound should be available by default.")
        print("On macOS, the 'afplay' command is used.")
        print("On Linux, install playsound: pip install playsound")
        return False
    except Exception as e:
        print(f"Error playing audio: {str(e)}")
        return False
    
    return True

def text_to_speech(input_file, output_file="output.wav", voice="af_bella", play_aloud=True, save_audio=True):
    """
    Convert text from a file to speech using the Kokoro-82M model.
    
    Args:
        input_file (str): Path to the input .txt file
        output_file (str): Path to save the output audio file
        voice (str): Voice to use for speech generation
        play_aloud (bool): Whether to play audio out loud during generation
        save_audio (bool): Whether to save audio files to disk
    """
    try:
        # Make sure output directory exists
        if save_audio and output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
        
        # Initialize the Kokoro TTS pipeline
        print("Loading Kokoro TTS model...")
        # 'a' => American English
        pipeline = KPipeline(lang_code='a')
        
        # Read the text file
        print(f"Reading text from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Generate speech
        print(f"Generating speech using voice: '{voice}'...")
        # Available voices:
        # - American Female: af_bella, af_nicole, af_sarah, af_sky
        # - American Male: am_adam, am_michael
        # - British Female: bf_emma, bf_isabella
        # - British Male: bm_george, bm_lewis
        generator = pipeline(
            text, 
            voice=voice,
            speed=1,
            split_pattern=r'\n+'
        )
        
        # Process the generated audio segments
        output_audio = []
        sample_rate = 24000  # Kokoro uses 24kHz sample rate
        
        print("Processing audio segments...")
        # Process each segment separately and save them individually
        segment_index = 0
        for i, (gs, ps, audio) in enumerate(generator):
            segment_index += 1
            print(f"Segment {segment_index}: {gs[:50]}...")
            
            # Create a file path - either temporary or permanent
            if save_audio:
                # Ensure segment files are saved to the same directory as the output file
                output_dir = os.path.dirname(output_file)
                output_basename = os.path.basename(output_file)
                segment_basename = f"{os.path.splitext(output_basename)[0]}_segment_{segment_index}.wav"
                segment_file = os.path.join(output_dir, segment_basename) if output_dir else segment_basename
                
                print(f"Saving segment to {segment_file}")
                sf.write(segment_file, audio, sample_rate)
                output_audio.append(segment_file)
            else:
                # Create a temporary file for playing audio
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    segment_file = temp_file.name
                    sf.write(segment_file, audio, sample_rate)
            
            # Try to display audio in notebook environments
            try:
                if 'ipykernel' in sys.modules:
                    display(Audio(data=audio, rate=24000, autoplay=False))
            except:
                pass
            
            # Play audio out loud if requested
            if play_aloud:
                print(f"Playing segment {segment_index}...")
                play_success = play_audio(segment_file)
                if not play_success:
                    print(f"Warning: Audio playback failed. File is saved at: {segment_file}")
                
            # Delete the temporary file if we're not saving audio
            if not save_audio and os.path.exists(segment_file):
                try:
                    os.unlink(segment_file)
                except:
                    pass
        
        # Save the segment list if we're saving audio
        if save_audio and output_audio:
            # If only one segment, just rename it to the output file
            if len(output_audio) == 1:
                os.rename(output_audio[0], output_file)
                print(f"Single segment saved as {output_file}")
            else:
                # Leave the segments as individual files
                print(f"Generated {len(output_audio)} audio segments as separate files.")
                # Create a simple text file listing all segments
                output_dir = os.path.dirname(output_file)
                output_basename = os.path.basename(output_file)
                segments_list_basename = f"{os.path.splitext(output_basename)[0]}_segments.txt"
                segments_list_file = os.path.join(output_dir, segments_list_basename) if output_dir else segments_list_basename
                
                with open(segments_list_file, 'w') as f:
                    for segment in output_audio:
                        f.write(f"{segment}\n")
                print(f"List of segments saved to {segments_list_file}")
        elif not save_audio:
            print(f"Audio playback complete. No files were saved to disk.")
        else:
            raise Exception("No audio was generated")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print more details about the error for debugging
        if "voices" in str(e) and ".pt" in str(e):
            print(f"\nLikely cause: Voice file not found. Valid voices are: af_bella, af_nicole, af_sarah, af_sky,")
            print(f"am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis")
            print(f"\nTried to use voice: '{voice}'")
            
if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Text to Speech Converter")
    parser.add_argument("input_file", help="Path to the input .txt file")
    parser.add_argument("-o", "--output", default="output.wav", 
                       help="Output audio file name (default: output.wav)")
    parser.add_argument("-v", "--voice", default="af_bella",
                       help="Voice to use (default: af_bella). Options: af_bella, af_nicole, af_sarah, af_sky, "
                            "am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis")
    parser.add_argument("-p", "--play", action="store_true", default=True,
                       help="Play audio out loud during generation (default: True)")
    parser.add_argument("--no-play", action="store_false", dest="play",
                       help="Don't play audio out loud during generation")
    parser.add_argument("-s", "--save", action="store_true", default=True,
                       help="Save audio files to disk (default: True)")
    parser.add_argument("--no-save", action="store_false", dest="save",
                       help="Don't save audio files to disk, just play them")
    
    args = parser.parse_args()
    
    # Run the text-to-speech conversion
    text_to_speech(args.input_file, args.output, args.voice, args.play, args.save) 