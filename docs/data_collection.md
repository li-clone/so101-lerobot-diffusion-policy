# 70 条数据采集

## 任务与分布

任务：`Pick up the yellow cable bundle and place it in the black target area.`

最终训练集 `so101_pick_place_compare_v1_70`：

| 距离 | Episodes |
|---|---:|
| 近 | 24 |
| 中 | 23 |
| 远 | 23 |
| 合计 | 70 |

数据集包含 21,016 帧、20 FPS、两路 640×480 视频。分布接近平衡，避免模型只学习最常见距离。

## 录制

```bash
export FOLLOWER_PORT=/dev/serial/by-id/<FOLLOWER_SERIAL_DEVICE>
export LEADER_PORT=/dev/serial/by-id/<LEADER_SERIAL_DEVICE>
export HANDEYE_CAMERA=/dev/v4l/by-path/<HANDEYE_VIDEO_INDEX0>
export ENVIRONMENT_CAMERA=/dev/v4l/by-id/<ENVIRONMENT_VIDEO_INDEX0>
export DATASET_ID=local/so101_pick_place_compare_v1_70
export DATASET_ROOT="$DATA_ROOT/so101_pick_place_compare_v1_70"
export TASK="Pick up the yellow cable bundle and place it in the black target area."
export NUM_EPISODES=10
export RESUME=false

bash scripts/dataset/record_diffusion_batch.sh
```

第一轮必须使用 `RESUME=false` 且目标目录不存在；向同一数据集追加时使用 `RESUME=true`。每轮结束后同时检查视频和表格，不要等70条全部完成后才发现相机语义或亮度错误。

## 验收条件

- episode、frame 和全局 index 连续。
- timestamp 单调，标称间隔为 0.05 秒。
- action 与 observation.state 均为有限值。
- 两路视频帧数与表格帧数一致，且可完整解码。
- 任务字段完全一致。
- 长轨迹必须能由真实操作过程解释；无法解释的异常长录制需要删除并重录。

最终审计：

```bash
python scripts/evaluation/audit_dataset.py \
  "$DATA_ROOT/so101_pick_place_compare_v1_70" \
  --expected-episodes 70 --expected-frames 21016
```

通过后生成 SHA-256 清单，并在服务器上传后使用 `sha256sum -c` 验证。
