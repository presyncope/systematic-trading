#!/usr/bin/env bash
# Runs the daily sync from the repo root and appends everything to data/logs/daily-sync.log.
# Called by deploy/systemd/daily-sync.service; safe to run by hand: deploy/bin/daily-sync.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
mkdir -p data/logs
{
  echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily-sync start"
  .venv/bin/daily-sync "$@"
  rc=$?
  echo "===== end rc=$rc"
  exit $rc
} >> data/logs/daily-sync.log 2>&1
