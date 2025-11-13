document.addEventListener('DOMContentLoaded', () => {
  const targets = document.querySelectorAll('.fade-up, .fade-in, .slide-left, .slide-right');

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) {
    targets.forEach(el => el.classList.add('animate-in'));
    return;
  }

  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  if (isMobile) {
    targets.forEach(el => el.classList.add('animate-in'));
    return;
  }

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        const el = entry.target;
        const hasManualDelay = Array.from(el.classList).some(cls => cls.startsWith('delay-'));

        if (!hasManualDelay) {
          const siblings = Array.from(el.parentElement?.children || []);
          const index = Math.max(0, siblings.indexOf(el));
          el.style.setProperty('--stagger', `${index * 0.12}s`);
        }

        el.classList.add('animate-in');
        io.unobserve(el);
      });
    }, { threshold: 0.01 });

    targets.forEach(el => io.observe(el));
  } else {
    setTimeout(() => {
      targets.forEach((el, i) => {
        const hasManualDelay = Array.from(el.classList).some(cls => cls.startsWith('delay-'));
        if (!hasManualDelay) el.style.setProperty('--stagger', `${i * 0.12}s`);
        el.classList.add('animate-in');
      });
    }, 100);
  }
});
