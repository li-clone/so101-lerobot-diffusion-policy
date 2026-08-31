# Diffusion 训练与模型选择

## 正式训练

```bash
export DATA_ROOT=/path/to/data
export OUTPUT_ROOT=/path/to/outputs
export DATASET_NAME=so101_pick_place_compare_v1_70
export RUN_NAME=diffusion_so101_pick_place_compare_v1_70_v1_50k

bash scripts/training/train_diffusion.sh
```

默认参数与本实验一致：50k steps、batch 16、seed 1000、10%验证集、每1k验证、每5k保存、4个workers、AMP关闭、W&B关闭。学习率从500步warmup升到 `1e-4`，随后余弦衰减。

数据集的63条训练轨迹包含18,935帧。batch 16 时每约1,183步相当于一轮，50k约为42.25轮。

## 训练结果

- 训练耗时：3小时39分。
- 模型参数：277,819,846。
- 训练显存峰值：约12.73 GB。
- 最低验证损失：8k 的0.0255，但8k没有保存。
- 已保存模型中最低：5k 的0.0274。
- 10k：0.0313，作为候选保留。
- 50k：0.1399，已明显过拟合。

验证曲线从8k后总体上升，而训练损失最终下降到约0.003。不要默认使用最后一个checkpoint，也不要仅凭训练loss选择模型。

## 提取曲线

```bash
python scripts/training/extract_eval_curve.py \
  "$OUTPUT_ROOT/${RUN_NAME}_console.log" \
  results/training_curves/diffusion_v1_eval.csv \
  --run diffusion_v1

python scripts/training/plot_eval_curve.py \
  results/training_curves/diffusion_v1_eval.csv \
  --output results/figures/diffusion_eval_curve.svg
```

不同策略的loss定义、归一化方式和模型结构不同。ACT的0.2643与Diffusion的0.0274不能用于直接判断哪个策略更好；最终选择必须结合固定协议实机评测。
