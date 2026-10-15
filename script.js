(function () {
  const $ = function (id) { return document.getElementById(id); };
  const startB = $('start');
  const pauseB = $('pause');
  const resumeB = $('resume');
  const sendB = $('send');
  const copyB = $('copy');
  const box = $('text');
  const statusEl = $('status');
  const statusText = $('statusText');
  const hint = $('hint');

  const API_BASE = 'http://127.0.0.1:5000/api';
  let hintTimeout = null;
  let currentState = 'checking';

  function flash(msg, duration = 3000) {
    if (hintTimeout) clearTimeout(hintTimeout);
    hint.textContent = msg;
    hintTimeout = setTimeout(() => {
      hint.textContent = '';
    }, duration);
  }

  function setState(state) {
    currentState = state;

    statusEl.classList.remove('live', 'transcribing', 'disconnected');

    if (state === 'idle') {
      startB.disabled = false;
      pauseB.disabled = true;
      resumeB.disabled = true;
      sendB.disabled = true;
      statusText.textContent = 'Ready to record';
    } else if (state === 'recording') {
      startB.disabled = true;
      pauseB.disabled = false;
      resumeB.disabled = true;
      sendB.disabled = false;
      statusEl.classList.add('live');
      statusText.textContent = 'Listening & recording...';
    } else if (state === 'paused') {
      startB.disabled = true;
      pauseB.disabled = true;
      resumeB.disabled = false;
      sendB.disabled = false;
      statusText.textContent = 'Paused';
    } else if (state === 'transcribing') {
      startB.disabled = true;
      pauseB.disabled = true;
      resumeB.disabled = true;
      sendB.disabled = true;
      statusEl.classList.add('transcribing');
      statusText.textContent = 'Transcribing with Whisper...';
    } else if (state === 'disconnected') {
      startB.disabled = false; // allow clicking to retry connection
      pauseB.disabled = true;
      resumeB.disabled = true;
      sendB.disabled = true;
      statusEl.classList.add('disconnected');
      statusText.textContent = 'Offline (click to retry)';
    }
  }

  async function apiCall(endpoint, method = 'POST') {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.message || data.error || `HTTP ${res.status}`);
      }

      return data;
    } catch (err) {
      console.warn(`API call failed for ${endpoint}:`, err);
      setState('disconnected');
      flash('Cannot reach server. Run `python server.py`.');
      throw err;
    }
  }

  async function syncStatus() {
    try {
      const data = await apiCall('/status', 'GET');
      if (data && data.status) {
        setState(data.status);
      }
    } catch (_) {
      // Handled in apiCall
    }
  }

  startB.onclick = async function () {
    if (currentState === 'disconnected') {
      flash('Connecting to backend...');
      await syncStatus();
      if (currentState === 'disconnected') return;
    }

    try {
      flash('Starting microphone...');
      const res = await apiCall('/start');
      setState(res.status || 'recording');
      flash('Microphone active. Recording speech...');
    } catch (_) {}
  };

  pauseB.onclick = async function () {
    try {
      const res = await apiCall('/pause');
      setState(res.status || 'paused');
      flash('Recording paused.');
    } catch (_) {}
  };

  resumeB.onclick = async function () {
    try {
      const res = await apiCall('/resume');
      setState(res.status || 'recording');
      flash('Recording resumed.');
    } catch (_) {}
  };

  sendB.onclick = async function () {
    try {
      setState('transcribing');
      flash('Processing audio with Faster-Whisper...');

      const res = await apiCall('/stop');
      setState(res.status || 'idle');

      if (res.text) {
        const currentVal = box.value.trim();
        box.value = currentVal ? `${currentVal}\n\n${res.text}` : res.text;
        flash('Transcribed & saved to storage.');
      } else {
        flash('No speech detected in recording.');
      }
    } catch (err) {
      flash(`Transcription failed: ${err.message || 'Error'}`);
      await syncStatus();
    }
  };

  statusEl.onclick = function () {
    if (currentState === 'disconnected') {
      flash('Reconnecting to server...');
      syncStatus();
    }
  };

  copyB.onclick = function () {
    const text = box.value;
    if (!text) {
      return flash('Nothing to copy yet.');
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        () => flash('Copied to clipboard.'),
        () => fallbackCopy(text)
      );
    } else {
      fallbackCopy(text);
    }
  };

  function fallbackCopy(text) {
    box.select();
    try {
      document.execCommand('copy');
      flash('Copied to clipboard.');
    } catch (_) {
      flash('Failed to copy.');
    }
  }

  // Initial status check on popup open
  syncStatus();
})();