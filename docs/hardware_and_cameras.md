# 硬件、标定与双摄像头

## 实验硬件

- SO-101 Leader + Follower，6 DoF
- Feetech STS3215 电机
- `handeye` 手眼相机：640×480、30 FPS、YUYV
- `environment` 第三视角相机：640×480、30 FPS、MJPG
- 数据集与控制频率：20 FPS

## 稳定设备路径

```bash
lsusb
v4l2-ctl --list-devices
ls -l /dev/serial/by-id/ /dev/v4l/by-id/ /dev/v4l/by-path/
```

优先使用 `/dev/serial/by-id/`、`/dev/v4l/by-id/` 和 `/dev/v4l/by-path/`，不要把易变化的 `/dev/video2` 或 `/dev/ttyACM0` 写入正式命令。真实设备路径只保存在本机配置中。

## 摄像头语义

- `handeye` 必须持续看到夹爪、黄色线束和黑色目标区域。
- `environment` 必须看到完整工作区、机械臂和目标区域。
- 训练、验证和部署的相机名称、顺序、分辨率必须一致。

预览命令：

```bash
ffplay -f v4l2 -input_format yuyv422 -video_size 640x480 -framerate 30 "$HANDEYE_CAMERA"
ffplay -f v4l2 -input_format mjpeg -video_size 640x480 -framerate 30 "$ENVIRONMENT_CAMERA"
```

录制期间不要改变机位、焦距或相机语义。光线变化可以保留为自然扰动，但画面必须清晰且颜色正常；明显偏红、过暗或遮挡的整轮数据应重录。

## 推理前健康检查

```bash
python scripts/diagnostics/diagnose_follower_health.py --port "$FOLLOWER_PORT"
```

本实验开始评测前六个电机均为 `Status=0`、电压约 12.1–12.3 V、温度 44–46°C、扭矩关闭。首次动作前还要确认从臂处于训练初始姿态范围，清空运动空间，并准备切断 12 V 电源。
