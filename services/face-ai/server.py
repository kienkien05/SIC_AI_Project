from __future__ import annotations

import base64
import json
import os
import re
import shutil
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN, fixed_image_standardization
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from huggingface_hub import hf_hub_download
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO

DATA_DIR = Path(os.getenv("FACE_AI_DATA_DIR", "/data"))
MODEL_DIR = Path(os.getenv("FACE_AI_MODEL_DIR", "/models"))
SEED_PATH = Path(os.getenv("FACE_AI_SEED_PATH", Path(__file__).with_name("seed.json")))
MODEL_SEED = json.loads(SEED_PATH.read_text(encoding="utf-8"))
GALLERY_PATH = DATA_DIR / "gallery.npz"
CROP_DIR = DATA_DIR / "enrollment_crops"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
AI_TOKEN = os.getenv("FACE_AI_TOKEN")
TRANSFORM = transforms.Compose([transforms.Resize((160, 160)), transforms.ToTensor(), fixed_image_standardization])
FACE_TEMPLATE = np.float32([[54.7, 73.9], [105.0, 73.6], [80.0, 102.5], [59.4, 132.0], [101.0, 131.7]])
app = FastAPI(title="SPAS Face AI")


def require_ai_token(x_spas_ai_token: str | None = Header(default=None)) -> None:
    if AI_TOKEN and x_spas_ai_token != AI_TOKEN:
        raise HTTPException(401, "Unauthorized AI request.")


def model_path(env_name: str, filename: str) -> Path:
    configured = os.getenv(env_name)
    if configured:
        return Path(configured)
    return Path(hf_hub_download(repo_id=MODEL_SEED["model_repo"], filename=filename, local_dir=MODEL_DIR, token=os.getenv("HF_TOKEN") or None))


@lru_cache
def models() -> tuple[YOLO, InceptionResnetV1]:
    detector = YOLO(str(model_path("FACE_DETECTOR_PATH", MODEL_SEED["detector_file"])))
    checkpoint = torch.load(model_path("FACE_RECOGNITION_PATH", MODEL_SEED["recognizer_file"]), map_location=DEVICE, weights_only=True)
    recognizer = InceptionResnetV1(classify=False, pretrained=None, num_classes=8631)
    recognizer.load_state_dict(checkpoint["state_dict"], strict=False)
    return detector, recognizer.eval().to(DEVICE)


@lru_cache
def landmark_model() -> MTCNN:
    return MTCNN(keep_all=False, device=DEVICE)


@app.on_event("startup")
def load_models() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    models()


@app.get("/health")
def health() -> dict[str, str]:
    models()
    return {"status": "ok", "device": str(DEVICE), "model_repo": MODEL_SEED["model_repo"]}


