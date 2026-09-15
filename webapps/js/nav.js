// ─── Sticky Header: fond blanc au scroll ───────────────────────────────────
(function () {
  const header = document.getElementById('main-header');
  if (!header) return;

  function onScroll() {
    if (window.scrollY > 10) {
      header.style.background = '#ffffff';
      header.style.boxShadow = '0 2px 12px rgba(0,0,0,0.08)';
      header.querySelectorAll('.nav-link').forEach(function (el) {
        el.classList.remove('text-white');
        el.classList.add('text-gray-800');
      });
    } else {
      header.style.background = 'transparent';
      header.style.boxShadow = 'none';
      header.querySelectorAll('.nav-link').forEach(function (el) {
        el.classList.remove('text-gray-800');
        el.classList.add('text-white');
      });
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
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

// ─── Hero Carousel (chaque slide a son propre contenu) ────────────────────
(function () {
  const slides     = Array.from(document.querySelectorAll('.hero-slide'));
  const indicators = Array.from(document.querySelectorAll('#hero-carousel [data-indicator]'));
  const nextBtn    = document.getElementById('hero-next');
  const prevBtn    = document.getElementById('hero-prev');
  const slideNum   = document.getElementById('hero-slide-num');

  if (!slides.length || !nextBtn || !prevBtn) return;

  let idx = 0;
  let timer = null;

  function show(i) {
    slides.forEach(function (s, si) {
      s.style.opacity = (si === i) ? '1' : '0';
      s.style.pointerEvents = (si === i) ? 'auto' : 'none';
    });

    indicators.forEach(function (b, bi) {
      if (bi === i) {
        b.style.backgroundColor = 'rgba(250,204,21,1)';
        b.style.width = '2rem';
      } else {
        b.style.backgroundColor = 'rgba(255,255,255,0.4)';
        b.style.width = '1rem';
      }
    });

    if (slideNum) slideNum.textContent = String(i + 1).padStart(2, '0');

    // Relance animation du contenu
    const activeContent = slides[i].querySelector('.slide-content');
    if (activeContent) {
      activeContent.style.animation = 'none';
      activeContent.offsetHeight;
      activeContent.style.animation = 'heroFadeUp 0.6s ease forwards';
    }

    idx = i;
  }

  function next() { show((idx + 1) % slides.length); }
  function prev() { show((idx - 1 + slides.length) % slides.length); }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(next, 5500);
  }

  nextBtn.addEventListener('click', function () { next(); resetTimer(); });
  prevBtn.addEventListener('click', function () { prev(); resetTimer(); });
  indicators.forEach(function (b, i) {
    b.addEventListener('click', function () { show(i); resetTimer(); });
  });

  show(0);
  resetTimer();
})();
