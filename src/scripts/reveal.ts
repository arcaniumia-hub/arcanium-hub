// Subtle reveal-on-scroll. Content is fully visible without JS (see global.css).
const items = document.querySelectorAll<HTMLElement>('[data-reveal]');
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!('IntersectionObserver' in window) || reduce) {
  items.forEach((el) => el.classList.add('is-visible'));
} else {
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
  );
  items.forEach((el) => io.observe(el));
}

// Mobile menu (<details>): close on Escape and when a link is chosen.
const menu = document.querySelector<HTMLDetailsElement>('[data-mobile-menu]');
if (menu) {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.open) {
      menu.open = false;
      menu.querySelector('summary')?.focus();
    }
  });
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => (menu.open = false)));
}
