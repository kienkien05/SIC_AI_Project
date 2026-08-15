# ESP-WHO Research Note

Research date: 2026-08-12

## Verdict

ESP-WHO is not one end-to-end face model. It is an embedded application framework built on ESP-IDF and ESP-DL. Its face-recognition example composes camera capture, face detection, feature extraction, local feature storage, enrollment, and similarity matching.

For attendance, copy this pipeline contract, not its edge-model capacity. Use a VPS GPU for high-accuracy models and retain an ESP32-P4 only as an optional camera/edge gateway.

## Current ESP-WHO flow

1. Mount local storage for the face-feature database and optional SD card for models.
2. Create a frame-capture pipeline: DVP on ESP32-S3; MIPI-CSI or UVC on ESP32-P4.
3. Start `WhoRecognitionAppLCD` or `WhoRecognitionAppTerm`.
4. Detect face candidates.
5. Extract a face feature embedding.
6. Enroll the feature or compare it against the local database.

The official demo exposes `recognize`, `enroll`, and `delete last feature` controls. Its recognizer integrates `HumanFaceDetect`, `HumanFaceFeat`, and a local `DataBase`.

## Official edge models

### Detection

- `MSR_S8_V1 + MNP_S8_V1`: two-stage candidate/refinement detector. ESP32-P4 reported model time is 13.1 ms plus 2.4 ms; reported custom validation mAP50-95 is 0.366.
- `ESPDET_PICO_224_224_FACE`: one-stage, ESP32-P4 reported model time 49.6 ms; mAP50-95 0.504.
- `ESPDET_PICO_416_416_FACE`: one-stage, ESP32-P4 reported model time 185.9 ms; mAP50-95 0.597.

### Recognition

- `mfn_s8_v1`: 1.2M parameters, 0.46 GFLOPs, reported IJB-C TAR@FAR=1e-4 of 90.03%; ESP32-P4 model time 93.0 ms.
- `mbf_s8_v1`: 3.4M parameters, 0.90 GFLOPs, reported IJB-C TAR@FAR=1e-4 of 93.94%; ESP32-P4 model time 188.2 ms.

These measurements show why ESP-WHO is useful at the edge but insufficient as the sole high-assurance attendance engine: detection, recognition, and image quality must share limited embedded compute.

## What ESP-WHO already gets right

- Pipeline composition rather than identity classification.
- Embedding and similarity matching instead of a fixed classifier label list.
- Explicit enrollment and persistent feature storage.
- Camera capture and inference are asynchronous in the current framework.
- Model deployment path: PyTorch/TensorFlow -> ONNX -> quantization -> `.espdl` model.

## Missing for production attendance

The reviewed examples/docs do not describe these controls, so the VPS system must provide them:

- Multi-frame enrollment with pose and quality diversity.
- Blur, exposure, face-size, occlusion, and duplicate-person gates.
- Presentation-attack/liveness detection.
- Multi-object tracking and temporal voting before writing attendance.
- `unknown` and manual-review outcomes.
- Tenant/user authorization, encryption, retention policy, and audit trail.
- Monitoring for false check-ins, latency, camera failures, and data drift.

## Recommended stronger equivalent

```text
RTSP camera / optional ESP32-P4 gateway
  -> detector
  -> tracker
  -> quality gate
  -> liveness gate
  -> face alignment
  -> ArcFace embedding
  -> vector-gallery cosine search
  -> multi-frame decision
  -> attendance service + dashboard
```

### Model policy

- Keep the current YOLO face-detector notebook as the simple baseline.
- Upgrade detector only after error analysis: server-side YOLO11s/YOLO11m fine-tuned on WIDER plus camera-domain images, or evaluate SCRFD.
- Recognition should be ArcFace-style embedding verification, not LFW identity-classification accuracy.
- Train/fine-tune detector and liveness on consented camera data. Use an enrollment gallery for staff/student identity rather than re-training the recognition classifier whenever a person is added.

### Enrollment contract

Capture 15-30 automatically accepted frames per person: frontal, left/right yaw, small pitch changes, normal lighting, and relevant mask/glasses conditions. Reject blur, low exposure, small face, multiple faces, spoof attempts, and near-duplicate frames. Store several normalized embeddings plus a robust centroid; require a stable match across multiple tracked frames at check-in.

## Deployment decision

- **Recommended MVP:** cameras send RTSP to VPS GPU. All inference and enrollment run server-side.
- **Hybrid later:** ESP32-P4 detects/crops a candidate locally and sends only approved crop/event data to VPS. This reduces bandwidth but adds embedded deployment work.
- **Do not start all-edge:** current edge model latency/accuracy and absence of liveness/quality workflow make it a poorer first implementation for school/factory attendance.

## Sources

- [ESP-WHO repository](https://github.com/espressif/esp-who)
- [ESP-WHO recognition example source](https://raw.githubusercontent.com/espressif/esp-who/master/examples/human_face_recognition/main/app_main.cpp)
- [ESP-WHO recognition controls](https://raw.githubusercontent.com/espressif/esp-who/master/examples/human_face_recognition/README.md)
- [ESP-DL runtime and deployment](https://github.com/espressif/esp-dl)
- [ESP-DL face detection models](https://raw.githubusercontent.com/espressif/esp-dl/master/models/human_face_detect/README.md)
- [ESP-DL face recognition models](https://raw.githubusercontent.com/espressif/esp-dl/master/models/human_face_recognition/README.md)
- [ESP-Detection train/export/quantize/deploy toolchain](https://github.com/espressif/esp-detection)
