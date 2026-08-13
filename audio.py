import sounddevice as sd
import numpy as np
import msvcrt
from faster_whisper import WhisperModel
from datetime import date, datetime

fs = 16000
channels = 1
audio_chunks = []
recording = True

def callback(indata, frames, time, status):
  if status:
    print("\033[91mAudio status: \033[0m", status)

  # only store audio while recording
  if recording:
    audio_chunks.append(indata.copy())

print("\033[93mStarting microphone...\033[0m")

stream = sd.InputStream(  
  samplerate=fs,
  channels=channels,
  callback=callback
)

stream.start()

# recording control keys
try:
  while True:
    if msvcrt.kbhit():
      key = msvcrt.getch()

      # p - pause
      if key == b'p':
        if recording:
          recording = False
          print("\033[95mPAUSED\033[0m")

      # r - resume
      elif key == b'r':
        if not recording:
          recording = True
          print("\033[96mRESUMED\033[0m")

      # enter - finalize
      elif key == b'\r':
        print("\033[94mRECORDED\033[0m")
        break

finally:
  stream.stop()
  stream.close()

# Combine all the chunks received by the callback
recording = np.concatenate(audio_chunks, axis=0)
flatten_rec = recording.flatten()

print("\n ----- Transcribing ----- \n")

model_size = "tiny"
model = WhisperModel(
  model_size,
  device="cpu",
  compute_type="int8"
)

segments, info = model.transcribe(flatten_rec, language='en')

for segment in segments:
  print("Transcription: \n", f"\033[92m{segment.text} \033[0m")

  with open(f"transcribes/{date.today().strftime("%d-%m-%Y")}.txt", "a") as f:
    f.write(f"{datetime.now().strftime("%I:%M %p")}\n{segment.text}\n\n ----------------------------------- \n\n")