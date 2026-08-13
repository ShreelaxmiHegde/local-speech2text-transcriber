import sounddevice as sd
import numpy as np
import msvcrt
from faster_whisper import WhisperModel

fs = 16000
channels = 1
audio_chunks = []
recording = True

def callback(indata, frames, time, status):
  if status:
    print("Audio status: ", status)

  # only store audio while recording
  if recording:
    audio_chunks.append(indata.copy())

print("Starting microphone...")
stream = sd.InputStream(  
  samplerate=fs,
  channels=channels,
  callback=callback
)

stream.start()

try:
  while True:
    if msvcrt.kbhit():
      key = msvcrt.getch()

      # p - pause
      if key == b'p':
        if recording:
          recording = False
          print("\nPAUSED")

      # r - resume
      elif key == b'r':
        if not recording:
          recording = True
          print("\nRESUMED")

      # enter - finalize
      elif key == b'\r':
        print("\nRECORDED")
        break

finally:
  stream.stop()
  stream.close()

# Combine all the chunks received by the callback
recording = np.concatenate(audio_chunks, axis=0)
flatten_rec = recording.flatten()

sd.play(recording)
sd.wait()

print("Transcribing...")

model_size = "tiny"
model = WhisperModel(
  model_size,
  device="cpu",
  compute_type="int8"
)

segments, info = model.transcribe(flatten_rec, language='en')
print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
  print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))