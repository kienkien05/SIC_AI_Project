# SPAS Presentation — Nội dung từng slide

> Mục tiêu của slide: trình bày dễ hiểu cho cả team và giảng viên, nhưng nhấn mạnh phần AI. Mỗi slide chỉ giữ ý chính; phần “Lời trình bày” dùng để nói thêm, không đưa toàn bộ lên màn hình.

## Slide 1 — Tiêu đề

### Trên slide

**Smart Passive Attendance System**  
Điểm danh hỗ trợ bằng AI và nhận diện khuôn mặt

- Samsung Innovation Campus — AI Course
- Nhóm: SIC AI Team
- Thành viên: `[điền tên thành viên]`

### Hình ảnh

Ảnh minh họa camera/lớp học hoặc ảnh theo slide template Samsung.

### Lời trình bày

Nhóm xây dựng một prototype điểm danh bằng camera. Điểm nhấn của dự án là pipeline AI gồm phát hiện khuôn mặt, tạo embedding, so khớp gallery và kiểm soát trường hợp không chắc chắn.

---

## Slide 2 — Vấn đề và mục tiêu

### Trên slide

**Vấn đề**

- Điểm danh thủ công mất thời gian.
- Có thể nhập nhầm hoặc bỏ sót.
- Khó kiểm tra lại khi có tranh chấp.

**Mục tiêu**

- Tự động tìm khuôn mặt trong frame.
- Nhận diện người thuộc roster.
- Lưu kết quả cùng score và evidence.
- Để giáo viên review trường hợp không chắc chắn.

### Lời trình bày

SPAS không thay thế giáo viên. AI chỉ tạo đề xuất ban đầu; giáo viên vẫn quyết định với các trường hợp score thấp, ảnh mờ hoặc người ngoài roster.

---

## Slide 3 — Câu hỏi AI của dự án

### Trên slide

| Câu hỏi | Thành phần trả lời |
|---|---|
| Khuôn mặt ở đâu? | YOLO11n |
| Khuôn mặt giống ai? | InceptionResnetV1 |
| So sánh bằng gì? | Embedding + cosine similarity |
| Khi nào không nên đoán? | Threshold + ambiguity margin |
| Kiểm tra lại thế nào? | Score + bounding box + evidence |

### Lời trình bày

Tách câu hỏi thành các bước giúp nhóm đánh giá đúng. Detector và recognizer không được gộp thành một metric duy nhất vì chúng làm hai nhiệm vụ khác nhau.

---

## Slide 4 — Tổng quan hệ thống

### Trên slide

```text
Camera/Webcam
      ↓
Frontend → Backend → AI service
                         ├─ YOLO11n
                         ├─ Alignment
                         └─ ArcFace embedding
                              ↓
                       Gallery + cosine
                              ↓
                 Attendance + evidence + review
```

### Lời trình bày

Frontend không gọi model trực tiếp. Backend giữ logic nghiệp vụ và gửi request nội bộ tới AI service. AI service chỉ xử lý ảnh và trả JSON có cấu trúc.

---

## Slide 5 — Kiến trúc thành phần

### Trên slide

- **Frontend**: camera, preview, kết quả, teacher review.
- **Backend**: auth, session, roster, attendance, evidence.
- **AI service**: model loading, detection, embedding, matching.
- **Database**: user, lớp, enrollment, attendance.
- **Gallery**: identity + vector 512D.

### Hình ảnh

Sơ đồ mũi tên:

```text
Frontend → Backend → AI service
               ↓          ↓
           Database    Model files
               ↓
           Evidence
```

### Lời trình bày

Thiết kế tách service giúp có thể thay detector hoặc recognizer mà không thay đổi toàn bộ quy tắc attendance.

---

## Slide 6 — Pipeline xử lý một frame

### Trên slide

1. Nhận ảnh BGR.
2. YOLO11n phát hiện box khuôn mặt.
3. Crop khuôn mặt.
4. MTCNN landmark hỗ trợ alignment.
5. Resize và normalize về 160 × 160.
6. InceptionResnetV1 tạo vector 512D.
7. L2-normalize và so với gallery.
8. Trả identity hoặc UNKNOWN/AMBIGUOUS.

### Lời trình bày

Alignment quan trọng vì cùng một khuôn mặt nhưng mắt, mũi và miệng lệch vị trí có thể làm embedding thay đổi. Hệ thống dùng landmark để đưa khuôn mặt về template thống nhất trước khi đưa vào recognizer.

---

## Slide 7 — Model 1: YOLO11n detector

