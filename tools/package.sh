#!/usr/bin/env bash
# Rebuild dist/paradigma.zip (the upload for Claude apps) from skills/paradigma.
set -euo pipefail
cd "$(dirname "$0")/../skills"
mkdir -p ../dist && rm -f ../dist/paradigma.zip
zip -rq ../dist/paradigma.zip paradigma -x '*/__pycache__/*' '*.pyc'
echo "wrote dist/paradigma.zip"
