# Local Speech-to-Text Transcriber

A lightweight local speech-to-text application that captures microphone input and transcribes speech locally using **Faster-Whisper**.

The project runs the AI model entirely on local hardware, without needing to send recorded audio to cloud-based transcription APIs. It can be used via an interactive **CLI** or connected to a **Chrome Extension UI**.

Transcribed text is stored in date-based text files with timestamps under `transcription_storage/`, keeping transcript archiving simple and structured.

---

## Tech Stack

- **Python** - application runtime (using built-in `http.server` for the backend API)
- **SoundDevice** - system microphone audio streaming
- **NumPy** - audio data processing and concatenation
- **Faster-Whisper** - fast local Whisper speech-to-text inference
- **Chrome Extension (HTML/CSS/JS)** - desktop popup UI to control recording and inspect transcripts

---

## Architecture & Workflows

```
  [ Chrome Extension UI ]
 (Start / Pause / Resume / Stop)
          │
          │ HTTP REST (127.0.0.1:5000)
          ▼
   [ server.py ] ──────────┐
                           ▼
                 [ transcriber.py ] ◄─── [ audio.py (CLI Mode) ]
                  (AudioTranscriber)
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
     Microphone Capture        Faster-Whisper Model
        (SoundDevice)            (Local CPU/int8)
                │                     │
                └──────────┬──────────┘
                           ▼
            transcription_storage/<Date>.txt
```

---

## Project Structure

- **[`transcriber.py`](transcriber.py)**: Core modular audio recorder and Faster-Whisper transcriber class (`AudioTranscriber`).
- **[`server.py`](server.py)**: Lightweight HTTP API server built with Python standard library (`http.server.ThreadingHTTPServer`) with full CORS support.
- **[`audio.py`](audio.py)**: Standalone CLI interface with real-time keyboard controls (`p`, `r`, `Enter`). Also supports `--server` mode.
- **[`manifest.json`](manifest.json)**, **[`popup.html`](popup.html)**, **[`script.js`](script.js)**, **[`style.css`](style.css)**: Chrome Extension UI interface connecting directly to the Python backend API.
- **[`transcription_storage/`](transcription_storage)**: Date-stamped transcript text logs.

---

## How to Run

### Option 1: Chrome Extension UI Mode

1. **Start the local Python backend server**:
   ```bash
   python server.py
   # or: python audio.py --server
   ```
   The server starts on `http://127.0.0.1:5000/`.

2. **Load the extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`.
   - Enable **Developer mode** (top-right toggle).
   - Click **Load unpacked** and select this project directory.
   - Click the extension icon in the toolbar to open the popup.

3. **Use the UI**:
   - Click **Start** (microphone icon) to begin recording.
   - Click **Pause** / **Resume** as needed.
   - Click **Send / Stop** (airplane icon) to finalize recording, run Faster-Whisper, display the transcript in the textarea, and auto-save it to file.
   - Click **Copy** to copy the transcribed text to clipboard.

---

### Option 2: Standalone CLI Mode

Run the CLI transcriber directly in your terminal:

```bash
python audio.py
```

Controls:
- Press `p` to pause recording.
- Press `r` to resume recording.
- Press `Enter` to finalize recording, run Whisper transcription, and save to storage.

---

## API Endpoints (Port 5000)

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | `GET` | Get current state (`idle`, `recording`, `paused`, `transcribing`) |
| `/api/start` | `POST` | Start microphone recording stream |
| `/api/pause` | `POST` | Pause audio collection |
| `/api/resume` | `POST` | Resume audio collection |
| `/api/stop` | `POST` | Stop recording, run Faster-Whisper inference, and save transcript |
