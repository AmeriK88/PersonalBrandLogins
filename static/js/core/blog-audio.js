(function () {
  function initializeAudio() {
    const audio = document.getElementById('about-narration');
    const btn = document.getElementById('about-audio-toggle');
    if (!audio || !btn) return;
    if (audio.dataset.initialized === 'true') return;
    audio.dataset.initialized = 'true';

    // Initial btn state
    function setBtnPlayingUI(playing) {
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.textContent = playing ? '🔇 Pause Narration' : '🔊 Play Narration';
    }

    // Silence autoplay (permitido)
    const tryAutoplayMuted = async () => {
      try {
        audio.muted = true;
        await audio.play();
      } catch (_) {}
    };
    tryAutoplayMuted();

    // Unmute at 1st interaction
    const enableSoundOnce = async () => {
      if (!audio) return;
      if (!audio.muted) return;

      try {
        audio.muted = false;
        await audio.play();
        setBtnPlayingUI(true);
      } catch (_) {
        // fallback
        setBtnPlayingUI(false);
      }

      // Remove listener
      document.removeEventListener('click', enableSoundOnce);
    };

    // Click listener
    document.addEventListener('click', enableSoundOnce, { once: true });

    // Play/pause btn
    btn.addEventListener('click', async () => {
      if (audio.paused) {
        audio.muted = false;
        try {
          await audio.play();
          setBtnPlayingUI(true);
        } catch (_) {
          setBtnPlayingUI(false);
        }
      } else {
        audio.pause();
        setBtnPlayingUI(false);
      }
    });

    // Reflect state
    audio.addEventListener('play', () => setBtnPlayingUI(true));
    audio.addEventListener('pause', () => setBtnPlayingUI(false));

    // Pause if minimize/hidden
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && !audio.paused) audio.pause();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAudio, { once: true });
  } else {
    initializeAudio();
  }
})();
