import torch
from TTS.api import TTS
import simpleaudio as sa

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Run TTS
tts.tts_to_file(text="Hello world, I'm Pajama Sam!", speaker_wav="pajama_sam_test_reduced.wav", language="en", file_path="output.wav")

# Play the output.wav file
wave_obj = sa.WaveObject.from_wave_file("output.wav")
play_obj = wave_obj.play()
play_obj.wait_done()  # Wait until sound has finished playing