/* Fascia alta — secondo "battito" del bottone a meta' pagina.
   Un banner sempre uguale sparisce dalla percezione dopo pochi secondi:
   quando il visitatore ha letto meta' pagina la CTA si ri-annuncia una volta sola. */
(function () {
  var bar = document.querySelector('.cst-topbar');
  if (!bar) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var done = false;
  function onScroll() {
    if (done) return;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (h <= 0) return;
    if (window.scrollY / h < 0.5) return;
    done = true;
    window.removeEventListener('scroll', onScroll);
    bar.classList.remove('cst-pulse');
    void bar.offsetWidth;          /* forza il riavvio dell'animazione */
    bar.classList.add('cst-pulse');
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  /* primo battito, subito dopo che la fascia e' scesa */
  setTimeout(function () { bar.classList.add('cst-pulse'); }, 950);
})();
