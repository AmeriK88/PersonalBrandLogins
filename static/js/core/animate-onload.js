document.addEventListener("DOMContentLoaded", () => {
  const targets = document.querySelectorAll(
    ".fade-up, .fade-in, .slide-left, .slide-right"
  );

  if (!targets.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion) {
    targets.forEach((el) => {
      el.classList.add("animate-in");
    });
    return;
  }

  // Animate on load stagger
  const baseDelay = 0.12;

  setTimeout(() => {
    targets.forEach((el, i) => {
      const hasManualDelay = Array.from(el.classList).some((cls) =>
        cls.startsWith("delay-")
      );

      // If NO delay-*, apply stagger using CSS var --stagger
      if (!hasManualDelay) {
        el.style.setProperty("--stagger", `${i * baseDelay}s`);
      }

      el.classList.add("animate-in");
    });
  }, 80);
});
