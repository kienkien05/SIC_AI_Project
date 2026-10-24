# SPAS – Technical Deep Dive về AI và cách tích hợp hệ thống

> Phiên bản này viết cho người mới bắt đầu.
>
> Mỗi phần cố gắng trả lời bốn câu hỏi:
>
> 1. Model hoặc thuật toán này làm gì?
> 2. Nó nhận dữ liệu gì?
> 3. Nó trả ra kết quả gì?
> 4. Vì sao hệ thống chọn cách này?
>
> Các số liệu trong tài liệu được lấy từ notebook huấn luyện và mã nguồn hệ thống SPAS. Khi một con số không có trong mã nguồn, tài liệu sẽ nói rõ thay vì tự đoán.

---

## 1. Nhìn nhanh: hệ thống AI đang làm việc gì?

SPAS là hệ thống điểm danh bằng khuôn mặt. Khi camera chụp một khung hình, hệ thống không nhận ra tên ngay lập tức. Nó đi qua một chuỗi bước:

1. Tìm tất cả khuôn mặt trong ảnh.
2. Cắt riêng từng khuôn mặt.
3. Căn chỉnh khuôn mặt để mắt, mũi và miệng nằm đúng vị trí.
4. Biến khuôn mặt thành một mã số gồm 512 số.
5. So sánh mã số đó với mã số của những người đã đăng ký.
6. Nếu đủ giống thì trả về sinh viên tương ứng.
7. Nếu không đủ chắc chắn thì trả về UNKNOWN hoặc AMBIGUOUS.
8. Backend lưu kết quả thành bản ghi điểm danh.

Có thể hình dung đơn giản như sau:

| Thành phần | Cách hiểu đơn giản | Công việc chính |
|---|---|---|
| YOLO11n | Người khoanh vùng | Chỉ ra khuôn mặt nằm ở đâu trong ảnh |
| MTCNN | Người căn chỉnh | Tìm mắt, mũi, miệng để xoay và căn khuôn mặt |
| InceptionResnetV1 | Người tạo mã khuôn mặt | Đổi ảnh khuôn mặt thành vector 512 chiều |
| ArcFace | Cách dạy model | Dạy người giống nhau có mã gần nhau, người khác nhau có mã cách xa nhau |
| Gallery | Kho mã khuôn mặt | Lưu vector của những người đã đăng ký |
| Cosine similarity | Thước đo độ giống | Đo hai vector gần nhau đến mức nào |
| Threshold | Mức đạt tối thiểu | Quyết định có chấp nhận kết quả hay không |
| Backend | Bộ phận nghiệp vụ | Lưu và cập nhật trạng thái điểm danh |

### 1.1. AI không tự lưu điểm danh

AI Service chỉ trả lời câu hỏi:

> “Khuôn mặt trong ảnh có thể là ai và độ chắc chắn bao nhiêu?”

Backend mới xử lý các việc:

- Sinh viên có nằm trong roster của buổi học hay không.
- Lưu ảnh bằng chứng.
- Tạo hoặc cập nhật attendance log.
- Phát sự kiện để giao diện cập nhật.
- Xử lý người lạ hoặc kết quả chưa rõ.

Tách như vậy giúp hệ thống dễ sửa. Có thể thay model AI mà không phải viết lại toàn bộ nghiệp vụ điểm danh.

---

## 2. Luồng xử lý đầy đủ từ camera đến điểm danh

### 2.1. Luồng tổng quát

~~~text
Ảnh từ camera
    |
    v
YOLO11n tìm khuôn mặt
    |
    v
Cắt từng khuôn mặt
    |
    v
MTCNN tìm điểm mắt, mũi, miệng
    |
    v
Căn chỉnh thành ảnh 160 x 160
    |
    v
InceptionResnetV1 tạo vector 512 chiều
    |
    v
Chuẩn hóa vector bằng L2 normalization
    |
    v
So sánh với gallery bằng cosine similarity
    |
    v
Kiểm tra threshold và ambiguity margin
    |
    v
MATCHED / UNKNOWN_PERSON / AMBIGUOUS
    |
    v
Backend lưu kết quả điểm danh
~~~

### 2.2. Ví dụ dễ hiểu

Giả sử ảnh có ba người:

1. YOLO phát hiện ba vùng mặt.
2. Hệ thống cắt thành ba ảnh nhỏ.
3. Mỗi ảnh được căn chỉnh và đưa qua recognizer.
4. Kết quả là ba vector:
   - vector của người A;
   - vector của người B;
   - vector của người C.
5. Hệ thống so từng vector với gallery.
6. Nếu vector của người A giống mã của SV001 nhất và điểm là 0.78, hệ thống có thể trả về SV001.
7. Nếu điểm cao nhất chỉ là 0.42, hệ thống không nên đoán. Nó trả về UNKNOWN_PERSON.
8. Nếu hai người cùng có điểm gần nhau, hệ thống trả về AMBIGUOUS để tránh điểm danh nhầm.

---

# 3. Thuật toán và model thứ nhất: YOLO11n phát hiện khuôn mặt

## 3.1. YOLO11n làm gì?

YOLO là model dùng để tìm vật thể trong ảnh. Trong dự án này, vật thể cần tìm chỉ có một loại:

> face – khuôn mặt.

YOLO không trả lời người đó là ai. YOLO chỉ trả lời:

- khuôn mặt nằm ở tọa độ nào;
- vùng đó có khả năng là khuôn mặt bao nhiêu phần trăm.

Ví dụ kết quả có thể có dạng:

~~~text
x1 = 120, y1 = 80
x2 = 260, y2 = 250
confidence = 0.91
class = face
~~~

Bốn giá trị x1, y1, x2, y2 tạo thành một hình chữ nhật bao quanh khuôn mặt.

## 3.2. YOLO nhận gì và trả gì?

| Nội dung | Giá trị |
|---|---|
| Dữ liệu đầu vào | Ảnh camera hoặc ảnh đã đọc từ file |
| Kích thước đưa vào model | 640 x 640 |
| Số lớp cần nhận biết | 1 lớp: face |
| Kết quả | Tọa độ box, confidence và nhãn face |
| Ngưỡng gọi trong hệ thống | conf = 0.35 |
| Model khởi đầu | yolo11n.pt |
| Model dùng trong hệ thống | face_best.pt |

Trong mã nguồn production, detector được gọi gần như sau:

~~~python
detector(image_bgr, imgsz=640, conf=0.35, verbose=False)
~~~

Nói đơn giản:

- imgsz=640: đưa ảnh về kích thước xử lý 640.
- conf=0.35: chỉ giữ vùng có độ tin cậy từ 0.35 trở lên.
- verbose=False: không in quá nhiều thông tin trong lúc chạy.

## 3.3. YOLO xử lý bên trong như thế nào?

Không cần hiểu tất cả phép toán bên trong, có thể chia thành bốn ý:

