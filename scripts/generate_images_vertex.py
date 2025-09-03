import os, json, base64, pathlib, subprocess
from datetime import datetime
from tqdm import tqdm
import requests

BASE = pathlib.Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE / "data" / "prompts"
RENDERS_DIR = BASE / "data" / "renders"
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

PROJECT = os.environ.get("PROJECT_ID","learning-470300")
REGION  = os.environ.get("REGION","us-central1")
MODEL   = os.environ.get("IMAGEN_MODEL","imagen-4.0-ultra-generate-001")
IMAGE_PER_PROMPT = int(os.environ.get("IMAGES_PER_PROMPT","1"))
RENDERS_BUCKET = os.environ.get("RENDERS_BUCKET")

ENDPOINT = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{REGION}/publishers/google/models/{MODEL}:predict"

def access_token():
    return subprocess.check_output(["gcloud","auth","print-access-token"], text=True).strip()

def render_one(prompt_text, family, subcat, idx):
    body = {
        "instances": [ { "prompt": prompt_text } ],
        "parameters": { "sampleCount": IMAGE_PER_PROMPT, "aspectRatio": "1:1" }
    }
    headers = {"Authorization": f"Bearer {access_token()}", "Content-Type":"application/json"}
    r = requests.post(ENDPOINT, headers=headers, json=body, timeout=300)
    r.raise_for_status()
    data = r.json()
    outs=[]
    for i,p in enumerate(data.get("predictions",[]),1):
        b64 = p.get("bytesBase64Encoded")
        if not b64: continue
        raw = base64.b64decode(b64)
        subdir = RENDERS_DIR / family / subcat
        subdir.mkdir(parents=True, exist_ok=True)
        fname = f"{subcat}-{idx:04d}-{i}.png"
        path  = subdir / fname
        open(path,"wb").write(raw)
        outs.append(str(path))
    return outs

def upload_to_gcs(local_path, bucket_uri):
    subprocess.check_call(["gcloud","storage","cp", local_path, bucket_uri])

def main():
    if not list(PROMPTS_DIR.glob("*.jsonl")):
        print("No prompts found. Run generate_prompts.py first."); return
    count=0
    for jf in sorted(PROMPTS_DIR.glob("*.jsonl")):
        lines = list(open(jf,"r",encoding="utf-8"))
        for i,line in enumerate(tqdm(lines, desc=jf.name),1):
            rec = json.loads(line)
            family = rec["family"].replace("/","-")
            subcat = rec["subcategory"].replace("/","-")
            outs = render_one(rec["prompt"], family, subcat, i)
            count += len(outs)
            if RENDERS_BUCKET:
                for op in outs:
                    dest = f"{RENDERS_BUCKET}/{family}/{subcat}/"
                    upload_to_gcs(op, dest)
    print(f"Saved {count} images.")

if __name__=="__main__":
    main()
