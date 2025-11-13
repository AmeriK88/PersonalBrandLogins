document.addEventListener("DOMContentLoaded", () => {
  const animatedEls = document.querySelectorAll(
    ".fade-up, .fade-in, .slide-left, .slide-right"
  );

  // Delay natural, por si la carga es instantánea
  setTimeout(() => {
    animatedEls.forEach((el, i) => {
      // Pequeño escalonado automático si no tiene delay
      if (![...el.classList].some(cls => cls.startsWith("delay-"))) {
        el.style.transitionDelay = `${i * 0.15}s`;
      }
      el.classList.add("animate-in");
    });
  }, 100);
});