### Bước 1: Nhìn toàn bộ ảnh

YOLO là model one-stage. Từ one-stage có thể hiểu đơn giản là:

> Model đi qua ảnh một lần rồi dự đoán vị trí khuôn mặt.

Cách này thường nhanh, phù hợp với ảnh camera và ứng dụng gần thời gian thực.

### Bước 2: Lấy thông tin quan trọng của ảnh

Phần chính của YOLO nhìn các cạnh, vùng sáng tối, hình dạng và các mẫu giống khuôn mặt.

Ví dụ:

- hai vùng tối giống mắt;
- vùng giữa giống sống mũi;
- đường viền có thể là cằm;
- nhiều đặc điểm cùng xuất hiện trong một vùng.

### Bước 3: Dự đoán các vùng có thể là mặt

Model tạo ra nhiều dự đoán ban đầu. Mỗi dự đoán có:

- vị trí box;
- độ tin cậy;
- lớp face.

### Bước 4: Lọc kết quả

Các box có confidence thấp bị loại. Nếu nhiều box chồng lên cùng một khuôn mặt, thuật toán NMS giữ box tốt nhất và loại những box trùng.

NMS có thể hiểu như sau:

> Một khuôn mặt chỉ nên có một khung chính, không phải mười khung gần như giống nhau.

NMS là bước hậu xử lý thường có sẵn trong pipeline Ultralytics YOLO.

## 3.4. Vì sao chọn YOLO11n?

YOLO11n được chọn vì bốn lý do:

1. Nhẹ hơn các phiên bản lớn.
2. Tốc độ phù hợp với camera.
3. Đủ tốt cho bài toán chỉ có một lớp face.
4. Dễ huấn luyện và dễ tích hợp qua thư viện Ultralytics.

Chữ n thường được hiểu là nano, tức phiên bản nhỏ. Mục tiêu của bài toán điểm danh không phải nhận hàng chục loại vật thể, mà là tìm đúng vị trí khuôn mặt nhanh và ổn định.

Nếu dùng model quá lớn, độ chính xác có thể tăng nhưng:

- chạy chậm hơn;
- tốn bộ nhớ hơn;
- khó chạy trên máy yếu;
- không cần thiết nếu dữ liệu chỉ có một lớp.

## 3.5. Cấu hình huấn luyện YOLO

Notebook dùng các thông số sau:

| Tham số | Giá trị | Giải thích |
|---|---:|---|
| Dữ liệu train | 12.880 ảnh | Ảnh dùng để model học |
| Dữ liệu validation | 3.226 ảnh | Ảnh dùng để kiểm tra trong quá trình huấn luyện |
| Validation instances | 39.707 | Tổng số khuôn mặt được gắn nhãn trong tập validation |
| Kích thước ảnh | 640 x 640 | Kích thước xử lý |
| Batch size | 8 | Mỗi lần model học 8 ảnh |
| Epochs | 25 | Model đi qua toàn bộ tập train 25 vòng |
| Workers | 4 | Số luồng đọc dữ liệu |
| Seed | 42 | Giúp kết quả có thể lặp lại gần giống |
| GPU | 2 GPU T4 trong output notebook | Dùng để tăng tốc huấn luyện |
| Số lớp | 1 | Chỉ có lớp face |

### Epoch là gì?

Một epoch là một vòng model đã xem hết toàn bộ dữ liệu train một lần.

Ví dụ:

- 1 epoch: xem hết 12.880 ảnh một lần;
- 25 epochs: xem lại tập ảnh đó 25 vòng.

Nhiều epoch không luôn luôn tốt. Nếu học quá lâu, model có thể nhớ quá kỹ ảnh train nhưng kém với ảnh mới. Hiện tượng này gọi là overfitting, có thể hiểu là “học thuộc bài cũ nhưng làm bài mới không tốt”.

## 3.6. Số layer và số parameter của YOLO

Trong notebook, sau khi thay số lớp từ cấu hình ban đầu về 1 lớp face, summary chính ghi:

| Chỉ số | Giá trị |
|---|---:|
| Số layer trong summary | 181 |
| Parameters | 2.590.035 |
| Trainable gradients | 2.590.019 |
| GFLOPs | 6,5 |

Parameters là các con số bên trong model được cập nhật khi học. Có thể hiểu chúng là “nút điều chỉnh” giúp model học cách nhận biết.

GFLOPs là lượng phép tính tương đối cần cho một lần chạy. Số càng nhỏ thường giúp chạy nhanh hơn, nhưng độ chính xác còn phụ thuộc kiến trúc và dữ liệu.

Notebook cũng có summary sau khi fuse:

| Chế độ | Layer | Parameters | GFLOPs |
|---|---:|---:|---:|
| Summary trước fuse | 181 | 2.590.035 | 6,5 |
| Summary sau fuse | 100 | 2.582.347 | 6,4 |

Fuse có thể hiểu đơn giản là gộp một số lớp để chạy nhanh hơn khi dự đoán. Vì vậy số layer hiển thị trước và sau fuse khác nhau. Đây không phải là hai model được huấn luyện khác nhau.

## 3.7. Kết quả YOLO

Kết quả validation lấy từ notebook:

| Chỉ số | Giá trị gần đúng | Hiểu đơn giản |
|---|---:|---|
| Precision | 0,8253 | Trong các vùng model đã gọi là mặt, khoảng 82,53% là đúng |
| Recall | 0,5618 | Model tìm được khoảng 56,18% số mặt được gắn nhãn |
| mAP@50 | 0,6437 | Độ chính xác tổng hợp khi dùng mức IoU 0,50 |
| mAP@50-95 | 0,3397 | Điểm chặt hơn, yêu cầu box khớp tốt ở nhiều mức |

### Precision là gì?

Precision trả lời:

> Những gì model phát hiện là mặt thì đúng được bao nhiêu?

Precision cao nghĩa là ít báo nhầm.

### Recall là gì?

Recall trả lời:

> Trong tất cả khuôn mặt thật, model tìm ra được bao nhiêu?

Recall thấp nghĩa là model còn bỏ sót mặt. Trong bài toán điểm danh, bỏ sót mặt là vấn đề cần chú ý.

### IoU là gì?

IoU đo độ chồng lên nhau giữa:

- box model dự đoán;
- box đúng do người gắn nhãn.

Nếu hai box khớp nhiều thì IoU cao.

### mAP@50 và mAP@50-95 khác nhau thế nào?

- mAP@50 dùng một mức yêu cầu IoU là 0,50.
- mAP@50-95 tính ở nhiều mức từ dễ đến khó, nên thường thấp hơn.
- Vì vậy không nên chỉ nhìn một chỉ số duy nhất.

## 3.8. Lưu ý quan trọng về max_det

Notebook cảnh báo:

- có ảnh train chứa tối đa 1.968 object;
- có ảnh validation chứa tối đa 709 object;
- nhưng max_det đang là 300.

