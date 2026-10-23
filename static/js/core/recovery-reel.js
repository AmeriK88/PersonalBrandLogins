(function () {
  function initializeReel() {
    const reel = document.getElementById('recovery-reel');
    if (!reel || reel.dataset.initialized === 'true') return;

    const frames = Array.from(reel.querySelectorAll('.reel-frame'));
    if (frames.length === 0) return;
    reel.dataset.initialized = 'true';

    const readDuration = (name, fallback) => {
      const value = Number.parseInt(reel.getAttribute(name), 10);
      return Number.isFinite(value) && value > 0 ? value : fallback;
    };
    const imageDuration = readDuration('data-image-interval', 4600);
    const videoDuration = readDuration('data-video-interval', 5600);
    const audioId = reel.getAttribute('data-sync-audio');
    const audio = audioId ? document.getElementById(audioId) : null;

    let index = 0;
    let timer = null;
    let playing = true;
    let iosUnlocked = !/iPhone|iPad|iPod/i.test(navigator.userAgent);

    function isVideo(frame) {
      return frame.tagName.toLowerCase() === 'video';
    }

    function resetFrame(frame) {
      frame.classList.remove('active', 'kenburns', 'kenburns-rev');
      if (!isVideo(frame)) return;

      try {
        frame.pause();
        frame.currentTime = 0;
      } catch (_) {}
    }

    function unlockVideosOnce() {
      if (iosUnlocked) return;
      iosUnlocked = true;

      frames.forEach((frame) => {
        if (!isVideo(frame)) return;
        frame.muted = true;
        frame.playsInline = true;
        frame.setAttribute('muted', '');
        frame.setAttribute('playsinline', '');
        frame.setAttribute('webkit-playsinline', '');

        try {
          const playback = frame.play();
          if (playback && typeof playback.then === 'function') {
            playback.then(() => {
              frame.pause();
              frame.currentTime = 0;
            }).catch(() => {});
          }
        } catch (_) {}
      });
    }

    function activateFrame(frame, frameIndex) {
      frame.classList.add('active');
      if (!isVideo(frame)) {
        frame.classList.add(frameIndex % 2 === 0 ? 'kenburns' : 'kenburns-rev');
        return;
      }

      frame.muted = true;
      frame.playsInline = true;
      frame.setAttribute('muted', '');
      frame.setAttribute('playsinline', '');
      frame.setAttribute('webkit-playsinline', '');
      if (iosUnlocked) {
        try {
          const playback = frame.play();
          if (playback && typeof playback.catch === 'function') playback.catch(() => {});
        } catch (_) {}
      }
    }

    function setActive(next) {
      frames.forEach((frame) => resetFrame(frame));
      index = next;
      activateFrame(frames[index], index);
    }

    function scheduleNext() {
      if (!playing) return;
      const duration = isVideo(frames[index]) ? videoDuration : imageDuration;
      timer = window.setTimeout(() => {
        timer = null;
        setActive((index + 1) % frames.length);
        scheduleNext();
      }, duration);
    }

    function advanceAfterVideoError(event) {
      if (event.currentTarget !== frames[index] || !playing) return;
      if (timer !== null) window.clearTimeout(timer);
      timer = null;
      setActive((index + 1) % frames.length);
      scheduleNext();
    }

    function start() {
      if (playing) return;
      playing = true;
      activateFrame(frames[index], index);
      scheduleNext();
    }

    function stop() {
      playing = false;
      if (timer !== null) window.clearTimeout(timer);
      timer = null;
      frames.forEach((frame) => {
        if (isVideo(frame)) frame.pause();
      });
    }

    frames.forEach((frame) => {
      if (isVideo(frame)) frame.addEventListener('error', advanceAfterVideoError);
    });
    const narrationButton = document.getElementById('about-audio-toggle');
    // Never run video unlocking during a narration-button interaction.
    const unlockFromGesture = (event) => {
      if (narrationButton && event.target instanceof Node && narrationButton.contains(event.target)) return;
      document.removeEventListener('touchstart', unlockFromGesture);
      document.removeEventListener('click', unlockFromGesture);
      unlockVideosOnce();
    };
    document.addEventListener('touchstart', unlockFromGesture);
    document.addEventListener('click', unlockFromGesture);

    setActive(0);
    scheduleNext();

    if (audio) {
      audio.addEventListener('play', start);
      audio.addEventListener('pause', stop);
      audio.addEventListener('ended', stop);
    }

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop();
      else start();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeReel, { once: true });
  } else {
    initializeReel();
  }
})();