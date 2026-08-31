#!/usr/bin/env python3
"""Audit LeRobot v3 tabular and video integrity without modifying the dataset."""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

VIDEO_KEYS = ("observation.images.handeye", "observation.images.environment")


def read_all(files: list[Path]):
    if not files:
        raise ValueError("No parquet files found")
    return pa.concat_tables([pq.read_table(path) for path in files]).to_pandas()


def video_frames(path: Path) -> tuple[int, str, int, int, str]:
    raw = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames",
            "-of", "json", str(path),
        ],
        text=True,
    )
    stream = json.loads(raw)["streams"][0]
    return (
        int(stream["nb_read_frames"]), stream["codec_name"], int(stream["width"]),
        int(stream["height"]), stream["r_frame_rate"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--expected-episodes", type=int)
    parser.add_argument("--expected-frames", type=int)
    args = parser.parse_args()
    root = args.dataset.resolve()
    info = json.loads((root / "meta/info.json").read_text())
    data = read_all(sorted(root.glob("data/chunk-*/*.parquet")))
    episodes = read_all(sorted(root.glob("meta/episodes/chunk-*/*.parquet")))
    errors: list[str] = []

    if len(data) != info["total_frames"]:
        errors.append("info.total_frames does not match parquet rows")
    if len(episodes) != info["total_episodes"]:
        errors.append("info.total_episodes does not match episode metadata")
    if args.expected_episodes is not None and info["total_episodes"] != args.expected_episodes:
        errors.append("unexpected episode count")
    if args.expected_frames is not None and info["total_frames"] != args.expected_frames:
        errors.append("unexpected frame count")
    if not np.array_equal(np.asarray(data["index"], dtype=int), np.arange(len(data))):
        errors.append("global index is not contiguous")
    expected_episode_indices = list(range(info["total_episodes"]))
    if sorted(map(int, data.episode_index.unique())) != expected_episode_indices:
        errors.append("episode indices are not contiguous")
    if int(episodes.length.sum()) != len(data):
        errors.append("episode lengths do not sum to total frames")

    for episode_index, group in data.groupby("episode_index", sort=True):
        frame_index = np.asarray(group.frame_index, dtype=int)
        timestamp = np.asarray(group.timestamp, dtype=float)
        action = np.stack(group.action.to_numpy())
        state = np.stack(group["observation.state"].to_numpy())
        if not np.array_equal(frame_index, np.arange(len(group))):
            errors.append(f"episode {episode_index}: frame index")
        if not np.all(np.diff(timestamp) > 0):
            errors.append(f"episode {episode_index}: timestamp")
        if not np.isfinite(action).all() or not np.isfinite(state).all():
            errors.append(f"episode {episode_index}: non-finite action/state")
        print(
            f"episode={int(episode_index):02d} frames={len(group):4d} "
            f"duration={timestamp[-1] - timestamp[0]:6.2f}s"
        )

    for key in VIDEO_KEYS:
        files = sorted((root / "videos" / key).glob("chunk-*/*.mp4"))
        total = 0
        for path in files:
            frames, codec, width, height, rate = video_frames(path)
            total += frames
            if (codec, width, height, rate) != ("h264", 640, 480, "20/1"):
                errors.append(f"{path}: unexpected video format")
        print(f"{key}: files={len(files)} frames={total}")
        if total != len(data):
            errors.append(f"{key}: frame total does not match parquet")

    if errors:
        print("AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(
        f"AUDIT OK episodes={info['total_episodes']} frames={info['total_frames']} "
        f"fps={info['fps']}"
    )


if __name__ == "__main__":
    main()
