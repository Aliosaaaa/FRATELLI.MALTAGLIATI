# Ultimi video di Instagram in home

La sezione `#social` della home mostra gli ultimi reel. Ci sono **due modi**
di riempirla: quello a mano (in uso adesso) e quello automatico (pronto,
spento). Il file che comanda tutto è lo stesso, `assets/social.json`, quindi
si può passare dall'uno all'altro senza toccare il sito.

Finché `assets/social.json` non esiste, **la sezione resta invisibile**: il sito
non mostra mai un buco. Si accende da sola al primo aggiornamento riuscito.

---

## 1. A mano, una volta a settimana ← quello in uso

Il profilo Instagram non è un account Business, quindi l'API non è
disponibile. Ma il materiale è già in casa: in `CONSEGNA/PUBBLICAZIONI/` ogni
post ha la sua cartella datata col video e la caption. L'unica cosa che manca
davvero è il **link del post**, che si copia dall'app in due secondi.

**Il rito:**

1. Pubblichi il reel su Instagram.
2. Doppio clic su **`AGGIORNA SOCIAL.command`** (nella cartella del progetto,
   sopra a `repo/`).
3. Ti elenca i post senza link e te li chiede uno per uno. Incolli, Invio.
4. Rispondi `s` a "Pubblico sul sito?". Online in circa un minuto.

Miniatura, didascalia e data vengono da sole:

- la **miniatura** è un fotogramma preso al 35% della durata del reel,
  ritagliato 9:16 (l'inizio è quasi sempre uno stacco o un titolo, non
  l'immagine che racconta). Se non ti piace, aggiungi il secondo che vuoi
  come quarto campo in `tools/social_manuale.txt`;
- la **didascalia** sono le prime righe della caption Instagram del post;
- la **data** viene dal nome della cartella e in home diventa "3 giorni fa".

Serve `ffmpeg` (`brew install ffmpeg`).

Da riga di comando, se preferisci:

```bash
python3 tools/social_manuale.py          # interattivo, chiede i link
python3 tools/social_manuale.py --auto   # rigenera senza chiedere niente
```

Se le pubblicazioni si spostano:
`PUBBLICAZIONI="/nuovo/percorso" python3 tools/social_manuale.py`

---

## 2. In automatico ogni 6 ore — pronto ma spento

Serve che il profilo diventi **Business** (o Creator) e sia collegato alla
Pagina Facebook. Da quel momento `.github/workflows/social.yml` fa da solo
quello che oggi fai a mano, e `AGGIORNA SOCIAL.command` non serve più.

```
Instagram (Graph API)
   ↓  .github/workflows/social.yml  (cron ogni 6h + "Run workflow" a mano)
tools/fetch_instagram.py
   ↓  scarica le miniature in assets/img/social/  +  scrive assets/social.json
   ↓  commit e push
GitHub Pages ripubblica  →  assets/social.js riempie la sezione #social
```

**Come si accende:**

1. Instagram → Impostazioni → Tipo di account → **Business** o **Creator**.
2. Collega il profilo alla **Pagina Facebook**
   (Impostazioni Instagram → Condivisione su altre app → Facebook).
3. Su developers.facebook.com crea un'app **Business** e aggiungi il prodotto
   **Instagram Graph API**.
4. In **Graph API Explorer** chiedi i permessi `instagram_basic`,
   `pages_show_list`, `pages_read_engagement` e genera il token.
5. Portalo a lunga durata (Access Token Debugger → *Extend Access Token*).
6. `GET /me/accounts` → prendi il **token della Pagina**.
   👉 Il token di Pagina derivato da un token utente a lunga durata **non
   scade**: è il motivo per cui si passa da qui invece che dal login
   Instagram diretto, che invece va rinnovato ogni 60 giorni.
7. `GET /{page-id}?fields=instagram_business_account` → l'**ID numerico**
   dell'account Instagram.
8. GitHub → repo → Settings → Secrets and variables → Actions:

| Segreto      | Valore                          |
|--------------|---------------------------------|
| `IG_USER_ID` | l'ID numerico del punto 7       |
| `IG_TOKEN`   | il token di Pagina del punto 6  |

9. Actions → **Sync Instagram** → *Run workflow* per il primo giro.

---

## Perché così e non un widget

Il sito è statico su GitHub Pages con CSP `self`: non può chiamare Instagram
dal browser. I widget di terze parti (Elfsight, Curator e simili) vorrebbero
uno script esterno, cookie e un canone mensile, e rallenterebbero la home.
Qui invece il browser legge **solo file del sito**.

> ⚠️ Le miniature vengono **salvate nel repo**, mai linkate alla CDN di
> Instagram: quegli URL scadono dopo poche ore e la home si riempirebbe di
> riquadri rotti nel giro di mezza giornata. È l'errore classico di questa
> integrazione.

## Manutenzione

- **Quante card**: `QUANTI` in `tools/social_manuale.py` (e `HOW_MANY` in
  `fetch_instagram.py`). Default 6.
- **Cambiare social**: l'unico pezzo da riscrivere è la parte che legge i
  post. Miniature, json e griglia sono identici per YouTube o Facebook.
