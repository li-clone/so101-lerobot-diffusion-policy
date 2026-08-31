# 推理优化与实机评测

## 为什么使用10步去噪

LeRobot Diffusion默认 `num_inference_steps=None`，等价于100步DDPM。该配置在本机同步rollout的慢帧约为0.7 Hz，即一次动作块推理约1.4秒。改为10步后慢帧约5.7–6.2 Hz，单次推理约0.16–0.18秒。

模型缓存32个动作；其余动作仍接近20 FPS，因此10步配置的平均控制频率约18.6–18.7 Hz。警告显示的是生成新动作块的慢迭代，不代表整个episode持续只有6 Hz。不要把控制FPS改为1或6来掩盖推理延迟。

正式参数固定为：

```text
n_action_steps=32
num_inference_steps=10
fps=20
inference.type=sync
```

## 单次安全测试

```bash
export FOLLOWER_PORT=/dev/serial/by-id/<FOLLOWER_SERIAL_DEVICE>
export HANDEYE_CAMERA=/dev/v4l/by-path/<HANDEYE_VIDEO_INDEX0>
export ENVIRONMENT_CAMERA=/dev/v4l/by-id/<ENVIRONMENT_VIDEO_INDEX0>
export POLICY_PATH=/path/to/005000/pretrained_model
export N_ACTION_STEPS=32
export NUM_INFERENCE_STEPS=10
export DURATION=15

bash scripts/evaluation/rollout_diffusion.sh
```

第一次只验证方向、速度、动作范围和急停，不计入正式结果。

## 三轮正式评测

三轮写入同一数据集，每轮新增5条：

```bash
export EVAL_DATASET_ID=local/rollout_diffusion_5k_n10_compare_eval_15
export EVAL_DATASET_ROOT="$DATA_ROOT/evaluation/rollout_diffusion_5k_n10_compare_eval_15"
export NUM_EPISODES=5

# 近距离，episode 0-4
export RESUME=false
bash scripts/evaluation/record_rollout_batch.sh

# 中距离，episode 5-9
export RESUME=true
bash scripts/evaluation/record_rollout_batch.sh

# 远距离，episode 10-14
export RESUME=true
bash scripts/evaluation/record_rollout_batch.sh
```

失败也必须保留，不得为了提高成功率重录。成功定义为线材稳定放入黑色区域；抓到后掉落、推动目标盒、超时或人工干预均为失败。除最终成功率外，额外记录首次抓取成功和自主回抓。

同步推理的真实墙钟停顿不会完整反映在按标称20 FPS编码的视频时间戳中，因此本数据适合成功率与失败模式分析，不应直接用于精确推理延迟测量。
