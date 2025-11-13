(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('about-narration');
    const btn = document.getElementById('about-audio-toggle');
    if (!audio || !btn) return;

    // Estado inicial del botón
    function setBtnPlayingUI(playing) {
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.textContent = playing ? '🔇 Pause Narration' : '🔊 Play Narration';
    }

    // Intento de autoplay en silencio (permitido)
    const tryAutoplayMuted = async () => {
      try {
        audio.muted = true;
        await audio.play();
      } catch (_) {}
    };
    tryAutoplayMuted();

    // 🎯 Desmutear automáticamente en la primera interacción del usuario
    const enableSoundOnce = async () => {
      if (!audio) return;
      if (!audio.muted) return; // ya activo

      try {
        audio.muted = false;
        await audio.play();
        setBtnPlayingUI(true);
      } catch (_) {
        // fallback: si algo falla, mantenemos el botón manual
        setBtnPlayingUI(false);
      }

      // quitar el listener tras primera activación
      document.removeEventListener('click', enableSoundOnce);
    };

    // Escucha el primer clic del usuario (en cualquier parte)
    document.addEventListener('click', enableSoundOnce, { once: true });

    // Botón de control manual (play/pause)
    btn.addEventListener('click', async () => {
      if (audio.paused) {
        audio.muted = false;
        await audio.play();
        setBtnPlayingUI(true);
      } else {
        audio.pause();
        setBtnPlayingUI(false);
      }
    });

    // Reflejar estado si se pausa o reanuda
    audio.addEventListener('play', () => setBtnPlayingUI(true));
    audio.addEventListener('pause', () => setBtnPlayingUI(false));

    // Pausar si la pestaña se oculta
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && !audio.paused) audio.pause();
    });
  });
})();
