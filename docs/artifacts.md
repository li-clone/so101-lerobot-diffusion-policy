# 数据与模型清单

GitHub不保存原始数据和权重。公开仓库只保存结构化摘要与SHA-256，用于验证私有副本的一致性。

## 数据集

| ID | 用途 | Episodes | Frames | 大小 |
|---|---|---:|---:|---:|
| `so101_pick_place_compare_v1_70` | Diffusion训练 | 70 | 21,016 | 553 MB |
| `rollout_diffusion_5k_n10_compare_eval_15` | 5k实机评测 | 15 | 5,171 | 144 MB |

对应清单位于 `manifests/datasets/`。在数据集父目录执行：

```bash
sha256sum -c /path/to/manifest.sha256
```

## 模型

保留5k与10k两个 `pretrained_model`，单个约1.1 GB。5k用于正式结果，10k仅为候选。逐文件哈希见 `manifests/models/diffusion_models.csv`。

模型下载或迁移后必须同时检查：

- `config.json`
- `model.safetensors`
- preprocessor与postprocessor JSON
- normalization与unnormalization safetensors
- `train_config.json`

仅有 `model.safetensors` 不足以保证输入归一化和动作反归一化可复现。

从训练服务器断点续传5k和10k推理目录：

```bash
export REMOTE_HOST=user@training-host
export REMOTE_PORT=<SSH_PORT>
export REMOTE_OUTPUT=/path/to/diffusion_run
export LOCAL_MODEL_ROOT="$PWD/outputs/diffusion_compare_models"

bash scripts/models/download_pretrained_models.sh
```

`rsync -P` 支持中断后继续；传输完成后使用 `scripts/evaluation/verify_policy.py` 严格加载，并对照模型清单验证SHA-256。
