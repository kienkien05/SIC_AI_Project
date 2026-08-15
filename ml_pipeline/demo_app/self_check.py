from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from server import pose_from_landmarks


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "gallery.npz"
        vector = np.ones(512, dtype=np.float32)
        vector /= np.linalg.norm(vector)
        np.savez(path, student_ids=np.asarray(["SV001"]), names=np.asarray(["Demo Student"]), embeddings=np.asarray([vector]))
        with np.load(path, allow_pickle=False) as gallery:
            score = float(gallery["embeddings"][0] @ vector)
            assert gallery["student_ids"].tolist() == ["SV001"]
        assert score > 0.999
    landmarks = np.asarray([[0, 0], [100, 0], [50, 25], [25, 70], [75, 70]], dtype=np.float32)
    assert pose_from_landmarks(landmarks) == "front"
    landmarks[2, 0] = 30
    assert pose_from_landmarks(landmarks) == "left"
    landmarks[2, 0] = 70
    assert pose_from_landmarks(landmarks) == "right"
    print("Gallery self-check passed.")


if __name__ == "__main__":
    main()