### Trên slide

| Thuộc tính | Giá trị |
|---|---|
| Nhiệm vụ | Face detection |
| Input | 640 × 640 |
| Train | 25 epochs, batch 8 |
| Dataset | 12.880 train / 3.226 validation |
| Model | YOLO11n pretrained |
| Final summary | 181 layers, 2.590.035 params |
| Fused validation | 100 layers, 2.582.347 params |

### Lời trình bày

YOLO11n được chọn vì tốc độ phù hợp với camera và có sẵn pretrained checkpoint. Đây là detector nhẹ hơn các bản lớn, phù hợp cho prototype chạy real-time. YOLO chỉ trả vị trí, chưa trả danh tính.

---

## Slide 8 — Kiến trúc YOLO11n

### Trên slide

```text
Image 640×640
      ↓
Backbone: Conv + C3k2 + SPPF + C2PSA
      ↓
Neck: Upsample + Concat + C3k2
      ↓
Head: multi-scale Detect
      ↓
Bounding box + confidence + class face
```

### Lời trình bày

Backbone học đặc trưng; neck gom thông tin nhiều kích thước để phát hiện cả mặt lớn và mặt nhỏ; detection head trả box ở nhiều scale. Notebook chạy một class là `face`.

---

## Slide 9 — Kết quả YOLO11n

### Trên slide

| Metric | Kết quả |
|---|---:|
| Precision | 0.8253 |
| Recall | 0.5618 |
| mAP50 | 0.6437 |
| mAP50-95 | 0.3397 |

**Lưu ý:** dataset có ảnh nhiều khuôn mặt; notebook cảnh báo `max_det=300` có thể làm giới hạn Recall.

### Lời trình bày

Precision tốt hơn Recall nghĩa là model tương đối chính xác khi đã trả box nhưng vẫn bỏ sót một số mặt. Vì vậy cần chạy lại validation với `max_det` phù hợp trước khi kết luận benchmark cuối.

---

## Slide 10 — Model 2: InceptionResnetV1 + ArcFace

### Trên slide

| Thuộc tính | Giá trị |
|---|---|
| Nhiệm vụ | Face embedding/recognition |
| Input | 160 × 160 |
| Output | Embedding 512D |
| Dataset chọn | 1.500 identity |
| Train/validation | 37.501 / 9.383 ảnh |
| Train | 20 epochs, batch 64 |
| Backbone params | 27.910.327 |
| Checkpoint | `embedder_best.pt` |

### Lời trình bày

Nhóm chọn embedding thay vì classifier theo tên vì khi thêm sinh viên chỉ cần enrollment vector mới. ArcFace giúp các identity tạo ra cụm vector phân biệt tốt hơn trên không gian góc.

---

## Slide 11 — Kiến trúc recognition

### Trên slide

```text
160×160 face crop
      ↓
Inception-ResNet stem
      ↓
5× Inception-ResNet-A
      ↓
Reduction-A
      ↓
10× Inception-ResNet-B
      ↓
Reduction-B
      ↓
5× Inception-ResNet-C + block C cuối
      ↓
Pooling → Dropout → Linear → BatchNorm
      ↓
512D embedding
```

### Lời trình bày

Inception cho phép kết hợp nhiều nhánh convolution; residual connection giúp học mạng sâu ổn định hơn. Số “layer” của InceptionResnetV1 không nên ghi một con số duy nhất nếu chưa chạy summary theo đúng version thư viện, nên nhóm mô tả bằng các block lặp và dùng parameter count notebook đã in.

---

## Slide 12 — ArcFace và lý do chọn

### Trên slide

```text
Embedding 512D
      ↓ normalize
Cosine với weight của 1.500 class
      ↓
Angular margin m = 0.35
Scale s = 32
      ↓
Cross-entropy + label smoothing 0.05
```

**Head:** `1500 × 512 = 768.000 params`  
**Tổng train xấp xỉ:** `27.910.327 + 768.000 = 28.678.327 params`

### Lời trình bày

ArcFace làm class đúng khó hơn một chút bằng angular margin. Muốn đạt điểm tốt, model phải đưa embedding của cùng identity gần nhau và identity khác xa nhau. Khi deploy, head phân loại 1.500 class không cần giữ lại; chỉ cần backbone và gallery lớp.

---

## Slide 13 — Huấn luyện ArcFace

### Trên slide

