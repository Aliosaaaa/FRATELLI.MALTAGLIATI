#!/usr/bin/env python3
"""
Aggiorna a mano la griglia "ultimi video" della home — una volta a settimana.

Perche' esiste: il profilo Instagram non e' Business, quindi la Graph API
(e la GitHub Action che la usa) non e' disponibile. Ma il materiale ce l'abbiamo
gia' in casa: in CONSEGNA/PUBBLICAZIONI/ ogni post ha la sua cartella datata
col video e la caption. Quindi l'unica cosa che manca davvero e' il LINK
del post su Instagram, che si copia dall'app in due secondi.

Rito settimanale:
  1. pubblichi il reel su Instagram
  2. doppio clic su "AGGIORNA SOCIAL.command"
  3. incolli il link quando te lo chiede
  4. rispondi "s" a "pubblico?"

Tutto il resto (miniatura estratta dal video, didascalia, data) viene da solo.
Se un giorno il profilo diventa Business, si accende .github/workflows/social.yml
e questo script non serve piu': il formato di assets/social.json e' identico.
"""
import json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTA = ROOT / "tools" / "social_manuale.txt"
IMG_DIR = ROOT / "assets" / "img" / "social"
JSON_OUT = ROOT / "assets" / "social.json"
PROFILO = "https://www.instagram.com/salviamoicastagni/"

PUBBLICAZIONI = pathlib.Path(os.environ.get("PUBBLICAZIONI") or (
    pathlib.Path.home() / "Desktop" / "PROGETTI CLAUDE" / "AGENZIA MARKETING" /
    "clienti" / "salviamo-castagni" / "CONSEGNA" / "PUBBLICAZIONI"))

QUANTI = 6          # card in home
THUMB_W, THUMB_H = 540, 960
DATA_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})_")


# ---------------------------------------------------------------- lettura dati

def cartelle_recenti():
    """Le cartelle-post piu' recenti, dalla piu' nuova.

    ⚠️ Salta quelle con data FUTURA: il materiale si prepara in anticipo, ma
    un post non ancora uscito su Instagram non puo' finire in home — il link
    non porterebbe da nessuna parte e la data direbbe "oggi"."""
    if not PUBBLICAZIONI.is_dir():
        print(f"⚠️  Non trovo la cartella delle pubblicazioni:\n   {PUBBLICAZIONI}")
        print("   Se l'hai spostata, lancia con:  PUBBLICAZIONI='/nuovo/percorso' ...")
        return []
    import datetime
    oggi = datetime.date.today().isoformat()
    dirs, futuri = [], []
    for d in PUBBLICAZIONI.iterdir():
        if not (d.is_dir() and DATA_RE.match(d.name)):
            continue
        (futuri if d.name[:10] > oggi else dirs).append(d)
    if futuri:
        print(f"ℹ️  {len(futuri)} post con data futura, non ancora usciti: li salto "
              f"({', '.join(sorted(f.name for f in futuri))})")
    return sorted(dirs, key=lambda d: d.name, reverse=True)


def media_di(cartella):
    """Il video del post; se manca, la prima foto per le storie."""
    for v in sorted(cartella.glob("1_VIDEO*.mp4")):
        return v, True
    for v in sorted(cartella.glob("*.mp4")):
        return v, True
    foto = sorted((cartella / "2_FOTO_per_storie").glob("*.jpg")) if (cartella / "2_FOTO_per_storie").is_dir() else []
    if foto:
        return foto[0], False
    return None, False


def didascalia_proposta(cartella, limite=110):
    """Prende le prime righe vere della caption Instagram del post."""
    for md in sorted(cartella.glob("CAPTION*.md")):
        testo = md.read_text(encoding="utf-8", errors="ignore")
        # il corpo del post sta sotto il titolo della sezione Instagram
        m = re.search(r"^##\s*\d*\.?\s*Instagram.*$", testo, re.M | re.I)
        corpo = testo[m.end():] if m else testo
        righe = []
        for r in corpo.splitlines():
            r = r.strip()
            if not r or r.startswith(("#", "---", "**", ">", "\\#")):
                continue
            righe.append(r)
            if sum(len(x) for x in righe) > limite:
                break
        if righe:
            t = re.sub(r"\s+", " ", " ".join(righe)).strip()
            t = re.sub(r"[«»\"]", "", t)
            if len(t) > limite:
                t = t[:limite].rsplit(" ", 1)[0] + "…"
            return t
    return ""


def data_iso(nome):
    m = DATA_RE.match(nome)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T12:00:00+0000" if m else ""


# ------------------------------------------------------------------- miniature

def miniatura(sorgente, dest, video, secondo=None):
    """Un fotogramma dal video (o la foto), ritagliato 9:16 a 540x960.

    Il frame di default si prende al 35% della durata: l'inizio del reel
    e' quasi sempre una stacco o un titolo, non l'immagine che racconta."""
    if not video:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(sorgente)]
    else:
        if secondo is None:
            try:
                out = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(sorgente)], capture_output=True, text=True, check=True)
                secondo = max(0.5, float(out.stdout.strip()) * 0.35)
            except Exception:
                secondo = 2.0
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{secondo:.2f}", "-i", str(sorgente), "-frames:v", "1"]

    vf = (f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=increase,"
          f"crop={THUMB_W}:{THUMB_H}")
    cmd += ["-vf", vf, "-q:v", "4", str(dest)]
    subprocess.run(cmd, check=True, capture_output=True)


