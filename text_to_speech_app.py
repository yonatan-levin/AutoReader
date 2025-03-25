import heapq
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import argparse
import os
import numpy as np
import sys
import tempfile
import platform
import asyncio
import pygame

class OrderedQueue:
    def __init__(self):
        self._heap = []
        self._event = asyncio.Event()

    async def put(self, sequence, item):
        heapq.heappush(self._heap, (sequence, item))
        self._event.set()

    async def get(self, timeout=None):
        # Wait until at least one item is available
        while not self._heap:
            try:
                # Wait with timeout
                await asyncio.wait_for(self._event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                # If we time out, return None to indicate no item available
                print("Queue get operation timed out")
                return None, None
        sequence, item = heapq.heappop(self._heap)
        if not self._heap:
            self._event.clear()
        return sequence, item

class TextToSpeechProcessor:
    def __init__(self, input_file, output_file="output.wav", voice="af_bella", play_aloud=True, save_audio=True, speed=1.0):
        self.input_file = input_file
        self.output_file = output_file
        self.voice = voice
        self.play_aloud = play_aloud
        self.save_audio = save_audio
        self.speed = speed
        self.sample_rate = 24000  # Kokoro uses 24kHz sample rate
        self.pipeline = None
        self.text = ""
        
    # Function to play audio out loud
    def play_audio(self, audio_file):
        """Play audio file out loud"""
        try:
            # Use different methods depending on the platform
            system = platform.system()
            
            if system == 'Windows':
                # On Windows, use pygame instead of winsound
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init(frequency=self.sample_rate)
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    return True
                except ImportError:
                    print("Could not import pygame. Please install it with: pip install pygame")
                    # Try using the default media player as fallback
                    import subprocess
                    try:
                        subprocess.run(['start', audio_file], shell=True, check=False)
                        print("Using Windows default media player instead")
                        import time
                        time.sleep(2)  # Give some time for playback
                        return True
                    except:
                        print("Failed to play audio with default media player")
                        return False
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
            print("On Windows, pygame should be available by default.")
            print("On macOS, the 'afplay' command is used.")
            print("On Linux, install playsound: pip install playsound")
            return False
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            return False
    
    async def process_segment(self, i, gs, ps, audio):
        segment_index = i + 1
        segment_preview = gs[:50] if gs is not None else "No text"
        print(f"Segment {segment_index}: {segment_preview}...")
        
        if self.save_audio:
            output_dir = os.path.dirname(self.output_file)
            output_basename = os.path.basename(self.output_file)
            segment_basename = f"{os.path.splitext(output_basename)[0]}_segment_{segment_index}.wav"
            segment_file = os.path.join(output_dir, segment_basename) if output_dir else segment_basename
            print(f"Saving segment to {segment_file}")
            await asyncio.to_thread(sf.write, segment_file, audio, self.sample_rate)
            result = segment_file
            temp_flag = False
        else:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                segment_file = temp_file.name
            await asyncio.to_thread(sf.write, segment_file, audio, self.sample_rate)
            result = segment_file
            temp_flag = True
        
        try:
            if 'ipykernel' in sys.modules:
                display(Audio(data=audio, rate=self.sample_rate, autoplay=False))
        except Exception as e:
            pass
        
        return (segment_index, result, temp_flag)
    
    async def worker(self, segment_data, sequence, ordered_queue):
        gs, ps, audio = segment_data
        # Process the segment using the provided function signature
        result = await self.process_segment(sequence, gs, ps, audio)
        # Put the result into the ordered queue with its sequence number
        await ordered_queue.put(sequence, result)

    async def process(self):
        """
        Convert text from a file to speech using the Kokoro-82M model.
        """
        try:
            # Make sure output directory exists
            if self.save_audio and self.output_file:
                output_dir = os.path.dirname(self.output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    print(f"Created output directory: {output_dir}")
            
            # Initialize the Kokoro TTS pipeline
            print("Loading Kokoro TTS model...")
            # 'a' => American English
            self.pipeline = KPipeline(lang_code='a')
            
            # Read the text file
            print(f"Reading text from {self.input_file}...")
            with open(self.input_file, 'r', encoding='utf-8') as file:
                self.text = file.read()

            # Generate speech
            print(f"Generating speech using voice: '{self.voice}'...")
            # Available voices:
            # - American Female: af_bella, af_nicole, af_sarah, af_sky
            # - American Male: am_adam, am_michael
            # - British Female: bf_emma, bf_isabella
            # - British Male: bm_george, bm_lewis
            print("Creating generator from pipeline...")
            speech_generator = self.pipeline(
                self.text,
                voice=self.voice,
                speed=self.speed,
                split_pattern=r'\n+'
            )
            
            # to process items as they become available
            print("Starting speech generation and processing...")
            
            # Process the generated audio segments asynchronously
            print("Processing audio segments asynchronously...")

            print("Starting worker tasks...")
            ordered_queue = OrderedQueue()
            
            # Start consumer to process generator items
            generator_consumer = asyncio.create_task(self._process_generator(speech_generator, ordered_queue))
            
            # Wait for initial tasks to be created
            await asyncio.sleep(0.1)
            
            # Process results as they become available
            output_files = await self._process_results(ordered_queue)
            
            # Wait for generator consumer to complete
            await generator_consumer
            
            # Process output files if needed
            if self.save_audio and output_files:
                await self._combine_output_files(output_files)
            elif not self.save_audio:
                print("Audio playback complete. No files were saved to disk.")
            else:
                raise Exception("No audio was generated")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # Print more details about the error for debugging
            import traceback
            traceback.print_exc()
            if "voices" in str(e) and ".pt" in str(e):
                print(f"\nLikely cause: Voice file not found. Valid voices are: af_bella, af_nicole, af_sarah, af_sky,")
                print(f"am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis")
                print(f"\nTried to use voice: '{self.voice}'")
    
    async def _process_generator(self, generator, ordered_queue):
        """Process generator items and create worker tasks"""
        tasks = []
        task_count = 0
        
        print("Processing generator items...")
        # Process generator items
        for idx, segment in enumerate(generator):
            print(f"Creating worker for segment {idx+1}")
            task = asyncio.create_task(self.worker(segment, idx, ordered_queue))
            tasks.append(task)
            task_count += 1
            # Yield control to allow other tasks to run
            await asyncio.sleep(0)
        
        print(f"Created {task_count} worker tasks")
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks)
        
        return task_count
    
    async def _process_results(self, ordered_queue):
        """Process results from the ordered queue"""
        output_files = []
        processed_segments = 0
        running = True
        total_processed = 0
        
        print("Processing results as they arrive...")
        while running:
            # Use a timeout to avoid getting stuck indefinitely
            sequence, result = await ordered_queue.get(timeout=10)
            
            # If we got None from a timeout
            if sequence is None:
                print("Queue get timed out. Checking for more items...")
                # If we've processed everything we know about, break
                if total_processed > 0 and processed_segments >= total_processed:
                    print("All known segments processed. Finishing.")
                    break
                    
                # Otherwise, continue waiting
                continue

            # Make sure result is not None before unpacking
            if result is None:
                print("Received None result. Skipping this iteration.")
                continue
            
            try:
                seg_index, seg_file, temp_flag = result
                total_processed = max(total_processed, seg_index)
            except Exception as e:
                print(f"Error unpacking result: {e}, result was: {result}")
                continue
            
            print(f"Processing completed segment {seg_index}/{total_processed}...")
            if self.save_audio and seg_file:
                output_files.append((seg_index, seg_file))
            
            if self.play_aloud:
                print(f"Playing segment {seg_index}...")
                play_success = await asyncio.to_thread(self.play_audio, seg_file)
                if not play_success:
                    print(f"Warning: Audio playback failed. File is saved at: {seg_file}")
            
            if not self.save_audio and os.path.exists(seg_file):
                try:
                    os.unlink(seg_file)
                except Exception as e:
                    pass
                    
            print(f"Result for segment {seg_index}: {seg_file}")
            processed_segments += 1
        
        return output_files
    
    async def _combine_output_files(self, output_files):
        """Combine multiple output files into a single file"""
        # Sort output files by segment index
        output_files.sort(key=lambda x: x[0])
        output_audio = [seg for (idx, seg) in output_files]
        
        if len(output_audio) == 1:
            os.rename(output_audio[0], self.output_file)
            print(f"Single segment saved as {self.output_file}")
        else:
            print(f"Combining {len(output_audio)} audio segments into one file...")
            # Combine all audio segments into a single file
            combined_audio = []
            for segment_file in output_audio:
                audio_data, sr = sf.read(segment_file)
                combined_audio.append(audio_data)
            
            # Concatenate all audio segments
            concatenated_audio = np.concatenate(combined_audio)
            
            # Save the combined audio to the output file
            sf.write(self.output_file, concatenated_audio, self.sample_rate)
            
            # Delete the individual segment files
            for segment_file in output_audio:
                try:
                    os.unlink(segment_file)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file {segment_file}: {str(e)}")
            
            print(f"All segments combined and saved as {self.output_file}")

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
    parser.add_argument("--speed", type=float, default=1.0,
                       help="Speed multiplier for speech (default: 1.0)")
    
    args = parser.parse_args()
    
    # Create TextToSpeechProcessor instance
    processor = TextToSpeechProcessor(
        input_file=args.input_file,
        output_file=args.output,
        voice=args.voice,
        play_aloud=args.play,
        save_audio=args.save,
        speed=args.speed
    )
    
    # Run the text-to-speech conversion
    asyncio.run(processor.process()) 