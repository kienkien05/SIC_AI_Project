# Báo cáo thực nghiệm Model 1: Phát hiện khuôn mặt cho hệ thống điểm danh tự động

**Phiên bản:** 1.0  
**Ngày thực nghiệm:** 12/08/2026  
**Phạm vi:** Model 1 của pipeline điểm danh. Đầu ra là bounding box `face`; model không nhận diện danh tính, không phân loại người và không phát hiện giả mạo.

## Tóm tắt

Báo cáo trình bày việc xây dựng baseline phát hiện khuôn mặt cho hệ thống điểm danh tự động theo kiến trúc pipeline lấy cảm hứng từ ESP-WHO. YOLO11n được fine-tune từ trọng số pretrained `yolo11n.pt` trên WIDER FACE đã chuyển sang định dạng YOLO một lớp. Lần chạy sử dụng 12.880 ảnh huấn luyện, 3.226 ảnh validation và 39.707 face instances ở validation; ảnh được đưa về đầu vào 640 × 640 và tăng cường dữ liệu online trong Ultralytics. Sau 50 epoch trên một Tesla T4, checkpoint tốt nhất tại epoch 47 đạt precision 84,39%, recall 59,40%, mAP50 66,47% và mAP50-95 35,54%. Kết quả cho thấy detector đủ làm tầng crop đầu vào cho recognition, nhưng recall chưa đủ để tự đưa ra quyết định điểm danh từ một frame. Hệ thống hoàn chỉnh phải kết hợp tracking, voting nhiều frame, liveness và cơ chế `unknown`.

**Từ khóa:** face detection, YOLO11n, WIDER FACE, điểm danh tự động, computer vision.

## Abstract

This report describes a baseline face detector for an automated attendance pipeline inspired by the staged ESP-WHO architecture. A YOLO11n detector initialized from `yolo11n.pt` was fine-tuned on a one-class YOLO-format WIDER FACE mirror. The run used 12,880 training images and a validation split of 3,226 images containing 39,707 face instances. With 640 × 640 input and online augmentation, the best checkpoint at epoch 47 achieved 84.39% precision, 59.40% recall, 66.47% mAP50, and 35.54% mAP50-95 on the validation split. The detector is adequate as the face-cropping stage for downstream recognition, but its recall does not support single-frame attendance decisions. Production deployment therefore requires temporal voting, tracking, presentation-attack detection, and an unknown-person fallback.

**Keywords:** face detection, YOLO11n, WIDER FACE, automated attendance, computer vision.

## 1. Giới thiệu

Điểm danh bằng camera cần tách hai bài toán khác nhau: phát hiện vị trí khuôn mặt và xác định danh tính. Model 1 chỉ giải quyết bài toán thứ nhất: tìm tất cả khuôn mặt trong mỗi frame để tạo face crop cho Model 2 ArcFace embedding. Việc tách module giúp thêm người mới bằng enrollment embeddings thay vì phải train lại detector hoặc classifier danh tính.

WIDER FACE được chọn vì là benchmark phát hiện khuôn mặt trong điều kiện không kiểm soát, có biến thiên lớn về scale, pose, occlusion và bối cảnh [1]. Các thuộc tính này gần với camera cổng trường hoặc nhà máy hơn bộ dữ liệu chân dung có một khuôn mặt rõ nét. Tuy nhiên, WIDER FACE không thay thế kiểm thử tại địa điểm triển khai; camera thật, góc đặt, ánh sáng, khẩu trang và khoảng cách vẫn cần được đánh giá riêng.

## 2. Vật liệu và phương pháp

### 2.1. Dữ liệu