Điều này có nghĩa là trong một ảnh có quá nhiều mặt, phần validation có thể chỉ giữ tối đa 300 box. Khi đó recall có thể bị thấp giả tạo.

Cách xử lý nên ghi trong báo cáo:

> Kết quả hiện tại được giữ nguyên theo notebook. Tuy nhiên, cần chạy validation lại với max_det phù hợp với số object lớn nhất nếu muốn kết luận chính xác hơn về recall.

Không nên sửa số liệu để làm đẹp kết quả.

---

# 4. Thuật toán và model thứ hai: nhận diện khuôn mặt bằng ArcFace

## 4.1. Model nhận diện khác model phát hiện như thế nào?

Đây là điểm rất quan trọng:

- YOLO trả lời: “Mặt ở đâu?”
- Recognizer trả lời: “Mặt này giống ai?”

Hai model có nhiệm vụ khác nhau. Nếu bỏ YOLO, recognizer không biết nên cắt vùng nào. Nếu bỏ recognizer, hệ thống chỉ biết có mặt người nhưng không biết tên.

## 4.2. Recognizer nhận gì và trả gì?

| Nội dung | Giá trị |
|---|---|
| Dữ liệu đầu vào | Một ảnh khuôn mặt đã cắt và căn chỉnh |
| Kích thước ảnh | 160 x 160 |
| Model chính | InceptionResnetV1 |
| Đầu ra | Vector 512 chiều |
| Cách so sánh | Cosine similarity |
| Model trong production | facenet_best.pt |
| Checkpoint trong notebook mới | embedder_best.pt |

Vector 512 chiều là một dãy 512 số. Không cần hiểu đây là 512 pixel. Đây là 512 giá trị tóm tắt các đặc điểm khuôn mặt.

Ví dụ:

~~~text
[0.12, -0.08, 0.31, ..., 0.04]
~~~

Hai ảnh của cùng một người thường tạo ra hai vector gần nhau. Hai người khác nhau thường tạo ra vector xa nhau hơn.

## 4.3. Vì sao dùng vector thay vì phân loại thẳng tên sinh viên?

Có hai cách phổ biến:

### Cách 1: Phân loại trực tiếp

Model có một class cho mỗi sinh viên:

- SV001;
- SV002;
- SV003;
- ...

Nếu thêm sinh viên mới, thường phải:

- thêm class;
- huấn luyện lại đầu ra;
- kiểm tra lại model.

Cách này không thuận tiện cho hệ thống điểm danh thay đổi roster.

### Cách 2: Dùng embedding và gallery

Model chỉ tạo vector 512 chiều. Khi đăng ký sinh viên mới:

1. Chụp ảnh mới.
2. Tạo vector.
3. Lưu vector vào gallery.

Không nhất thiết phải huấn luyện lại toàn bộ model.

Đây là lý do kiến trúc embedding phù hợp với SPAS hơn. Hệ thống cần thêm hoặc xóa sinh viên thường xuyên theo lớp học và buổi học.

## 4.4. Dữ liệu ArcFace

Dataset ban đầu có:

- 10.572 danh tính;
- 490.623 ảnh.

Notebook chọn:

- 1.500 danh tính;
- 37.501 ảnh train;
- 9.383 ảnh validation.

Việc chọn 1.500 danh tính giúp giảm thời gian và tài nguyên huấn luyện cho phạm vi thử nghiệm, đồng thời vẫn đủ đa dạng để học đặc trưng khuôn mặt.

## 4.5. Cấu hình huấn luyện ArcFace

| Tham số | Giá trị |
|---|---:|
| Input | 160 x 160 |
| Embedding | 512 chiều |
| Epochs | 20 |
| Batch size | 64 |
| Learning rate ban đầu | 0,0001 |
| Workers | 4 |
| Seed | 42 |
| Số lớp train | 1.500 danh tính |
| GPU | 2 GPU khi notebook chạy |
| Optimizer | AdamW |
| Weight decay | 0,0001 |
| Scheduler | CosineAnnealingLR |
| Label smoothing | 0,05 |
| AMP | Bật khi có CUDA |

### Learning rate là gì?

Learning rate là kích thước bước cập nhật model sau mỗi lần học.

- Quá lớn: model cập nhật mạnh, dễ dao động.
- Quá nhỏ: model học chậm.
- 0,0001 là giá trị nhỏ, phù hợp với việc tinh chỉnh model đã có trọng số.

### AdamW là gì?

AdamW là thuật toán cập nhật parameter của model. Có thể hiểu nó là cách model tự điều chỉnh mức thay đổi của từng parameter sau mỗi batch.

AdamW còn có weight decay 0,0001. Weight decay giúp hạn chế model trở nên quá phức tạp và giảm nguy cơ học thuộc dữ liệu train.

### CosineAnnealingLR là gì?

Scheduler giảm learning rate theo đường cong cosine trong 20 epoch.

Nói đơn giản:

- lúc đầu model học với bước lớn hơn;
- về cuối bước học nhỏ dần;
- model có thời gian ổn định kết quả.

### Label smoothing là gì?

Thay vì dạy model rằng nhãn đúng chắc chắn 100%, label smoothing làm nhãn mềm hơn một chút.

Ví dụ thay vì:

~~~text
đúng = 1.0, sai = 0.0
~~~

có thể coi gần đúng là:

~~~text
đúng = 0.95, phần còn lại chia nhỏ cho các lớp khác
~~~

Điều này giúp model ít quá tự tin và thường ổn định hơn.

### AMP là gì?

AMP là cách dùng số chính xác thấp hơn ở một số phép tính để giảm bộ nhớ và tăng tốc GPU. Khi cần, model vẫn dùng độ chính xác cao hơn cho phần quan trọng.

## 4.6. Augmentation trong dữ liệu train

Ảnh train dùng các thay đổi nhỏ:

- Resize về 160 x 160;
- lật ngang ngẫu nhiên;
- thay đổi nhẹ độ sáng, độ tương phản hoặc màu;
- xoay nhẹ tối đa khoảng 5 độ;
- dịch ảnh nhẹ khoảng 3%;
- chuyển sang tensor;
- normalize với mean và std bằng 0,5.

Mục đích là làm model quen với ảnh thực tế:

- người hơi quay;
- ánh sáng khác nhau;
- camera đặt lệch;
- khuôn mặt không nằm chính giữa.

Ảnh validation không dùng các thay đổi ngẫu nhiên. Nếu validation cũng bị thay đổi ngẫu nhiên, kết quả sẽ khó so sánh giữa các lần chạy.

---

# 5. Kiến trúc InceptionResnetV1 giải thích đơn giản

## 5.1. Luồng trong model

Có thể nhìn model như một dây chuyền:

~~~text
Ảnh khuôn mặt 160 x 160 x 3
        |
        v
Các lớp convolution đầu vào
        |
        v
Block35 lặp 5 lần
        |
        v
