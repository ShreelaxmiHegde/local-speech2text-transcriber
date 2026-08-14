# Local Speech-to-Text Transcriber

A lightweight local speech-to-text CLI application that captures microphone input and transcribes speech locally using Faster-Whisper.

The project runs the AI model entirely on local hardware, without needing to send recorded audio to a cloud-based transcription API.

Supports microphone controls such as pausing and resuming through keyboard keys.

Stores transcribed text in date-based text files with timestamps, keeping file storage simple, practical, and sufficient.

## Tech Stack

- **Python** - application runtime
- **SoundDevice** - microphone and audio input
- **NumPy** - audio data processing
- **Faster-Whisper** - local speech-to-text inference

## How It Works
```
Microphone
    ↓
Audio Capture
    ↓
Keyboard Control
(Pause / Resume / Send)
    ↓
Audio Processing
    ↓
Local Whisper Model
    ↓
Transcription Segments
    ↓
Timestamped Transcript
    ↓
Date-based Text File
```

## Highlights

- **Local transcription:** Audio is processed locally using a Whisper model.
- **Microphone input:** Captures speech directly from the system microphone.
- **Keyboard controls:** Pause, resume, and send audio for transcription using keyboard input.
- **Date-based transcript storage:** Transcriptions are stored in text files organized by date.
- **Timestamped transcripts:** Transcribed segments are stored with their corresponding timestamps.
- **Hardware-aware inference:** Whisper model configuration is selected based on the available system hardware.
- **CLI-based interface:** No web server or external UI is required.