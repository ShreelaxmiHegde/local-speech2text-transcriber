import sounddevice as sd
import numpy as np
import msvcrt

fs = 44100
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

      # p
      if key == b'p':
        if recording:
          recording = False
          print("\nPAUSED")

      # r
      elif key == b'r':
        if not recording:
          recording = True
          print("\nRESUMED")

      # s
      elif key == b'\r':
        print("\nFINALIZING...")
        break

finally:
  stream.stop()
  stream.close()
  print("Recording stopped.")

# Combine all the chunks received by the callback
recording = np.concatenate(audio_chunks, axis=0)

print("Recorded shape:", recording.shape)
print(recording)
print("Playing recorded audio...")

sd.play(recording, fs)
sd.wait()

print("Playback finished.")