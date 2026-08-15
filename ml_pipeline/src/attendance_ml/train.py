from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from attendance_ml.data import (
    ManifestDataset,
    label_map_from_rows,
    make_transforms,
    read_manifest,
)
from attendance_ml.model import ArcMarginProduct, FaceEmbeddingNet


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_device(requested: str) -> torch.device:
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but no CUDA device is available")
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def run_epoch(
    model: FaceEmbeddingNet,
    margin: ArcMarginProduct,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scaler: torch.amp.GradScaler,
    train: bool,
) -> tuple[float, float]:
    model.train(train)
    margin.train(train)
    total_loss = 0.0
    total_correct = 0
    total_count = 0
    amp_enabled = device.type == "cuda"

    for images, labels in tqdm(loader, leave=False):
        images = images.to(device, non_blocking=amp_enabled)
        labels = labels.to(device, non_blocking=amp_enabled)
        if train:
            optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, enabled=amp_enabled):
            embeddings = model(images)
            logits = margin(embeddings, labels)
            loss = criterion(logits, labels)
        if train:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(
                list(model.parameters()) + list(margin.parameters()), max_norm=5.0
            )
            scaler.step(optimizer)
            scaler.update()
        total_loss += loss.item() * labels.size(0)
        total_correct += (logits.argmax(dim=1) == labels).sum().item()
        total_count += labels.size(0)

    if total_count == 0:
        raise ValueError("DataLoader is empty")
    return total_loss / total_count, total_correct / total_count


def save_checkpoint(
    path: Path,
    model: FaceEmbeddingNet,
    margin: ArcMarginProduct,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    metrics: dict[str, float],
    config: dict[str, object],
    label_to_index: dict[str, int],
) -> None:
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "margin_state_dict": margin.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "metrics": metrics,
            "config": config,
            "label_to_index": label_to_index,
        },
        path,
    )


def train(args: argparse.Namespace) -> dict[str, float]:
    set_seed(args.seed)
    device = resolve_device(args.device)
    rows = read_manifest(args.manifest)
    label_to_index = label_map_from_rows(rows)
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    if len(label_to_index) < 2:
        raise ValueError("Training needs at least two identities")
    if not train_rows:
        raise ValueError("Manifest has no train samples")

    train_transform, eval_transform = make_transforms(args.image_size)
    train_dataset = ManifestDataset(train_rows, label_to_index, train_transform)
    val_dataset = ManifestDataset(val_rows, label_to_index, eval_transform)
    loader_kwargs = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    train_loader = DataLoader(train_dataset, shuffle=True, **loader_kwargs)
    val_loader = DataLoader(val_dataset, shuffle=False, **loader_kwargs) if val_rows else None

    model = FaceEmbeddingNet(
        backbone=args.backbone,
        embedding_dim=args.embedding_dim,
        pretrained=not args.no_pretrained,
    ).to(device)
    margin = ArcMarginProduct(
        embedding_dim=args.embedding_dim,
        class_count=len(label_to_index),
        margin=args.margin,
        scale=args.scale,
    ).to(device)
    optimizer = torch.optim.AdamW(
        list(model.parameters()) + list(margin.parameters()),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    criterion = nn.CrossEntropyLoss()
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args).copy()
    config["device"] = str(device)
    (output_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    history_path = output_dir / "history.jsonl"
    best_val = -1.0
    final_metrics: dict[str, float] = {}

    for epoch in range(1, args.epochs + 1):
        train_loss, train_accuracy = run_epoch(
            model, margin, train_loader, optimizer, criterion, device, scaler, train=True
        )
        if val_loader is not None:
            with torch.no_grad():
                val_loss, val_accuracy = run_epoch(
                    model, margin, val_loader, optimizer, criterion, device, scaler, train=False
                )
        else:
            val_loss, val_accuracy = 0.0, 0.0
        scheduler.step()
        final_metrics = {
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
        }
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"epoch": epoch, **final_metrics}) + "\n")
        save_checkpoint(
            output_dir / "last.pt",
            model,
            margin,
            optimizer,
            epoch,
            final_metrics,
            config,
            label_to_index,
        )
        score = val_accuracy if val_loader is not None else train_accuracy
        if score > best_val:
            best_val = score
            save_checkpoint(
                output_dir / "best.pt",
                model,
                margin,
                optimizer,
                epoch,
                final_metrics,
                config,
                label_to_index,
            )
        print(json.dumps({"epoch": epoch, **final_metrics}))
    return final_metrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a baseline face embedding model")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", default="outputs/recognition")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--embedding-dim", type=int, default=512)
    parser.add_argument("--image-size", type=int, default=112)
    parser.add_argument("--backbone", choices=["resnet18", "resnet50"], default="resnet18")
    parser.add_argument("--margin", type=float, default=0.5)
    parser.add_argument("--scale", type=float, default=64.0)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--no-pretrained", action="store_true")
    return parser


if __name__ == "__main__":
    train(build_parser().parse_args())
