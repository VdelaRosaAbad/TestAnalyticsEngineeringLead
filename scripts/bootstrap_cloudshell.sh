#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "If needed, run: gcloud auth application-default login"

