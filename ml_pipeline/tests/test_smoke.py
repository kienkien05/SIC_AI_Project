from pathlib import Path

import torch
from PIL import Image

from attendance_ml.data import build_manifest, read_manifest
from attendance_ml.model import ArcMarginProduct, FaceEmbeddingNet
from attendance_ml.train import train


def _write_dataset(root: Path) -> None:
    generator = torch.Generator().manual_seed(7)
    for subject in ("alice", "bob", "carol"):
        subject_dir = root / subject
        subject_dir.mkdir(parents=True)
        for index in range(4):
            pixels = torch.randint(0, 255, (112, 112, 3), generator=generator, dtype=torch.uint8)
            Image.fromarray(pixels.numpy()).save(subject_dir / f"{index}.png")


def test_manifest_split_and_model_forward(tmp_path: Path) -> None:
    root = tmp_path / "images"
    _write_dataset(root)
    manifest = tmp_path / "manifest.csv"
    stats = build_manifest(root, manifest, "synthetic", "normal")
    rows = read_manifest(manifest)
    assert stats["train"] > 0
    assert {row["split"] for row in rows} == {"train", "val", "test"}

    model = FaceEmbeddingNet(backbone="resnet18", embedding_dim=32, pretrained=False)
    margin = ArcMarginProduct(embedding_dim=32, class_count=3)
    embeddings = model(torch.randn(2, 3, 112, 112))
    logits = margin(embeddings, torch.tensor([0, 1]))
    assert embeddings.shape == (2, 32)
    assert torch.allclose(embeddings.norm(dim=1), torch.ones(2), atol=1e-5)
    assert logits.shape == (2, 3)


def test_one_epoch_training_smoke(tmp_path: Path) -> None:
    root = tmp_path / "images"
    _write_dataset(root)
    manifest = tmp_path / "manifest.csv"
    build_manifest(root, manifest, "synthetic", "normal")
    args = type(
        "Args",
        (),
        {
            "manifest": str(manifest),
            "output_dir": str(tmp_path / "outputs"),
            "epochs": 1,
            "batch_size": 4,
            "learning_rate": 3e-4,
            "weight_decay": 1e-4,
            "embedding_dim": 32,
            "image_size": 112,
            "backbone": "resnet18",
            "margin": 0.5,
            "scale": 64.0,
            "num_workers": 0,
            "seed": 42,
            "device": "cpu",
            "no_pretrained": True,
        },
    )()
    metrics = train(args)
    assert "train_loss" in metrics
    assert (tmp_path / "outputs" / "best.pt").exists()
