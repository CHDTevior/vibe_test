#!/usr/bin/env python3
"""Deterministic synthetic data generation for a tiny regression task."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic regression data.")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--num-samples", type=int, default=2048)
    parser.add_argument("--num-features", type=int, default=16)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--noise-std", type=float, default=0.01)
    parser.add_argument("--artifact-root", type=Path, default=Path("artifacts/data"))
    return parser.parse_args()


def make_regression_batch(rng: np.random.Generator, n: int, d: int) -> torch.Tensor:
    x = rng.normal(size=(n, d)).astype(np.float32)
    w = np.linspace(0.1, 1.0, d, dtype=np.float32)
    y = x @ w + 0.5 * np.sin(x[:, 0]) + 0.25 * x[:, 1] ** 2
    return torch.from_numpy(x), torch.from_numpy(y).unsqueeze(-1)


def main() -> None:
    args = parse_args()
    if args.num_samples <= 0:
        raise SystemExit("num-samples must be > 0")
    if not (0 < args.train_ratio < 1):
        raise SystemExit("train-ratio must be in (0, 1)")

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    rng = np.random.default_rng(args.seed)

    x, y = make_regression_batch(rng, args.num_samples, args.num_features)

    if not torch.isfinite(x).all() or not torch.isfinite(y).all():
        raise SystemExit("Generated data contains NaN/Inf")

    n_train = int(round(args.num_samples * args.train_ratio))
    if n_train < 1 or n_train >= args.num_samples:
        n_train = int(args.num_samples * args.train_ratio)
    n_train = max(1, min(args.num_samples - 1, n_train))
    n_val = args.num_samples - n_train

    perm = torch.randperm(args.num_samples, generator=torch.Generator().manual_seed(args.seed))
    x = x[perm]
    y = y[perm]

    train_x, val_x = x[:n_train], x[n_train:]
    train_y, val_y = y[:n_train], y[n_train:]
    if val_x.shape[0] != n_val:
        raise SystemExit("Data split mismatch")

    torch.save({"x": train_x, "y": train_y}, args.artifact_root / "train.pt")
    torch.save({"x": val_x, "y": val_y}, args.artifact_root / "val.pt")

    meta = {
        "seed": args.seed,
        "num_samples": args.num_samples,
        "num_features": args.num_features,
        "train_ratio": args.train_ratio,
        "train_size": int(train_x.shape[0]),
        "val_size": int(val_x.shape[0]),
        "noise_std": args.noise_std,
        "torch_seed": args.seed,
    }
    (args.artifact_root / "dataset_meta.json").write_text(json.dumps(meta, indent=2))

    print(
        json.dumps(
            {
                "status": "ok",
                "train_path": str((args.artifact_root / "train.pt").resolve()),
                "val_path": str((args.artifact_root / "val.pt").resolve()),
                "meta": meta,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
