# 环境配置

## 已验证环境

- Ubuntu 22.04
- Python 3.12
- NVIDIA RTX 4090 24 GB
- PyTorch `2.11.0+cu128`
- torchvision `0.26.0+cu128`
- LeRobot `0.6.1`
- Diffusers `0.39.0`

驱动显示的最高 CUDA 版本不需要与 PyTorch wheel 后缀完全相同；以 `torch.cuda.is_available()` 和真实前后向测试为准。

## 安装

```bash
conda create -n lerobot-diffusion python=3.12 -y
conda activate lerobot-diffusion

python -m pip install \
  torch==2.11.0+cu128 torchvision==0.26.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128

git submodule update --init --recursive
python -m pip install -e "./upstream/lerobot[diffusion,feetech,training,core_scripts]"
python -m pip install "packaging>=24.2,<26" "setuptools>=71,<82"
python -m pip check
```

国内网络可以为普通 PyPI 包配置可信镜像，但 PyTorch CUDA wheel 建议继续使用官方索引，避免得到 CPU wheel 或不匹配的 CUDA 构建。

## 验证

```bash
python - <<'PY'
import torch
import diffusers
import lerobot

print("LeRobot:", lerobot.__version__)
print("PyTorch:", torch.__version__)
print("Diffusers:", diffusers.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
PY
```

正式训练前用小 batch 跑 2 步 smoke training。smoke test 的 `End of training`、checkpoint 和退出码都正常时，DataLoader 在解释器退出阶段产生的 worker 清理 traceback 可以单独分析，但不能把 OOM 或训练中途异常当作清理告警忽略。

## 服务器磁盘

本实验单个完整 Diffusion checkpoint 约 3.2 GB，其中包含训练状态；单独用于推理的 `pretrained_model` 约 1.1 GB。50 GB 数据盘保存十个完整 checkpoint 后达到 93%，因此训练前必须估算 checkpoint 数量并监控：

```bash
df -h "$DATA_DISK"
du -sh "$OUTPUT_ROOT"/diffusion_*/checkpoints/*
```
