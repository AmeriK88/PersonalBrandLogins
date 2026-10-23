(function () {
  const PLAY_LABEL = '\uD83D\uDD0A Play Narration';
  const PAUSE_LABEL = '\uD83D\uDD07 Pause Narration';

  function initializeAudio() {
    const audio = document.getElementById('about-narration');
    const btn = document.getElementById('about-audio-toggle');
    if (!audio || !btn) return;
    if (audio.dataset.initialized === 'true') return;
    audio.dataset.initialized = 'true';

    function setBtnPlayingUI(playing) {
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.setAttribute('aria-label', playing ? 'Pause narration' : 'Play narration');
      btn.textContent = playing ? PAUSE_LABEL : PLAY_LABEL;
    }

    // Manual playback only: audible play() must run synchronously inside this
    // trusted click handler (iOS Safari rejects it otherwise).
    btn.addEventListener('click', () => {
      if (audio.paused || audio.ended) {
        audio.muted = false;
        try {
          const playback = audio.play();
          if (playback && typeof playback.catch === 'function') {
            playback.catch(() => setBtnPlayingUI(false));
          }
        } catch (_) {
          setBtnPlayingUI(false);
        }
      } else {
        audio.pause();
      }
    });

    // The button always mirrors the real playback state.
    audio.addEventListener('playing', () => setBtnPlayingUI(true));
    audio.addEventListener('play', () => setBtnPlayingUI(true));
    audio.addEventListener('pause', () => setBtnPlayingUI(false));
    audio.addEventListener('ended', () => setBtnPlayingUI(false));
    audio.addEventListener('error', () => setBtnPlayingUI(false));

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