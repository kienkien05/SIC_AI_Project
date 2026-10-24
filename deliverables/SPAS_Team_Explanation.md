# SPAS – Giải thích hệ thống AI cho team

> Tài liệu này dùng để cả team hiểu nhanh hệ thống và trả lời khi thuyết trình.
>
> Cách giải thích ưu tiên câu ngắn, ví dụ dễ hiểu và chỉ dùng thuật ngữ khi cần.

---

## 1. Bài toán của hệ thống

SPAS dùng AI để điểm danh bằng khuôn mặt.

Hệ thống cần thực hiện hai việc:

1. Tìm khuôn mặt trong ảnh.
2. Xác định khuôn mặt đó là sinh viên nào.

AI không chỉ nhìn ảnh rồi trả thẳng tên. Ảnh phải đi qua nhiều bước nhỏ.

---

## 2. Luồng xử lý chính

~~~text
Camera chụp ảnh
    ↓
YOLO tìm khuôn mặt
    ↓
Cắt và căn chỉnh khuôn mặt
    ↓
InceptionResnetV1 tạo vector 512 chiều
    ↓
So sánh với gallery
    ↓
Kiểm tra threshold
    ↓
Gửi kết quả cho Backend để lưu điểm danh
~~~

Có thể hiểu đơn giản:

- YOLO là người khoanh vùng mặt.
- MTCNN là người căn chỉnh mặt.
- InceptionResnetV1 là người tạo mã khuôn mặt.
- ArcFace là cách dạy model phân biệt các khuôn mặt.
- Gallery là kho mã khuôn mặt của sinh viên.
- Cosine similarity là thước đo độ giống.
- Backend là phần lưu và xử lý điểm danh.

---

## 3. YOLO11n làm gì?

YOLO11n có nhiệm vụ tìm vị trí khuôn mặt trong ảnh.

YOLO trả về:

- tọa độ khung bao quanh khuôn mặt;
- confidence;
- nhãn face.

Ví dụ:

~~~text
x1 = 120, y1 = 80
x2 = 260, y2 = 250
confidence = 0.91
class = face
~~~

YOLO chỉ biết khuôn mặt nằm ở đâu. Nó chưa biết đó là sinh viên nào.

### Cấu hình chính

| Nội dung | Giá trị |
|---|---:|
| Input | 640 × 640 |
| Số lớp | 1 lớp: face |
| Epochs | 25 |
| Batch size | 8 |
| Train images | 12.880 |
| Validation images | 3.226 |
| Parameters | 2.590.035 |
| Layers trong summary | 181 |

### Kết quả YOLO

| Metric | Giá trị |
|---|---:|
| Precision | 82,53% |
| Recall | 56,18% |
| mAP@50 | 64,37% |
| mAP@50-95 | 33,97% |

Giải thích ngắn:

- Precision: trong các vùng model gọi là mặt, có bao nhiêu vùng đúng.
- Recall: trong tất cả mặt thật, model tìm được bao nhiêu.
- mAP: đánh giá tổng hợp độ chính xác của vị trí box.

Notebook có cảnh báo max_det = 300, trong khi một số ảnh có rất nhiều object. Vì vậy recall có thể cần được kiểm tra lại với giá trị max_det phù hợp hơn.

---

## 4. MTCNN làm gì?

Sau khi YOLO tìm được khuôn mặt, MTCNN hỗ trợ căn chỉnh khuôn mặt.

MTCNN tìm các điểm:

- mắt;
- mũi;
- miệng.

Sau đó hệ thống xoay và đưa khuôn mặt về ảnh 160 × 160.

MTCNN không phải detector chính. YOLO vẫn là model chính để tìm mặt.

Có thể giải thích như sau:

> YOLO tìm đúng khuôn mặt, còn MTCNN giúp đặt khuôn mặt vào đúng tư thế trước khi nhận diện.

---

## 5. InceptionResnetV1 và ArcFace

### 5.1. InceptionResnetV1

InceptionResnetV1 nhận ảnh khuôn mặt đã căn chỉnh và tạo ra một vector gồm 512 số.

Có thể coi vector này là một “mã đặc trưng” của khuôn mặt.

| Nội dung | Giá trị |
|---|---:|
| Input | 160 × 160 |
| Output | Vector 512 chiều |
| Parameters | 27.910.327 |
| Model production | facenet_best.pt |
| Checkpoint notebook mới | embedder_best.pt |

Vector không phải là ảnh. Nó là một dãy số mô tả những đặc điểm quan trọng của khuôn mặt.

### 5.2. ArcFace

ArcFace là cách dạy model phân biệt khuôn mặt.

Nó cố gắng làm cho:

- ảnh của cùng một người có vector gần nhau;
- ảnh của người khác nhau có vector xa nhau.

Ví dụ:

~~~text
Ảnh A lần 1 ── gần ── Ảnh A lần 2

Ảnh A ───────── xa ───────── Ảnh B
~~~

ArcFace được dùng trong lúc train. Khi chạy production, hệ thống chủ yếu dùng phần tạo vector rồi so sánh với gallery.

