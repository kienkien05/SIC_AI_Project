from __future__ import annotations

import base64
import os
import re
import shutil
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN, fixed_image_standardization
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image
from torchvision import transforms
from ultralytics import YOLO

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("FACE_DEMO_DATA_DIR", APP_DIR / "data"))
GALLERY_PATH = DATA_DIR / "gallery.npz"
CROP_DIR = DATA_DIR / "enrollment_crops"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRANSFORM = transforms.Compose(
    [transforms.Resize((160, 160)), transforms.ToTensor(), fixed_image_standardization]
)
FACE_TEMPLATE = np.float32(
    [[54.7, 73.9], [105.0, 73.6], [80.0, 102.5], [59.4, 132.0], [101.0, 131.7]]
)
app = FastAPI(title="Face Attendance Demo")


def find_model(env_name: str, filename: str) -> Path:
    configured = os.getenv(env_name)
    candidates = [Path(configured)] if configured else []
    candidates += [APP_DIR / "models" / filename, Path.home() / "Downloads" / filename]
    return next((path for path in candidates if path.is_file()), Path(filename))


@app.get("/health")
def health() -> dict[str, str]:
    detector = find_model("FACE_DETECTOR_PATH", "face_best.pt")
    recognizer = find_model("FACE_RECOGNITION_PATH", "facenet_best.pt")
    if not detector.is_file() or not recognizer.is_file():
        raise HTTPException(503, "Face model files are missing.")
    return {"status": "ok", "device": str(DEVICE)}


@lru_cache
def models() -> tuple[YOLO, InceptionResnetV1]:
    detector_path = find_model("FACE_DETECTOR_PATH", "face_best.pt")
    recognizer_path = find_model("FACE_RECOGNITION_PATH", "facenet_best.pt")
    if not detector_path.is_file() or not recognizer_path.is_file():
        raise FileNotFoundError("Đặt face_best.pt và facenet_best.pt trong Downloads hoặc cấu hình biến môi trường model.")
    detector = YOLO(str(detector_path))
    checkpoint = torch.load(recognizer_path, map_location=DEVICE, weights_only=True)
    recognizer = InceptionResnetV1(classify=False, pretrained=None, num_classes=8631)
    recognizer.load_state_dict(checkpoint["state_dict"], strict=False)
    return detector, recognizer.eval().to(DEVICE)


@lru_cache
def landmark_model() -> MTCNN:
    return MTCNN(keep_all=False, device=DEVICE)