| Thông số | Giá trị |
|---|---|
| Pretrained | VGGFace2 InceptionResnetV1 |
| Optimizer | AdamW, lr 1e-4, weight decay 1e-4 |
| Scheduler | Cosine Annealing, T_max=20, eta_min=1e-6 |
| Augmentation | Flip, ColorJitter, RandomAffine nhẹ |
| Precision | AMP khi chạy CUDA |
| Seed | 42 |
| Chọn model | Checkpoint có validation Top-1 tốt nhất |

### Lời trình bày

Train transform có augmentation để model bớt phụ thuộc vào một điều kiện ảnh. Evaluation transform không dùng augmentation ngẫu nhiên. Checkpoint tốt nhất được chọn theo validation Top-1, không mặc định lấy epoch cuối.

---

## Slide 14 — Kết quả ArcFace và gallery

### Trên slide

| Metric | Kết quả |
|---|---:|
| Validation Top-1 | 0.8896 |
| Validation Top-5 | 0.9208 |
| Gallery Top-1 | 0.8801 |
| Gallery Top-5 | 0.9141 |
| Mean true cosine | 0.7742 |
| Mean margin | 0.3713 |

**Không gộp với diagnostic production:** model đang cài đặt có leave-one-out Top-1 0.9750 trên 40 enrollment frames của 5 identity.

### Lời trình bày

Gallery metric gần với cách hệ thống sử dụng thực tế hơn classification Top-1 vì query được so với gallery vector. Diagnostic production cao hơn nhưng có phạm vi nhỏ và dùng chính frame enrollment, nên không đại diện cho sinh viên mới.

---

## Slide 15 — Model kết nối với hệ thống thế nào?

### Trên slide

```text
face_best.pt       → YOLO detector
facenet_best.pt    → InceptionResnetV1 embedder
gallery.npz        → student_ids + embeddings[512]

query embedding · gallery embedding
             ↓
          cosine score
             ↓
  threshold 0.60 / margin 0.05
             ↓
 MATCHED / UNKNOWN / AMBIGUOUS
```

### Lời trình bày

Production hiện load `face_best.pt` và `facenet_best.pt`. Checkpoint latest notebook là `embedder_best.pt`, nên nếu thay vào production cần kiểm tra format, preprocessing và chạy lại metric. Không nên nhầm “model latest đã train” với “model đang được mount trong container”.

---

## Slide 16 — Kiểm thử, giới hạn và quyền riêng tư

### Trên slide

**Kiểm thử**

- Known student.
- Người ngoài roster.
- Ảnh mờ/thiếu sáng.
- Góc nghiêng/mặt nhỏ.
- Roster chưa load hoặc AI service lỗi.
- Evidence và teacher review.

**Giới hạn**

- Chưa có test camera độc lập đủ lớn.
- Chưa có liveness/anti-spoofing.
- Recall detector còn bị ảnh hưởng bởi `max_det`.
- Threshold chưa calibration theo từng camera.

### Lời trình bày

Điểm quan trọng không chỉ là accuracy. Hệ thống phải biết khi nào không chắc chắn, giữ evidence và không ghi nhầm người ngoài roster. Dữ liệu khuôn mặt cần được bảo vệ và có chính sách lưu/xóa.

---

## Slide 17 — Kết luận và hướng phát triển

### Trên slide

**Đã đạt**

- Có pipeline AI từ camera đến attendance.
- Có detector YOLO11n và recognizer embedding.
- Có gallery, cosine, threshold và evidence.
- Có Backend giữ logic và teacher review.

**Tiếp theo**

- Test camera lớp học độc lập.
- Calibration threshold.
- Chạy lại YOLO với `max_det` phù hợp.
- Xác nhận dùng checkpoint ArcFace latest trong production.
- Thêm liveness, tracking và batching.

### Lời trình bày

SPAS là prototype AI end-to-end có thể demo và giải thích được. Kết quả hiện tại đủ để chứng minh pipeline; bước tiếp theo là đánh giá trên dữ liệu camera thật và hoàn thiện độ tin cậy trước khi triển khai rộng.

---

## Gợi ý phân bổ thời gian

| Nhóm slide | Nội dung | Thời lượng |
|---|---|---:|
| 1–3 | Vấn đề, mục tiêu, câu hỏi AI | 2 phút |
| 4–6 | Kiến trúc và pipeline | 2 phút |
| 7–9 | YOLO11n | 2 phút |
| 10–14 | ArcFace, train và metric | 4 phút |
| 15–16 | Tích hợp, kiểm thử, giới hạn | 2 phút |
| 17 | Kết luận | 1 phút |

Tổng thời lượng gợi ý: **13 phút**.
