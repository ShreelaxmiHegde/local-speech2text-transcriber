
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var startB = $('start'), pauseB = $('pause'), resumeB = $('resume'), sendB = $('send');
  var box = $('text'), hint = $('hint'), status = $('status'), statusText = $('statusText');
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var rec = null, running = false, base = '';

  function setState(state) {
    startB.disabled = state !== 'idle';
    pauseB.disabled = state !== 'recording';
    resumeB.disabled = state !== 'paused';
    sendB.disabled = state === 'idle' && !box.value.trim();
    status.classList.toggle('live', state === 'recording');
    statusText.textContent = { idle: 'Ready to record', recording: 'Listening…', paused: 'Paused' }[state];
  }
  function flash(msg) { hint.textContent = msg; setTimeout(function () { hint.textContent = ''; }, 2000); }

  function begin() {
    if (!SR) { flash('Speech recognition is not supported in this browser.'); return false; }
    rec = new SR();
    rec.continuous = true; rec.interimResults = true; rec.lang = 'en-US';
    rec.onresult = function (e) {
      var t = '';
      for (var i = 0; i < e.results.length; i++) t += e.results[i][0].transcript;
      box.value = (base + ' ' + t).trim();
    };
    rec.onerror = function (e) { flash('Microphone error: ' + e.error); setState('idle'); running = false; };
    rec.onend = function () { if (running) { try { rec.start(); } catch (_) { } } };
    try { rec.start(); } catch (_) { return false; }
    running = true; return true;
  }
  function halt() { running = false; if (rec) rec.stop(); }

  startB.onclick = function () { base = box.value; if (begin()) setState('recording'); };
  pauseB.onclick = function () { halt(); setState('paused'); };
  resumeB.onclick = function () { base = box.value; if (begin()) setState('recording'); };
  sendB.onclick = function () { halt(); setState('idle'); flash(box.value.trim() ? 'Recording sent.' : 'Nothing to send yet.'); };
  box.oninput = function () { if (startB.disabled === false) setState('idle'); };
  $('copy').onclick = function () {
    var v = box.value; if (!v) return flash('Nothing to copy yet.');
    (navigator.clipboard ? navigator.clipboard.writeText(v) : Promise.reject()).then(
      function () { flash('Copied.'); },
      function () { box.select(); document.execCommand('copy'); flash('Copied.'); });
  };
  setState('idle');
})();