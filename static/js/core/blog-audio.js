(function () {
  const PLAY_LABEL = '\uD83D\uDD0A Play Narration';
  const PAUSE_LABEL = '\uD83D\uDD07 Pause Narration';
  const MEDIA_ERRORS = ['', 'aborted', 'network', 'decode', 'src_not_supported'];

  function initializeAudio() {
    const audio = document.getElementById('about-narration');
    const btn = document.getElementById('about-audio-toggle');
    if (!audio || !btn) return;
    if (audio.dataset.initialized === 'true') return;
    audio.dataset.initialized = 'true';

    // Opt-in diagnostics: append ?narration_debug=1 to the article URL. Shows the
    // native audio controls plus a status line; ordinary visitors never see it.
    let debugLine = null;
    let debugEnabled = false;
    try {
      debugEnabled = new URLSearchParams(window.location.search).get('narration_debug') === '1';
    } catch (_) {}

    function describe() {
      const sw = window.navigator && window.navigator.serviceWorker;
      return [
        'src=' + (audio.currentSrc || '(none)'),
        'readyState=' + audio.readyState,
        'networkState=' + audio.networkState,
        'paused=' + audio.paused,
        'muted=' + audio.muted,
        'error=' + (audio.error ? MEDIA_ERRORS[audio.error.code] || audio.error.code : 'none'),
        'swControlled=' + Boolean(sw && sw.controller),
      ].join(' | ');
    }

    function report(label, detail) {
      if (debugLine) debugLine.textContent = label + (detail ? ' (' + detail + ')' : '') + ' :: ' + describe();
      if (debugEnabled) console.info('[narration]', label, detail || '', describe());
    }

    if (debugEnabled && document.createElement) {
      audio.controls = true;
      audio.preload = 'metadata';
      audio.style.display = 'block';
      audio.style.width = '100%';
      debugLine = document.createElement('p');
      debugLine.className = 'small text-muted mt-2';
      debugLine.setAttribute('role', 'status');
      if (btn.parentNode && btn.parentNode.insertBefore) {
        btn.parentNode.insertBefore(audio, btn.nextSibling);
        btn.parentNode.insertBefore(debugLine, audio.nextSibling);
      }
      report('debug ready');
    }

    function setBtnPlayingUI(playing) {
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.setAttribute('aria-label', playing ? 'Pause narration' : 'Play narration');
      btn.textContent = playing ? PAUSE_LABEL : PLAY_LABEL;
    }

    function failed(kind, detail) {
      setBtnPlayingUI(false);
      btn.dataset.narrationError = kind;
      console.warn('[narration] playback failed:', kind, detail || '');
      report('failed: ' + kind, detail);
    }

    // Manual playback only: audible play() must run synchronously inside this
    // trusted click handler (iOS Safari rejects it otherwise).
    btn.addEventListener('click', () => {
      if (audio.paused || audio.ended) {
        audio.muted = false;
        delete btn.dataset.narrationError;
        try {
          const playback = audio.play();
          if (playback && typeof playback.catch === 'function') {
            playback.catch((err) => failed('play-rejected', err && err.name));
          }
        } catch (err) {
          failed('play-threw', err && err.name);
        }
      } else {
        audio.pause();
      }
    });

    // The button always mirrors the real playback state.
    audio.addEventListener('playing', () => { setBtnPlayingUI(true); report('playing'); });
    audio.addEventListener('play', () => setBtnPlayingUI(true));
    audio.addEventListener('pause', () => { setBtnPlayingUI(false); report('pause'); });
    audio.addEventListener('ended', () => { setBtnPlayingUI(false); report('ended'); });
    // A failing <source> fires "error" on the source, which does not bubble: capture it.
    audio.addEventListener('error', () => failed('media-error'), true);
    ['stalled', 'waiting', 'loadedmetadata'].forEach((name) => {
      audio.addEventListener(name, () => report(name));
    });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden && !audio.paused) audio.pause();
    });

    setBtnPlayingUI(!audio.paused);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAudio, { once: true });
  } else {
    initializeAudio();
  }
})();