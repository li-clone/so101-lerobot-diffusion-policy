#!/usr/bin/env bash
set -euo pipefail

DATA_ROOT="${DATA_ROOT:-$PWD/data}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PWD/outputs}"
DATASET_NAME="${DATASET_NAME:-so101_pick_place_compare_v1_70}"
RUN_NAME="${RUN_NAME:-diffusion_so101_pick_place_compare_v1_70_v1_50k}"
STEPS="${STEPS:-50000}"
BATCH_SIZE="${BATCH_SIZE:-16}"
SEED="${SEED:-1000}"
EVAL_STEPS="${EVAL_STEPS:-1000}"
SAVE_FREQ="${SAVE_FREQ:-5000}"
NUM_WORKERS="${NUM_WORKERS:-4}"

mkdir -p "$OUTPUT_ROOT"
set -o pipefail

lerobot-train \
  --dataset.repo_id="local/$DATASET_NAME" \
  --dataset.root="$DATA_ROOT/$DATASET_NAME" \
  --dataset.return_uint8=true \
  --dataset.eval_split=0.1 \
  --policy.type=diffusion \
  --policy.device=cuda \
  --policy.use_amp=false \
  --policy.push_to_hub=false \
  --policy.n_action_steps=32 \
  --output_dir="$OUTPUT_ROOT/$RUN_NAME" \
  --job_name="$RUN_NAME" \
  --batch_size="$BATCH_SIZE" \
  --steps="$STEPS" \
  --seed="$SEED" \
  --num_workers="$NUM_WORKERS" \
  --persistent_workers=false \
  --eval_steps="$EVAL_STEPS" \
  --log_freq=100 \
  --save_checkpoint=true \
  --save_freq="$SAVE_FREQ" \
  --wandb.enable=false \
  2>&1 | tee "$OUTPUT_ROOT/${RUN_NAME}_console.log"
