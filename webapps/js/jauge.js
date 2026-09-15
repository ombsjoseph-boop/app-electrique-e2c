
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateStats(entry.target);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.4 });

function animateStats(section) {
  const items = section.querySelectorAll('[data-value]');
  const circumference = 283;

  items.forEach(item => {
    const value = +item.dataset.value;
    const max = +item.dataset.max;
    const circle = item.querySelector('.progress');
    const counter = item.querySelector('.counter');
    let current = 0;
    const step = value / 60;

    const interval = setInterval(() => {
      current += step;
      if (current >= value) {
        current = value;
        clearInterval(interval);
      }
      const percent = current / max;
      circle.style.strokeDashoffset = circumference * (1 - percent);
      counter.textContent = Math.round(current) + '+';
    }, 20);
  });
}

document.querySelectorAll('.energy-section').forEach(sec => observer.observe(sec));

