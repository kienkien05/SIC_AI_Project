from __future__ import annotations

import csv
import hashlib
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class Sample:
    path: str
    subject_id: str
    split: str
    source: str
    scenario: str
    width: int
    height: int
    sha256: str


def _subject_id(path: Path, root: Path, mode: str) -> str:
    relative = path.relative_to(root)
    if mode == "folder":
        if len(relative.parts) < 2:
            raise ValueError(f"Folder mode needs identity subdirectories: {path}")
        return relative.parts[0]
    if mode == "filename":
        return re.sub(r"_\d+$", "", path.stem)
    raise ValueError(f"Unsupported subject mode: {mode}")


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _split_subject_samples(
    paths: list[Path],
    root: Path,
    subject_mode: str,
    val_fraction: float,
    test_fraction: float,
    rng: random.Random,
) -> dict[str, str]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        grouped[_subject_id(path, root, subject_mode)].append(path)

    split_by_path: dict[str, str] = {}
    for subject, subject_paths in grouped.items():
        shuffled = list(subject_paths)
        rng.shuffle(shuffled)
        total = len(shuffled)
        test_count = max(1, round(total * test_fraction)) if total >= 3 else 0
        val_count = max(1, round(total * val_fraction)) if total >= 2 else 0
        while total - test_count - val_count < 1:
            if test_count > 0:
                test_count -= 1
            elif val_count > 0:
                val_count -= 1
            else:
                break

        for path in shuffled[:val_count]:
            split_by_path[str(path)] = "val"
        test_start = val_count
        for path in shuffled[test_start : test_start + test_count]:
            split_by_path[str(path)] = "test"
        for path in shuffled[val_count + test_count :]:
            split_by_path[str(path)] = "train"

        if not any(split_by_path[str(path)] == "train" for path in shuffled):
            split_by_path[str(shuffled[-1])] = "train"

    return split_by_path


def build_manifest(
    root: str | Path,
    output: str | Path,
    source: str,
    scenario: str,
    subject_mode: str = "folder",
    val_fraction: float = 0.15,
    test_fraction: float = 0.15,
    seed: int = 42,
) -> dict[str, int]:
    root_path = Path(root).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    if not root_path.is_dir():
        raise FileNotFoundError(f"Dataset root does not exist: {root_path}")
    if val_fraction < 0 or test_fraction < 0 or val_fraction + test_fraction >= 1:
        raise ValueError("val_fraction + test_fraction must be in [0, 1)")

    paths = sorted(
        path
        for path in root_path.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not paths:
        raise ValueError(f"No images found under {root_path}")

    split_by_path = _split_subject_samples(
        paths,
        root_path,
        subject_mode,
        val_fraction,
        test_fraction,
        random.Random(seed),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = defaultdict(int)
    skipped = 0
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "path",
            "subject_id",
            "split",
            "source",
            "scenario",
            "width",
            "height",
            "sha256",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for path in paths:
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    width, height = image.size
                subject = _subject_id(path, root_path, subject_mode)
                split = split_by_path[str(path)]
                writer.writerow(
                    {
                        "path": str(path),
                        "subject_id": subject,
                        "split": split,
                        "source": source,
                        "scenario": scenario,
                        "width": width,
                        "height": height,
                        "sha256": _sha256(path),
                    }
                )
                counts[split] += 1
            except Exception:
                skipped += 1

    if counts["train"] == 0 or len({
        row["subject_id"] for row in read_manifest(output_path) if row["split"] == "train"
    }) < 2:
        raise ValueError("Manifest needs at least two identities in train split")
    counts["skipped"] = skipped
    return dict(counts)


def read_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class ManifestDataset(Dataset[tuple[object, int]]):
    def __init__(
        self,
        rows: Iterable[dict[str, str]],
        label_to_index: dict[str, int],
        transform: transforms.Compose,
    ) -> None:
        self.rows = list(rows)
        self.label_to_index = label_to_index
        self.transform = transform

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[object, int]:
        row = self.rows[index]
        with Image.open(row["path"]) as image:
            image_rgb = image.convert("RGB")
        return self.transform(image_rgb), self.label_to_index[row["subject_id"]]


def make_transforms(image_size: int = 112) -> tuple[transforms.Compose, transforms.Compose]:
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size, scale=(0.85, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.15),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    return train_transform, eval_transform


def label_map_from_rows(rows: Iterable[dict[str, str]]) -> dict[str, int]:
    labels = sorted({row["subject_id"] for row in rows if row["split"] == "train"})
    return {label: index for index, label in enumerate(labels)}
