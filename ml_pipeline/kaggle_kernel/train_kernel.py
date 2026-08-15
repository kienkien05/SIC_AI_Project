from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import Tensor, nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm.auto import tqdm


INPUT_ROOT = Path("/kaggle/input")
WORK_DIR = Path("/kaggle/working/face-attendance-baseline")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SEED = 42
EPOCHS = 5
BATCH_SIZE = 64
IMAGE_SIZE = 112
EMBEDDING_DIM = 512


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_data_root() -> Path:
    for candidate in INPUT_ROOT.rglob("p1"):
        if not candidate.is_dir():
            continue
        identity_dirs = [path for path in candidate.parent.iterdir() if path.is_dir() and path.name.startswith("p")]
        if len(identity_dirs) >= 2:
            return candidate.parent
    available = sorted(str(path.relative_to(INPUT_ROOT)) for path in INPUT_ROOT.iterdir()) if INPUT_ROOT.is_dir() else []
    raise FileNotFoundError(f"Could not find identity folders below {INPUT_ROOT}; inputs={available}")


def resolve_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    capability_major, _ = torch.cuda.get_device_capability(0)
    if capability_major < 7:
        print("CUDA device is incompatible with this PyTorch build; using CPU.")
        return torch.device("cpu")
    return torch.device("cuda")


def build_rows(root: Path) -> list[dict[str, str]]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            relative = path.relative_to(root)
            if len(relative.parts) >= 2:
                grouped[relative.parts[0]].append(path)

    rows: list[dict[str, str]] = []
    rng = random.Random(SEED)
    for subject_id, paths in grouped.items():
        rng.shuffle(paths)
        val_count = max(1, round(len(paths) * 0.15)) if len(paths) >= 2 else 0
        test_count = max(1, round(len(paths) * 0.15)) if len(paths) >= 3 else 0
        while len(paths) - val_count - test_count < 1:
            if test_count:
                test_count -= 1
            elif val_count:
                val_count -= 1
            else:
                break
        for index, path in enumerate(paths):
            split = "val" if index < val_count else "test" if index < val_count + test_count else "train"
            try:
                with Image.open(path) as image:
                    width, height = image.size
                    image.verify()
            except Exception:
                continue
            rows.append(
                {
                    "path": str(path),
                    "subject_id": subject_id,
                    "split": split,
                    "width": str(width),
                    "height": str(height),
                    "source": "nanimasaka/masked-face-recognition-dataset",
                    "scenario": "mask_pose_illumination",
                }
            )
    return rows


class FaceDataset(Dataset[tuple[Tensor, int]]):
    def __init__(
        self,
        rows: list[dict[str, str]],
        labels: dict[str, int],
        transform: transforms.Compose,
    ) -> None:
        self.rows = rows
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[Tensor, int]:
        row = self.rows[index]
        with Image.open(row["path"]) as image:
            image_rgb = image.convert("RGB")
        return self.transform(image_rgb), self.labels[row["subject_id"]]


class FaceEmbeddingNet(nn.Module):
    def __init__(self, embedding_dim: int) -> None:
        super().__init__()
        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        feature_dim = backbone.fc.in_features
        backbone.fc = nn.Identity()
        self.backbone = backbone
        self.embedding = nn.Linear(feature_dim, embedding_dim, bias=False)
        self.embedding_bn = nn.BatchNorm1d(embedding_dim)

    def forward(self, images: Tensor) -> Tensor:
        features = self.backbone(images)
        embeddings = self.embedding_bn(self.embedding(features))
        return F.normalize(embeddings, p=2, dim=1)


class ArcMarginProduct(nn.Module):
    def __init__(self, embedding_dim: int, class_count: int, margin: float = 0.5, scale: float = 64.0) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(class_count, embedding_dim))
        nn.init.xavier_uniform_(self.weight)
        self.cos_m = math.cos(margin)
        self.sin_m = math.sin(margin)
        self.threshold = math.cos(math.pi - margin)
        self.mm = math.sin(math.pi - margin) * margin
        self.scale = scale

    def forward(self, embeddings: Tensor, labels: Tensor) -> Tensor:
        cosine = F.linear(F.normalize(embeddings), F.normalize(self.weight))
        sine = torch.sqrt(torch.clamp(1.0 - cosine.square(), min=1e-7))
        phi = cosine * self.cos_m - sine * self.sin_m
        phi = torch.where(cosine > self.threshold, phi, cosine - self.mm)
        one_hot = torch.zeros_like(cosine)
        one_hot.scatter_(1, labels.view(-1, 1), 1.0)
        return (one_hot * phi + (1.0 - one_hot) * cosine) * self.scale


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
    use_amp = device.type == "cuda"
    for images, labels in tqdm(loader, leave=False):
        images = images.to(device, non_blocking=use_amp)
        labels = labels.to(device, non_blocking=use_amp)
        if train:
            optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, enabled=use_amp):
            logits = margin(model(images), labels)
            loss = criterion(logits, labels)
        if train:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(list(model.parameters()) + list(margin.parameters()), 5.0)
            scaler.step(optimizer)
            scaler.update()
        total_loss += loss.item() * labels.size(0)
        total_correct += (logits.argmax(dim=1) == labels).sum().item()
        total_count += labels.size(0)
    return total_loss / total_count, total_correct / total_count


def main() -> None:
    set_seed(SEED)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    data_root = resolve_data_root()
    rows = build_rows(data_root)
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    labels = {subject: index for index, subject in enumerate(sorted({row["subject_id"] for row in train_rows}))}
    if len(labels) < 2 or not val_rows:
        raise ValueError("Dataset needs at least two identities and validation samples")
    with (WORK_DIR / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.85, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.15),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    device = resolve_device()
    loader_options = {"batch_size": BATCH_SIZE, "num_workers": 2, "pin_memory": device.type == "cuda"}
    train_loader = DataLoader(FaceDataset(train_rows, labels, train_transform), shuffle=True, **loader_options)
    val_loader = DataLoader(FaceDataset(val_rows, labels, eval_transform), shuffle=False, **loader_options)
    model = FaceEmbeddingNet(EMBEDDING_DIM).to(device)
    margin = ArcMarginProduct(EMBEDDING_DIM, len(labels)).to(device)
    optimizer = torch.optim.AdamW(list(model.parameters()) + list(margin.parameters()), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    output_dir = WORK_DIR / "recognition"
    output_dir.mkdir(exist_ok=True)
    best_accuracy = -1.0
    history: list[dict[str, float]] = []

    for epoch in range(1, EPOCHS + 1):
        train_loss, train_accuracy = run_epoch(model, margin, train_loader, optimizer, criterion, device, scaler, True)
        with torch.no_grad():
            val_loss, val_accuracy = run_epoch(model, margin, val_loader, optimizer, criterion, device, scaler, False)
        scheduler.step()
        metrics = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
        }
        history.append(metrics)
        checkpoint = {
            "model_state_dict": model.state_dict(),
            "margin_state_dict": margin.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "labels": labels,
            "metrics": metrics,
            "embedding_dim": EMBEDDING_DIM,
        }
        torch.save(checkpoint, output_dir / "last.pt")
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save(checkpoint, output_dir / "best.pt")
        print(json.dumps(metrics))
    (output_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(json.dumps({"data_root": str(data_root), "device": str(device), "output_dir": str(output_dir), "best_val_accuracy": best_accuracy}, indent=2))


if __name__ == "__main__":
    main()
