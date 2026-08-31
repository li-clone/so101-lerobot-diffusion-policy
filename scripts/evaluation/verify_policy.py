#!/usr/bin/env python3
"""Strictly load local Diffusion checkpoints and verify parameter counts."""

import argparse
from pathlib import Path

from lerobot.policies.diffusion.modeling_diffusion import DiffusionPolicy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--expected-parameters", type=int, default=277819846)
    args = parser.parse_args()
    for path in args.paths:
        policy = DiffusionPolicy.from_pretrained(path, local_files_only=True, strict=True)
        parameters = sum(item.numel() for item in policy.parameters())
        if parameters != args.expected_parameters:
            raise SystemExit(f"{path}: expected {args.expected_parameters} parameters, got {parameters}")
        print(f"OK {path}: device={next(policy.parameters()).device} parameters={parameters}")


if __name__ == "__main__":
    main()