### Cấu hình train

| Nội dung | Giá trị |
|---|---:|
| Dataset ban đầu | 10.572 identities, 490.623 ảnh |
| Dataset được chọn | 1.500 identities |
| Train images | 37.501 |
| Validation images | 9.383 |
| Epochs | 20 |
| Batch size | 64 |
| Embedding | 512 chiều |
| Optimizer | AdamW |
| Scheduler | CosineAnnealingLR |
| Learning rate | 0,0001 |

### Kết quả ArcFace

| Metric | Giá trị |
|---|---:|
| Validation Top-1 | 88,96% |
| Validation Top-5 | 92,08% |
| Gallery Top-1 | 88,01% |
| Gallery Top-5 | 91,41% |
| Cosine trung bình của cặp đúng | 0,7742 |

---

## 6. Gallery và ma trận

Gallery là nơi lưu vector khuôn mặt của các sinh viên đã đăng ký.

Nếu có N sinh viên thì gallery có dạng:

~~~text
N × 512
~~~

Trong đó:

- N là số sinh viên;
- 512 là số đặc trưng của mỗi khuôn mặt;
- mỗi hàng là vector của một sinh viên.

Ví dụ:

~~~text
Gallery =
[
  vector của SV001 → 512 số
  vector của SV002 → 512 số
  vector của SV003 → 512 số
]
~~~

Khi camera nhận một khuôn mặt mới, model tạo ra một query vector 512 chiều.

Hệ thống so query vector với tất cả các hàng trong gallery.

---

## 7. Cosine similarity

Cosine similarity là điểm đo độ giống giữa hai vector.

Do hai vector đã được chuẩn hóa L2, code có thể tính bằng tích vô hướng:

~~~python
scores = gallery_matrix @ query_vector
~~~

Kết quả có thể là:

~~~text
SV001 → 0,78
SV002 → 0,43
SV003 → 0,61
~~~

0,78 nghĩa là khuôn mặt mới giống vector của SV001 ở mức 0,78.

Cần nhớ:

> 0,78 là điểm giống của một cặp vector, không phải accuracy tổng thể.

Cosine được chọn vì ArcFace cũng học dựa trên góc giữa các vector. Với embedding đã chuẩn hóa, cosine dễ tính và phù hợp với cách model được train.

Trong notebook:

- cosine trung bình của các cặp đúng là khoảng 0,7742;
- gallery Top-1 accuracy là khoảng 88,01%.

Đây là hai loại kết quả khác nhau.

---

## 8. Cách hệ thống quyết định kết quả

Production dùng hai giá trị:

~~~text
acceptThreshold = 0,60
ambiguityMargin = 0,05
~~~

Quy tắc:

~~~text
Nếu điểm cao nhất < 0,60:
    UNKNOWN_PERSON

Nếu điểm cao nhất và điểm thứ hai chênh nhau < 0,05:
    AMBIGUOUS

Ngược lại:
    MATCHED
~~~

### Ví dụ MATCHED

~~~text
SV001 = 0,78
SV002 = 0,61
~~~

Điểm cao nhất là 0,78:

- lớn hơn 0,60;
- chênh với điểm thứ hai là 0,17;
- lớn hơn 0,05.

Kết quả: MATCHED – SV001.

### Ví dụ UNKNOWN

~~~text
SV001 = 0,48
SV002 = 0,35
~~~

Dù SV001 có điểm cao nhất, 0,48 vẫn thấp hơn 0,60.

Kết quả: UNKNOWN_PERSON.

### Ví dụ AMBIGUOUS

~~~text
SV001 = 0,72
SV002 = 0,70
~~~

Hai điểm quá gần nhau.

Kết quả: AMBIGUOUS.

Cách này giúp hệ thống không cố đoán khi chưa đủ chắc chắn.

---

## 9. Backend kết nối với AI như thế nào?

Backend gửi ảnh đến AI Service thông qua API:

~~~text
POST /internal/v1/attendance-sessions/{sessionId}/recognitions
~~~

AI Service thực hiện:

1. Nhận frame ảnh.
2. Dùng YOLO tìm khuôn mặt.
3. Căn chỉnh khuôn mặt.
4. Tạo embedding 512 chiều.
5. So sánh với gallery của roster.
6. Trả kết quả nhận diện.

Kết quả có thể gồm:

- bbox;
- quality;
- pose;
- score;
- runnerUpScore;
- evidenceCrop;
- studentId nếu kết quả là MATCHED.

Backend sau đó:

- kiểm tra sinh viên có trong roster không;
- lưu detection;
- lưu ảnh bằng chứng;
- tạo hoặc cập nhật attendance log;
- gửi kết quả lên giao diện.

Có thể nói:

> AI chịu trách nhiệm nhận diện. Backend chịu trách nhiệm lưu và xử lý nghiệp vụ điểm danh.

---

## 10. Vì sao không dùng một model duy nhất?

Vì mỗi nhiệm vụ cần một cách xử lý khác nhau:

| Nhiệm vụ | Thành phần |
|---|---|
| Tìm khuôn mặt | YOLO11n |
| Căn chỉnh khuôn mặt | MTCNN |
| Tạo đặc trưng | InceptionResnetV1 |
| Dạy model phân biệt | ArcFace |
| So sánh vector | Cosine similarity |
| Quyết định kết quả | Threshold và ambiguity margin |

Tách riêng giúp:

- dễ thay model;
- dễ kiểm thử;
- dễ tối ưu từng bước;
- thêm sinh viên mới mà không cần train lại toàn bộ.

---

## 11. Vì sao dùng embedding và gallery thay vì trả thẳng tên?

Nếu model phân loại trực tiếp tên sinh viên, khi thêm sinh viên mới thường phải thay đổi class và train lại.

Với embedding và gallery:

1. Chụp ảnh sinh viên mới.
2. Tạo vector 512 chiều.
3. Lưu vector vào gallery.

Không cần train lại toàn bộ model.

Đây là cách phù hợp vì roster của các buổi học có thể thay đổi.

---

## 12. Checkpoint cần lưu ý

Notebook mới tạo:

~~~text
embedder_best.pt
~~~

Production hiện mặc định đọc:

~~~text
facenet_best.pt
~~~

Không được tự kết luận rằng production đã dùng model notebook mới.

Trước khi thay model cần kiểm tra:

- cấu trúc model;
- output có đúng 512 chiều không;
- preprocessing có giống không;
- gallery cũ được tạo từ model nào;
- có cần tạo lại gallery không;
- threshold có cần điều chỉnh không.

Nếu gallery được tạo bằng model cũ nhưng query được tạo bằng model mới, hai vector có thể không nằm cùng một không gian. Khi đó nên tạo lại gallery bằng checkpoint production.

---

## 13. Kịch bản nói ngắn khi thuyết trình

> Hệ thống của nhóm gồm hai phần AI chính. YOLO11n dùng để phát hiện vị trí khuôn mặt trong ảnh. Sau đó MTCNN căn chỉnh khuôn mặt về kích thước 160 x 160. InceptionResnetV1 biến khuôn mặt thành vector 512 chiều. ArcFace được dùng trong quá trình train để làm cho ảnh của cùng một người có vector gần nhau và ảnh của người khác nhau có vector cách xa nhau.
>
> Các vector của sinh viên được lưu trong gallery dưới dạng ma trận N × 512. Khi nhận được khuôn mặt mới, hệ thống tạo một query vector và so sánh với các hàng trong ma trận bằng cosine similarity. Điểm cao nhất là người giống nhất. Nếu điểm dưới 0,60 thì trả về UNKNOWN. Nếu điểm cao nhất quá gần điểm thứ hai thì trả về AMBIGUOUS. Nếu đủ rõ thì trả về MATCHED.
>
> AI Service chỉ chịu trách nhiệm nhận diện. Backend kiểm tra roster, lưu ảnh bằng chứng và cập nhật trạng thái điểm danh.

---

## 14. Câu hỏi vấn đáp thường gặp

### YOLO và ArcFace khác nhau thế nào?

YOLO tìm vị trí khuôn mặt. ArcFace giúp tạo đặc trưng để phân biệt khuôn mặt của các người khác nhau.

### Vì sao output là 512 chiều?

512 số là mã đặc trưng của khuôn mặt. Kích thước này đủ để biểu diễn nhiều đặc điểm nhưng vẫn dễ lưu và so sánh.

### Cosine similarity tính như thế nào?

Hai vector được chuẩn hóa L2 rồi tính tích vô hướng. Kết quả càng cao thì hai vector càng giống nhau.

### 0,78 có phải accuracy không?

Không. 0,78 là điểm giống giữa một query vector và một vector trong gallery. Accuracy tổng thể phải xem Top-1, Top-5 hoặc metric end-to-end.

### Vì sao không dùng Euclidean distance?

Euclidean cũng có thể dùng. Tuy nhiên ArcFace học theo góc giữa các vector nên cosine phù hợp và dễ giải thích hơn. Với vector đã chuẩn hóa, hai cách này cho thứ hạng gần tương đương.

### Vì sao cần threshold?

Để hệ thống không nhận diện khi điểm giống quá thấp. Nếu không có threshold, hệ thống luôn phải chọn một người dù khuôn mặt đó có thể là người lạ.

### Vì sao cần ambiguity margin?

Nếu hai người có điểm gần nhau, hệ thống chưa đủ chắc chắn. Trả về AMBIGUOUS an toàn hơn là chọn nhầm người.

### Model notebook mới đã chạy production chưa?

Notebook có embedder_best.pt, còn production mặc định dùng facenet_best.pt. Cần kiểm tra compatibility và gallery trước khi thay model.

---

## 15. Câu kết cần nhớ

> YOLO tìm mặt, MTCNN căn mặt, InceptionResnetV1 biến mặt thành mã 512 số, ArcFace giúp phân biệt người, cosine tìm người giống nhất, còn threshold quyết định có đủ chắc chắn để điểm danh hay không.

