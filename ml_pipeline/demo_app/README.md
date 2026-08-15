# Face AI service

FastAPI service combining YOLO face detection (`face_best.pt`) and FaceNet recognition (`facenet_best.pt`). It is called only by `ai-adapter-service`; browsers never call it directly.

Enrollment accepts eight camera frames and requires clear front, left and right poses. MTCNN aligns each face before creating a 512-D FaceNet embedding.

## Cloud deployment

Use the repository-root command in [CLOUD_AI_SETUP.md](../../CLOUD_AI_SETUP.md). Set `FACE_AI_TOKEN` before the service starts. All biometric endpoints require the matching `x-spas-ai-token` header; keep port `8503` behind an HTTPS reverse proxy.

## Local AI development

```powershell
python -m pip install -r requirements.txt
$env:FACE_DETECTOR_PATH = "../../models/face_best.pt"
$env:FACE_RECOGNITION_PATH = "../../models/facenet_best.pt"
$env:FACE_AI_TOKEN = "local-development-token"
python -m uvicorn server:app --host 127.0.0.1 --port 8503
```

`data/gallery.npz` and `data/enrollment_crops/` contain biometric gallery state. They are ignored by Git; secure their storage and backups.

## Checks

```powershell
python model_check.py
python self_check.py
```
