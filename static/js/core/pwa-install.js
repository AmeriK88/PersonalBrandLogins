document.addEventListener('DOMContentLoaded', () => {
  const banner = document.getElementById('pwa-install-banner');
  const installBtn = document.getElementById('pwa-install-btn');
  const closeBtn = document.getElementById('pwa-install-close');
  const hintEl = document.getElementById('pwa-install-hint');

  if (!banner || !installBtn || !closeBtn) {
    return; // por si en alguna plantilla no están
  }

  let deferredPrompt = null;

  // Detectar iOS
  const isIos = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;

  // 1) Flujo especial para iOS (no hay beforeinstallprompt)
  if (isIos && !isStandalone) {
    banner.classList.remove('d-none');
    if (hintEl) {
      hintEl.textContent =
        "On iOS, tap the share button and select 'Add to Home Screen'.";
    }
  }

  // 2) Flujo estándar Chrome/Chromium (beforeinstallprompt)
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    // Si no estamos ya mostrando el banner por iOS:
    if (banner.classList.contains('d-none')) {
      banner.classList.remove('d-none');
    }
  });

  installBtn.addEventListener('click', async () => {
    // Si estamos en un navegador sin beforeinstallprompt
    if (!deferredPrompt) {
      if (isIos) {
        alert("On iOS, use the share button and choose 'Add to Home Screen'.");
      } else {
        alert("Use your browser menu to 'Add to Home Screen' or install the app.");
      }
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log('User choice:', outcome);
    deferredPrompt = null;
    banner.classList.add('d-none');
  });

  closeBtn.addEventListener('click', () => {
    banner.classList.add('d-none');
  });
});