# ----------------------------------------------------------------- lista posts

def leggi_lista():
    """cartella | link | didascalia | [secondo del fotogramma]"""
    voci = {}
    if not LISTA.exists():
        return voci
    for riga in LISTA.read_text(encoding="utf-8").splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("#"):
            continue
        p = [x.strip() for x in riga.split("|")]
        if len(p) < 2 or not p[1]:
            continue
        voci[p[0]] = {
            "link": p[1],
            "testo": p[2] if len(p) > 2 else "",
            "secondo": float(p[3]) if len(p) > 3 and p[3] else None,
        }
    return voci


def scrivi_lista(voci):
    righe = [
        "# Ultimi post pubblicati su Instagram — li legge tools/social_manuale.py.",
        "# Una riga per post:  cartella | link instagram | didascalia | [secondo del fotogramma]",
        "# Il 4o campo e' facoltativo: mettilo solo se la miniatura scelta non ti piace",
        "# (es. ...| 8.5  prende il fotogramma all'8,5o secondo).",
        "",
    ]
    for nome in sorted(voci, reverse=True):
        v = voci[nome]
        sec = f" | {v['secondo']}" if v.get("secondo") else ""
        righe.append(f"{nome} | {v['link']} | {v['testo']}{sec}")
    LISTA.write_text("\n".join(righe) + "\n", encoding="utf-8")


# ------------------------------------------------------------------------ main

def main():
    interattivo = sys.stdin.isatty() and "--auto" not in sys.argv
    voci = leggi_lista()
    cartelle = cartelle_recenti()
    if not cartelle:
        return 1

    if interattivo:
        mancanti = [d for d in cartelle[:QUANTI + 4] if d.name not in voci]
        if mancanti:
            print(f"\n🌰 Ci sono {len(mancanti)} post senza il link di Instagram.")
            print("   Incolla il link del post (o premi Invio per saltarlo).\n")
        for d in mancanti:
            proposta = didascalia_proposta(d)
            print(f"── {d.name}")
            if proposta:
                print(f"   didascalia: {proposta}")
            link = input("   link Instagram: ").strip()
            if not link:
                print("   saltato.\n")
                continue
            if "instagram.com" not in link:
                print("   ⚠️  non sembra un link di Instagram, lo salto.\n")
                continue
            nuovo = input("   didascalia (Invio per tenere quella sopra): ").strip()
            voci[d.name] = {"link": link.split("?")[0], "testo": nuovo or proposta, "secondo": None}
            print()
        scrivi_lista(voci)

    # --- costruisce la griglia
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    items, tieni = [], set()

    for d in cartelle:
        if len(items) >= QUANTI:
            break
        v = voci.get(d.name)
        if not v:
            if "--fallback-profilo" not in sys.argv:
                continue
            # ripiego: la card porta al profilo. Meglio una sezione viva con un
            # click in piu' che una sezione invisibile. Il post resta comunque
            # nell'elenco dei "senza link", quindi al prossimo giro lo richiede.
            v = {"link": PROFILO, "testo": "", "secondo": None}
        # didascalia lasciata vuota nel file: la ricava dalla caption del post
        if not v.get("testo"):
            v["testo"] = didascalia_proposta(d)
        sorgente, is_video = media_di(d)
        if not sorgente:
            print(f"⚠️  {d.name}: nessun video o foto, salto.")
            continue
        nome = re.sub(r"[^a-zA-Z0-9_-]", "", d.name) + ".jpg"
        dest = IMG_DIR / nome
        firma = IMG_DIR / (nome + ".src")
        marca = f"{sorgente}|{v.get('secondo')}"
        if not dest.exists() or not firma.exists() or firma.read_text(encoding="utf-8") != marca:
            try:
                miniatura(sorgente, dest, is_video, v.get("secondo"))
                firma.write_text(marca, encoding="utf-8")
            except Exception as e:
                print(f"⚠️  {d.name}: miniatura non riuscita ({e}), salto.")
                continue
        tieni |= {nome, nome + ".src"}
        items.append({
            "id": d.name,
            "permalink": v["link"],
            "caption": v["testo"],
            "timestamp": data_iso(d.name),
            "video": is_video,
            "thumb": f"assets/img/social/{nome}",
        })

    if not items:
        print("\n⚠️  Nessun post con link: la sezione resta nascosta.")
        print(f"   Aggiungi i link in {LISTA.relative_to(ROOT)} e rilancia.")
        return 1

    for f in IMG_DIR.iterdir():
        if f.name not in tieni and f.name != ".gitkeep":
            f.unlink()

    JSON_OUT.write_text(json.dumps({"profile": PROFILO, "items": items},
                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n✅ {len(items)} video pronti per la home:")
    for it in items:
        print(f"   · {it['id']}  —  {it['caption'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
