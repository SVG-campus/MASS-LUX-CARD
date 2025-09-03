import os, json, random, time, pathlib, yaml
from slugify import slugify

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
CATS_YAML = BASE_DIR / "config" / "categories.yaml"
OUT_DIR   = BASE_DIR / "data" / "prompts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

APPEND_DIRECTIVE = (
    "flat card on the most luxurious cotton paper, matte finish, "
    "no embossing, no debossing, no foil, no raised or protruding elements; "
    "top-down front view, perfectly straight for easy crop, soft studio light, 1:1"
)

PALETTES = ["white on white", "ivory & ecru", "eggshell & gold ink", "dove gray", "midnight on bone"]
MOTIFS   = ["subtle floral vignette", "minimal border", "regal filigree drawn flat", "tone-on-tone pattern", "blank luxe field"]
TYPE_STYLES = ["engraved-look flat ink", "elegant serif typography", "modern small caps", "script headline with small-caps body"]

HEADINGS = {
  "Thank You":"Thank You",
  "Condolence":"With Deepest Sympathy",
  "Save the Date":"Save the Date",
  "Wedding Invitation Suite":"Together with their families",
  "Baby Shower":"Baby Shower",
  "Birth Announcement":"Welcome to the World",
  "Anniversary (1, 5, 10, 25, 50+)":"Happy Anniversary",
  "Graduation & Academic":"Congratulations Graduate",
  "Corporate Holiday Cards":"Season’s Greetings",
}

def load_rows():
    with open(CATS_YAML, "r", encoding="utf-8") as f:
        fams = yaml.safe_load(f)["families"]
    rows=[]
    for fam, subs in fams.items():
        for sub in subs:
            rows.append((fam, sub))
    return rows

def make_variations(family, sub, n):
    out=[]
    heading = HEADINGS.get(sub, HEADINGS.get(family, sub))
    for _ in range(n):
        palette = random.choice(PALETTES)
        motif   = random.choice(MOTIFS)
        type_   = random.choice(TYPE_STYLES)
        phrase  = f'Luxury {sub} card with {motif}, {palette}, {type_}, {APPEND_DIRECTIVE}.'
        prompt  = f'"{heading}"; {phrase}'
        out.append({
            "family": family,
            "subcategory": sub,
            "title": f"{sub} – {palette} – {motif} – {type_}",
            "prompt": prompt
        })
    return out

def main():
    n = int(os.environ.get("MLC_VARIATIONS","30"))
    total=0
    for fam, sub in load_rows():
        slug = slugify(f"{fam}-{sub}")
        fpath = OUT_DIR / f"{slug}.jsonl"
        items = make_variations(fam, sub, n)
        with open(fpath,"w",encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False)+"\n")
        print(f"[OK] {sub} → {fpath} ({len(items)})"); total += len(items)
    print(f"Finished {total} prompts.")

if __name__=="__main__":
    main()
