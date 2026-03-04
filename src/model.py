"""Model definitions for deterministic tiny MLP regression."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class MLPConfig:
    input_dim: int = 16
    hidden_dim: int = 24
    hidden_layers: int = 1
    output_dim: int = 1
    activation: str = "relu"


def _activation(name: str):
    if name == "relu":
        return nn.ReLU()
    if name == "tanh":
        return nn.Tanh()
    raise ValueError(f"Unsupported activation: {name}")


def build_model(config: MLPConfig = MLPConfig()) -> nn.Module:
    if not (1 <= config.hidden_layers <= 2):
        raise ValueError(f"hidden_layers must be 1 or 2, got {config.hidden_layers}")
    if config.hidden_dim < 1 or config.hidden_dim > 32:
        raise ValueError(f"hidden_dim must be in [1, 32], got {config.hidden_dim}")
    if config.input_dim <= 0 or config.output_dim <= 0:
        raise ValueError("input_dim/output_dim must be positive")

    layers = [nn.Linear(config.input_dim, config.hidden_dim), _activation(config.activation)]
    if config.hidden_layers == 2:
        layers += [nn.Linear(config.hidden_dim, config.hidden_dim), _activation(config.activation)]
    layers.append(nn.Linear(config.hidden_dim, config.output_dim))
    return nn.Sequential(*layers)


class TinyMLP(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 24,
        hidden_layers: int = 1,
        output_dim: int = 1,
        activation: str = "relu",
    ) -> None:
        super().__init__()
        self.cfg = MLPConfig(input_dim, hidden_dim, hidden_layers, output_dim, activation)
        self.model = build_model(self.cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
