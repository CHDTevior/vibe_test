#!/usr/bin/env python3
"""Deterministic training loop for the synthetic regression dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from model import TinyMLP


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train tiny MLP regression model.")
    p.add_argument("--seed", type=int, default=123)
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-2)
    p.add_argument("--hidden-dim", type=int, default=24)
    p.add_argument("--hidden-layers", type=int, default=1)
    p.add_argument("--data-root", type=Path, default=Path("artifacts/data"))
    p.add_argument("--artifacts-root", type=Path, default=Path("artifacts"))
    p.add_argument("--no-git-sync", action="store_true")
    return p.parse_args()


def set_deterministic(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)


def load_split(path: Path, label: str) -> Dict[str, torch.Tensor]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label} data: {path}")
    payload = torch.load(path, weights_only=False)
    if not isinstance(payload, dict) or "x" not in payload or "y" not in payload:
        raise ValueError(f"{label} data must contain {'x','y'} tensors")
    x = payload["x"]
    y = payload["y"]
    if x.ndim != 2 or y.ndim != 2 or y.shape[0] != x.shape[0]:
        raise ValueError(f"Invalid shapes in {label} split: x={tuple(x.shape)}, y={tuple(y.shape)}")
    if not torch.isfinite(x).all() or not torch.isfinite(y).all():
        raise ValueError(f"Non-finite values in {label} split")
    return {"x": x.float(), "y": y.float()}


def evaluate(x: torch.Tensor, y: torch.Tensor, model: nn.Module, loss_fn: nn.Module) -> float:
    model.eval()
    with torch.no_grad():
        pred = model(x)
        loss = loss_fn(pred, y).item()
    return float(loss)


def main() -> None:
    args = parse_args()
    if args.epochs < 1:
        raise SystemExit("epochs must be >= 1")
    if args.batch_size < 1:
        raise SystemExit("batch-size must be >= 1")
    if args.lr <= 0:
        raise SystemExit("lr must be > 0")

    set_deterministic(args.seed)
    args.artifacts_root.mkdir(parents=True, exist_ok=True)
    (args.artifacts_root / "logs").mkdir(parents=True, exist_ok=True)
    (args.artifacts_root / "checkpoints").mkdir(parents=True, exist_ok=True)

    train_data = load_split(args.data_root / "train.pt", "train")
    val_data = load_split(args.data_root / "val.pt", "val")

    train_loader = DataLoader(
        TensorDataset(train_data["x"], train_data["y"]),
        batch_size=args.batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
    )

    val_x = val_data["x"]
    val_y = val_data["y"]

    model = TinyMLP(
        input_dim=train_data["x"].shape[1],
        hidden_dim=args.hidden_dim,
        hidden_layers=args.hidden_layers,
        output_dim=1,
    )
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    train_log = []
    best_val = float("inf")
    best_epoch = -1
    last_ckpt = args.artifacts_root / "checkpoints" / "last.pt"

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = []
        for bx, by in train_loader:
            opt.zero_grad(set_to_none=True)
            pred = model(bx)
            loss = loss_fn(pred, by)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite train loss at epoch {epoch}")
            loss.backward()
            opt.step()
            epoch_loss.append(float(loss.item()))

        avg_train = float(np.mean(epoch_loss)) if epoch_loss else float("nan")
        val_mse = evaluate(val_x, val_y, model, loss_fn)
        entry = {
            "epoch": epoch,
            "train_mse": avg_train,
            "val_mse": val_mse,
            "seed": args.seed,
            "hidden_dim": args.hidden_dim,
            "hidden_layers": args.hidden_layers,
        }
        train_log.append(entry)

        ckpt_epoch = args.artifacts_root / "checkpoints" / f"last_epoch_{epoch}.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "epoch": epoch,
                "val_mse": val_mse,
                "config": vars(args),
            },
            ckpt_epoch,
        )
        torch.save(model.state_dict(), last_ckpt)

        if val_mse < best_val:
            best_val = val_mse
            best_epoch = epoch
            torch.save(
                model.state_dict(),
                args.artifacts_root / "checkpoints" / "best.pt",
            )

    log_path = args.artifacts_root / "logs" / "train_progress.jsonl"
    with log_path.open("w", encoding="utf-8") as f:
        for rec in train_log:
            f.write(json.dumps(rec) + "\n")

    summary = {
        "status": "completed",
        "best_epoch": best_epoch,
        "best_val_mse": best_val,
        "final_epoch": args.epochs,
        "seed": args.seed,
    }
    (args.artifacts_root / "logs" / "train_summary.json").write_text(
        json.dumps(summary, indent=2),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
