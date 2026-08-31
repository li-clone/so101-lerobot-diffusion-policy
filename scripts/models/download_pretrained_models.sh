#!/usr/bin/env bash
set -euo pipefail

: "${REMOTE_HOST:?Set REMOTE_HOST, for example user@training-host}"
: "${REMOTE_OUTPUT:?Set REMOTE_OUTPUT to the remote training output directory}"

REMOTE_PORT="${REMOTE_PORT:-22}"
LOCAL_MODEL_ROOT="${LOCAL_MODEL_ROOT:-$PWD/outputs/diffusion_compare_models}"
CHECKPOINTS="${CHECKPOINTS:-005000 010000}"

for checkpoint in $CHECKPOINTS; do
  destination="$LOCAL_MODEL_ROOT/$checkpoint/pretrained_model"
  mkdir -p "$destination"
  rsync -avP \
    -e "ssh -p $REMOTE_PORT" \
    "$REMOTE_HOST:$REMOTE_OUTPUT/checkpoints/$checkpoint/pretrained_model/" \
    "$destination/"
done

echo "Transfer complete. Re-run with rsync -avnc for checksum verification or verify the published SHA-256 manifest."