Reduction-A
        |
        v
Block17 lặp 10 lần
        |
        v
Reduction-B
        |
        v
Block8 lặp 5 lần
        |
        v
Lớp cuối Block8
        |
        v
Average pooling
        |
        v
Linear layer
        |
        v
Vector khuôn mặt 512 chiều
~~~

### Convolution là gì?

Convolution là phép lọc ảnh. Ở lớp đầu, model có thể học các cạnh đơn giản. Ở lớp sâu hơn, model kết hợp các cạnh thành:

- mắt;
- mũi;
- miệng;
- hình dạng khuôn mặt;
- các đặc điểm khó nhìn hơn.

### Block là gì?

Block là một nhóm lớp được đóng gói thành một khối để lặp lại. Thay vì viết từng lớp rời rạc, kiến trúc gom chúng thành các block.

Notebook dùng kiến trúc InceptionResnetV1. Các nhóm block chính được thể hiện như sau:

| Nhóm | Số lần lặp trong kiến trúc |
|---|---:|
| Block35 | 5 |
| Block17 | 10 |
| Block8 | 5 |
| Block8 cuối | 1 |

Ngoài các block trên còn có các lớp đầu vào, lớp giảm kích thước, pooling, dropout và lớp tạo embedding. Notebook không in một con số layer tổng duy nhất theo cách đủ rõ để dùng làm số layer chính thức của recognizer. Vì vậy báo cáo nên dùng số block và số parameter đã đo được, không tự đoán tổng layer.

## 5.2. Vì sao dùng InceptionResnetV1?

Model này phù hợp vì:

1. Được thiết kế cho đặc trưng khuôn mặt.
2. Có thể tạo embedding cố định 512 chiều.
3. Có các kết nối residual giúp học sâu ổn định hơn.
4. Phù hợp với cách so sánh bằng khoảng cách giữa các vector.
5. Có thể dùng lại trọng số VGGFace2 làm điểm khởi đầu.

Kết nối residual có thể hiểu đơn giản:

> Một block không cần học lại toàn bộ thông tin từ đầu. Nó có thể giữ lại thông tin cũ rồi chỉ học thêm phần mới.

Cách này giúp việc học model sâu ổn định hơn.

## 5.3. Số parameter của recognizer

Notebook ghi số parameter của embedder:

| Thành phần | Parameters |
|---|---:|
| InceptionResnetV1 embedder | 27.910.327 |
| ArcMarginProduct với 1.500 lớp | 768.000 |
| Tổng xấp xỉ khi train | 28.678.327 |

Phép tính của ArcMarginProduct:

~~~text
1.500 lớp x 512 chiều = 768.000 parameter
~~~

Trong lúc chạy production, hệ thống dùng phần tạo embedding để biến ảnh thành vector. Phần classifier dùng trong train không cần dùng như một đầu ra tên người trong pipeline gallery.

---

# 6. ArcFace là gì và học như thế nào?

## 6.1. Ý tưởng cốt lõi

ArcFace không chỉ dạy model trả đúng class. Nó còn dạy khoảng cách giữa các khuôn mặt:

- ảnh của cùng một người phải gần nhau;
- ảnh của người khác nhau phải xa nhau;
- cần có một khoảng cách an toàn giữa hai nhóm.

Ví dụ trong lớp học:

- Ba ảnh của bạn A phải nằm gần nhau trên bản đồ.
- Ảnh của bạn B phải nằm ở khu vực khác.
- Không chỉ cần A gần hơn B một chút; A cần gần đủ rõ để giảm nhầm lẫn.

## 6.2. ArcMarginProduct trong notebook

Notebook tạo head với:

| Tham số | Giá trị |
|---|---:|
| Embedding dimension | 512 |
| Số class | 1.500 |
| Scale | 32,0 |
| Margin | 0,35 |

### Embedding dimension = 512

Mỗi khuôn mặt được biểu diễn bằng 512 số.

### Margin = 0,35

Margin là khoảng cách an toàn thêm vào khi học. Nó làm yêu cầu phân biệt giữa các class khó hơn một chút, nhờ đó vector sau cùng thường có tính phân biệt tốt hơn.

### Scale = 32

Scale giúp giá trị dùng trong hàm loss có độ lớn phù hợp để model học ổn định.

Không cần nhớ công thức ngay. Chỉ cần nhớ:

> ArcFace ép các vector cùng người gần nhau hơn và các vector khác người tách nhau rõ hơn.

## 6.3. Loss trong quá trình học

Trong mỗi batch, model làm các việc:

1. Nhận ảnh khuôn mặt.
2. Tạo embedding 512 chiều.
3. Dùng ArcMarginProduct để so embedding với 1.500 class.
4. Tính loss.
5. Cập nhật parameter bằng AdamW.
6. Lặp lại cho đến hết epoch.

Loss là một con số cho biết model đang sai nhiều hay ít. Mục tiêu là giảm loss trên train và giữ validation tốt.

## 6.4. Vì sao model train có 1.500 class nhưng production dùng gallery?

1.500 class là các danh tính được dùng làm nhãn trong giai đoạn huấn luyện.

Production lại dùng vector và gallery vì:

- roster theo từng session có thể thay đổi;
- thêm sinh viên mới không cần thay đổi classifier;
- dễ kiểm soát threshold;
- dễ trả về UNKNOWN khi không có người phù hợp.

Đây là sự khác nhau giữa:

- cách dạy model;
- cách sử dụng model sau khi đã học.

---

# 7. Kết quả huấn luyện và đánh giá ArcFace

## 7.1. Validation theo epoch

| Epoch | Top-1 | Top-5 |
|---:|---:|---:|
| 1 | 0,5054 | 0,6800 |
| 2 | 0,7040 | 0,8333 |
| 3 | 0,7745 | 0,8802 |
| 4 | 0,8158 | 0,8962 |
| 5 | 0,8393 | 0,9058 |
| 6 | 0,8528 | 0,9113 |
| 7 | 0,8627 | 0,9164 |
| 8 | 0,8723 | 0,9183 |
| 9 | 0,8751 | 0,9186 |
| 10 | 0,8784 | 0,9219 |
| 11 | 0,8820 | 0,9205 |
| 12 | 0,8803 | 0,9201 |
| 13 | 0,8860 | 0,9217 |
| 14 | 0,8850 | 0,9219 |
| 15 | 0,8879 | 0,9208 |
| 16 | 0,8865 | 0,9207 |
| 17 | 0,8876 | 0,9215 |
| 18 | 0,8883 | 0,9209 |
| 19 | 0,8888 | 0,9208 |
| 20 | 0,8896 | 0,9208 |

Ở epoch 20:

- Top-1 = 0,8896, tương đương 88,96%;
- Top-5 = 0,9208, tương đương 92,08%.

### Top-1 là gì?

Nếu đáp án đúng nằm ở vị trí đầu tiên model chọn, đó là một lần đúng Top-1.

