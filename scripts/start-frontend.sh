#!/usr/bin/env bash
# Start frontend (Next.js :3001) — run from repo root after npm run build
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export HOSTNAME=0.0.0.0
export PORT=3001
exec npm run start:prod
