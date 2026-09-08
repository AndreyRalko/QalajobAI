#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env.production.local && ! -f .env.production ]]; then
  echo "Create .env.production.local from .env.production.example first"
  echo "NEXT_PUBLIC_API_URL must point to your API before build"
fi

if [[ ! -d node_modules ]]; then
  npm install
fi

if [[ ! -d .next ]]; then
  npm run build
fi

export HOSTNAME="${HOSTNAME:-0.0.0.0}"
export PORT="${PORT:-3001}"
exec npm run start:prod
