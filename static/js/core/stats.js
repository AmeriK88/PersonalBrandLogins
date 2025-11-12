document.addEventListener('DOMContentLoaded', function () {
    const counters = document.querySelectorAll('.about-stat-number');
    if (!counters.length) return;

    function animateCounters() {
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.target, 10);
            if (isNaN(target)) return;

            const duration = 1200; // ms
            const startTime = performance.now();

            function update(now) {
                const progress = Math.min((now - startTime) / duration, 1);
                const value = Math.floor(progress * target);
                counter.textContent = value.toLocaleString();
                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            }

            requestAnimationFrame(update);
        });
    }

    const statsSection = document.querySelector('.about-stats');
    if (!statsSection) return;

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.disconnect();
                }
            });
        }, { threshold: 0.4 });

        observer.observe(statsSection);
    } else {
        // Fallback si el navegador es viejo
        animateCounters();
    }
});
