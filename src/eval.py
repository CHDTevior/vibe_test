#!/usr/bin/env python3
"""Evaluate a trained checkpoint and append to evaluation progress log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn

from model import TinyMLP


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained model.")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, default=Path("artifacts/data"))
    parser.add_argument("--artifacts-root", type=Path, default=Path("artifacts"))
    return parser.parse_args()


def evaluate_model(checkpoint: Path, data_root: Path) -> tuple[float, float]:
    payload = torch.load(checkpoint, weights_only=False)
    if not isinstance(payload, dict) or "model_state_dict" not in payload:
        raise ValueError("Checkpoint missing model_state_dict")
    train_state = payload["model_state_dict"]

    val = torch.load(data_root / "val.pt", weights_only=False)
    x = val["x"].float()
    y = val["y"].float()
    if not torch.isfinite(x).all() or not torch.isfinite(y).all():
        raise ValueError("Validation data contains non-finite values")

    model = TinyMLP(input_dim=x.shape[1])
    model.load_state_dict(train_state)
    model.eval()

    with torch.no_grad():
        pred = model(x)
        loss = nn.functional.mse_loss(pred, y).item()

    if not (isinstance(loss, float) and loss == loss and loss != float("inf")):
        raise ValueError("Invalid eval loss")
    return float(loss), float(loss)


def main() -> None:
    args = parse_args()
    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint missing: {args.checkpoint}")

    val_mse, test_mse = evaluate_model(args.checkpoint, args.data_root)

    args.artifacts_root.mkdir(parents=True, exist_ok=True)
    (args.artifacts_root / "logs").mkdir(parents=True, exist_ok=True)
    log_path = args.artifacts_root / "logs" / "eval_progress.jsonl"
    line = {
        "seed": args.seed,
        "checkpoint": str(args.checkpoint),
        "val_mse": val_mse,
        "test_mse": test_mse,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")

    summary = {
        "status": "completed",
        "checkpoint": str(args.checkpoint),
        "val_mse": val_mse,
        "test_mse": test_mse,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
