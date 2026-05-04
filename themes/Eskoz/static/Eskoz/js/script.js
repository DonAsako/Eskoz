document.addEventListener('DOMContentLoaded', () => {
  // Mobile menu
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const hamburger = navbar.querySelector('.navbar-hamburger');
    const menu = navbar.querySelector('.navbar-menu');

    if (menu && hamburger) {
      const close = () => {
        menu.classList.remove('active');
        hamburger.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
      };
      hamburger.addEventListener('click', () => {
        const open = menu.classList.toggle('active');
        hamburger.classList.toggle('active', open);
        hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      menu.querySelectorAll('.navbar-item--link').forEach(link => {
        link.addEventListener('click', close);
      });
      document.addEventListener('click', e => {
        if (menu.classList.contains('active') && !navbar.contains(e.target)) close();
      });
    }
  }

  // Mark as read
  const markReadBtn = document.querySelector('.mark-read-btn');
  if (markReadBtn) {
    const slug = markReadBtn.dataset.lesson;
    if (slug) {
      const readLessons = JSON.parse(localStorage.getItem('readLessons') || '[]');
      if (readLessons.includes(slug)) {
        markReadBtn.classList.add('read');
        markReadBtn.innerHTML = '✓ Read';
      }

      markReadBtn.addEventListener('click', () => {
        let lessons = JSON.parse(localStorage.getItem('readLessons') || '[]');
        if (lessons.includes(slug)) {
          lessons = lessons.filter(s => s !== slug);
          markReadBtn.classList.remove('read');
          markReadBtn.innerHTML = '○ Mark as read';
        } else {
          lessons.push(slug);
          markReadBtn.classList.add('read');
          markReadBtn.innerHTML = '✓ Read';
        }
        localStorage.setItem('readLessons', JSON.stringify(lessons));
      });
    }
  }

  // Theme toggle: flip data-theme + swap which highlight.js stylesheet is enabled
  function applyHighlightTheme(mode) {
    document.querySelectorAll('link[data-hljs-theme]').forEach(link => {
      link.disabled = link.dataset.hljsTheme !== mode;
    });
  }
  applyHighlightTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
  document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      if (next === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      applyHighlightTheme(next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  });

  // Close <details> category-picker on outside click
  document.querySelectorAll('.category-picker').forEach(picker => {
    document.addEventListener('click', e => {
      if (picker.open && !picker.contains(e.target)) picker.open = false;
    });
  });

  // Lesson list badges
  const lessonCards = document.querySelectorAll('.article_card[data-lesson]');
  if (lessonCards.length) {
    const readLessons = JSON.parse(localStorage.getItem('readLessons') || '[]');
    let count = 0;

    lessonCards.forEach(card => {
      if (readLessons.includes(card.dataset.lesson)) {
        count++;
        const topLeft = card.querySelector('.article_card--top-left');
        if (topLeft && !card.querySelector('.lesson-read-badge')) {
          const badge = document.createElement('span');
          badge.className = 'lesson-read-badge';
          badge.textContent = '✓';
          topLeft.appendChild(badge);
        }
      }
    });

    const counter = document.querySelector('.lesson-progress-counter');
    if (counter) {
      counter.textContent = `${count}/${lessonCards.length}`;
    }
  }
});
