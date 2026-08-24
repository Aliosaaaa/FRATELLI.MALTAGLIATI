# Ultimi video di Instagram in home — come si accende

Il sito è statico su GitHub Pages con CSP `self`: non può chiamare Instagram
dal browser. Quindi il flusso è al contrario — è una GitHub Action che ogni
6 ore va a prendere i post e li **scrive dentro il repo**:

```
Instagram (Graph API)
   ↓  .github/workflows/social.yml  (cron ogni 6h + "Run workflow" a mano)
tools/fetch_instagram.py
   ↓  scarica le miniature in assets/img/social/  +  scrive assets/social.json
   ↓  commit e push
GitHub Pages ripubblica  →  assets/social.js riempie la sezione #social della home
```

Finché `assets/social.json` non esiste, **la sezione resta invisibile**: il sito
non mostra mai un buco. Si accende da sola al primo giro riuscito.

> ⚠️ Le miniature vengono **scaricate**, non linkate. Gli URL della CDN di
> Instagram scadono dopo poche ore: linkarli direttamente riempirebbe la home
> di riquadri rotti nel giro di mezza giornata. È l'errore classico.

---

## Cosa serve (una volta sola)

**Prerequisiti sull'account:**

1. Il profilo Instagram `@salviamoicastagni` deve essere **Business** o
   **Creator** (Impostazioni → Tipo di account).
2. Deve essere **collegato alla Pagina Facebook** dei fratelli
   (Impostazioni Instagram → Condivisione su altre app → Facebook).

**Poi, su developers.facebook.com:**

3. Crea un'app di tipo **Business**.
4. Aggiungi il prodotto **Instagram Graph API**.
5. In **Graph API Explorer**: seleziona l'app, chiedi i permessi
   `instagram_basic`, `pages_show_list`, `pages_read_engagement`, genera il token.
6. Passa il token a **lunga durata** (Access Token Debugger → *Extend Access Token*).
7. Con quel token chiama `GET /me/accounts` → prendi il **token della Pagina**.
   👉 Il token di Pagina derivato da un token utente a lunga durata **non scade**:
   è il motivo per cui questa strada è preferibile al login diretto Instagram,
   che invece scade ogni 60 giorni e va rinnovato.
8. Chiama `GET /{page-id}?fields=instagram_business_account` → ottieni l'**ID
   numerico dell'account Instagram**.

**Infine, su GitHub** → repo → Settings → Secrets and variables → Actions →
*New repository secret*:

| Segreto      | Valore                                   |
|--------------|------------------------------------------|
| `IG_USER_ID` | l'ID numerico del punto 8                |
| `IG_TOKEN`   | il token di Pagina del punto 7           |

Poi Actions → **Sync Instagram** → *Run workflow* per il primo giro.

---

## Prova in locale

```bash
IG_USER_ID=xxx IG_TOKEN=yyy python3 tools/fetch_instagram.py
```

## Manutenzione

- **Quanti post**: `HOW_MANY` in `tools/fetch_instagram.py` (default 6).
- **Ogni quanto**: il `cron` in `.github/workflows/social.yml`.
- **Il token smette di funzionare** (cambio password, app rimossa, permessi
  revocati): la Action fallisce ma **il sito non cambia** — restano visibili
  gli ultimi post scaricati. Si rifà il giro dal punto 5.
- **Cambiare social**: l'unico pezzo da riscrivere è `fetch_media()`. Il resto
  della catena (miniature, json, griglia) è identico per YouTube o Facebook.