def decode(data: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Ảnh camera không hợp lệ.")
    return image


def face_boxes(image_bgr: np.ndarray) -> list[tuple[int, int, int, int]]:
    detector, _ = models()
    result = detector(image_bgr, imgsz=640, conf=0.35, verbose=False)[0]
    if result.boxes is None:
        return []
    return [tuple(map(int, box)) for box in result.boxes.xyxy.cpu().numpy()]


def crop(image_bgr: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = box
    height, width = image_bgr.shape[:2]
    margin_x, margin_y = int((x2 - x1) * 0.2), int((y2 - y1) * 0.2)
    return image_bgr[max(0, y1 - margin_y) : min(height, y2 + margin_y), max(0, x1 - margin_x) : min(width, x2 + margin_x)]


def align_face(face_bgr: np.ndarray) -> np.ndarray:
    """Align five facial landmarks to FaceNet's 160x160 reference crop."""
    rotations = [
        None,
        cv2.ROTATE_90_CLOCKWISE,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
        cv2.ROTATE_180,
    ]
    detector = landmark_model()
    best_candidate = best_landmarks = None
    best_probability = -1.0
    for rotation in rotations:
        candidate = face_bgr if rotation is None else cv2.rotate(face_bgr, rotation)
        face_rgb = cv2.cvtColor(candidate, cv2.COLOR_BGR2RGB)
        _, probabilities, landmarks = detector.detect(Image.fromarray(face_rgb), landmarks=True)
        if landmarks is None or probabilities is None:
            continue
        probability = float(probabilities[0])
        if probability > best_probability:
            best_candidate, best_landmarks, best_probability = candidate, landmarks[0], probability
    if best_candidate is not None:
        matrix, _ = cv2.estimateAffinePartial2D(
            np.asarray(best_landmarks, dtype=np.float32), FACE_TEMPLATE, method=cv2.LMEDS
        )
        if matrix is not None:
            return cv2.warpAffine(
                best_candidate,
                matrix,
                (160, 160),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT,
            )
    return face_bgr


def pose_from_landmarks(landmarks: np.ndarray) -> str:
    left_eye, right_eye, nose = np.asarray(landmarks, dtype=np.float32)[:3]
    eye_width = float(right_eye[0] - left_eye[0])
    if eye_width <= 1:
        return "unknown"
    nose_ratio = float((nose[0] - left_eye[0]) / eye_width)
    if nose_ratio < 0.40:
        return "left"
    if nose_ratio > 0.60:
        return "right"
    return "front"


def face_pose(face_bgr: np.ndarray) -> tuple[str, float]:
    face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    _, probabilities, landmarks = landmark_model().detect(Image.fromarray(face_rgb), landmarks=True)
    if landmarks is None or probabilities is None or probabilities[0] is None:
        return "unknown", 0.0
    return pose_from_landmarks(landmarks[0]), float(probabilities[0])


def embed(face_bgr: np.ndarray) -> np.ndarray:
    _, recognizer = models()
    face_bgr = align_face(face_bgr)
    face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    pixels = TRANSFORM(Image.fromarray(face_rgb)).unsqueeze(0).to(DEVICE)
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
    if not student_ids:
        return "", "", 0.0
    candidate = np.mean(vectors, axis=0)
    candidate /= np.linalg.norm(candidate)
    scores = embeddings @ candidate
    allowed = [index for index, student_id in enumerate(student_ids) if student_id != ignored_id]
    if not allowed:
        return "", "", 0.0
    index = max(allowed, key=lambda candidate_index: scores[candidate_index])
    return student_ids[index], names[index], float(scores[index])


def remove_gallery_person(student_id: str) -> None:
    student_ids, names, embeddings = load_gallery()
    kept = [index for index, value in enumerate(student_ids) if value != student_id]
    GALLERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        GALLERY_PATH,
        student_ids=np.asarray([student_ids[index] for index in kept]),
        names=np.asarray([names[index] for index in kept]),
        embeddings=embeddings[kept] if kept else np.empty((0, 512), dtype=np.float32),
    )


def base64_jpeg(image_bgr: np.ndarray) -> str:
    _, encoded = cv2.imencode(".jpg", image_bgr)
    return base64.b64encode(encoded).decode("ascii")


def safe_student_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", value)[:50]


def best_enrollment_crops(frames: list[np.ndarray]) -> list[np.ndarray]:
    candidates = []
    for frame in frames:
        boxes = face_boxes(frame)
        if len(boxes) != 1:
            continue
        face = crop(frame, boxes[0])
        if min(face.shape[:2]) >= 80:
            candidates.append(face)
    if len(candidates) <= 8:
        return candidates
    indexes = np.linspace(0, len(candidates) - 1, 8, dtype=int)
    return [candidates[index] for index in indexes]


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Face Attendance Demo</title><style>
body{font-family:Arial,sans-serif;max-width:950px;margin:30px auto;padding:0 16px;background:#f6f8fb;color:#172033}h1{margin-bottom:4px}.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:20px}.card{background:white;border-radius:14px;padding:20px;box-shadow:0 2px 12px #0001}video,img{width:100%;border-radius:10px;background:#111}video{transform:scaleX(-1)}input,button{box-sizing:border-box;width:100%;padding:11px;margin:6px 0;border-radius:8px;border:1px solid #d4d9e2}button{background:#1667d9;color:white;border:0;font-weight:bold;cursor:pointer}button:disabled{background:#9da8b8}.hint{color:#526074;min-height:22px}.ok{color:#09833a}.bad{color:#b42318}.crops{display:flex;gap:8px;flex-wrap:wrap}.crops img{width:90px;height:90px;object-fit:cover}.result{margin-top:12px;padding:10px;background:#eef5ff;border-radius:8px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head><body>
<h1>Face Attendance Demo</h1><p>YOLO detect -> FaceNet 512D -> cosine gallery</p>
<div class="grid"><section class="card"><video id="video" autoplay playsinline></video><canvas id="canvas" hidden></canvas><p id="cameraStatus" class="hint">Đang mở camera...</p><button id="scanButton">Quét điểm danh</button><div id="scanResult"></div></section>
<section class="card"><h2>Đăng ký khuôn mặt</h2><input id="studentId" placeholder="MSSV / mã nhân viên"><input id="name" placeholder="Họ tên"><p id="enrollStatus" class="hint">Hệ thống tự chụp 12 frame trong 8 giây.</p><button id="enrollButton">Đăng ký khuôn mặt</button><div id="crops" class="crops"></div></section></div>
<section class="card"><h2>Gallery</h2><div id="gallery" class="hint">Đang tải...</div></section>
<script>
const video=document.querySelector('#video'), canvas=document.querySelector('#canvas');
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function openCamera(){try{video.srcObject=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:1280},height:{ideal:720}},audio:false});document.querySelector('#cameraStatus').textContent='Camera sẵn sàng.'}catch(error){document.querySelector('#cameraStatus').textContent='Không mở được camera: '+error.message;}}
function capture(){return new Promise(resolve=>{canvas.width=video.videoWidth;canvas.height=video.videoHeight;const context=canvas.getContext('2d');context.save();context.translate(canvas.width,0);context.scale(-1,1);context.drawImage(video,0,0);context.restore();canvas.toBlob(resolve,'image/jpeg',.9);});}
async function gallery(){const data=await fetch('/api/gallery').then(r=>r.json());document.querySelector('#gallery').textContent=data.people.length?data.people.map(p=>p.student_id+' - '+p.name).join(' | '):'Chưa có enrollment.';}
document.querySelector('#enrollButton').onclick=async()=>{const id=document.querySelector('#studentId').value.trim(),name=document.querySelector('#name').value.trim(),status=document.querySelector('#enrollStatus');if(!id||!name||!video.videoWidth){status.textContent='Nhập mã, tên và cho phép camera trước.';status.className='hint bad';return;}const actions=['Nhìn thẳng','Quay nhẹ sang trái','Quay nhẹ sang phải','Cúi nhẹ rồi nhìn thẳng'];const frames=[];const button=document.querySelector('#enrollButton');button.disabled=true;for(let index=0;index<12;index++){status.textContent=actions[Math.floor(index/3)]+' ('+(index+1)+'/12)';status.className='hint';frames.push(await capture());await sleep(650);}const form=new FormData();form.append('student_id',id);form.append('name',name);frames.forEach((frame,index)=>form.append('frames',frame,'frame_'+index+'.jpg'));const response=await fetch('/api/enroll',{method:'POST',body:form});const data=await response.json();button.disabled=false;if(!response.ok){status.textContent=data.detail;status.className='hint bad';return;}status.textContent='Đã lưu '+data.accepted+' face crop và embedding 512D.';status.className='hint ok';document.querySelector('#crops').innerHTML=data.previews.map(image=>'<img src="data:image/jpeg;base64,'+image+'">').join('');gallery();};
document.querySelector('#scanButton').onclick=async()=>{if(!video.videoWidth)return;const form=new FormData();form.append('image',await capture(),'scan.jpg');const response=await fetch('/api/recognize',{method:'POST',body:form});const data=await response.json();const result=document.querySelector('#scanResult');if(!response.ok){result.textContent=data.detail;return;}result.innerHTML='<img src="data:image/jpeg;base64,'+data.image+'"><div class="result">'+data.results.map(item=>(item.student_id||'Unknown')+' | '+item.name+' | cosine '+item.score.toFixed(3)).join('<br>')+'</div>';};
openCamera();gallery();
</script></body></html>"""


@app.get("/api/gallery")
def gallery() -> dict:
    student_ids, names, _ = load_gallery()
    return {"people": [{"student_id": student_id, "name": name} for student_id, name in zip(student_ids, names)]}


@app.post("/api/face-pose")
async def detect_face_pose(image: UploadFile = File()) -> dict:
    frame = decode(await image.read())
    boxes = face_boxes(frame)
    if len(boxes) != 1:
        return {"pose": "unknown", "confidence": 0.0, "detail": "Cần đúng một khuôn mặt trong khung hình."}
    face = crop(frame, boxes[0])
    if min(face.shape[:2]) < 80:
        return {"pose": "unknown", "confidence": 0.0, "detail": "Đưa khuôn mặt gần camera hơn."}
    pose, confidence = face_pose(face)
    return {"pose": pose, "confidence": confidence, "detail": "" if pose != "unknown" else "Không đọc được điểm neo khuôn mặt."}


@app.post("/api/enroll")
async def enroll(student_id: str = Form(), name: str = Form(), frames: list[UploadFile] = File()) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id or not name.strip() or len(frames) < 3:
        raise HTTPException(400, "Cần mã, tên và ít nhất 3 frame camera.")
    existing_ids, _, _ = load_gallery()
    if student_id in existing_ids:
        raise HTTPException(409, "Tài khoản đã đăng ký khuôn mặt. Chỉ admin mới có thể reset.")
    face_crops = best_enrollment_crops([decode(await frame.read()) for frame in frames])
    if len(face_crops) < 5:
        raise HTTPException(400, "Chưa có đủ 5 frame tốt: cần đúng một khuôn mặt rõ, kích thước đủ lớn.")
    face_crops = face_crops[:8]
    poses = {face_pose(face)[0] for face in face_crops}
    if not {"front", "left", "right"}.issubset(poses):
        raise HTTPException(400, "Enrollment cần đủ pose nhìn thẳng, quay trái và quay phải.")
    vectors = [embed(face) for face in face_crops]
    matched_id, matched_name, score = gallery_match(vectors, ignored_id=student_id)
    if matched_id and score >= 0.60:
        raise HTTPException(409, f"Khuôn mặt đã được đăng ký cho {matched_id} ({matched_name}).")
    save_gallery(student_id, name.strip(), vectors)
    output_dir = CROP_DIR / student_id
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, face in enumerate(face_crops, 1):
        cv2.imwrite(str(output_dir / f"face_{index:02d}.jpg"), face)
    return {"accepted": len(face_crops), "previews": [base64_jpeg(face) for face in face_crops]}


@app.post("/api/check-enrollment")
async def check_enrollment(student_id: str = Form(), frames: list[UploadFile] = File()) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id or len(frames) < 3:
        raise HTTPException(400, "Cần mã và ít nhất 3 frame camera.")
    face_crops = best_enrollment_crops([decode(await frame.read()) for frame in frames])
    if len(face_crops) < 5:
        raise HTTPException(400, "Chưa có đủ 5 frame rõ, đúng một khuôn mặt.")
    matched_id, matched_name, score = gallery_match([embed(face) for face in face_crops[:8]], ignored_id=student_id)
    return {"duplicate": bool(matched_id and score >= 0.60), "student_id": matched_id, "name": matched_name, "score": score}


@app.delete("/api/enrollment/{student_id}")
def reset_enrollment(student_id: str) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id:
        raise HTTPException(400, "Mã không hợp lệ.")
    remove_gallery_person(student_id)
    shutil.rmtree(CROP_DIR / student_id, ignore_errors=True)
    return {"reset": student_id}


@app.get("/api/enrollment/{student_id}/previews")
def enrollment_previews(student_id: str) -> dict:
    student_id = safe_student_id(student_id)
    if not student_id:
        raise HTTPException(400, "Mã không hợp lệ.")
    previews = []
    for image_path in sorted((CROP_DIR / student_id).glob("face_*.jpg")):
        image = cv2.imread(str(image_path))
        if image is not None:
            previews.append(base64_jpeg(image))
    return {"previews": previews}


@app.post("/api/recognize")
async def recognize(image: UploadFile = File()) -> dict:
    frame = decode(await image.read())
    student_ids, names, gallery_vectors = load_gallery()
    annotated, results = frame.copy(), []
    for box in face_boxes(frame):
        vector = embed(crop(frame, box))
        score = 0.0
        student_id = name = "Unknown"
        if student_ids:
            scores = gallery_vectors @ vector
            index = int(scores.argmax())
            score = float(scores[index])
            if score >= 0.60:
                student_id, name = student_ids[index], names[index]
        x1, y1, x2, y2 = box
        color = (0, 180, 0) if student_id != "Unknown" else (0, 80, 255)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{name} {score:.2f}", (x1, max(24, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        results.append({"student_id": student_id if student_id != "Unknown" else "", "name": name, "score": score})
    return {"faces": len(results), "results": results, "image": base64_jpeg(annotated)}
