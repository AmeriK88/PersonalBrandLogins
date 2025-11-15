(function () {
  const reel = document.getElementById('recovery-reel');
  if (!reel) return;

  const frames = Array.from(reel.querySelectorAll('.reel-frame'));
  if (frames.length === 0) return;

  // Duraciones diferenciadas (ms)
  const imageDuration = parseInt(reel.getAttribute('data-image-interval') || '4600', 10);
  const videoDuration = parseInt(reel.getAttribute('data-video-interval') || '5600', 10);

  const audioId = reel.getAttribute('data-sync-audio');
  const audioEl = audioId ? document.getElementById(audioId) : null;

  let idx = 0;
  let timer = null;
  let playing = true;

  function isVideo(el) {
    return el.tagName.toLowerCase() === 'video';
  }

  function resetFrame(frame) {
    frame.classList.remove('active', 'kenburns', 'kenburns-rev');

    if (isVideo(frame)) {
      try {
        frame.pause();
        frame.currentTime = 0;
      } catch (e) {
        // nada
      }
    }
  }

  // ---- 🔓 DESBLOQUEO iOS ----
  let iosUnlocked = !/iPhone|iPad|iPod/i.test(navigator.userAgent);
  // En no-iOS: true (funciona como antes)
  // En iOS: false hasta que el usuario toque algo

  function unlockVideosOnce() {
    if (iosUnlocked) return;
    iosUnlocked = true;

    // “Primar” TODOS los vídeos con el primer gesto
    frames.forEach((frame) => {
      if (!isVideo(frame)) return;

      frame.muted = true;
      frame.setAttribute('muted', '');
      frame.playsInline = true;
      frame.setAttribute('playsinline', '');
      frame.setAttribute('webkit-playsinline', '');

      try {
        frame.play()
          .then(() => {
            // Los pausamos al momento: solo queremos que iOS “confíe”
            frame.pause();
            frame.currentTime = 0;
          })
          .catch(() => {});
      } catch (e) {}
    });
  }

  // Primer tap/click en la página = desbloquea video
  document.addEventListener('touchstart', unlockVideosOnce, { once: true });
  document.addEventListener('click', unlockVideosOnce, { once: true });

  // Si el usuario pulsa el botón de narración, también desbloquea
  const narrationBtn = document.getElementById('about-audio-toggle');
  if (narrationBtn) {
    narrationBtn.addEventListener('click', unlockVideosOnce, { once: true });
  }
  // ---- fin desbloqueo iOS ----

  function activateFrame(frame, index) {
    frame.classList.add('active');

    if (isVideo(frame)) {
      // Aseguramos flags de iOS
      frame.muted = true;
      frame.setAttribute('muted', '');
      frame.playsInline = true;
      frame.setAttribute('playsinline', '');
      frame.setAttribute('webkit-playsinline', '');

      // Solo intentamos play si ya está desbloqueado
      if (iosUnlocked) {
        frame.play().catch(() => {});
      }
    } else {
      // Imagen: efecto Ken Burns alternando direcciones
      frame.classList.add((index % 2 === 0) ? 'kenburns' : 'kenburns-rev');
    }
  }

  function setActive(next) {
    frames.forEach((frame, i) => {
      resetFrame(frame);
      if (i === next) {
        activateFrame(frame, i);
      }
    });
    idx = next;
  }

  function scheduleNext() {
    if (!playing) return;

    const current = frames[idx];
    const isVid = isVideo(current);
    const dur = isVid ? videoDuration : imageDuration;

    timer = setTimeout(() => {
      const n = (idx + 1) % frames.length;
      setActive(n);
      scheduleNext();
    }, dur);
  }

  function start() {
    if (playing) return;
    playing = true;
    scheduleNext();
  }

  function stop() {
    playing = false;
    if (timer) clearTimeout(timer);
    timer = null;

    // Pausar vídeos cuando paramos el reel
    frames.forEach(frame => {
      if (isVideo(frame)) {
        try { frame.pause(); } catch (e) {}
      }
    });
  }

  // Inicia con la primera visible
  setActive(0);
  scheduleNext(); // comenzamos la secuencia

  // Sincronización básica con audio: pausa/reanuda si el usuario pausa/reproduce
  if (audioEl) {
    audioEl.addEventListener('play', () => {
      if (!playing) {
        start();
      }
    });
    audioEl.addEventListener('pause', () => {
      stop();
    });
    audioEl.addEventListener('ended', () => {
      stop();
    });
  }

  // Pausa al ocultarse (ahorro batería)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stop();
    } else if (!playing) {
      start();
    }
  });
})();
(function () {
  const reel = document.getElementById('recovery-reel');
  if (!reel) return;

  const frames = Array.from(reel.querySelectorAll('.reel-frame'));
  if (frames.length === 0) return;

  // Duraciones diferenciadas (ms)
  const imageDuration = parseInt(reel.getAttribute('data-image-interval') || '4600', 10);
  const videoDuration = parseInt(reel.getAttribute('data-video-interval') || '5600', 10);

  const audioId = reel.getAttribute('data-sync-audio');
  const audioEl = audioId ? document.getElementById(audioId) : null;

  let idx = 0;
  let timer = null;
  let playing = true;

  function isVideo(el) {
    return el.tagName.toLowerCase() === 'video';
  }

  function resetFrame(frame) {
    frame.classList.remove('active', 'kenburns', 'kenburns-rev');

    if (isVideo(frame)) {
      try {
        frame.pause();
        frame.currentTime = 0;
      } catch (e) {
        // nada
      }
    }
  }

  // ---- 🔓 DESBLOQUEO iOS ----
  let iosUnlocked = !/iPhone|iPad|iPod/i.test(navigator.userAgent);
  // En no-iOS: true (funciona como antes)
  // En iOS: false hasta que el usuario toque algo

  function unlockVideosOnce() {
    if (iosUnlocked) return;
    iosUnlocked = true;

    // “Primar” TODOS los vídeos con el primer gesto
    frames.forEach((frame) => {
      if (!isVideo(frame)) return;

      frame.muted = true;
      frame.setAttribute('muted', '');
      frame.playsInline = true;
      frame.setAttribute('playsinline', '');
      frame.setAttribute('webkit-playsinline', '');

      try {
        frame.play()
          .then(() => {
            // Los pausamos al momento: solo queremos que iOS “confíe”
            frame.pause();
            frame.currentTime = 0;
          })
          .catch(() => {});
      } catch (e) {}
    });
  }

  // Primer tap/click en la página = desbloquea video
  document.addEventListener('touchstart', unlockVideosOnce, { once: true });
  document.addEventListener('click', unlockVideosOnce, { once: true });

  // Si el usuario pulsa el botón de narración, también desbloquea
  const narrationBtn = document.getElementById('about-audio-toggle');
  if (narrationBtn) {
    narrationBtn.addEventListener('click', unlockVideosOnce, { once: true });
  }
  // ---- fin desbloqueo iOS ----

  function activateFrame(frame, index) {
    frame.classList.add('active');

    if (isVideo(frame)) {
      // Aseguramos flags de iOS
      frame.muted = true;
      frame.setAttribute('muted', '');
      frame.playsInline = true;
      frame.setAttribute('playsinline', '');
      frame.setAttribute('webkit-playsinline', '');

      // Solo intentamos play si ya está desbloqueado
      if (iosUnlocked) {
        frame.play().catch(() => {});
      }
    } else {
      // Imagen: efecto Ken Burns alternando direcciones
      frame.classList.add((index % 2 === 0) ? 'kenburns' : 'kenburns-rev');
    }
  }

  function setActive(next) {
    frames.forEach((frame, i) => {
      resetFrame(frame);
      if (i === next) {
        activateFrame(frame, i);
      }
    });
    idx = next;
  }

  function scheduleNext() {
    if (!playing) return;

    const current = frames[idx];
    const isVid = isVideo(current);
    const dur = isVid ? videoDuration : imageDuration;

    timer = setTimeout(() => {
      const n = (idx + 1) % frames.length;
      setActive(n);
      scheduleNext();
    }, dur);
  }

  function start() {
    if (playing) return;
    playing = true;
    scheduleNext();
  }

  function stop() {
    playing = false;
    if (timer) clearTimeout(timer);
    timer = null;

    // Pausar vídeos cuando paramos el reel
    frames.forEach(frame => {
      if (isVideo(frame)) {
        try { frame.pause(); } catch (e) {}
      }
    });
  }

  // Inicia con la primera visible
  setActive(0);
  scheduleNext(); // comenzamos la secuencia

  // Sincronización básica con audio: pausa/reanuda si el usuario pausa/reproduce
  if (audioEl) {
    audioEl.addEventListener('play', () => {
      if (!playing) {
        start();
      }
    });
    audioEl.addEventListener('pause', () => {
      stop();
    });
    audioEl.addEventListener('ended', () => {
      stop();
    });
  }

  // Pausa al ocultarse (ahorro batería)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stop();
    } else if (!playing) {
      start();
    }
  });
})();
