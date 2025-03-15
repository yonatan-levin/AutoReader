import unittest
import os
import time
from text_to_speech_app import text_to_speech

class TestTextToSpeech(unittest.TestCase):
    def setUp(self):
        self.test_file = "test.txt"
        self.output_file = "test_output.wav"
        
        # Ensure test file exists
        if not os.path.exists(self.test_file):
            with open(self.test_file, 'w', encoding='utf-8') as f:
                f.write("This is a test for the Kokoro TTS model.")

    def test_text_to_speech(self):
        try:
            # Test successful conversion
            text_to_speech(self.test_file, self.output_file)
            
            # Allow time for file to be created and closed
            time.sleep(1)
            
            # Check if output file exists
            self.assertTrue(os.path.exists(self.output_file), 
                           f"Output file {self.output_file} was not created")
            
            # Test file size is reasonable
            file_size = os.path.getsize(self.output_file)
            self.assertGreater(file_size, 1000, 
                              f"Output file size ({file_size} bytes) is too small")
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")

    def tearDown(self):
        # Only remove the output file, keep the test.txt since it might be manually created
        if os.path.exists(self.output_file):
            try:
                os.remove(self.output_file)
            except:
                pass  # Ignore errors during cleanup

if __name__ == '__main__':
    unittest.main() 