### Top-5 là gì?

Nếu đáp án đúng nằm trong năm lựa chọn đầu tiên, đó là một lần đúng Top-5.

Top-5 cao hơn Top-1 là bình thường vì model được phép có thêm bốn lựa chọn dự phòng.

## 7.2. Kết quả gallery

Notebook đánh giá theo cách tạo gallery:

| Chỉ số | Giá trị |
|---|---:|
| Số identities | 1.500 |
| Số ảnh đánh giá | 9.383 |
| Gallery Top-1 accuracy | 0,8801 |
| Gallery Top-5 accuracy | 0,9141 |
| Cosine trung bình của cặp đúng | 0,7742 |
| Khoảng cách trung bình giữa top-1 và runner-up | 0,3713 |

Hai nhóm metric khác nhau:

- Validation Top-1/Top-5 đánh giá theo đầu ra classifier trong quá trình train.
- Gallery Top-1/Top-5 gần hơn với cách hệ thống production sử dụng: so vector với kho vector.

Vì vậy khi nói về khả năng chạy thật, nên ưu tiên giải thích gallery metrics cùng với test end-to-end.

## 7.3. Cosine similarity là gì?

Cosine similarity đo góc giữa hai vector.

- Gần cùng hướng: giá trị cao, có thể là cùng người.
- Khác hướng nhiều: giá trị thấp, có thể là người khác.

Trong hệ thống, điểm được tính bằng tích vô hướng giữa các vector đã L2 normalize. Khi cả hai vector đã được chuẩn hóa, tích vô hướng chính là cosine similarity.

Công thức ý tưởng:

~~~text
score = gallery_vector . query_vector
~~~

Nếu gallery có N người, hệ thống tính N điểm cho một khuôn mặt query, rồi sắp xếp từ cao xuống thấp.

## 7.4. L2 normalization là gì?

L2 normalization đưa vector về cùng một độ dài chuẩn.

Nói đơn giản:

> Trước khi so sánh, hệ thống đưa các vector về cùng thang đo để không vector nào thắng chỉ vì có số lớn hơn.

Hệ thống normalize:

- vector của ảnh query;
- vector lưu trong gallery.

## 7.5. Threshold và ambiguity margin

Trong mã nguồn production:

- acceptThreshold mặc định là 0,60;
- ambiguityMargin mặc định là 0,05.

Quy tắc nhận diện:

~~~text
Nếu top1 < 0,60:
    UNKNOWN_PERSON

Nếu top1 - runner_up < 0,05:
    AMBIGUOUS

Ngược lại:
    MATCHED
~~~

Trong đó:

- top1 là điểm cao nhất;
- runner_up là điểm cao thứ hai.

### Ví dụ 1: MATCHED

~~~text
top1 = 0,78
runner_up = 0,61
hiệu = 0,17
~~~

0,78 lớn hơn 0,60 và chênh lệch 0,17 lớn hơn 0,05. Kết quả đủ rõ để MATCHED.

### Ví dụ 2: UNKNOWN_PERSON

~~~text
top1 = 0,48
runner_up = 0,35
~~~

Dù top1 cao nhất, nó vẫn thấp hơn 0,60. Hệ thống không đoán tên và trả UNKNOWN_PERSON.

### Ví dụ 3: AMBIGUOUS

~~~text
top1 = 0,72
runner_up = 0,70
hiệu = 0,02
~~~

Top1 vượt ngưỡng nhưng hai người quá gần nhau. Hệ thống trả AMBIGUOUS để tránh nhận nhầm.

---

# 8. Tiền xử lý và căn chỉnh khuôn mặt

## 8.1. Vì sao không đưa ảnh crop thẳng vào recognizer?

Nếu khuôn mặt bị nghiêng hoặc lệch vị trí, recognizer phải học quá nhiều biến đổi không cần thiết.

Ví dụ:

- mắt bên trái lúc cao, lúc thấp;
- mặt quay 90 độ;
- khuôn mặt nằm sát mép ảnh;
- kích thước mặt thay đổi.

Căn chỉnh giúp đưa các khuôn mặt về dạng gần giống nhau trước khi nhận diện.

## 8.2. MTCNN làm gì?

Trong hệ thống, MTCNN được dùng như bộ phận hỗ trợ:

1. Tìm các điểm quan trọng trên mặt.
2. Thử một số góc xoay.
3. Chọn kết quả có xác suất tốt nhất.
4. Dùng điểm mắt, mũi và miệng để căn ảnh.

Các góc được thử trong mã nguồn:

- không xoay;
- xoay 90 độ theo chiều kim đồng hồ;
- xoay 90 độ ngược chiều kim đồng hồ;
- xoay 180 độ.

MTCNN không phải detector chính của hệ thống. Detector chính vẫn là YOLO11n. MTCNN chỉ giúp căn chỉnh sau khi YOLO đã tìm được box.

Mã nguồn hiện không ghi một con số layer hoặc parameter count chính thức cho MTCNN. Báo cáo không nên tự đưa ra con số chưa được kiểm tra.

## 8.3. Affine transform là gì?

Sau khi có vị trí mắt, mũi và miệng, hệ thống tìm phép biến đổi để đưa các điểm đó về một mẫu cố định.

Có thể hiểu như việc:

> Xoay, co giãn và dịch ảnh để mắt, mũi, miệng nằm đúng các vị trí chuẩn.

Sau đó ảnh được warp về 160 x 160.

## 8.4. Chuẩn bị ảnh trước khi chạy recognizer

Pipeline trong production:

1. Crop khuôn mặt từ box YOLO.
2. Căn chỉnh bằng landmark.
3. Chuyển BGR sang RGB.
4. Resize về 160 x 160.
5. Chuyển ảnh thành tensor.
6. Normalize bằng fixed image standardization.
7. Chạy InceptionResnetV1.
8. L2 normalize vector đầu ra.

Nếu kích thước nhỏ nhất của crop dưới 80 pixel, hệ thống bỏ qua vì ảnh quá nhỏ để nhận diện ổn định.

---

# 9. Đăng ký sinh viên và tạo gallery

## 9.1. Vì sao cần nhiều ảnh khi đăng ký?

Một ảnh có thể:

- bị mờ;
- thiếu sáng;
- bị nghiêng;
- có biểu cảm khác;
- bị che một phần.

Dùng nhiều ảnh giúp vector đại diện cho người đó ổn định hơn.

## 9.2. Quy tắc enrollment trong hệ thống

Mã nguồn yêu cầu:

- ít nhất 3 frame được upload;
- ít nhất 5 crop rõ ràng;
- có đủ tư thế front, left và right.

Quy trình:

1. Nhận các frame đăng ký.
2. Dùng YOLO tìm mặt trong từng frame.
3. Lọc crop quá nhỏ hoặc quá xấu.
4. Căn chỉnh từng mặt.
5. Tạo vector 512 chiều cho từng crop.
6. Tính vector trung bình.
7. L2 normalize vector trung bình.
8. Kiểm tra trùng với gallery cũ.
9. Lưu student_id và embedding vào gallery.npz.

