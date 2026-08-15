# Attendance ML baseline

Minimal Kaggle-ready recognition training path:

```text
raw images -> pretrained SCRFD detection + five-point alignment
           -> identity folders -> validated manifest -> deterministic split
                -> augmentation -> ResNet embedding + ArcFace loss
                -> best.pt / last.pt + history.jsonl
```

This first baseline trains recognition only. Detection stays on the pretrained SCRFD path until a bbox/landmark annotation set is available for detector fine-tuning.

## Kaggle setup

Add a dataset as Kaggle Input. The dataset must either use identity folders:

```text
/kaggle/input/my-face-data/
  person_001/*.jpg
  person_002/*.jpg
```

or use filenames such as `Person_Name_0001.jpg` and run `--subject-mode filename`.

For raw images, align them first:

```bash
pip install -e '.[align]'

python scripts/align_faces.py \
  --root /kaggle/input/my-face-data \
  --output /kaggle/working/aligned \
  --rejected /kaggle/working/rejected.csv \
  --subject-mode folder
```

Use the aligned output as the `--root` for manifest creation. `align_faces.py` rejects unreadable files, zero-face images, and multi-face images so they cannot silently enter training.

Run from the project root:

```bash
pip install -e .

python scripts/prepare_manifest.py \
  --root /kaggle/input/my-face-data \
  --output /kaggle/working/manifest.csv \
  --source pilot-or-public \
  --scenario normal

python scripts/train_recognition.py \
  --manifest /kaggle/working/manifest.csv \
  --output-dir /kaggle/working/recognition \
  --epochs 5 \
  --batch-size 64 \
  --backbone resnet18 \
  --device auto
```

For a first smoke test, use `resnet18`. After the pipeline is verified, switch to `resnet50`, then replace the backbone with the licensed ArcFace/IResNet50 checkpoint intended for deployment.

## Artifacts

- `manifest.csv`: source, subject, split, dimensions, checksum.
- `best.pt`: best validation checkpoint.
- `last.pt`: latest resumable checkpoint.
- `history.jsonl`: loss and classification accuracy per epoch.
- `config.json`: reproducibility parameters.

## Interpretation

Training accuracy is not production recognition accuracy. The next step must add gallery matching, unknown rejection, FAR/FRR, scenario-sliced evaluation, and pilot-camera data. Do not use LFW accuracy as a deployment guarantee.
