#!/usr/bin/env python3
"""
Sincronizza gli ultimi video/reel di Instagram dentro il repo.

Come funziona (e perche' cosi'):
  Il sito e' statico su GitHub Pages con CSP 'self': non puo' chiamare
  API esterne dal browser, e i widget di terze parti costerebbero
  velocita', cookie e canone. Quindi ci pensa una GitHub Action:
  interroga la Graph API, SCARICA LE MINIATURE DENTRO IL REPO e scrive
  assets/social.json. Il sito legge solo file suoi.

  ⚠️ Le miniature vanno scaricate, non linkate: gli URL della CDN di
  Instagram scadono dopo poche ore e la home si riempirebbe di riquadri
  rotti. E' l'errore classico di questa integrazione.

Segreti richiesti (GitHub → Settings → Secrets and variables → Actions):
  IG_USER_ID  id numerico dell'account Instagram Business
  IG_TOKEN    token di accesso (vedi tools/README_SOCIAL.md)
"""
import json, os, pathlib, re, sys, urllib.parse, urllib.request

API = "https://graph.facebook.com/v21.0"
ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "assets" / "img" / "social"
JSON_OUT = ROOT / "assets" / "social.json"

HOW_MANY = 6          # quante card in home
FETCH = 25            # quanti post leggere per trovarne 6 con video
THUMB_W = 540         # larghezza miniatura salvata (card ~270px @2x)


def api_get(path, **params):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def fetch_media(user_id, token):
    fields = "id,caption,media_type,media_product_type,media_url,permalink,thumbnail_url,timestamp"
    data = api_get(user_id, fields=f"media.limit({FETCH}){{{fields}}}", access_token=token)
    return data.get("media", {}).get("data", [])


def pick(items):
    """Prima i video/reel. Se non bastano, completa con le foto:
    meglio una griglia piena di post veri che tre buchi."""
    videos = [m for m in items if m.get("media_type") == "VIDEO"]
    others = [m for m in items if m.get("media_type") != "VIDEO"]
    return (videos + others)[:HOW_MANY]


def caption_short(txt, limit=110):
    if not txt:
        return ""
    txt = re.sub(r"#\S+", "", txt)                 # via gli hashtag: in home fanno rumore
    txt = re.sub(r"\s+", " ", txt).strip(" ·-–—")
    if len(txt) <= limit:
        return txt
    return txt[:limit].rsplit(" ", 1)[0] + "…"


def save_thumb(url, dest):
    with urllib.request.urlopen(url, timeout=60) as r:
        raw = r.read()
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width > THUMB_W:
            im = im.resize((THUMB_W, round(im.height * THUMB_W / im.width)), Image.LANCZOS)
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=False)
    except ImportError:                             # senza Pillow salva l'originale
        dest.write_bytes(raw)


def main():
    user_id = os.environ.get("IG_USER_ID", "").strip()
    token = os.environ.get("IG_TOKEN", "").strip()
    if not user_id or not token:
        print("IG_USER_ID / IG_TOKEN mancanti: niente da fare.", file=sys.stderr)
        return 1

    media = pick(fetch_media(user_id, token))
    if not media:
        print("Nessun post restituito dall'API: lascio il sito com'e'.", file=sys.stderr)
        return 1

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    items, keep = [], set()

    for m in media:
        src = m.get("thumbnail_url") or m.get("media_url")
        if not src:
            continue
        name = f"{m['id']}.jpg"
        dest = IMG_DIR / name
        if not dest.exists():
            try:
                save_thumb(src, dest)
            except Exception as e:
                print(f"miniatura non scaricata per {m['id']}: {e}", file=sys.stderr)
                continue
        keep.add(name)
        items.append({
            "id": m["id"],
            "permalink": m.get("permalink", ""),
            "caption": caption_short(m.get("caption")),
            "timestamp": m.get("timestamp", ""),
            "video": m.get("media_type") == "VIDEO",
            "thumb": f"assets/img/social/{name}",
        })

    if not items:
        print("Nessuna miniatura utilizzabile: lascio il sito com'e'.", file=sys.stderr)
        return 1

    # ripulisce le miniature dei post usciti dalla griglia
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()

    JSON_OUT.write_text(
        json.dumps({"profile": "https://www.instagram.com/salviamoicastagni/", "items": items},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} post scritti in assets/social.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
