from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def subject_id(path: Path, root: Path, mode: str) -> str:
    relative = path.relative_to(root)
    if mode == "folder":
        if len(relative.parts) < 2:
            raise ValueError(f"Folder mode needs identity subdirectories: {path}")
        return relative.parts[0]
    name = path.stem
    while name and name[-1].isdigit():
        name = name[:-1]
    return name.rstrip("_-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect and align one face per image")
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rejected", required=True)
    parser.add_argument("--subject-mode", choices=["folder", "filename"], default="folder")
    parser.add_argument("--model-name", default="buffalo_m")
    parser.add_argument("--image-size", type=int, default=112)
    parser.add_argument("--det-size", type=int, default=640)
    args = parser.parse_args()

    import cv2
    import onnxruntime as ort
    from insightface.app import FaceAnalysis
    from insightface.utils.face_align import norm_crop

    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    rejected_path = Path(args.rejected).expanduser().resolve()
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    has_cuda = "CUDAExecutionProvider" in ort.get_available_providers()
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if has_cuda else ["CPUExecutionProvider"]
    app = FaceAnalysis(name=args.model_name, providers=providers)
    app.prepare(ctx_id=0 if has_cuda else -1, det_size=(args.det_size, args.det_size))

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    rejected: list[tuple[str, str]] = []
    accepted = 0
    with rejected_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "reason"])
        for path in files:
            image = cv2.imread(str(path))
            if image is None:
                rejected.append((str(path), "unreadable"))
                continue
            faces = app.get(image)
            if len(faces) != 1:
                rejected.append((str(path), f"face_count={len(faces)}"))
                continue
            face = faces[0]
            try:
                subject = subject_id(path, root, args.subject_mode)
                aligned = norm_crop(image, face.kps, image_size=args.image_size)
            except Exception as error:
                rejected.append((str(path), f"alignment_error={type(error).__name__}"))
                continue
            relative_key = str(path.relative_to(root)).encode("utf-8")
            suffix = hashlib.sha1(relative_key).hexdigest()[:10]
            target_dir = output / subject
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / f"{path.stem}_{suffix}.png"
            if not cv2.imwrite(str(target), aligned):
                rejected.append((str(path), "write_failed"))
                continue
            accepted += 1
        writer.writerows(rejected)
    print({"accepted": accepted, "rejected": len(rejected), "output": str(output)})


if __name__ == "__main__":
    main()