## 9.3. Tại sao lấy trung bình vector?

Nếu một sinh viên có nhiều vector:

~~~text
v1, v2, v3, v4, v5
~~~

Hệ thống lấy vector trung bình:

~~~text
v_mean = (v1 + v2 + v3 + v4 + v5) / 5
~~~

Sau đó chuẩn hóa lại.

Cách này làm giảm ảnh hưởng của một frame xấu và tạo một vector đại diện chung cho sinh viên.

## 9.4. Kiểm tra trùng khi đăng ký

Nếu vector mới quá giống một người đã có trong gallery, hệ thống kiểm tra duplicate ở score từ 0,60 trở lên.

Mục tiêu là cảnh báo:

> Có khả năng người này đã được đăng ký trước đó.

Đây là lớp bảo vệ dữ liệu, tránh một student bị tạo nhiều bản ghi khuôn mặt.

---

# 10. Gallery và roster của từng buổi học

## 10.1. Gallery là gì?

Gallery là kho vector khuôn mặt đã đăng ký.

Nó không chỉ là thư mục ảnh. Thành phần quan trọng là:

- student_ids;
- embeddings.

Trong đó embeddings có dạng:

~~~text
N x 512
~~~

N là số người trong gallery, mỗi người có một vector 512 chiều.

## 10.2. Roster là gì?

Một gallery có thể chứa nhiều sinh viên của cả hệ thống. Một buổi học chỉ có một nhóm sinh viên.

Khi bắt đầu session:

1. Backend gửi session_id.
2. AI Service lấy roster của session.
3. Hệ thống chỉ giữ vector của những sinh viên thuộc roster.
4. Các frame sau đó chỉ được so với nhóm này.

Lợi ích:

- giảm số lần so sánh;
- giảm khả năng nhận nhầm người không có trong buổi;
- đúng với nghiệp vụ lớp học.

## 10.3. Cách tìm người gần nhất

Giả sử roster có 4 người:

~~~text
score(SV001) = 0,78
score(SV002) = 0,43
score(SV003) = 0,61
score(SV004) = 0,39
~~~

Hệ thống sắp xếp:

~~~text
SV001, SV003, SV002, SV004
~~~

Sau đó áp dụng threshold và ambiguity margin trước khi quyết định.

---

# 11. Cấu trúc tích hợp AI với hệ thống SPAS

## 11.1. Các phần chính

Có thể chia hệ thống thành bốn phần:

| Phần | Vai trò |
|---|---|
| Frontend | Hiển thị camera, kết quả và trạng thái điểm danh |
| Backend | Quản lý session, roster, attendance và dữ liệu nghiệp vụ |
| AI Service | Chạy YOLO, alignment, recognizer và similarity search |
| Gallery/Storage | Lưu vector khuôn mặt, checkpoint và ảnh bằng chứng |

## 11.2. Vì sao tách AI Service?

Nếu chạy model trực tiếp trong Backend:

- Backend phải cài toàn bộ PyTorch, Ultralytics và thư viện ảnh;
- việc scale API khó hơn;
- lỗi model có thể ảnh hưởng API nghiệp vụ;
- thay model khó hơn.

Tách AI Service giúp:

- đóng gói môi trường AI riêng;
- dùng GPU nếu cần;
- cập nhật checkpoint độc lập;
- API Backend vẫn ổn định;
- dễ kiểm thử từng phần.

## 11.3. Luồng gọi API

Backend gọi endpoint nội bộ:

~~~text
POST /internal/v1/attendance-sessions/{sessionId}/recognitions
~~~

Request chứa ảnh frame. AI Service thực hiện:

1. Kiểm tra session và roster.
2. Chạy detector.
3. Tạo embedding cho từng mặt.
4. So với roster gallery.
5. Trả về danh sách nhận diện.

Kết quả có thể chứa:

- bbox;
- quality;
- pose;
- score;
- runnerUpScore;
- evidenceCrop;
- studentId nếu MATCHED.

Nếu kết quả UNKNOWN hoặc AMBIGUOUS, studentId không được trả như một người đã xác nhận.

## 11.4. Backend xử lý kết quả như thế nào?

Backend có service xử lý recognition. Nó:

1. Đọc studentId nếu AI trả MATCHED.
2. Kiểm tra student đó có trong roster không.
3. Lưu detection.
4. Lưu evidence crop nếu cần.
5. Tạo hoặc cập nhật attendance log.
6. Phát event cho giao diện.
7. Xử lý UNKNOWN và AMBIGUOUS theo nghiệp vụ.

AI chỉ đưa ra bằng chứng và điểm số. Backend mới là nơi quyết định trạng thái nghiệp vụ cuối cùng.

## 11.5. Cache model và cache roster

Mã nguồn dùng cache cho model:

- detector được load một lần;
- recognizer được load một lần;
- các lần gọi sau dùng lại model trong bộ nhớ.

Mục tiêu là không đọc file checkpoint và khởi tạo model lại sau mỗi frame.

Roster của session cũng được lưu trong bộ nhớ:

~~~text
ROSTERS[session_id] = matrix N x 512
~~~

Nhờ vậy hệ thống có thể so sánh nhanh hơn.

## 11.6. Thiết bị chạy model

Mã nguồn chọn:

- CUDA nếu máy có GPU hỗ trợ;
- CPU nếu không có GPU.

Điều này giúp hệ thống có thể chạy ở nhiều môi trường. Tuy nhiên tốc độ camera sẽ khác nhau giữa GPU và CPU.

---

# 12. Checkpoint notebook và checkpoint production

## 12.1. Hai tên file không nên đánh đồng

Notebook mới ghi checkpoint:

~~~text
embedder_best.pt
~~~

Production mặc định đọc:

~~~text
facenet_best.pt
~~~

Đây là hai file khác tên. Không được kết luận rằng production đã tự động dùng checkpoint notebook mới.

## 12.2. Cần kiểm tra gì trước khi thay model?

Trước khi dùng embedder_best.pt cho production, phải kiểm tra:

1. Cấu trúc model có đúng InceptionResnetV1 không.
2. Tên key trong state_dict có phù hợp không.
3. Kích thước output có đúng 512 không.
4. Cách preprocess có giống lúc train không.
5. Vector cũ trong gallery có được tạo bởi cùng model hay không.
6. Nếu khác model, có cần tạo lại gallery không.
7. Threshold 0,60 có còn phù hợp không.

Điểm số của hai model khác nhau không nên so trực tiếp nếu gallery được tạo bằng một model còn query được tạo bằng model khác.

## 12.3. Vì sao có thể phải tạo lại gallery?

Giả sử:

- gallery cũ được tạo bởi facenet_best.pt;
- query mới được tạo bởi embedder_best.pt.

Dù cả hai đều trả vector 512 chiều, không có nghĩa là hai vector nằm cùng một không gian. 512 chiều chỉ là kích thước; cách model học ra từng chiều có thể khác.

Cách an toàn:

1. Chọn checkpoint production.
2. Dùng checkpoint đó tạo lại embedding cho toàn bộ gallery.
3. Chạy test nhận diện.
4. Chọn lại threshold nếu cần.
5. Sau đó mới triển khai.

---

# 13. Vì sao chọn kiến trúc hai model?

## 13.1. Không dùng một model làm tất cả

Một model duy nhất phải vừa:

- tìm vị trí mặt;
- căn chỉnh;
- nhận diện danh tính;
- xử lý người lạ;
- chạy nhanh theo camera.

Việc tách hai model làm từng việc rõ ràng hơn:

| Bài toán | Model |
|---|---|
| Tìm vị trí khuôn mặt | YOLO11n |
| Căn chỉnh mặt | MTCNN + affine transform |
| Tạo đặc trưng nhận diện | InceptionResnetV1 |
| Phân biệt trong lúc train | ArcFace |
| Tìm người gần nhất | Cosine similarity |
| Quyết định có nhận hay không | Threshold + ambiguity margin |

## 13.2. Lợi ích của kiến trúc này

- Dễ thay detector mà không sửa recognizer.
- Dễ thay recognizer mà không sửa API nghiệp vụ.
- Có thể thêm sinh viên bằng enrollment.
- Có cơ chế UNKNOWN.
- Có cơ chế AMBIGUOUS.
- Dễ giải thích trong báo cáo.
- Dễ đo metric riêng cho từng công đoạn.

## 13.3. Nhược điểm

- Có nhiều bước nên tổng thời gian xử lý tăng.
- Nếu detector bỏ sót mặt, recognizer không có cơ hội sửa.
- Nếu alignment sai, embedding có thể sai.
- Threshold phụ thuộc môi trường thực tế.
- Ánh sáng, góc mặt, khẩu trang và chất lượng camera ảnh hưởng kết quả.
- Cần đồng bộ checkpoint và gallery.

---

# 14. Đánh giá theo từng tầng của hệ thống

Không nên chỉ nói “accuracy của hệ thống là X%”. Cần tách ra:

## 14.1. Tầng detector

Đo:

- Precision;
- Recall;
- mAP@50;
- mAP@50-95;
- thời gian chạy mỗi frame.

Câu hỏi chính:

> Model có tìm đủ mặt và vẽ box đúng vị trí không?

## 14.2. Tầng recognizer

Đo:

- Top-1;
- Top-5;
- cosine similarity của cặp đúng;
- khoảng cách giữa top1 và runner-up;
- false accept;
- false reject.

Câu hỏi chính:

> Khi đã có crop đúng, model có phân biệt đúng người không?

## 14.3. Tầng quyết định

Đo:

- số MATCHED đúng;
- số UNKNOWN đúng;
- số AMBIGUOUS;
- false accept rate;
- false reject rate.

Câu hỏi chính:

> Threshold có giúp hệ thống an toàn không?

## 14.4. Tầng end-to-end

Đo:

- từ frame đến kết quả mất bao lâu;
- tỷ lệ frame có nhận diện đúng;
- tỷ lệ điểm danh đúng;
- số lần trùng hoặc ghi lặp;
- độ ổn định khi nhiều người xuất hiện.

Câu hỏi chính:

> Người dùng có thể dùng hệ thống trong buổi học thật không?

---

# 15. Các lỗi thường gặp và cách giải thích

## 15.1. YOLO tìm thấy mặt nhưng nhận diện sai

Có thể do:

- crop quá nhỏ;
- ánh sáng xấu;
- mặt nghiêng;
- alignment sai;
- checkpoint recognizer không tương thích gallery;
- threshold chưa phù hợp.

## 15.2. Người đã đăng ký nhưng bị UNKNOWN

Có thể do:

- cosine score dưới 0,60;
- ảnh camera khác xa ảnh enrollment;
- gallery chưa được tạo lại bằng đúng checkpoint;
- mặt bị che;
- detector chỉ cắt một phần mặt.

## 15.3. Nhận nhầm hai người

Có thể do:

- top1 và runner-up quá gần;
- threshold quá thấp;
- hai người có góc hoặc ánh sáng làm đặc trưng gần nhau;
- dữ liệu enrollment chưa đủ nhiều tư thế.

Ambiguity margin 0,05 giúp chuyển các trường hợp không rõ thành AMBIGUOUS thay vì ép chọn một người.

## 15.4. Model chạy chậm

Có thể do:

- chạy CPU;
- load model nhiều lần;
- ảnh đầu vào quá lớn;
- xử lý từng frame quá dày;
- không dùng cache;
- chạy quá nhiều bước alignment.

Các cách cải thiện:

- giữ model trong memory;
- dùng GPU;
- giảm tần suất xử lý frame;
- chỉ chạy recognizer trên box hợp lệ;
- cân nhắc fuse model khi inference;
- đo thời gian từng bước trước khi tối ưu.

---

# 16. Câu hỏi bảo vệ thường gặp

## Câu 1: YOLO và ArcFace khác nhau thế nào?

YOLO tìm vị trí khuôn mặt. ArcFace giúp model học đặc trưng để phân biệt danh tính. YOLO không nhận ra tên người.

## Câu 2: Vì sao output của recognizer là 512 chiều?

512 là một kích thước đủ gọn để lưu và so sánh nhanh, nhưng vẫn đủ khả năng biểu diễn nhiều đặc điểm khuôn mặt. Đây là lựa chọn của kiến trúc InceptionResnetV1 trong dự án.

## Câu 3: Vì sao không dùng classifier để trả thẳng tên?

Vì danh sách sinh viên có thể thay đổi. Dùng embedding và gallery cho phép thêm sinh viên mới mà không cần train lại toàn bộ model.

## Câu 4: ArcFace có phải một model riêng không?

Trong notebook, ArcFace được thể hiện qua ArcMarginProduct gắn sau InceptionResnetV1. InceptionResnetV1 tạo embedding; ArcMarginProduct giúp việc học phân biệt các identity tốt hơn.

## Câu 5: Cosine similarity dùng để làm gì?

Nó đo độ giống giữa vector query và vector trong gallery. Điểm càng cao thì hai vector càng giống về hướng.

## Câu 6: Threshold 0,60 có phải luôn đúng không?

Không. Đây là giá trị hiện tại trong mã nguồn. Threshold nên được kiểm tra lại trên dữ liệu thực tế để cân bằng nhận nhầm và bỏ sót.

## Câu 7: Tại sao cần ambiguity margin?

Nếu người đứng đầu chỉ hơn người thứ hai một chút, model chưa đủ chắc chắn. Trả AMBIGUOUS an toàn hơn tự chọn sai.