Dataset nguồn là WIDER FACE, gồm 32.203 ảnh và 393.703 bounding box khuôn mặt theo công bố gốc [1]. Thực nghiệm dùng mirror Kaggle đã chuyển nhãn về YOLO format: [`canomercik/wider-face-dataset-for-yolov12-format`](https://www.kaggle.com/datasets/canomercik/wider-face-dataset-for-yolov12-format). Cấu hình dữ liệu chỉ định một nhãn:

```yaml
names:
  0: face
```

Theo log train, split được dùng gồm 12.880 ảnh train và 3.226 ảnh validation có 39.707 face instances. Test split không được đưa vào `face.yaml`, do đó mọi metric trong báo cáo là metric validation của mirror Kaggle, không phải điểm official WIDER FACE easy/medium/hard.

### 2.2. Khám phá dữ liệu và kiểm tra tính hợp lệ

EDA trong notebook tối giản theo yêu cầu MVP, gồm:

1. Duyệt input để tìm thư mục dataset có `train/images`, tránh phụ thuộc tên thư mục con của Kaggle.
2. Tìm split validation theo thứ tự `valid/images`, sau đó `val/images`.
3. Dừng bằng `assert` nếu validation split không tồn tại.
4. Sinh `face.yaml` độc lập với thư mục checkpoint để DDP/output cleanup không xóa cấu hình dữ liệu.
5. Xác nhận bằng log train số ảnh và instances của validation split.

Các phép EDA **chưa thực hiện** trong notebook 3 cell là histogram diện tích box, số face mỗi ảnh, tỷ lệ face nhỏ, tỷ lệ ảnh không nhãn và preview ngẫu nhiên nhãn. Vì vậy báo cáo không suy diễn các phân bố này. Đây là hạng mục bắt buộc trước lần fine-tune tiếp theo vì recall thấp có thể tập trung ở nhóm face nhỏ hoặc bị che khuất.

### 2.3. Tiền xử lý và augmentation

Không tạo bản sao blur/mask hay chỉnh nhãn offline. Mirror đầu vào đã ở YOLO format; Ultralytics đọc ảnh, letterbox/resize về 640 × 640 và biến đổi box tương ứng trong dataloader [2]. Augmentation được áp dụng online để giữ nguyên dữ liệu gốc và tái lập được qua checkpoint `train_args`:

| Augmentation | Giá trị |
|---|---:|
| HSV hue / saturation / value | `0.015 / 0.7 / 0.4` |
| Translation | `0.1` |
| Scale | `0.5` |
| Horizontal flip | `0.5` |
| Mosaic | `1.0`, đóng trong 10 epoch cuối |
| Blur, MedianBlur, ToGray, CLAHE | mỗi phép `p=0.01` theo log Ultralytics |
| Rotation, shear, perspective, vertical flip | `0.0` |
| MixUp, CutMix, Copy-Paste | `0.0` |

Hai trường `auto_augment=randaugment` và `erasing=0.4` có mặt trong `train_args`, nhưng tài liệu Ultralytics hiện hành đánh dấu chúng là augmentation cho classification, không phải detector [2]. Chúng không được diễn giải là augmentation detector đã áp dụng.

### 2.4. Kiến trúc và cấu hình huấn luyện

YOLO11n được khởi tạo từ `yolo11n.pt` pretrained; model sau fine-tune chỉ còn một class `face`. Ultralytics hỗ trợ train/validation bằng Python API và cấu hình hyperparameter theo arguments [2]. Cấu hình tái lập được trích trực tiếp từ checkpoint và log:

| Thuộc tính | Giá trị |
|---|---|
| Framework | Ultralytics `8.4.118`, PyTorch `2.10.0+cu128` |
| Kiến trúc | YOLO11n detect, 1 class |
| Weight khởi tạo | `yolo11n.pt` pretrained |
| Kích thước input | 640 × 640 |
| Epoch | 50 |
| Batch size | 8 |
| DataLoader workers | 4 |
| Thiết bị | `CUDA:0`, Tesla T4 14.912 MiB |
| Mixed precision | AMP bật |
| Seed / deterministic | `0` / bật |
| Optimizer | `auto` của Ultralytics |
| Learning rate đầu / cuối | `0.01 / 0.01` |
| Momentum / weight decay | `0.937 / 0.0005` |
| Warmup | 3 epoch |
| Loss weights (`box`, `cls`, `dfl`) | `7.5`, `0.5`, `1.5` |

Checkpoint raw có 2.590.035 tham số. Sau fuse để inference, log báo 2.582.347 tham số và 6,4 GFLOPs [3]. Thử nghiệm DDP 2 T4 trước đó gây lỗi bộ nhớ/NCCL ở `rank1`; run tạo checkpoint dùng một GPU (`device=0`) để bảo đảm hoàn tất. Tổng thời gian train là 3,071 giờ.

## 3. Kết quả

### 3.1. Kết quả validation

`face_best.pt` được chọn theo fitness `mAP50-95` cao nhất tại epoch 47. Bảng 1 sử dụng metric full precision lưu trong checkpoint; final validation log của `best.pt` làm tròn thành `P=0,843`, `R=0,594`, `mAP50=0,663`, `mAP50-95=0,354` [3].

**Bảng 1. Hiệu năng validation của checkpoint.**

| Checkpoint | Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| `face_best.pt` | 47 | 84,39% | 59,40% | 66,47% | 35,54% |
| `face_last.pt` | 50 | 84,48% | 59,45% | 66,37% | 35,49% |

Loss train giảm từ `box=1,9366`, `cls=1,4975`, `dfl=1,1408` ở epoch 1 xuống `box=1,3958`, `cls=0,6477`, `dfl=0,9548` ở epoch 50. mAP50-95 tăng từ 23,99% lên vùng 35,5% rồi ổn định ở cuối run. Điều này cho thấy train hội tụ, nhưng việc cải thiện sau epoch 40 là rất nhỏ.

### 3.2. Tốc độ và sanity check ngoài WIDER FACE

Final validation trên T4 báo 0,2 ms preprocessing, 1,6 ms inference và 1,2 ms postprocessing mỗi ảnh [3]. Một sanity check CPU với threshold `conf=0.25` trên bốn ảnh công khai ngoài WIDER FACE (ba ảnh đơn và một ảnh hai người) phát hiện đúng số face theo quan sát: `1/1/1/2`, tức 5/5 face; confidence của `face_best.pt` là 0,8424–0,9052. Đây chỉ là kiểm tra tích hợp model, không phải benchmark hoặc ước lượng accuracy production.

## 4. Thảo luận

Precision 84,39% cho thấy phần lớn box được dự đoán là face, trong khi recall 59,40% cho thấy detector vẫn bỏ sót nhiều khuôn mặt trong validation. Đây là rủi ro đáng kể với điểm danh: quyết định trực tiếp từ một frame có thể chuyển một người có mặt thành vắng. Vì vậy, detector chỉ nên là tầng đầu của pipeline:

```text
camera/RTSP → face detection → tracking → quality gate → liveness
→ ArcFace embedding → cosine gallery search → vote nhiều frame → attendance rule
```

Trong pipeline này, tracking và vote nhiều frame giảm phụ thuộc vào một lần detect; `unknown` hoặc manual review được ưu tiên hơn một check-in sai. Model 1 chưa đánh giá theo nhóm mask, kính, ánh sáng yếu, pose, face nhỏ hoặc camera cụ thể. Không có kết quả liveness, recognition, TAR/FAR hay false check-in trong báo cáo này; các metric đó thuộc Model 2/3 và tầng decision.

Một hạn chế tái lập là console đính kèm có thông báo NCCL watchdog từ một worker DDP xen trong log. Tuy nhiên, phần kết thúc log xác nhận hoàn thành 50 epoch, lưu `best.pt`/`last.pt` và validate lại `best.pt`. Để audit nghiêm ngặt, lần chạy kế tiếp cần dùng kernel single-GPU sạch, lưu `results.csv`, `args.yaml`, confusion matrix và ảnh validation cùng checkpoint.

## 5. Kết luận

YOLO11n fine-tuned trên WIDER FACE đã tạo được baseline face detector một lớp, đủ để crop mặt cho module recognition tiếp theo. `face_best.pt` tại epoch 47 là artifact được chọn với mAP50-95 35,54%. Hạn chế chính là recall 59,40%, do đó model chưa đủ làm cơ chế điểm danh độc lập. Ưu tiên tiếp theo là xây dựng tập đánh giá camera có consent, phân tích lỗi theo face-size/ánh sáng/occlusion, sau đó mới quyết định tăng lên YOLO11s/YOLO11m, tăng input resolution hoặc fine-tune bằng ảnh camera thực.

## Tái lập thực nghiệm và artifact

| Artifact | Mục đích | SHA-256 |
|---|---|---|
| `C:\Users\dangv\Downloads\face_best.pt` | Checkpoint deployment Model 1 | `1b4073b25c14e36cb922b1ec83aaffebda3d9b0b103da09a42847c5039ca68f5` |
| `C:\Users\dangv\Downloads\face_last.pt` | Checkpoint epoch cuối để đối chiếu | `99cffd4187daedbd94e023a867aa5a1ceac3ca751e22aed50fdd8e13d0f21f1d` |
| `ml_pipeline/kaggle_detector_kernel/yolo11n_face_detector.ipynb` | Notebook train 3 cell | — |
| `artifacts/external-face-test/results.json` | Kết quả sanity check ngoài WIDER FACE | — |

## Đạo đức và quản trị dữ liệu

Hệ thống dùng dữ liệu sinh trắc học. Khi thu ảnh camera/enrollment cần thông báo mục đích, lấy consent phù hợp, giới hạn quyền truy cập, mã hóa embedding và ảnh audit, áp dụng thời hạn xóa dữ liệu, và có luồng khiếu nại/sửa kết quả. Không sử dụng detector để suy diễn thuộc tính nhạy cảm; không tự động kỷ luật/chấm công chỉ từ một prediction có độ tin cậy thấp.

## Tài liệu tham khảo

[1] S. Yang, P. Luo, C.-C. Loy, and X. Tang, “WIDER FACE: A Face Detection Benchmark,” *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, pp. 5525–5533, 2016. [Online]. Available: https://openaccess.thecvf.com/content_cvpr_2016/html/Yang_WIDER_FACE_A_CVPR_2016_paper.html

[2] Ultralytics, “Model Training with Ultralytics YOLO,” *Ultralytics Documentation*. [Online]. Available: https://docs.ultralytics.com/modes/train. Accessed: Aug. 13, 2026.

[3] SIC Project, “YOLO11n WIDER FACE training log and checkpoint metadata,” experimental artifact, Aug. 12, 2026. Local artifacts: `face_best.pt`, `face_last.pt`, and Kaggle run output.
