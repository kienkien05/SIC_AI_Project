# Face Attendance — Data Plan

## Objective

Build a reproducible dataset pipeline for two separate tasks:

1. face detection and five-point landmark localization;
2. open-set face recognition through embeddings, gallery matching, and unknown rejection.

Public datasets provide baseline coverage. Pilot camera data remains mandatory for domain adaptation, threshold calibration, and final acceptance.

## Dataset roles

| Dataset | Role | Decision |
|---|---|---|
| [WIDER FACE](https://www.kaggle.com/datasets/mksaad/wider-face-a-face-detection-benchmark) | crowded/occluded face detection baseline | use for detector pretraining or fine-tuning only; verify source license before redistribution |
| [LFW](https://www.kaggle.com/datasets/quadeer15sh/lfw-facial-recognition) | pipeline smoke test and verification benchmark | use for development only; it is not evidence of production suitability |
| [Dark Face](https://www.kaggle.com/datasets/soumikrakshit/dark-face-dataset) | low-light detection stress test | use only after license/provenance review |
| [Masked Face Recognition](https://www.kaggle.com/datasets/nanimasaka/masked-face-recognition-dataset) | mask/partial-occlusion stress test | use for experiments; only 19 identities, so not a production recognition set |
| [Anti-Spoofing Dataset](https://www.kaggle.com/datasets/axondata/face-anti-spoofing-dataset) | liveness/PAD phase | defer until the base attendance flow works; license is non-commercial |

Kaggle copies are convenient mirrors, not automatic permission for commercial biometric use. Each dataset gets a `source_url`, `license`, `download_date`, `sha256`, and `allowed_use` record before entering a training run.

## Required data contract

Every sample manifest row must contain:

```text
sample_id, source, source_url, relative_path, split, subject_id,
session_id, camera_id, scenario, label, bbox, landmarks,
quality_score, consent_status, license, dataset_version, sha256
```

Rules:

- `subject_id` is pseudonymous; never use a real name in ML files.
- Raw enrollment images and video stay outside source control.
- Training and serving use the same decode, color, crop, alignment, and normalization code.
- Test data stays immutable after threshold selection.
- Every trained model points to an immutable dataset version.

## Collection plan for pilot data

For each consenting person, collect multiple sessions rather than many near-duplicate frames from one session:

- enrollment: 5–10 clear images for the gallery;
- training: short clips or images across normal, difficult, and camera-specific conditions;
- evaluation: a later session, held out from training;
- unknown set: people never enrolled in the gallery.

Capture the same scenario matrix for both school and factory profiles. Do not mix class/department labels into the face model; those belong to the attendance domain layer.

## Split policy

- Detector: split by image/event source; keep the pilot camera set out of training for final validation.
- Recognition: split by `subject_id` and `session_id`; never split adjacent frames from one clip across train and test.
- Threshold calibration: validation only.
- Final report: immutable test set, including unknown identities and hard cases.

## Preparation pipeline

```text
raw -> validate -> deduplicate -> annotate -> quality filter
    -> face detect -> landmark align -> normalize -> manifest
    -> split -> augment train only -> train/evaluate
```

Required checks:

- corrupt or unreadable files;
- duplicate and near-duplicate frames;
- missing identity or conflicting labels;
- invalid bounding boxes and landmarks;
- face too small, blur, severe darkness, or heavy occlusion;
- class and scenario balance;
- train/test leakage;
- license and consent completeness.

## First experiment

1. Download WIDER FACE and LFW into Kaggle input storage.
2. Build a manifest without copying images into the repository.
3. Run pretrained detector and embedding baseline.
4. Evaluate by scenario, not only aggregate accuracy.
5. Add pilot camera samples and recalibrate threshold.
6. Fine-tune only the component whose error analysis justifies it.

## Promotion gate

Do not promote a model because one benchmark score is high. Require:

- detector recall/precision report by face size and scenario;
- recognition FAR/FRR and unknown rejection report;
- event-level duplicate and review rates;
- latency and memory benchmark on target VPS;
- manual review of false accepts and false rejects;
- model, preprocessing, threshold, and dataset versions recorded together.

## Data safety

Biometric data is sensitive. Store raw images encrypted with limited retention, keep database access private, redact logs, and provide deletion/audit flows before using real school or factory data.
