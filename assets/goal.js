/* Raccolta fondi — Lotto 01.
   PER AGGIORNARE LA CIFRA RACCOLTA: cambia solo il numero "raised" qui sotto,
   poi committa e pubblica. Tutte le pagine (IT/EN/DE, grafico e teaser) si aggiornano da sole. */
window.GOAL_DATA = { raised: 150, goal: 15000 };

(function () {
  var data = window.GOAL_DATA;
  var locale = document.documentElement.lang || 'it';
  function eur(n) { return '€ ' + n.toLocaleString(locale); }
  function pct(r, g) { return Math.min(100, Math.max(r / g * 100, r > 0 ? 1.5 : 0)) + '%'; }
  function animateFill(el, width) {
    if (!el) return;
    function show() { el.style.width = width; }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { setTimeout(show, 150); io.disconnect(); } });
      }, { threshold: 0.3 });
      io.observe(el.parentElement);
    } else { show(); }
  }

  /* Teaser compatto (home) */
  var mini = document.querySelector('[data-goal-mini-label]');
  if (mini) {
    mini.textContent = eur(data.raised) + ' / ' + eur(data.goal);
    var miniFill = document.querySelector('[data-goal-mini-fill]');
    if (miniFill) { miniFill.style.transition = 'width 1.2s ease-out'; miniFill.style.width = '0%'; animateFill(miniFill, pct(data.raised, data.goal)); }
  }

  /* Grafico a tappe (il-progetto) */
  var box = document.querySelector('[data-goal-chart]');
  if (!box) return;
  box.querySelector('[data-goal-raised]').textContent = eur(data.raised);
  box.querySelector('[data-goal-total]').textContent = eur(data.goal);

  var next = null;
  box.querySelectorAll('[data-amount]').forEach(function (li) {
    var amt = parseInt(li.getAttribute('data-amount'), 10);
    var label = li.querySelector('[data-amount-label]');
    if (label) label.textContent = eur(amt);
    var check = li.querySelector('.goal-check');
    var badge = li.querySelector('.goal-next-badge');
    if (data.raised >= amt) {
      li.classList.remove('border-surface-container-highest');
      li.classList.add('border-secondary', 'bg-secondary-container/20');
      if (check) { check.classList.remove('hidden'); check.classList.add('flex'); }
    } else if (!next) {
      next = { amt: amt, label: li.getAttribute('data-label') };
      li.classList.remove('border-surface-container-highest');
      li.classList.add('border-tertiary', 'ring-2', 'ring-tertiary', 'shadow-md');
      if (badge) badge.classList.remove('hidden');
    }
  });

  var nextEl = box.querySelector('[data-goal-next]');
  if (nextEl) {
    if (next) {
      nextEl.innerHTML = '<strong>' + box.getAttribute('data-txt-next') + ':</strong> ' + next.label +
        ' — ' + box.getAttribute('data-txt-missing').replace('%s', '<strong class="text-tertiary whitespace-nowrap">' + eur(next.amt - data.raised) + '</strong>');
    } else {
      nextEl.textContent = box.getAttribute('data-txt-done');
    }
  }

  var fill = box.querySelector('[data-goal-fill]');
  if (fill) { fill.style.transition = 'width 1.2s ease-out'; fill.style.width = '0%'; animateFill(fill, pct(data.raised, data.goal)); }
})();
