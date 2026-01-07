document.addEventListener('DOMContentLoaded', () => {
  // Mobile menu
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    let hamburger = navbar.querySelector('.navbar-hamburger');
    const navItems = navbar.querySelector('.navbar-items');

    if (navItems && hamburger) {
      hamburger.addEventListener('click', () => {
        navItems.classList.toggle('active');
        hamburger.classList.toggle('active');
        document.body.style.overflow = navItems.classList.contains('active') ? 'hidden' : '';
      });

      navItems.querySelectorAll('.navbar-item--link').forEach(link => {
        link.addEventListener('click', () => {
          navItems.classList.remove('active');
          hamburger.classList.remove('active');
          document.body.style.overflow = '';
        });
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
