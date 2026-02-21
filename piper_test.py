import wave
from piper.voice import PiperVoice

# Point to the voice model that is already in your folder
model_path = "en_US-lessac-medium.onnx" 

text = "Hello from WSL! Piper is ready to connect to Claude."

print("Loading voice model...")
voice = PiperVoice.load(model_path)

print("Synthesizing audio...")
with wave.open("test_output.wav", "wb") as wav_file:
    voice.synthesize(text, wav_file)

print("Audio generated! Check your folder for test_output.wav")
