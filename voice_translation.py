#Tamil, Hindi, Kannada, Marathi, Urdu, Nepali to English

from openai import OpenAI
import sounddevice as sd
from scipy.io.wavfile import write
import os

# === CONFIG ===
DURATION = 5   # seconds of recording
FILENAME = "input.wav"
SAMPLE_RATE = 16000  # Whisper works best at 16kHz

# === RECORD AUDIO ===
print("🎙️ Recording... Speak now!")
recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
sd.wait()  # Wait until recording is finished
write(FILENAME, SAMPLE_RATE, recording)  # Save as WAV
print(f"✅ Recording saved to {FILENAME}")

# === TRANSCRIBE AUDIO ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open(FILENAME, "rb") as audio_file:
    translation = client.audio.translations.create(
        model="whisper-1", 
        file=audio_file,
    )

print("📝 Translation:")
print(translation.text)