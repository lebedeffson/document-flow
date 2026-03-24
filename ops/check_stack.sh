#!/usr/bin/env bash
set -euo pipefail

echo "[check] containers"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "[check] gateway http -> https redirect"
curl -I --max-time 10 http://localhost:18090 || true

echo
echo "[check] gateway health"
curl -k --max-time 10 https://localhost:18443/healthz || true

echo
echo "[check] middleware health through gateway"
curl -k --max-time 10 https://localhost:18443/bridge/health || true

echo
echo "[check] onlyoffice health through gateway"
curl -k --max-time 10 https://localhost:18443/office/healthcheck || true
