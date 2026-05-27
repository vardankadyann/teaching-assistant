#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/public/static"
cp "$ROOT/backend/static/"* "$ROOT/public/static/"
cp "$ROOT/backend/static/index.html" "$ROOT/public/index.html"
echo "Prepared public/ for Vercel."
