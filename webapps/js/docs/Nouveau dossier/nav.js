// ─── Sticky Header: fond blanc au scroll ───────────────────────────────────
(function () {
  const header = document.getElementById('main-header');
  if (!header) return;

  function onScroll() {
    if (window.scrollY > 10) {
      // Scrollé : fond blanc, texte sombre, ombre légère
      header.style.background = '#ffffff';
      header.style.boxShadow = '0 2px 12px rgba(0,0,0,0.08)';
      header.querySelectorAll('.nav-link').forEach(function (el) {
        el.classList.remove('text-white');
        el.classList.add('text-gray-800');
      });
    } else {
      // En haut : fond transparent, texte blanc
      header.style.background = 'transparent';
      header.style.boxShadow = 'none';
      header.querySelectorAll('.nav-link').forEach(function (el) {
        el.classList.remove('text-gray-800');
        el.classList.add('text-white');
      });
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // applique l'état initial
})();

// ─── Mobile menu toggle ────────────────────────────────────────────────────
(function () {
  const btn = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      menu.classList.toggle('hidden');
    });
  }
})();

// ─── Hero Carousel ────────────────────────────────────────────────────────
(function () {
  const slides = Array.from(document.querySelectorAll('#hero-carousel [data-slide]'));
  const nextBtn = document.getElementById('hero-next');
  const prevBtn = document.getElementById('hero-prev');
  const indicators = Array.from(document.querySelectorAll('#hero-carousel [data-indicator]'));

  if (!slides.length || !nextBtn || !prevBtn) return;

  let idx = 0, timer = null;

  function show(i) {
    slides.forEach(function (s) {
      s.style.opacity = (s.getAttribute('data-slide') == i ? '1' : '0');
    });
    indicators.forEach(function (b, bi) {
      b.style.backgroundColor = (bi === i ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.45)');
    });
  }

  function next() { idx = (idx + 1) % slides.length; show(idx); }
  function prev() { idx = (idx - 1 + slides.length) % slides.length; show(idx); }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(next, 5000);
  }

  nextBtn.addEventListener('click', function () { next(); resetTimer(); });
  prevBtn.addEventListener('click', function () { prev(); resetTimer(); });
  indicators.forEach(function (b, i) {
    b.addEventListener('click', function () { idx = i; show(i); resetTimer(); });
  });

  show(0);
  resetTimer();
})();
