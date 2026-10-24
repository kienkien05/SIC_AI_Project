# Smart Passive Attendance System (SPAS)

## Nội dung báo cáo tiếng Việt

> Tài liệu này là bản nội dung Markdown đầy đủ để nhóm rà soát trước khi đưa vào mẫu báo cáo Samsung. Nội dung AI được viết theo hai nguồn riêng:
>
> - **Notebook latest**: dùng để báo cáo quá trình train và metric của YOLO11n, ArcFace.
> - **Model đang tích hợp trong hệ thống**: dùng để mô tả cách production AI service load model, tạo gallery và nhận diện trong phiên điểm danh.
>
> Hai nguồn không được gộp thành một metric duy nhất vì checkpoint và tập dữ liệu khác nhau.

---

## Tóm tắt

Smart Passive Attendance System (SPAS) là hệ thống hỗ trợ điểm danh bằng camera và trí tuệ nhân tạo. Hệ thống nhận ảnh hoặc video frame từ camera, phát hiện khuôn mặt, biến từng khuôn mặt thành vector đặc trưng, so sánh vector với gallery của lớp học và trả về kết quả điểm danh.

Pipeline AI gồm hai mô hình chính:

1. **YOLO11n** phát hiện vị trí khuôn mặt trong ảnh và trả về bounding box.
2. **InceptionResnetV1 fine-tune với ArcFace** tạo embedding 512 chiều cho khuôn mặt.

Sau bước nhận diện, hệ thống dùng cosine similarity, ngưỡng chấp nhận và khoảng cách giữa hai ứng viên đứng đầu để quyết định `MATCHED`, `UNKNOWN_PERSON` hoặc `AMBIGUOUS`. Các kết quả được Backend lưu cùng score, bounding box và ảnh evidence để giáo viên kiểm tra.

Notebook detector latest được train 25 epoch trên WIDER Face dạng YOLO với 12.880 ảnh train và 3.226 ảnh validation. Kết quả validation cuối gồm Precision 0.8253, Recall 0.5618, mAP50 0.6437 và mAP50-95 0.3397. Notebook recognition latest được train 20 epoch trên 1.500 identity, 37.501 ảnh train và 9.383 ảnh validation. Kết quả gồm validation Top-1 0.8896, Top-5 0.9208, gallery Top-1 0.8801 và gallery Top-5 0.9141.

Các con số trên chứng minh pipeline có thể hoạt động trên dữ liệu thí nghiệm. Tuy nhiên, chúng chưa thay thế cho một test set camera lớp học độc lập. Vì vậy hệ thống vẫn giữ teacher review và trả `UNKNOWN_PERSON` khi chưa đủ cơ sở nhận diện.

---

## Mục lục

