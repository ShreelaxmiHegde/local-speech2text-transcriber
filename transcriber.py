import os
import threading
from datetime import date, datetime
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class AudioTranscriber:
    """Core audio recording and transcription manager using sounddevice and Faster-Whisper."""

    def __init__(self, model_size="tiny", device="cpu", compute_type="int8", fs=16000, channels=1):
        self.fs = fs
        self.channels = channels
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        self._model = None
        self.stream = None
        self.audio_chunks = []
        self.state = "idle"  # idle, recording, paused, transcribing
        self.lock = threading.Lock()

        # Ensure base directories exist
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_dir = os.path.join(self.base_dir, "transcription_storage")
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_model(self):
        """Lazy load Whisper model."""
        if self._model is None:
            print("\033[93mLoading Faster-Whisper model...\033[0m")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        return self._model

    def _audio_callback(self, indata, frames, time_info, status):
        """Sounddevice stream callback running on the audio thread."""
        if status:
            print("\033[91mAudio status:\033[0m", status)

        with self.lock:
            if self.state == "recording":
                self.audio_chunks.append(indata.copy())

    def start(self):
        """Starts recording audio from the microphone."""
        with self.lock:
            if self.state in ("recording", "transcribing"):
                return False, f"Cannot start recording while in state '{self.state}'"

            # Clean up any leftover stream
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None

            self.audio_chunks = []
            self.state = "recording"

            try:
                self.stream = sd.InputStream(
                    samplerate=self.fs,
                    channels=self.channels,
                    callback=self._audio_callback
                )
                self.stream.start()
                return True, "Recording started"
            except Exception as e:
                self.state = "idle"
                return False, f"Failed to start audio stream: {e}"

    def pause(self):
        """Pauses audio chunk accumulation."""
        with self.lock:
            if self.state != "recording":
                return False, f"Cannot pause while in state '{self.state}'"
            self.state = "paused"
            return True, "Recording paused"

    def resume(self):
        """Resumes audio chunk accumulation."""
        with self.lock:
            if self.state != "paused":
                return False, f"Cannot resume while in state '{self.state}'"
            self.state = "recording"
            return True, "Recording resumed"

    def stop_and_transcribe(self):
        """Stops recording, flattens audio, transcribes with Whisper, and saves to file."""
        with self.lock:
            if self.state not in ("recording", "paused"):
                return {
                    "success": False,
                    "error": f"Cannot stop recording while in state '{self.state}'",
                    "text": "",
                    "segments": []
                }

            self.state = "transcribing"

            # Stop and close the audio stream
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None

            chunks = list(self.audio_chunks)
            self.audio_chunks = []

        if not chunks:
            with self.lock:
                self.state = "idle"
            return {
                "success": True,
                "text": "",
                "segments": []
            }

        try:
            # Combine all chunks
            recording = np.concatenate(chunks, axis=0)
            flatten_rec = recording.flatten()

            print("\n\033[93m----- Transcribing with Faster-Whisper ----- \033[0m\n")
            model = self._get_model()
            segments_gen, info = model.transcribe(flatten_rec, language='en')

            segments = []
            full_text = ""
            for segment in segments_gen:
                print(f"\033[92m{segment.text}\033[0m")
                full_text += segment.text
                segments.append({
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })

            full_text = full_text.strip()

            # Save to storage (date-based file with timestamps)
            today_file = os.path.join(self.storage_dir, f"{date.today().strftime('%d-%m-%Y')}.txt")
            with open(today_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%I:%M %p')}\n")
                if full_text:
                    f.write(full_text)
                f.write("\n\n ----------------------------------- \n\n")

            return {
                "success": True,
                "text": full_text,
                "segments": segments
            }
        except Exception as e:
            print(f"\033[91mTranscription error: {e}\033[0m")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "segments": []
            }
        finally:
            with self.lock:
                self.state = "idle"

    def get_status(self):
        """Returns the current state of the transcriber."""
        with self.lock:
            return {
                "status": self.state
            }
