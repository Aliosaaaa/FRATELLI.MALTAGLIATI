/* Griglia "ultimi video dai social".
   Legge assets/social.json, scritto ogni 6 ore dalla GitHub Action
   (tools/fetch_instagram.py). Nessuna chiamata a Instagram dal browser:
   miniature e dati sono file del sito, quindi CSP 'self' intatta,
   zero cookie di terze parti e nessun rallentamento. */
(function () {
  var wrap = document.querySelector('[data-social]');
  if (!wrap) return;

  var grid = wrap.querySelector('[data-social-grid]');
  var src = wrap.getAttribute('data-social');   // percorso del json (cambia in /en e /de)
  var base = wrap.getAttribute('data-social-base') || '';
  var lang = (document.documentElement.lang || 'it').slice(0, 2);

  var AGO = {
    it: { today: 'oggi', d: 'giorni fa', w: 'settimane fa', mo: 'mesi fa' },
    en: { today: 'today', d: 'days ago', w: 'weeks ago', mo: 'months ago' },
    de: { today: 'heute', d: 'Tage her', w: 'Wochen her', mo: 'Monate her' }
  }[lang] || { today: 'oggi', d: 'giorni fa', w: 'settimane fa', mo: 'mesi fa' };

  function ago(iso) {
    if (!iso) return '';
    var days = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000);
    if (days <= 0) return AGO.today;
    if (days < 14) return days + ' ' + AGO.d;
    if (days < 60) return Math.round(days / 7) + ' ' + AGO.w;
    return Math.round(days / 30) + ' ' + AGO.mo;
  }

  /* Didascalie e link arrivano da Instagram: si scrivono come testo, mai come HTML. */
  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var PLAY = '<span class="sc-play" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>';

  fetch(src, { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.items || !data.items.length) return;   // resta nascosta

      grid.innerHTML = data.items.map(function (it) {
        var href = /^https:\/\/(www\.)?instagram\.com\//.test(it.permalink || '') ? it.permalink : '';
        return '<a class="sc-card" href="' + esc(href) + '" target="_blank" rel="noopener">' +
                 '<span class="sc-thumb">' +
                   '<img src="' + esc(base + it.thumb) + '" alt="" loading="lazy" decoding="async" width="540" height="960">' +
                   (it.video ? PLAY : '') +
                   '<span class="sc-date">' + esc(ago(it.timestamp)) + '</span>' +
                 '</span>' +
                 (it.caption ? '<span class="sc-cap">' + esc(it.caption) + '</span>' : '') +
               '</a>';
      }).join('');

      if (data.profile) {
        var link = wrap.querySelector('[data-social-profile]');
        if (link) link.setAttribute('href', data.profile);
      }
      wrap.hidden = false;
    })
    .catch(function () { /* json assente o rotto: la sezione resta invisibile */ });
})();