1. [Đặt vấn đề và tổng quan hệ thống](#chương-1-đặt-vấn-đề-và-tổng-quan-hệ-thống)
2. [Cơ sở lý thuyết](#chương-2-cơ-sở-lý-thuyết)
3. [Phân tích và thiết kế hệ thống](#chương-3-phân-tích-và-thiết-kế-hệ-thống)
4. [Huấn luyện mô hình và tích hợp hệ thống](#chương-4-huấn-luyện-mô-hình-và-tích-hợp-hệ-thống)
5. [Kết quả, kiểm thử và đánh giá hệ thống](#chương-5-kết-quả-kiểm-thử-và-đánh-giá-hệ-thống)
6. [Kết luận và hướng phát triển](#kết-luận-và-hướng-phát-triển)
7. [Tài liệu tham khảo](#tài-liệu-tham-khảo)
8. [Phụ lục](#phụ-lục)

---

# Chương 1. Đặt vấn đề và tổng quan hệ thống

## 1.1. Bối cảnh

Điểm danh thủ công bằng cách đọc tên hoặc ký tên tốn thời gian, đặc biệt khi lớp có nhiều sinh viên. Cách làm này cũng có thể xảy ra nhập nhầm, bỏ sót hoặc khó kiểm tra lại khi có tranh chấp. Nếu chỉ dùng camera để ghi hình mà không có AI, giáo viên vẫn phải xem lại video bằng mắt.

SPAS được đề xuất để tự động hóa phần quan sát lặp lại trong quy trình điểm danh. Camera cung cấp ảnh đầu vào; AI hỗ trợ tìm khuôn mặt và đề xuất danh tính; Backend lưu kết quả; giáo viên vẫn kiểm tra các trường hợp không rõ. Cách tiếp cận này coi AI là công cụ hỗ trợ quyết định, không phải người quyết định tuyệt đối.

Đây là bài toán phù hợp với môn AI vì có đầy đủ các bước của một hệ thống thị giác máy tính thực tế:

- chuẩn bị và kiểm tra dữ liệu;
- tiền xử lý ảnh;
- huấn luyện mô hình;
- đo metric;
- đóng gói checkpoint;
- tích hợp model vào API;
- xử lý ngưỡng và trường hợp không chắc chắn;
- đánh giá toàn bộ pipeline thay vì chỉ nhìn vào một ví dụ đúng.

## 1.2. Mục tiêu

### Mục tiêu tổng quát

Xây dựng prototype điểm danh khuôn mặt có thể nhận ảnh từ camera, nhận diện người thuộc roster của lớp và lưu kết quả kèm bằng chứng để giáo viên kiểm tra.

### Mục tiêu AI

1. Huấn luyện hoặc fine-tune mô hình phát hiện khuôn mặt.
2. Huấn luyện mô hình embedding cho nhận diện khuôn mặt.
3. Đo riêng chất lượng detector và recognizer.
4. Giải thích được tại sao chọn YOLO11n, InceptionResnetV1 và ArcFace.
5. Hiểu mối quan hệ giữa embedding, gallery, cosine similarity và threshold.
6. Phân biệt metric trên notebook với metric trên model đang chạy trong hệ thống.

### Mục tiêu hệ thống

1. Có đăng nhập và phân quyền cơ bản.
2. Có đăng ký khuôn mặt bằng nhiều frame.
3. Có quản lý lớp và roster.
4. Có mở session điểm danh và nhận frame.
5. Có nhận diện người đã đăng ký và đánh dấu người chưa chắc chắn.
6. Có lưu attendance, score, bounding box và evidence.
7. Có màn hình để giáo viên review hoặc sửa kết quả.

## 1.3. Phạm vi

Phạm vi của prototype gồm đăng nhập, phân quyền, enrollment, quản lý roster, camera/webcam, nhận diện known student, trả `UNKNOWN_PERSON`, lưu ảnh minh chứng và teacher review.

Phạm vi chưa bao gồm nhận diện cảm xúc, nhận diện hành vi, chống giả mạo chuyên sâu, theo dõi đa camera hoặc kết luận pháp lý về danh tính. Những phần này cần dữ liệu, thiết kế và kiểm thử riêng.

## 1.4. Tổng quan hệ thống

SPAS gồm các lớp chính:

| Thành phần | Vai trò |
|---|---|
| Frontend | Cho giáo viên chọn lớp, mở camera, xem kết quả và review evidence. |
| Backend | Xác thực, giữ logic nghiệp vụ, tạo session, gọi AI service và lưu attendance. |
| AI service | Load YOLO11n và InceptionResnetV1, xử lý ảnh, tạo embedding và trả kết quả. |
| Database | Lưu user, lớp, enrollment, attendance, detection và trạng thái review. |
| Gallery | Lưu identity và vector 512 chiều của những người đã enrollment. |
| Evidence storage | Lưu crop khuôn mặt hoặc đường dẫn ảnh để kiểm tra lại. |

Luồng tổng quát:

```text
Camera/Webcam
    -> Frontend gửi frame
    -> Backend kiểm tra session và quyền
    -> AI service gọi YOLO11n
    -> Crop + alignment khuôn mặt
    -> InceptionResnetV1 tạo embedding 512D
    -> Cosine similarity với gallery của roster
    -> Threshold + ambiguity margin
    -> Backend lưu attendance/evidence
    -> Frontend hiển thị kết quả cho giáo viên
```

## 1.5. Vì sao cần AI hỗ trợ

AI phù hợp với những phần lặp lại và có thể mô tả bằng dữ liệu ảnh:

- tìm khuôn mặt trong ảnh có nhiều người;
- biến ảnh khuôn mặt thành vector số;
- so sánh một vector với gallery;
- phát hiện khi điểm giống nhau thấp;
- cung cấp evidence để người dùng kiểm tra.

AI không nên tự động ghi nhận mọi dự đoán. Trong điều kiện thiếu sáng, khuôn mặt nhỏ, mặt bị che hoặc người ngoài roster, hệ thống có thể không đủ thông tin. Vì vậy thiết kế có ba kết quả: khớp, không xác định và mơ hồ.

## 1.6. Câu hỏi AI của dự án

| Câu hỏi | Cách hệ thống trả lời |
|---|---|
| Ảnh có bao nhiêu khuôn mặt? | YOLO11n trả các bounding box. |
| Khuôn mặt nằm ở đâu? | Box được trả ở dạng tọa độ góc trái/phải. |
| Khuôn mặt thuộc ai? | Recognizer tạo embedding rồi so với gallery. |
| Khi nào không nên đoán? | Score dưới threshold hoặc margin quá nhỏ. |
| Có thể giải thích kết quả không? | Lưu score, runner-up score, box và evidence crop. |
| Có thể thay người vào roster mà không train lại không? | Có; chỉ cần enrollment vector mới và cập nhật gallery. |

## 1.7. Kết quả mong muốn

Một phiên điểm danh cần tạo ra kết quả có thể kiểm tra lại:

- session và thời điểm chụp;
- số khuôn mặt phát hiện được;
- bounding box;
- identity được đề xuất;
- score cosine;
- runner-up score;
- trạng thái `MATCHED`, `UNKNOWN_PERSON` hoặc `AMBIGUOUS`;
- ảnh preview và crop evidence;
- trạng thái cuối do giáo viên xác nhận.

---

# Chương 2. Cơ sở lý thuyết

## 2.1. Computer Vision

Computer Vision là nhóm kỹ thuật giúp máy tính xử lý và hiểu ảnh hoặc video. Với SPAS, ảnh đầu vào được chuyển thành ba loại thông tin:

1. vị trí khuôn mặt;
2. vector đặc trưng khuôn mặt;
3. quyết định điểm danh.

AI không nhìn ảnh theo cách con người nhìn. Mô hình nhận tensor số và học mối quan hệ giữa mẫu pixel với nhãn hoặc vector đặc trưng.

## 2.2. Face Detection

Face Detection trả lời câu hỏi “khuôn mặt nằm ở đâu?”. Đầu ra cơ bản là bounding box và confidence. Với ảnh lớp học, detector phải tìm được nhiều khuôn mặt ở kích thước và vị trí khác nhau.

Detector không biết chắc người trong box là ai. Nó chỉ cung cấp vùng ảnh cho bước recognition. Vì vậy detector tốt chưa đủ để hệ thống điểm danh đúng.

## 2.3. CNN và transfer learning

CNN dùng các convolution filter để học đặc trưng không gian. Các tầng đầu thường học cạnh, góc và vùng sáng tối. Các tầng sâu kết hợp đặc trưng thành mẫu phức tạp hơn.

Transfer learning bắt đầu từ checkpoint đã học trên tập dữ liệu lớn, sau đó điều chỉnh cho bài toán mới. Cách này giúp:

- giảm thời gian train;
- giảm nhu cầu dữ liệu gán nhãn;
- bắt đầu từ đặc trưng tổng quát tốt hơn so với train từ đầu;
- phù hợp với nhóm sinh viên và tài nguyên GPU giới hạn.

## 2.4. Face embedding

Embedding là vector số mô tả đặc trưng khuôn mặt. Trong dự án, recognizer trả vector 512 chiều. Hai ảnh cùng một người nên tạo vector gần nhau; ảnh hai người khác nhau nên tạo vector xa hơn.

Thay vì train classifier mới mỗi khi thêm sinh viên, hệ thống lưu vector enrollment vào gallery. Khi có người mới, chỉ cần chạy enrollment và thêm vector vào gallery.

## 2.5. Các khái niệm bổ sung

### 2.5.1. Cosine similarity

Cosine similarity đo độ giống nhau về hướng giữa hai vector:

```text
cosine(a, b) = (a · b) / (||a|| ||b||)
```

Sau khi L2-normalize, tích vô hướng giữa hai vector chính là cosine similarity. Score càng cao thì hai vector càng giống nhau về hướng. Hệ thống dùng score cao nhất để chọn ứng viên, nhưng vẫn kiểm tra threshold và khoảng cách với ứng viên thứ hai.

### 2.5.2. ArcFace

ArcFace thêm angular margin vào quá trình phân loại lúc train. Mục tiêu là:

- vector cùng identity nằm thành cụm chặt hơn;
- vector khác identity tách nhau rõ hơn;
- ranh giới trên không gian góc có tính phân biệt tốt hơn.

Trong lúc train, ArcMarginProduct tạo logits có scale và margin. Khi deploy, hệ thống không cần giữ classifier head của 1.500 identity trong notebook; hệ thống chỉ cần backbone tạo embedding và gallery của lớp đang điểm danh.

### 2.5.3. Metric

| Metric | Ý nghĩa |
|---|---|
| Precision | Trong những dự đoán có mặt, bao nhiêu dự đoán đúng. |
| Recall | Trong những khuôn mặt thật, detector tìm được bao nhiêu. |
| IoU | Mức chồng lấn giữa box dự đoán và box ground truth. |
| mAP50 | Chất lượng detection ở IoU 0.50. |
| mAP50-95 | Chất lượng detection trung bình ở nhiều ngưỡng IoU. |
| Top-1 | Identity đúng có đứng đầu không. |
| Top-5 | Identity đúng có nằm trong 5 ứng viên đầu không. |
| Cosine mean | Mức giống trung bình giữa query và identity đúng. |
| Margin | Khoảng cách giữa ứng viên đứng đầu và runner-up. |

Không được so sánh trực tiếp mAP với Top-1 vì chúng đo hai nhiệm vụ khác nhau.

### 2.5.4. Quyền riêng tư

Dữ liệu khuôn mặt là dữ liệu nhạy cảm. Hệ thống cần có consent, giới hạn quyền xem, bảo vệ ảnh và embedding, không ghi vector thô vào log, quy định thời hạn lưu và cho phép giáo viên kiểm tra các trường hợp bất thường.

## 2.6. Ví dụ minh họa dễ hiểu

### 2.6.1. Một ảnh đi qua hệ thống

1. Camera gửi một frame.
2. YOLO11n tìm các khuôn mặt.
3. Mỗi box được crop.
4. MTCNN landmark hỗ trợ alignment khuôn mặt.
5. InceptionResnetV1 biến crop thành vector 512 số.
6. Vector được chuẩn hóa và so với gallery.
7. Nếu score đủ cao và margin đủ lớn, trả identity.
8. Nếu không, trả `UNKNOWN_PERSON` hoặc `AMBIGUOUS`.

### 2.6.2. Ví dụ về cosine similarity

Giả sử query có score 0.78 với sinh viên A và 0.42 với sinh viên B. Hệ thống có cơ sở đề xuất A. Nếu score cao nhất là 0.61 nhưng score thứ hai là 0.59, khoảng cách chỉ là 0.02. Trường hợp này dễ nhầm nên hệ thống nên trả `AMBIGUOUS` để giáo viên kiểm tra.

### 2.6.3. Tóm tắt chương

Detector trả lời “khuôn mặt ở đâu”. Recognizer trả lời “khuôn mặt giống ai”. ArcFace giúp học embedding có tính phân biệt. Cosine similarity, threshold và teacher review biến dự đoán AI thành quy trình điểm danh có kiểm soát.

---

# Chương 3. Phân tích và thiết kế hệ thống

## 3.1. Người sử dụng

| Đối tượng | Nhu cầu |
|---|---|
| Sinh viên | Đăng ký khuôn mặt và xem lịch sử điểm danh. |
| Giáo viên | Chọn lớp, mở session, quét camera, review và sửa kết quả. |
| Quản trị viên | Quản lý user, lớp, camera, model và enrollment. |
| AI service | Nhận ảnh, phát hiện, embedding và trả JSON kết quả. |

## 3.2. Chức năng chính

- Đăng nhập và phân quyền.
- Enrollment khuôn mặt từ nhiều frame.
- Kiểm tra pose front/left/right khi enrollment.
- Quản lý lớp và roster.
- Nạp roster vào AI service theo session.
- Nhận frame từ webcam hoặc camera.
- Phát hiện khuôn mặt.
- Nhận diện known student.
- Trả `UNKNOWN_PERSON` và `AMBIGUOUS`.
- Lưu attendance, score, box và evidence.
- Cho phép giáo viên review và chỉnh trạng thái.

## 3.3. Nguyên tắc thiết kế

Frontend không gọi model trực tiếp. Frontend gọi Backend. Backend kiểm tra JWT, role và session rồi gọi AI service bằng request nội bộ có khóa.

AI service chỉ chịu trách nhiệm xử lý ảnh và trả dữ liệu có cấu trúc. Backend mới là nơi quyết định trạng thái attendance, chống ghi trùng, lưu evidence và áp dụng nghiệp vụ lớp học.

Thiết kế này giúp thay model mà không phải thay toàn bộ hệ thống. Model có thể trả prediction; Backend vẫn giữ luật điểm danh.

## 3.4. Yêu cầu chức năng

| Mã | Yêu cầu | Đối tượng |
|---|---|---|
| FR-01 | Đăng nhập và phân quyền. | Tất cả |
| FR-02 | Tạo enrollment từ nhiều frame. | Sinh viên/quản trị |
| FR-03 | Tạo session theo lớp. | Giáo viên |
| FR-04 | Phân biệt known, unknown và ambiguous. | AI service |
| FR-05 | Lưu prediction và evidence. | Backend |
| FR-06 | Xem và sửa kết quả. | Giáo viên |
| FR-07 | Kiểm tra trạng thái model/service. | Quản trị |

### 3.4.1. Yêu cầu theo người dùng

Giáo viên cần xem được lớp, roster, frame preview, danh sách khuôn mặt, score và evidence. Sinh viên cần đăng ký được đủ pose. Quản trị viên cần biết model có load thành công hay không.

### 3.4.2. Yêu cầu phi chức năng

- Dễ dùng: thao tác demo ít bước, thông báo lỗi rõ.
- Tin cậy: không ghi identity khi score chưa đủ.
- Bảo mật: AI service không mở trực tiếp cho Internet.
- Mở rộng: detector và recognizer có thể thay riêng.
- Theo dõi: log được request, score, trạng thái và lỗi tổng quát.

### 3.4.3. Quy tắc nghiệp vụ

Một sinh viên chỉ có một trạng thái cuối trong một session. Identity ngoài roster không được ghi vào danh sách lớp. Khuôn mặt gắn với tài khoản khác ở score kiểm tra duplicate từ 0.60 trở lên cần bị từ chối để tránh enrollment trùng.

## 3.5. Luồng nghiệp vụ

### 3.5.1. Luồng điểm danh

1. Giáo viên chọn lớp.
2. Backend lấy roster và gửi sang AI service.
3. Frontend chụp frame.
4. Backend gửi frame tới endpoint recognition.
5. AI service gọi detector, crop, alignment và recognizer.
6. AI service trả danh sách khuôn mặt.
7. Backend lọc identity theo roster, lưu evidence và cập nhật attendance.
8. Frontend nhận event để hiển thị kết quả.

### 3.5.2. Xử lý kết quả không chắc chắn

Nếu score nhỏ hơn `acceptThreshold`, kết quả là `UNKNOWN_PERSON`. Nếu score cao nhưng margin giữa top-1 và top-2 nhỏ hơn `ambiguityMargin`, kết quả là `AMBIGUOUS`. Các trường hợp này vẫn có crop evidence để review.

### 3.5.3. Enrollment

Enrollment yêu cầu tối thiểu năm crop rõ, có đủ pose front, left và right. Các vector được trung bình, L2-normalize rồi lưu vào gallery. Cách dùng nhiều pose giúp gallery đại diện tốt hơn so với chỉ dùng một ảnh nhìn thẳng.

## 3.6. Use case và activity

### 3.6.1. Use case chính

| Actor | Use case | Kết quả |
|---|---|---|
| Giáo viên | Mở session | Session có roster. |
| Giáo viên | Quét camera | Có prediction và evidence. |
| Giáo viên | Review evidence | Xác nhận hoặc sửa trạng thái. |
| Sinh viên | Enrollment | Có embedding trong gallery. |
| Quản trị | Quản lý lớp/user | Dữ liệu sẵn sàng cho session. |

### 3.6.2. Activity đơn giản

```text
Bắt đầu
  -> Giáo viên chọn lớp
  -> Backend tạo session và nạp roster
  -> Frontend gửi frame
  -> AI service nhận diện
  -> Backend cập nhật attendance
  -> Giáo viên review trường hợp cần chú ý
  -> Kết thúc và lưu session
```

### 3.6.3. Trường hợp ngoại lệ

Camera không đọc được frame: trả lỗi kết nối. AI service không sẵn sàng: Backend không tạo attendance giả. Score thấp: giữ evidence nhưng không gán identity. Roster chưa được load: trả lỗi session để giáo viên biết cần khởi tạo lại.

## 3.7. Mô hình dữ liệu và API

### 3.7.1. Entity chính

| Entity | Vai trò |
|---|---|
| User | Tài khoản và role. |
| Section/CourseClass | Lớp học phần. |
| Enrollment | Trạng thái đăng ký khuôn mặt. |
| FaceEmbedding | Vector đại diện. |
| AttendanceSession | Một lần mở quét. |
| AttendanceLog | Trạng thái của sinh viên. |
| SessionFaceDetection | Một khuôn mặt trong frame. |
| Evidence/ProofSnapshot | Ảnh hoặc đường dẫn minh chứng. |

### 3.7.2. API AI quan trọng

| API | Chức năng |
|---|---|
| `GET /health` | Kiểm tra model file, device và trạng thái service. |
| `POST /internal/v1/enrollments` | Nhận frame enrollment và tạo gallery vector. |
| `PUT /internal/v1/attendance-sessions/{id}/roster` | Nạp roster cho session. |
| `POST /internal/v1/attendance-sessions/{id}/recognitions` | Nhận frame và trả prediction. |
| `POST /internal/v1/attendance-sessions/{id}/capture` | Capture từ camera/RTSP. |

### 3.7.3. Vì sao tách detector và recognizer

Detector và recognizer giải quyết hai nhiệm vụ khác nhau nên có thể train, đo metric và thay thế độc lập. Khi thêm sinh viên, hệ thống chỉ cập nhật gallery. Không cần train lại classifier với tên của toàn bộ lớp.

## 3.8. Thiết kế dữ liệu và luồng trạng thái

### 3.8.1. Dữ liệu cần lưu

Roster lưu `student_id` và status. Embedding lưu vector 512D. Prediction lưu identity, score, runner-up score, box, quality và pose. Session lưu lớp và thời điểm. Evidence lưu ảnh crop hoặc URL.

### 3.8.2. Trạng thái attendance

```text
PRESENT_AI -> PRESENT_CONFIRMED
PRESENT_AI -> REVIEW
UNKNOWN -> REVIEW hoặc bỏ qua
ABSENT -> PRESENT_AI khi phát hiện ở checkpoint sau
```

Giáo viên có thể sửa trạng thái, nhưng hệ thống vẫn giữ log hoặc evidence cơ bản để biết kết quả đến từ AI hay người dùng.

### 3.8.3. Tính nhất quán

AI service chỉ trả prediction. Backend quyết định trạng thái cuối, chống ghi trùng, lưu evidence và cập nhật session. Cách tách này giúp thay checkpoint mà không thay đổi quy tắc nghiệp vụ.

---

# Chương 4. Huấn luyện mô hình và tích hợp hệ thống

## 4.1. Quy trình chung

Hai notebook có flow tương tự:

```text
EDA -> preprocessing -> train/fine-tune -> validation -> metric -> inference -> checkpoint
```

Khi triển khai, checkpoint phải đi cùng preprocessing, kích thước input, threshold và format gallery. Nếu chỉ thay file model mà giữ preprocessing cũ không đúng, metric notebook có thể không phản ánh hành vi production.

## 4.2. Model phát hiện khuôn mặt: YOLO11n

### 4.2.1. Dữ liệu và cấu hình train

| Thông số | Giá trị |
|---|---|
| Dataset | WIDER Face dạng YOLO |
| Train images | 12.880 |
| Validation images | 3.226 |
| Input | 640 × 640 |
| Batch size | 8 |
| Epochs | 25 |
| Workers | 4 |
| GPU | 2 GPU trong notebook |
| Initial checkpoint | `yolo11n.pt` |
| Class | `face` |

### 4.2.2. Cấu trúc tổng quát

YOLO11n gồm ba vùng chính:

1. **Backbone**: trích xuất đặc trưng từ ảnh qua convolution và block C3k2.
2. **Neck**: kết hợp đặc trưng nhiều tỉ lệ, gồm upsample, concat và các block xử lý.
3. **Detection head**: nhận feature map nhiều scale và trả box/class/confidence.

Output notebook ghi:

- bản model sau khi override thành một class có **181 layer và 2.590.035 parameter**;
- khi fused để validation có **100 layer và 2.582.347 parameter**;
- 6.5 GFLOPs ở bản chưa fused và 6.4 GFLOPs ở bản fused.

Cell đầu notebook in ra 2.624.080 parameter vì đó là số parameter được đếm trên object checkpoint trước khi Ultralytics override head từ 80 class mặc định về 1 class. Khi model được build cho bài toán một class, summary sau override mới là số nên dùng để mô tả model train.

### 4.2.3. Kết quả YOLO11n

| Metric | Giá trị |
|---|---:|
| Precision | 0.8253 |
| Recall | 0.5618 |
| mAP50 | 0.6437 |
| mAP50-95 | 0.3397 |

Notebook có cảnh báo một số ảnh chứa nhiều object hơn `max_det=300`, trong khi validation quan sát được tối đa 709 object ở một ảnh. Vì vậy Recall và mAP cần được xem là kết quả của lần chạy hiện tại, chưa phải benchmark cuối cùng. Nên chạy lại với `max_det` phù hợp rồi so sánh.

## 4.3. Chuẩn bị dữ liệu và augmentation

### 4.3.1. Detector

Ảnh được đọc, kiểm tra label, đưa về kích thước 640 và giữ box theo format YOLO. WIDER Face có ảnh nhiều người, kích thước mặt khác nhau và bối cảnh đa dạng; đây là lý do phù hợp để khởi đầu cho detector.

### 4.3.2. Recognizer

Notebook recognition dùng WebFace 112 × 112, sau đó resize thành 160 × 160 cho InceptionResnetV1. Train transform gồm RandomHorizontalFlip, ColorJitter và RandomAffine nhẹ. Evaluation chỉ resize, ToTensor và normalize.

Augmentation giúp model gặp các thay đổi nhẹ về sáng, màu, vị trí và góc. Không nên dùng biến đổi quá mạnh khiến ảnh train khác xa camera lớp học.

### 4.3.3. Tránh data leakage

Train và validation phải được tách trước khi chọn checkpoint. Nếu ảnh gần như giống nhau nằm ở cả hai tập, Top-1 có thể cao nhưng không phản ánh khả năng nhận diện người mới hoặc camera mới.

## 4.4. Model nhận diện: InceptionResnetV1 + ArcFace

### 4.4.1. Dữ liệu và cấu hình

| Thông số | Giá trị |
|---|---|
| Dataset gốc | WebFace 112 × 112 |
| Identity gốc | 10.572 |
| Ảnh gốc | 490.623 |
| Identity được chọn | 1.500 |
| Train images | 37.501 |
| Validation images | 9.383 |
| Input model | 160 × 160 |
| Embedding | 512 chiều |
| Epochs | 20 |
| Batch size | 64 |
| Learning rate | 1e-4 |
| Optimizer | AdamW |
| Weight decay | 1e-4 |
| Scheduler | CosineAnnealingLR, T_max=20, eta_min=1e-6 |
| Label smoothing | 0.05 |
| GPU | 2 GPU, DataParallel |
| Checkpoint | `embedder_best.pt` |

### 4.4.2. Backbone InceptionResnetV1

Notebook dùng:

```python
InceptionResnetV1(
    classify=False,
    pretrained=None,
    num_classes=8631,
)
```

Weight được nạp từ checkpoint VGGFace2 trước khi fine-tune. Notebook in ra **27.910.327 parameter cho embedder** và embedding dimension 512.

Cấu trúc cấp cao của Inception-ResNet gồm:

1. stem convolution để giảm kích thước và tăng số channel;
2. năm block Inception-ResNet-A;
3. Reduction-A;
4. mười block Inception-ResNet-B;
5. Reduction-B;
6. năm block Inception-ResNet-C;
7. một block C cuối;
8. average pooling, dropout;
9. linear projection từ feature cuối thành vector 512 chiều;
10. BatchNorm cho embedding.

Số “layer” của InceptionResnetV1 không nên ghi như một con số duy nhất nếu chưa chạy `torchinfo` hoặc in `named_modules()`, vì mỗi Inception block có nhiều branch convolution và BatchNorm con. Trong report nên ghi rõ cấu trúc block ở trên và parameter count đã được notebook xác nhận.

### 4.4.3. ArcMarginProduct

Head ArcFace trong notebook có:

```python
embedding_dim = 512
classes = 1500
scale = 32.0
margin = 0.35
```

Trọng số của head có kích thước `1500 × 512 = 768.000 parameter`. Notebook in 27.910.327 parameter cho embedder; nếu cộng thêm ArcMarginProduct thì tổng số parameter được tối ưu trong lúc train xấp xỉ **28.678.327**.

ArcFace không chỉ dùng cross-entropy trên logits thông thường. Với target class, góc được cộng thêm margin rồi mới chuyển lại thành cosine có scale. Điều này tạo ranh giới chặt hơn giữa các identity.

### 4.4.4. Vì sao chọn InceptionResnetV1 và ArcFace

- FaceNet-style embedding phù hợp với gallery vì thêm người mới không cần train lại toàn bộ classifier.
- InceptionResnetV1 có residual connection giúp truyền gradient qua mạng sâu hơn.
- VGGFace2 pretraining cung cấp đặc trưng khuôn mặt tốt hơn so với khởi tạo ngẫu nhiên.
- ArcFace tối ưu tính phân biệt trên không gian góc, phù hợp với cosine similarity khi deploy.
- Embedding 512D là cân bằng giữa thông tin nhận diện, dung lượng gallery và tốc độ so sánh.
- Dataset 1.500 identity đủ để có bài toán classification rõ ràng trong notebook, đồng thời vẫn có thể train trong giới hạn GPU.

## 4.5. Kết quả huấn luyện và metric ArcFace

### 4.5.1. Validation classification

| Metric | Giá trị |
|---|---:|
| Best validation Top-1 | 0.8896 |
| Validation Top-5 | 0.9208 |
| Best epoch | 20 |

Top-1 tăng từ 0.5054 ở epoch 1 lên 0.8896 ở epoch 20. Điều này cho thấy model học được ranh giới identity tốt hơn theo thời gian. Top-5 cao hơn Top-1 vì một số query không đứng đúng vị trí đầu nhưng identity đúng vẫn nằm trong nhóm ứng viên đầu.

### 4.5.2. Gallery recognition

| Metric | Giá trị |
|---|---:|
| Gallery Top-1 | 0.8801 |
| Gallery Top-5 | 0.9141 |
| Mean true cosine | 0.7742 |
| Mean top-1 margin | 0.3713 |
| Gallery identities | 1.500 |
| Evaluated images | 9.383 |

Gallery metric mô phỏng cách production dùng embedding: tạo gallery từ một số ảnh train rồi so query validation với gallery. Đây là lý do gallery Top-1 thấp hơn validation Top-1 một chút.

## 4.6. Tích hợp model vào hệ thống

### 4.6.1. Model file và runtime

AI service hiện load:

- `face_best.pt` bằng Ultralytics `YOLO`;
- `facenet_best.pt` bằng `InceptionResnetV1(classify=False, pretrained=None, num_classes=8631)`;
- checkpoint recognizer được load từ key `state_dict`;
- model chuyển sang `eval()` và chạy trên CPU hoặc CUDA tùy runtime.

Checkpoint notebook latest có tên `embedder_best.pt`. Nếu muốn đưa checkpoint latest vào production, cần kiểm tra tương thích với format `facenet_best.pt`, preprocessing, gallery và validation lại trên model sau khi copy. Không nên chỉ đổi tên file.

### 4.6.2. Xử lý frame

1. Backend gửi multipart image tới AI service.
2. YOLO11n chạy với `imgsz=640`, `conf=0.35`.
3. Từng box được crop; crop quá nhỏ thì bỏ qua.
4. MTCNN landmark thử các rotation và chọn candidate có xác suất tốt nhất.
5. `estimateAffinePartial2D` align năm landmark về template 160 × 160.
6. Ảnh được đổi BGR sang RGB, resize 160 × 160 và standardize.
7. InceptionResnetV1 tạo vector.
8. Vector được L2-normalize.
9. Dot product với matrix embedding của roster cho cosine score.
10. Threshold và margin tạo trạng thái.

### 4.6.3. Enrollment và gallery

Production enrollment yêu cầu tối thiểu năm crop rõ và đủ front/left/right pose. Các vector được trung bình rồi L2-normalize. Gallery được lưu trong `gallery.npz` gồm `student_ids` và `embeddings`.

Khi bắt đầu session, Backend gọi API load roster. AI service lọc gallery theo danh sách lớp và giữ matrix embedding trong bộ nhớ cho session. Nhờ vậy hệ thống chỉ so sánh với người trong lớp, không so với toàn bộ 1.500 identity của notebook.

### 4.6.4. Quyết định identity

Mặc định policy của AI service:

```text
acceptThreshold = 0.60
ambiguityMargin = 0.05
```

Pseudo-code:

```text
score_1, id_1 = max(cosine(query, gallery))
score_2 = score của ứng viên đứng thứ hai

nếu score_1 < 0.60:
    UNKNOWN_PERSON
ngược lại nếu score_1 - score_2 < 0.05:
    AMBIGUOUS
ngược lại:
    MATCHED với id_1
```

Các ngưỡng này là policy hiện tại, chưa phải kết quả calibration trên test camera độc lập. Khi có test set thực tế, cần chọn threshold dựa trên false accept và false reject.

## 4.7. Reproducibility và triển khai

Muốn chạy lại đúng cần cố định:

- notebook và version package;
- seed 42;
- dataset và cách chọn identity;
- transform train/eval;
- input size;
- checkpoint;
- threshold và ambiguity margin;
- format gallery;
- device và precision.

Kết quả notebook latest và kết quả model production phải được ghi bằng tên checkpoint và nguồn metric. Không dùng accuracy train để kết luận hệ thống camera đã sẵn sàng production.

---

# Chương 5. Kết quả, kiểm thử và đánh giá hệ thống

## 5.1. Môi trường

| Thành phần | Cấu hình |
|---|---|
| Training | Kaggle notebook, 2 GPU T4 trong output notebook. |
| Serving | Docker Compose và AI service FastAPI. |
| Detector | YOLO11n với `face_best.pt`. |
| Recognizer | InceptionResnetV1 với `facenet_best.pt`. |
| Landmark/alignment | MTCNN landmark trong AI service. |
| Input | Webcam, ảnh upload hoặc camera frame. |
| Output | Identity, score, attendance và evidence. |

## 5.2. Kết quả detector

YOLO11n đạt Precision 0.8253, Recall 0.5618, mAP50 0.6437 và mAP50-95 0.3397 trên 3.226 ảnh validation với 39.707 instance khuôn mặt.

Precision cao hơn Recall cho thấy trong số box model đã trả về, tỉ lệ box đúng tương đối tốt; tuy nhiên model vẫn bỏ sót một số khuôn mặt. Recall cần được xem cùng cảnh báo `max_det`, vì ảnh đông người có thể vượt giới hạn số detection tối đa.

## 5.3. Kết quả recognizer

Notebook ArcFace latest đạt validation Top-1 0.8896 và Top-5 0.9208 trên 9.383 ảnh của 1.500 identity. Khi dùng gallery, Top-1 là 0.8801 và Top-5 là 0.9141.

Model đang tích hợp trong hệ thống có phép đo nội bộ leave-one-out trên 40 frame enrollment của 5 identity:

| Metric | Giá trị |
|---|---:|
| Top-1 | 0.9750 |
| Top-5 | 1.0000 |
| Mean cosine | 0.7936 |
| Min cosine | 0.0594 |
| Mean margin | 0.3351 |

Phép đo này chỉ là diagnostic nội bộ. Nó không thể thay thế test trên sinh viên mới vì query và gallery đều đến từ enrollment của hệ thống.

## 5.4. Kiểm thử chức năng

| ID | Tình huống | Kỳ vọng |
|---|---|---|
| T01 | Đăng nhập | Đúng màn hình theo role. |
| T02 | Enrollment | Lưu vector sau khi đủ frame và đủ pose. |
| T03 | Mở camera | Session bắt đầu quét. |
| T04 | Known student | Ghi đúng identity khi score đủ. |
| T05 | Người ngoài roster | Không gán nhầm người trong lớp. |
| T06 | Khuôn mặt trùng enrollment | Từ chối và báo lỗi. |
| T07 | Evidence | Giáo viên xem được crop/ảnh minh chứng. |
| T08 | Chỉnh sửa | Trạng thái mới được lưu và có audit cơ bản. |
| T09 | Roster chưa load | Trả lỗi rõ, không ghi attendance giả. |
| T10 | AI service lỗi | Backend giữ trạng thái an toàn và báo lỗi. |

## 5.5. Phương pháp kiểm thử

### 5.5.1. Kiểm thử model

- Detector validation: Precision, Recall, mAP50, mAP50-95.
- ArcFace validation: Top-1, Top-5 theo classification head.
- Gallery recognition: Top-1, Top-5, cosine mean, margin.
- Unknown test: false accept rate trên người ngoài roster.
- Camera test: accuracy, latency và failure cases.

### 5.5.2. Kiểm thử theo tầng

1. Tầng model: kiểm tra box, vector và score.
2. Tầng AI service: kiểm tra model load, API, ảnh lỗi và roster.
3. Tầng Backend: kiểm tra session, roster, evidence và chống ghi trùng.
4. Tầng Frontend: kiểm tra camera, preview, status và review.
5. End-to-end: chạy một session từ đăng nhập đến kết thúc.

### 5.5.3. Tiêu chí Pass/Fail

Test Pass khi output đúng kỳ vọng và không tạo side effect sai. Test Fail khi service trả lỗi không rõ, ghi nhầm roster, mất evidence, hoặc không thể khôi phục session. Mỗi case Fail cần ghi input, log và bước tái hiện.

## 5.6. Phân tích lỗi và giới hạn

| Tình huống | Nguyên nhân | Cách giảm lỗi |
|---|---|---|
| Ảnh mờ | Camera rung hoặc người di chuyển. | Quét nhiều frame và chọn frame tốt. |
| Ánh sáng yếu | Mặt có ít thông tin. | Thêm dữ liệu low-light và điều chỉnh camera. |
| Góc nghiêng | Khác ảnh enrollment. | Enrollment nhiều pose. |
| Mặt nhỏ | Khoảng cách xa. | Điều chỉnh camera hoặc crop strategy. |
| Người giống nhau | Vector gần nhau. | Margin, threshold và teacher review. |
| Replay ảnh/video | Không có liveness. | Bổ sung anti-spoofing. |
| Đông người | max_det giới hạn số detection. | Chạy validation/inference với max_det phù hợp. |

Metric public không đại diện hoàn toàn cho camera lớp học. Threshold phụ thuộc ánh sáng, góc camera, chất lượng enrollment và roster. Không nên kết luận production chỉ từ validation WebFace hoặc WIDER Face.

## 5.7. Đánh giá vận hành và quyền riêng tư

### 5.7.1. Các yếu tố ảnh hưởng tốc độ

- số khuôn mặt trong frame;
- kích thước ảnh;
- thời gian decode;
- số vector trong roster;
- latency giữa Backend và AI service;
- thời gian ghi evidence.

Roster theo lớp giúp giảm số vector phải so sánh. Batching, tracking và giới hạn kích thước ảnh có thể giảm tải khi triển khai nhiều người.

### 5.7.2. Quyền riêng tư

- Chỉ thu thập dữ liệu khi người dùng biết mục đích.
- Chỉ role phù hợp được xem ảnh và embedding.
- Không hiển thị vector thô trên UI.
- Không đưa ảnh khuôn mặt vào log lỗi.
- Có thời hạn lưu và quy trình xóa.
- Giáo viên có thể sửa kết quả nhưng vẫn giữ audit cơ bản.

### 5.7.3. Trách nhiệm người vận hành

Giáo viên cần kiểm tra `UNKNOWN_PERSON` và `AMBIGUOUS`, không dùng một score duy nhất để quyết định kỷ luật. Hệ thống nên được xem là công cụ hỗ trợ, đặc biệt khi camera mờ, thiếu sáng hoặc có người ngoài roster.

## 5.8. Kịch bản demo và tiêu chí nghiệm thu

### Kịch bản demo

1. Đăng nhập tài khoản giáo viên.
2. Chọn lớp và xem roster.
3. Mở camera và chụp frame.
4. Quan sát box, identity và score.
5. Đưa người ngoài roster vào để kiểm tra `UNKNOWN_PERSON`.
6. Mở evidence.
7. Sửa trạng thái một sinh viên.
8. Kiểm tra attendance history hoặc báo cáo.

### Tiêu chí nghiệm thu

- Role đăng nhập đúng.
- Enrollment tạo được vector.
- Known student được ghi nhận.
- Unknown không bị gán nhầm.
- Evidence xem lại được.
- Giáo viên sửa được kết quả.
- Metric và giới hạn được trình bày trung thực.
- Hệ thống không ghi attendance khi AI service hoặc roster chưa sẵn sàng.

## 5.9. Bài học từ dự án

Metric chỉ có ý nghĩa khi ghi rõ dữ liệu, checkpoint và cách đo. Training, validation, enrollment và camera thật là các nguồn dữ liệu khác nhau.

Một model tốt vẫn cần API, gallery, roster, evidence, quyền truy cập và màn hình review. Teacher review không phải phần phụ mà là cơ chế xử lý sự không chắc chắn của AI.

Khi thuyết trình, nên bắt đầu bằng vấn đề và demo pipeline, sau đó giải thích detector, embedding, ArcFace và metric. Mỗi con số nên đi cùng một câu giải thích đơn giản.

---

# Kết luận và hướng phát triển

Nhóm đã xây dựng prototype điểm danh tự động có luồng từ ảnh camera đến attendance record. AI gồm YOLO11n để phát hiện khuôn mặt, InceptionResnetV1 để tạo embedding 512 chiều, cosine similarity để so khớp và policy threshold để kiểm soát kết quả.

Kết quả notebook cho thấy detector và recognizer đã học được khả năng xử lý dữ liệu thí nghiệm. Tuy nhiên, hệ thống vẫn cần test camera thật độc lập trước khi gọi là production. Thiết kế có `UNKNOWN_PERSON`, `AMBIGUOUS` và teacher review để tránh biến một dự đoán không chắc chắn thành attendance chắc chắn.

Hướng phát triển:

1. Tạo test set camera lớp học có known và người ngoài roster.
2. Calibration threshold theo từng camera và điều kiện sáng.
3. Chạy lại YOLO validation với `max_det` phù hợp.
4. Xác nhận tương thích giữa `embedder_best.pt` latest và `facenet_best.pt` production.
5. Bổ sung liveness và anti-spoofing.
6. Tối ưu tracking, batching và nhiều camera.
7. Bổ sung retention policy và quy trình xóa dữ liệu.
8. Theo dõi latency, false accept và false reject khi vận hành.

---

# Tài liệu tham khảo

1. Samsung Innovation Campus. *AI Course Capstone Project Final Report Template*.
2. Samsung Innovation Campus. *AI Course Capstone Project Action Plan Template*.
3. Ultralytics. *YOLO Documentation*. https://docs.ultralytics.com/
4. Deng, J. et al. *ArcFace: Additive Angular Margin Loss for Deep Face Recognition*. CVPR, 2019.
5. Schroff, F. et al. *FaceNet: A Unified Embedding for Face Recognition and Clustering*. CVPR, 2015.
6. Szegedy, C. et al. *Inception-v4, Inception-ResNet and the Impact of Residual Connections on Learning*. AAAI, 2017.
7. Notebook `face-attendance-yolo11n-detector.ipynb`.
8. Notebook `face-attendance-arcface-recognition (1).ipynb`.
9. SPAS source code, AI service and Backend integration.

---

# Phụ lục

## Phụ lục A. Bảng số liệu cần giữ trong bản nộp

| Hạng mục | Giá trị | Nguồn |
|---|---:|---|
| YOLO11n train images | 12.880 | Notebook detector |
| YOLO11n validation images | 3.226 | Notebook detector |
| YOLO11n epochs | 25 | Notebook detector |
| YOLO11n final summary | 181 layers, 2.590.035 params | Notebook output |
| YOLO11n fused validation summary | 100 layers, 2.582.347 params | Notebook output |
| YOLO Precision | 0.8253 | Notebook metrics |
| YOLO Recall | 0.5618 | Notebook metrics |
| YOLO mAP50 | 0.6437 | Notebook metrics |
| YOLO mAP50-95 | 0.3397 | Notebook metrics |
| ArcFace selected identities | 1.500 | Notebook recognition |
| ArcFace train images | 37.501 | Notebook recognition |
| ArcFace validation images | 9.383 | Notebook recognition |
| ArcFace epochs | 20 | Notebook recognition |
| ArcFace embedding | 512D | Notebook and system |
| ArcFace embedder params | 27.910.327 | Notebook output |
| ArcMargin head params | 768.000 | 1.500 × 512 |
| ArcFace validation Top-1 | 0.8896 | Notebook recognition |
| ArcFace validation Top-5 | 0.9208 | Notebook recognition |
| Gallery Top-1 | 0.8801 | Notebook recognition |
| Gallery Top-5 | 0.9141 | Notebook recognition |
| System diagnostic Top-1 | 0.9750 | 40 enrollment frames |
| System diagnostic Top-5 | 1.0000 | 40 enrollment frames |

## Phụ lục B. Những số liệu cần bổ sung trước khi gọi production

- số người ngoài roster trong test;
- false accept rate;
- false reject rate;
- latency trung bình và p95;
- kết quả theo điều kiện sáng;
- kết quả theo khoảng cách camera;
- kết quả khi có che mặt hoặc góc nghiêng;
- kết quả sau khi calibration threshold;
- thời gian load model và thời gian xử lý từng frame.

## Phụ lục C. Quy ước thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| Detector | Model tìm vị trí khuôn mặt. |
| Recognizer | Model tạo embedding và hỗ trợ nhận diện. |
| Embedding | Vector số đại diện cho khuôn mặt. |
| Gallery | Tập vector đã enrollment. |
| Roster | Danh sách người thuộc lớp. |
| Top-1/Top-5 | Vị trí của identity đúng trong ranking. |
| Threshold | Ngưỡng score tối thiểu để nhận. |
| Margin | Khoảng cách giữa top-1 và top-2. |
| Evidence | Ảnh hoặc crop dùng để review. |
