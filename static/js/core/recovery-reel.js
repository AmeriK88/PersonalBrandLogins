(function () {
  const reel = document.getElementById('recovery-reel');
  if (!reel) return;

  const frames = Array.from(reel.querySelectorAll('.reel-frame'));
  if (frames.length === 0) return;

  const interval = parseInt(reel.getAttribute('data-interval') || '5500', 10);
  const audioId  = reel.getAttribute('data-sync-audio');
  const audioEl  = audioId ? document.getElementById(audioId) : null;

  let idx = 0;
  let timer = null;
  let playing = true;

  function setActive(next) {
    frames.forEach((img, i) => {
      img.classList.remove('active', 'kenburns', 'kenburns-rev');
      if (i === next) {
        img.classList.add('active', (next % 2 === 0) ? 'kenburns' : 'kenburns-rev');
      }
    });
    idx = next;
  }

  function nextFrame() {
    const n = (idx + 1) % frames.length;
    setActive(n);
  }

  function start() {
    if (timer) return;
    timer = setInterval(nextFrame, interval);
    playing = true;
  }

  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
    playing = false;
  }

  // Inicia con la primera visible
  setActive(0);

  // Autoplay del reel (independiente del audio)
  start();

  // Sincronización básica con audio: pausa/reanuda si el usuario pausa/reproduce
  if (audioEl) {
    audioEl.addEventListener('play', () => start());
    audioEl.addEventListener('pause', () => stop());
    audioEl.addEventListener('ended', () => stop());
  }

  // Pausa al ocultarse (ahorro batería)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop();
    else if (!playing) start();
  });
})();
