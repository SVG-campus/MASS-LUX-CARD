#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export PROJECT_ID="${PROJECT_ID:-learning-470300}"
export REGION="${REGION:-us-central1}"
export RENDERS_BUCKET="${RENDERS_BUCKET:-gs://masslux-renders-$PROJECT_ID}"
export MLC_VARIATIONS="${MLC_VARIATIONS:-60}"
export IMAGES_PER_PROMPT="${IMAGES_PER_PROMPT:-1}"

mkdir -p logs data/prompts data/renders artifacts config scripts bin

# ensure bucket exists
if ! gcloud storage buckets describe "${RENDERS_BUCKET}" >/dev/null 2>&1; then
  gcloud storage buckets create "${RENDERS_BUCKET}" --location="${REGION}" || true
fi

source .venv/bin/activate

echo "[1/4] Generating prompts…"
python scripts/generate_prompts.py

echo "[2/4] Rendering via Imagen 4 Ultra…"
python scripts/generate_images_vertex.py

echo "[3/4] Building Shopify CSV + image URL list…"
python scripts/make_shopify_csv.py

echo "[4/4] Auto-pushing to GitHub…"
bin/git_autopush.sh

echo "All done."
