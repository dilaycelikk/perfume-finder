// Intersection Observer for scroll animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = 'running';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.anim-fade-up').forEach(el => {
  el.style.animationPlayState = 'paused';
  observer.observe(el);
});

// Nav scroll effect
const nav = document.querySelector('nav');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.scrollY;
  if (currentScroll > 80) {
    nav.style.padding = '1rem 2.5rem';
  } else {
    nav.style.padding = '1.5rem 2.5rem';
  }
  lastScroll = currentScroll;
}, { passive: true });
