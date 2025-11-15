(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const nativeBtn = document.querySelector('.js-share-native');
    const copyBtn   = document.querySelector('.js-share-copy');

    // ---- Web Share API (móvil, algunos navegadores de escritorio) ----
    if (nativeBtn && navigator.share) {
      nativeBtn.addEventListener('click', function () {
        const url   = this.dataset.url || window.location.href;
        const title = this.dataset.title || document.title;

        navigator.share({
          title: title,
          url: url
        }).catch(function (err) {
          // El usuario puede cancelar, no pasa nada
          console.debug('Share cancelled or failed:', err);
        });
      });
    } else if (nativeBtn) {
      // Si no hay Web Share API, ocultamos el botón nativo para no liar
      nativeBtn.style.display = 'none';
    }

    // ---- Copiar enlace al portapapeles ----
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        const url = this.dataset.url || window.location.href;

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url)
            .then(function () {
              alert('Link copied to clipboard ✅');
            })
            .catch(function () {
              alert('Could not copy the link. Please copy it manually.');
            });
        } else {
          // Fallback muy básico
          const tempInput = document.createElement('input');
          tempInput.value = url;
          document.body.appendChild(tempInput);
          tempInput.select();
          try {
            document.execCommand('copy');
            alert('Link copied to clipboard ✅');
          } catch (e) {
            alert('Could not copy the link. Please copy it manually.');
          }
          document.body.removeChild(tempInput);
        }
      });
    }
  });
})();
