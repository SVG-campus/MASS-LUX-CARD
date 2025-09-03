import csv, pathlib, html
from slugify import slugify

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_OWNER = "SVG-campus"
REPO_NAME  = "MASS-LUX-CARD"
BRANCH     = "main"

renders = sorted((ROOT/"data"/"renders").rglob("*.png"))
outdir   = ROOT/"artifacts"; outdir.mkdir(parents=True, exist_ok=True)
csv_path = outdir/"shopify_products.csv"
urls_txt = outdir/"image_urls.txt"

header = [
  "Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
  "Option1 Name","Option1 Value","Variant Price","Image Src","Image Alt Text","Image Position"
]

def raw_url(rel_path:str)->str:
    return f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{rel_path}"

rows, url_lines = [], []
for img in renders:
    rel = img.relative_to(ROOT).as_posix()
    parts = img.parts
    family = parts[-3] if len(parts)>=3 else "General"
    subcat = parts[-2] if len(parts)>=2 else "Card"
    title  = f"{subcat} – {family} – Luxury Flat Card"
    handle = slugify(f"{subcat}-{family}-{img.stem}")[:80]
    body = f"""
<p><strong>Mass Lux Card</strong> — ultra-luxury flat card on 100% cotton paper (matte), no raised elements for a clean, archival finish.</p>
<ul>
  <li>Category: {html.escape(family)} — {html.escape(subcat)}</li>
  <li>Set size: 50 cards</li>
  <li>Printing partners: Czar Press or Smythson (UK), with Smartpress as backup</li>
  <li>Studio photograph: top-down, straight for easy crop (1:1)</li>
</ul>
""".strip()
    url = raw_url(rel)
    rows.append([handle, title, body, "Mass Lux Card", "Luxury Card",
                 f"{family}, {subcat}, flat-card, cotton, luxe", "TRUE",
                 "Set","50 Cards","500.00", url, f"{title} product image","1"])
    url_lines.append(url)

with open(csv_path,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(header); w.writerows(rows)
with open(urls_txt,"w",encoding="utf-8") as f:
    f.write("\n".join(url_lines))

print(f"Wrote {csv_path} and {urls_txt}")
