# Model 1 — Face Detection

## Mục tiêu

Phát hiện toàn bộ khuôn mặt trong khung camera điểm danh. Một class duy nhất: `face`.

Không nhận diện danh tính, không phân loại khẩu trang, không chống giả mạo trong model này.

## Dataset chọn

| Vai trò | Dataset | Dùng thế nào |
| --- | --- | --- |
| Train chính | WIDER FACE đầy đủ | Bounding box, đa người, mặt nhỏ, pose, che khuất, nền phức tạp. |
| Fine-tune domain | CCTV masked-face YOLO | Remap mọi class có box mặt thành `face`; chỉ dùng sau WIDER. |
| Validation cuối | Camera thật tại cổng/lớp/xưởng | Không dùng train; 500–1,000 frame đã gán nhãn. |

## Kaggle dataset

- WIDER raw, ưu tiên nguồn gần bản benchmark: `mksaad/wider-face-a-face-detection-benchmark`.
- Nếu cần train ngay theo YOLO format: `canomercik/wider-face-dataset-for-yolov12-format`.
- Fine-tune mask/CCTV: `mariamali333/labelled-face-mask-dataset-of-cctv-footage` hoặc `parot99/face-mask-detection-yolo-darknet-format`.

Không dùng LFW, WebFace, Masked Face Recognition hay Livesess cho detector: chúng thuộc recognition/liveness hoặc không có box detector phù hợp.

## Task nhỏ

1. Attach WIDER full; kiểm image/label và số box.
2. Chuẩn hoá WIDER sang YOLO class `0=face`.
3. Tạo split train/val theo split gốc, không random lại.
4. Attach mask/CCTV; remap classes về `face` và kiểm label.
5. Train `YOLO11n`, `imgsz=640`, batch per GPU phù hợp VRAM, 50 epoch.
6. Fine-tune mask/CCTV 10–20 epoch với learning rate thấp.
7. Đánh giá WIDER và tập camera thật: Recall là metric chính; mục tiêu recall >= 90% ở ngưỡng vận hành.

## Acceptance

- Không có ảnh thiếu label hoặc label ngoài ảnh.
- Tất cả label chỉ còn class `0`.
- Báo Precision, Recall, mAP50, mAP50-95 và false negatives theo tình huống: đông người, xa, tối, khẩu trang.
- Chỉ deploy checkpoint sau khi pass tập camera thật độc lập.

## Cloud artifact

- Checkpoint chuẩn: `best.pt` của `YOLO11n`.
- Notebook copy `best.pt`, `last.pt`, `results.csv`, `args.yaml` vào `/kaggle/working/model-1-face-detector/`.
- Kaggle giữ các file trong phần Output của kernel; tải bằng Kaggle API khi deploy VPS.
