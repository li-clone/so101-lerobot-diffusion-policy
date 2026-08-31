# 故障排查

## 训练结束后的DataLoader traceback

如果已经出现 `End of training`、目标checkpoint且进程退出码为0，随后仅在Python解释器退出阶段出现DataLoader worker清理 traceback，通常不影响已保存模型。若错误出现在训练中、退出码非0或checkpoint缺失，则不能忽略。

## Rollout低于目标FPS

- 约0.7 Hz且每约3秒一次：通常是100步DDPM推理约1.4秒。
- 约6 Hz且每约2秒一次：通常是10步DDPM推理约0.16秒。
- 每一帧都持续告警：检查摄像头FPS、CPU占用、GPU进程和视频编码。

本实验保留20 FPS与 `n_action_steps=32`，使用10步推理。不要通过降低控制FPS掩盖问题。

## 摄像头打开失败

关闭 `ffplay`、Cheese和其他占用摄像头的进程，重新确认稳定设备路径与fourcc。手眼使用YUYV，第三视角使用MJPG。

## 异常退出后机械臂仍有扭矩

```bash
python scripts/diagnostics/diagnose_follower_health.py --port "$FOLLOWER_PORT"
python scripts/safety/safe_disable_follower_torque.py --port "$FOLLOWER_PORT"
```

只有六个电机全部读回 `Torque_Enable=0` 才算成功。通信异常时立即切断Follower 12 V电源，不要强行移动关节。

## 磁盘不足

完整checkpoint约3.2 GB，推理目录约1.1 GB。训练期间定期运行：

```bash
df -h "$DATA_DISK"
du -sh "$OUTPUT_ROOT"/*/checkpoints/*
```

只做推理时下载 `pretrained_model/`，不需要优化器与scheduler训练状态。
