
(function () {
    const slides = Array.from(document.querySelectorAll('#hero-carousel [data-slide]'));
    const nextBtn = document.getElementById('hero-next');

    (function () {
        const slides = Array.from(document.querySelectorAll('#hero-carousel [data-slide]'));
        const nextBtn = document.getElementById('hero-next');
        const prevBtn = document.getElementById('hero-prev');
        const indicators = Array.from(document.querySelectorAll('#hero-carousel [data-indicator]'));
        let idx = 0, timer = null;
        function show(i) {
            slides.forEach(s => s.style.opacity = (s.getAttribute('data-slide') == i ? '1' : '0'));
            indicators.forEach((b, bi) => b.style.backgroundColor = (bi == i ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.45)'));
        }
        function next() { idx = (idx + 1) % slides.length; show(idx); }
        function prev() { idx = (idx - 1 + slides.length) % slides.length; show(idx); }
        nextBtn.addEventListener('click', () => { next(); resetTimer(); });
        prevBtn.addEventListener('click', () => { prev(); resetTimer(); });
        indicators.forEach((b, i) => b.addEventListener('click', () => { idx = i; show(i); resetTimer(); }));
        function resetTimer() { clearInterval(timer); timer = setInterval(next, 5000); }
        // init
        show(0); resetTimer();
    })();

    })();
