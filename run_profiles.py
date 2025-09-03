import unicodedata, re, os, yaml, sys
from pathlib import Path
from linkedin_scraper.cli import run_search

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    import re as _re
    s = _re.sub(r"[^a-zA-Z0-9]+","-", s.strip().lower())
    return _re.sub(r"-{2,}","-", s).strip("-")

def main():
    base_dir = Path(__file__).resolve().parent
    profiles_path = base_dir / "profiles.yaml"
    out_dir = base_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not profiles_path.exists():
        print(f"❌ Fichier introuvable : {profiles_path}")
        print("Créez un profiles.yaml comme ceci :\n"
              "profiles:\n"
              "  - job: \"Développeur Java\"\n"
              "    location: \"Paris\"\n"
              "    pages: 1\n"
              "    past_hours: 24\n")
        sys.exit(1)

    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print("❌ Erreur en lisant profiles.yaml:", e, file=sys.stderr)
        sys.exit(1)

    if not cfg or "profiles" not in cfg or not isinstance(cfg["profiles"], list):
        print("❌ profiles.yaml invalide : clé 'profiles' manquante ou mauvaise forme.", file=sys.stderr)
        sys.exit(1)

    for p in cfg["profiles"]:
        job = p.get("job"); loc = p.get("location")
        pages = str(p.get("pages", 1))
        past = str(p.get("past_hours", 24))
        if not job or not loc:
            print("⚠️ Profil ignoré (job/location manquants) :", p); continue

        csv = out_dir / f"jobs_{slugify(job)}_{slugify(loc)}.csv"
        print("▶", f"{job} @ {loc} pages={pages} past_hours={past}")
        try:
            rc = run_search(job=job, location=loc, pages=int(pages), past_hours=int(past), csv_path=str(csv))
        except Exception as e:
            print("❌ Error:", e, file=sys.stderr)
        else:
            if rc == 0:
                print("✅ Done")
            else:
                print("⚠️ Finished with non-zero code", rc)

if __name__ == "__main__":
    main()