def decode(data: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Ảnh camera không hợp lệ.")
    return image


def face_boxes(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    detector, _ = models()
    result = detector(image, imgsz=MODEL_SEED["detector_image_size"], conf=MODEL_SEED["detector_confidence"], verbose=False)[0]
    if result.boxes is None:
        return []
    return [tuple(map(int, box)) for box in result.boxes.xyxy.cpu().numpy()]


def crop(image: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = box
    height, width = image.shape[:2]
    margin_x, margin_y = int((x2 - x1) * 0.2), int((y2 - y1) * 0.2)
    return image[max(0, y1 - margin_y):min(height, y2 + margin_y), max(0, x1 - margin_x):min(width, x2 + margin_x)]


def face_pose(face: np.ndarray) -> tuple[str, float]:
    _, probabilities, landmarks = landmark_model().detect(Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB)), landmarks=True)
    if landmarks is None or probabilities is None or probabilities[0] is None:
        return "unknown", 0.0
    left_eye, right_eye, nose = np.asarray(landmarks[0], dtype=np.float32)[:3]
    eye_width = float(right_eye[0] - left_eye[0])
    if eye_width <= 1:
        return "unknown", float(probabilities[0])
    nose_ratio = float((nose[0] - left_eye[0]) / eye_width)
    return ("left" if nose_ratio < 0.40 else "right" if nose_ratio > 0.60 else "front"), float(probabilities[0])


def align_face(face: np.ndarray) -> np.ndarray:
    best_face = best_landmarks = None
    best_probability = -1.0
    for rotation in (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180):
        candidate = face if rotation is None else cv2.rotate(face, rotation)
        _, probabilities, landmarks = landmark_model().detect(Image.fromarray(cv2.cvtColor(candidate, cv2.COLOR_BGR2RGB)), landmarks=True)
        if landmarks is not None and probabilities is not None and float(probabilities[0]) > best_probability:
            best_face, best_landmarks, best_probability = candidate, landmarks[0], float(probabilities[0])
    if best_face is None:
        return face
    matrix, _ = cv2.estimateAffinePartial2D(np.asarray(best_landmarks, dtype=np.float32), FACE_TEMPLATE, method=cv2.LMEDS)
    return cv2.warpAffine(best_face, matrix, (160, 160), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) if matrix is not None else best_face


def embed(face: np.ndarray) -> np.ndarray:
    _, recognizer = models()
    pixels = TRANSFORM(Image.fromarray(cv2.cvtColor(align_face(face), cv2.COLOR_BGR2RGB))).unsqueeze(0).to(DEVICE)
    with torch.inference_mode():
        vector = torch.nn.functional.normalize(recognizer(pixels), dim=1)[0]
    return vector.cpu().numpy()


def load_gallery() -> tuple[list[str], list[str], np.ndarray]:
    if not GALLERY_PATH.is_file():
        return [], [], np.empty((0, 512), dtype=np.float32)
    with np.load(GALLERY_PATH, allow_pickle=False) as data:
        return data["student_ids"].tolist(), data["names"].tolist(), data["embeddings"]


def save_gallery(student_id: str, name: str, vectors: list[np.ndarray]) -> None:
    student_ids, names, embeddings = load_gallery()
    vector = np.mean(vectors, axis=0)
    vector /= np.linalg.norm(vector)
    if student_id in student_ids:
        index = student_ids.index(student_id)
        names[index], embeddings[index] = name, vector
    else:
        student_ids.append(student_id)
        names.append(name)
        embeddings = np.vstack([embeddings, vector])
    GALLERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez(GALLERY_PATH, student_ids=np.asarray(student_ids), names=np.asarray(names), embeddings=embeddings)


def gallery_match(vectors: list[np.ndarray], ignored_id: str = "") -> tuple[str, str, float]:
    student_ids, names, embeddings = load_gallery()
    allowed = [index for index, student_id in enumerate(student_ids) if student_id != ignored_id]
    if not allowed:
        return "", "", 0.0
    candidate = np.mean(vectors, axis=0)
    candidate /= np.linalg.norm(candidate)
    scores = embeddings @ candidate
    index = max(allowed, key=lambda candidate_index: scores[candidate_index])
    return student_ids[index], names[index], float(scores[index])


def remove_gallery_person(student_id: str) -> None:
    student_ids, names, embeddings = load_gallery()
    kept = [index for index, value in enumerate(student_ids) if value != student_id]
    GALLERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez(GALLERY_PATH, student_ids=np.asarray([student_ids[index] for index in kept]), names=np.asarray([names[index] for index in kept]), embeddings=embeddings[kept] if kept else np.empty((0, 512), dtype=np.float32))


def base64_jpeg(image: np.ndarray) -> str:
    _, encoded = cv2.imencode(".jpg", image)
    return base64.b64encode(encoded).decode("ascii")


def safe_student_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", value)[:50]


def enrollment_faces(frames: list[np.ndarray]) -> list[np.ndarray]:
    faces = []
    for frame in frames:
        boxes = face_boxes(frame)
        if len(boxes) == 1:
            face = crop(frame, boxes[0])
            if min(face.shape[:2]) >= 80:
                faces.append(face)
    return faces[:8]


@app.post("/api/face-pose")
async def detect_face_pose(image: UploadFile = File(), _authorized: None = Depends(require_ai_token)) -> dict:
    frame = decode(await image.read())
    boxes = face_boxes(frame)
    if len(boxes) != 1:
        return {"pose": "unknown", "confidence": 0.0, "detail": "Cần đúng một khuôn mặt trong khung hình."}
    pose, confidence = face_pose(crop(frame, boxes[0]))
    return {"pose": pose, "confidence": confidence, "detail": "" if pose != "unknown" else "Không đọc được điểm neo khuôn mặt."}


@app.post("/api/enroll")
async def enroll(student_id: str = Form(), name: str = Form(), frames: list[UploadFile] = File(), _authorized: None = Depends(require_ai_token)) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id or not name.strip() or len(frames) < 3:
        raise HTTPException(400, "Cần mã, tên và ít nhất 3 frame camera.")
    if student_id in load_gallery()[0]:
        raise HTTPException(409, "Tài khoản đã đăng ký khuôn mặt. Chỉ admin mới có thể reset.")
    faces = enrollment_faces([decode(await frame.read()) for frame in frames])
    if len(faces) < MODEL_SEED["minimum_enrollment_faces"]:
        raise HTTPException(400, "Chưa có đủ frame tốt: cần đúng một khuôn mặt rõ, kích thước đủ lớn.")
    poses = {face_pose(face)[0] for face in faces}
    if not set(MODEL_SEED["required_enrollment_poses"]).issubset(poses):
        raise HTTPException(400, "Enrollment cần đủ pose nhìn thẳng, quay trái và quay phải.")
    vectors = [embed(face) for face in faces]
    matched_id, matched_name, score = gallery_match(vectors, ignored_id=student_id)
    if matched_id and score >= MODEL_SEED["recognition_threshold"]:
        raise HTTPException(409, f"Khuôn mặt đã được đăng ký cho {matched_id} ({matched_name}).")
    save_gallery(student_id, name.strip(), vectors)
    output_dir = CROP_DIR / student_id
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, face in enumerate(faces, 1):
        cv2.imwrite(str(output_dir / f"face_{index:02d}.jpg"), face)
    return {"accepted": len(faces), "previews": [base64_jpeg(face) for face in faces]}


@app.delete("/api/enrollment/{student_id}")
def reset_enrollment(student_id: str, _authorized: None = Depends(require_ai_token)) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id:
        raise HTTPException(400, "Mã không hợp lệ.")
    remove_gallery_person(student_id)
    shutil.rmtree(CROP_DIR / student_id, ignore_errors=True)
    return {"reset": student_id}


@app.get("/api/enrollment/{student_id}/previews")
def enrollment_previews(student_id: str, _authorized: None = Depends(require_ai_token)) -> dict:
    student_id = safe_student_id(student_id)
    previews = []
    for image_path in sorted((CROP_DIR / student_id).glob("face_*.jpg")):
        image = cv2.imread(str(image_path))
        if image is not None:
            previews.append(base64_jpeg(image))
    return {"previews": previews}


@app.post("/api/recognize")
async def recognize(image: UploadFile = File(), _authorized: None = Depends(require_ai_token)) -> dict:
    frame = decode(await image.read())
    student_ids, names, gallery_vectors = load_gallery()
    annotated, results = frame.copy(), []
    for box in face_boxes(frame):
        vector = embed(crop(frame, box))
        student_id = name = "Unknown"
        score = 0.0
        if student_ids:
            index = int((gallery_vectors @ vector).argmax())
            score = float((gallery_vectors @ vector)[index])
            if score >= MODEL_SEED["recognition_threshold"]:
                student_id, name = student_ids[index], names[index]
        x1, y1, x2, y2 = box
        color = (0, 180, 0) if student_id != "Unknown" else (0, 80, 255)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{name} {score:.2f}", (x1, max(24, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        results.append({"student_id": "" if student_id == "Unknown" else student_id, "name": name, "score": score})
    return {"faces": len(results), "results": results, "image": base64_jpeg(annotated)}
