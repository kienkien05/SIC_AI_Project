from __future__ import annotations

from pathlib import Path

import cv2
import torch
from facenet_pytorch import InceptionResnetV1, fixed_image_standardization
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO

from server import align_face

ROOT = Path(__file__).resolve().parents[2]
DETECTOR_PATH = Path.home() / "Downloads" / "face_best.pt"
RECOGNITION_PATH = Path.home() / "Downloads" / "facenet_best.pt"
IMAGE_PATH = ROOT / "artifacts" / "external-face-test" / "images" / "two_people.jpg"


def main() -> None:
    detector = YOLO(DETECTOR_PATH)
    checkpoint = torch.load(RECOGNITION_PATH, map_location="cpu", weights_only=True)
    recognizer = InceptionResnetV1(classify=False, pretrained=None, num_classes=8631).eval()
    recognizer.load_state_dict(checkpoint["state_dict"], strict=False)
    image = cv2.cvtColor(cv2.imread(str(IMAGE_PATH)), cv2.COLOR_BGR2RGB)
    boxes = detector(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), conf=0.35, verbose=False)[0].boxes.xyxy.cpu().numpy()
    transform = transforms.Compose([transforms.Resize((160, 160)), transforms.ToTensor(), fixed_image_standardization])
    x1, y1, x2, y2 = boxes[0].astype(int)
    aligned = align_face(cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_RGB2BGR))
    with torch.inference_mode():
        vector = recognizer(transform(Image.fromarray(image[y1:y2, x1:x2])).unsqueeze(0))[0]
    assert len(boxes) == 2
    assert vector.shape == (512,)
    assert aligned.shape == (160, 160, 3)
    print({"faces_detected": len(boxes), "embedding_dim": vector.numel(), "aligned_shape": aligned.shape})


if __name__ == "__main__":
    main()
