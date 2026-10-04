#!/bin/bash
set -euo pipefail

echo "==> Pulling latest code..."
git pull origin main

echo "==> Rebuilding and restarting container..."
sudo docker compose up -d --build

echo "==> Done. Container status:"
sudo docker compose ps
