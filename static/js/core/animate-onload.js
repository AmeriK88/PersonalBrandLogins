// static/js/core/animate-onload.js
document.addEventListener("DOMContentLoaded", () => {
  const targets = document.querySelectorAll(
    ".fade-up, .fade-in, .slide-left, .slide-right"
  );

  if (!targets.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Si el usuario no quiere animaciones → mostrar todo sin efectos
  if (reduceMotion) {
    targets.forEach((el) => {
      el.classList.add("animate-in");
    });
    return;
  }

  // Animate on load con pequeño stagger automático
  const baseDelay = 0.12; // segundos

  setTimeout(() => {
    targets.forEach((el, i) => {
      const hasManualDelay = Array.from(el.classList).some((cls) =>
        cls.startsWith("delay-")
      );

      // Si NO tiene delay-*, aplicamos stagger usando la CSS var --stagger
      if (!hasManualDelay) {
        el.style.setProperty("--stagger", `${i * baseDelay}s`);
      }

      el.classList.add("animate-in");
    });
  }, 80);
});
