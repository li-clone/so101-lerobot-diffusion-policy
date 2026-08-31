# Artifact manifests

这个目录只保存公开元数据和SHA-256，不保存私有数据或模型。

- `datasets/datasets.csv`：数据集摘要。
- `datasets/*.sha256`：训练集与评测集逐文件校验。
- `evaluations/evaluation_protocols.csv`：部署和评测协议。
- `models/diffusion_models.csv`：5k与10k推理目录逐文件哈希。
- `artifact_locations.yaml`：公开仓库中的登记状态，不含本机绝对路径。