## Câu 8: MTCNN có thay YOLO không?

Không. YOLO là detector chính. MTCNN hỗ trợ tìm landmark và căn chỉnh sau khi đã có box.

## Câu 9: 181 layer của YOLO có giống 181 layer của recognizer không?

Không nên so trực tiếp. Mỗi framework có cách đếm layer khác nhau. YOLO notebook có summary rõ 181 layer trước fuse. Recognizer được mô tả tốt hơn bằng nhóm block và số parameter 27.910.327.

## Câu 10: Model notebook mới đã chạy production chưa?

Chưa thể kết luận chỉ dựa vào tên file. Notebook có embedder_best.pt, còn production mặc định đọc facenet_best.pt. Cần kiểm tra đường dẫn, state_dict, preprocess và gallery trước khi thay.

---

# 17. Cách trình bày phần AI trong báo cáo

Nên trình bày theo thứ tự sau để người đọc không bị rối:

1. Bài toán cần giải quyết.
2. Vì sao cần detector và recognizer riêng.
3. YOLO11n: nhiệm vụ, kiến trúc, cấu hình và metric.
4. ArcFace: embedding, kiến trúc và cách train.
5. Các bước alignment và preprocessing.
6. Cosine similarity, threshold và ambiguity margin.
7. Enrollment và gallery.
8. Cách AI Service kết nối Backend.
9. Kết quả từng tầng.
10. Hạn chế và hướng cải thiện.

Mỗi model nên có một đoạn tóm tắt ngắn:

> Model này nhận dữ liệu gì, trả kết quả gì, dùng ở bước nào và tại sao chọn nó.

## 17.1. Đoạn tóm tắt YOLO có thể dùng trong báo cáo

> YOLO11n được sử dụng để phát hiện khuôn mặt trong khung hình camera. Model nhận ảnh kích thước 640 x 640 và trả về các hình chữ nhật bao quanh khuôn mặt cùng độ tin cậy. Do hệ thống cần xử lý ảnh nhanh và bài toán chỉ có một lớp face, phiên bản nano được lựa chọn để cân bằng giữa tốc độ và độ chính xác. Sau khi huấn luyện, model có 181 layer trong summary, khoảng 2,59 triệu parameter và đạt Precision 0,8253, Recall 0,5618, mAP@50 0,6437 và mAP@50-95 0,3397 trên tập validation.

## 17.2. Đoạn tóm tắt ArcFace có thể dùng trong báo cáo

> InceptionResnetV1 được sử dụng để chuyển ảnh khuôn mặt đã căn chỉnh thành vector embedding 512 chiều. Trong quá trình train, ArcMarginProduct giúp tăng khoảng cách giữa các identity khác nhau và làm các ảnh của cùng identity gần nhau hơn. Model được huấn luyện trên 1.500 identity trong 20 epoch, dùng AdamW, CosineAnnealingLR, label smoothing và AMP. Ở epoch 20, validation Top-1 đạt 88,96% và Top-5 đạt 92,08%. Khi đánh giá theo gallery, Top-1 đạt 88,01% và Top-5 đạt 91,41%.

## 17.3. Đoạn tóm tắt tích hợp có thể dùng trong báo cáo

> AI Service nhận frame từ Backend thông qua API nội bộ. YOLO11n phát hiện các khuôn mặt, MTCNN hỗ trợ tìm landmark và căn chỉnh, sau đó InceptionResnetV1 tạo embedding 512 chiều. Embedding được chuẩn hóa L2 và so sánh với gallery bằng cosine similarity. Hệ thống sử dụng acceptThreshold bằng 0,60 và ambiguityMargin bằng 0,05 để phân biệt MATCHED, UNKNOWN_PERSON và AMBIGUOUS. Backend tiếp nhận kết quả, lưu detection và cập nhật attendance log.

---

# 18. Checklist kỹ thuật trước khi chốt báo cáo

## Model và dữ liệu

- [ ] Ghi rõ YOLO chỉ phát hiện, không nhận tên.
- [ ] Ghi rõ recognizer tạo embedding 512 chiều.
- [ ] Ghi số ảnh train, validation và số identity.
- [ ] Ghi input size của từng model.
- [ ] Ghi epoch, batch size và learning rate.
- [ ] Ghi parameter count đã đo được.
- [ ] Không tự đoán tổng layer của recognizer.
- [ ] Nêu rõ MTCNN là alignment hỗ trợ.

## Metric

- [ ] Có Precision và Recall cho detector.
- [ ] Có mAP@50 và mAP@50-95.
- [ ] Có Top-1 và Top-5 cho recognizer.
- [ ] Có gallery metrics.
- [ ] Giải thích ý nghĩa từng metric.
- [ ] Nêu cảnh báo max_det = 300.
- [ ] Không gọi gallery accuracy là accuracy end-to-end.

## Tích hợp

- [ ] Nêu tên checkpoint notebook: embedder_best.pt.
- [ ] Nêu tên checkpoint production: facenet_best.pt.
- [ ] Kiểm tra model và gallery có cùng không gian embedding.
- [ ] Nêu endpoint Backend gọi AI Service.
- [ ] Nêu threshold và ambiguity margin.
- [ ] Nêu Backend mới là nơi lưu attendance.

## Cách viết

- [ ] Giải thích thuật ngữ ngay lần đầu xuất hiện.
- [ ] Dùng ví dụ số cho threshold.
- [ ] Không chỉ liệt kê tên model.
- [ ] Không khẳng định AI đã dùng checkpoint mới nếu chưa kiểm tra.
- [ ] Viết rõ hạn chế thay vì che giấu số liệu thấp.
- [ ] Với phần khó, viết câu ngắn và có bảng tóm tắt.

---

# 19. Kết luận ngắn

SPAS dùng một pipeline AI gồm nhiều bước, mỗi bước có một nhiệm vụ riêng:

1. YOLO11n tìm vị trí mặt.
2. MTCNN và affine transform căn chỉnh mặt.
3. InceptionResnetV1 tạo vector 512 chiều.
4. ArcFace giúp model học đặc trưng phân biệt người.
5. Cosine similarity so sánh với gallery.
6. Threshold và ambiguity margin giúp hệ thống không đoán bừa.
7. Backend lưu kết quả thành điểm danh.

Điểm quan trọng nhất của kiến trúc là hệ thống không phụ thuộc vào việc classifier phải biết trước toàn bộ sinh viên trong mọi buổi học. Model tạo embedding một lần, còn gallery và roster quyết định nhóm người được kiểm tra. Cách này phù hợp với hệ thống điểm danh vì danh sách lớp có thể thay đổi.

Khi thuyết trình, chỉ cần nhớ câu sau:

> YOLO tìm mặt, ArcFace biến mặt thành mã, cosine tìm người giống nhất, còn threshold quyết định có đủ chắc chắn để điểm danh hay không.

