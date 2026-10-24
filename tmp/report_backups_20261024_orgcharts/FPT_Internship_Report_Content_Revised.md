# BÁO CÁO THỰC TẬP TỐT NGHIỆP

## Gán nhãn dữ liệu và tinh chỉnh mô hình YOLO tại FPT Smart Cloud

---

## BÌA

**BỘ GIÁO DỤC VÀ ĐÀO TẠO**

**TRƯỜNG ĐẠI HỌC THĂNG LONG**

**KHOA TOÁN - TIN**

### BÁO CÁO THỰC TẬP TỐT NGHIỆP

**Đơn vị thực tập:** CÔNG TY TNHH FPT SMART CLOUD

**ĐỀ TÀI:** GÁN NHÃN DỮ LIỆU VÀ TINH CHỈNH MÔ HÌNH YOLO CHO BÀI TOÁN THỊ GIÁC MÁY TÍNH

**Sinh viên:** Trương Trung Kiên

**Mã sinh viên:** A48282

**Chuyên ngành:** Khoa học máy tính

**Giảng viên hướng dẫn:** ThS. Nguyễn Hà Doanh

**HÀ NỘI - 2026**

## BÌA PHỤ

**BỘ GIÁO DỤC VÀ ĐÀO TẠO**

**TRƯỜNG ĐẠI HỌC THĂNG LONG**

**KHOA TOÁN - TIN**

### BÁO CÁO THỰC TẬP TỐT NGHIỆP

**Đơn vị thực tập:** CÔNG TY TNHH FPT SMART CLOUD

**ĐỀ TÀI:** GÁN NHÃN DỮ LIỆU VÀ TINH CHỈNH MÔ HÌNH YOLO CHO BÀI TOÁN THỊ GIÁC MÁY TÍNH

**Sinh viên:** Trương Trung Kiên

**Mã sinh viên:** A48282

**Chuyên ngành:** Khoa học máy tính

**Giảng viên hướng dẫn:** ThS. Nguyễn Hà Doanh

**HÀ NỘI - 2026**

---

## LỜI CẢM ƠN

Em xin cảm ơn Ban Giám hiệu, các thầy cô Khoa Toán - Tin, Trường Đại học Thăng Long, đặc biệt là giảng viên hướng dẫn ThS. Nguyễn Hà Doanh, đã trang bị kiến thức nền tảng và tạo điều kiện để em hoàn thành kỳ thực tập và báo cáo này. Em cũng xin cảm ơn Ban lãnh đạo Công ty TNHH FPT Smart Cloud, Khối Sản phẩm AI và Trung tâm Sản phẩm Vision đã tiếp nhận, hướng dẫn em làm quen với môi trường làm việc và chia sẻ kinh nghiệm trong lĩnh vực thị giác máy tính.

Trong thời gian làm việc, em được tham gia gán nhãn dữ liệu và tinh chỉnh mô hình YOLO cho các bài toán thị giác máy tính. Những công việc này giúp em hiểu rõ hơn mối liên hệ giữa chất lượng dữ liệu, cách huấn luyện và kết quả mô hình. Em xin cảm ơn các anh, chị và các thành viên trong nhóm đã trao đổi, góp ý và hỗ trợ em trong quá trình thực hiện nhiệm vụ.

Do thời gian và kinh nghiệm còn hạn chế, báo cáo có thể còn thiếu sót. Em mong nhận được góp ý từ thầy cô và đơn vị để tiếp tục hoàn thiện kiến thức, kỹ năng của mình.

**Trương Trung Kiên**

---

## MỤC LỤC

- [Danh mục viết tắt](#danh-mục-viết-tắt)
- [Danh mục từ tiếng Anh chuyên ngành](#danh-mục-từ-tiếng-anh-chuyên-ngành)
- [Lời mở đầu](#lời-mở-đầu)
- [Phần I. Khái quát về đơn vị thực tập](#phần-i-khái-quát-về-đơn-vị-thực-tập)
  - Giới thiệu chung; lĩnh vực hoạt động; cơ cấu tổ chức; nội dung thực tập; tình hình hoạt động hai năm gần nhất
- [Phần II. Gán nhãn dữ liệu và tinh chỉnh mô hình YOLO](#phần-ii-gán-nhãn-dữ-liệu-và-tinh-chỉnh-mô-hình-yolo)
  - Bối cảnh và phạm vi chuyên đề
  - Chương 1. Cơ sở lý thuyết
  - Chương 2. Phân tích và thiết kế quy trình
  - Chương 3. Thực hiện gán nhãn và tinh chỉnh mô hình
  - Chương 4. Kết quả, kiểm thử và đánh giá
- [Phần III. Nhận xét và đề xuất](#phần-iii-nhận-xét-và-đề-xuất)
- [Kết luận và hướng phát triển](#kết-luận-và-hướng-phát-triển)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)

---

## DANH MỤC VIẾT TẮT

| Từ viết tắt | Tên đầy đủ và giải thích |
|---|---|
| AI | Artificial Intelligence, trí tuệ nhân tạo |
| CNN | Convolutional Neural Network, mạng nơ-ron tích chập |
| CV | Computer Vision, thị giác máy tính |
| GPU | Graphics Processing Unit, bộ xử lý đồ họa thường dùng để tăng tốc huấn luyện |
| IoU | Intersection over Union, tỷ lệ phần giao trên phần hợp giữa hai hộp |
| mAP | mean Average Precision, chỉ số tổng hợp chất lượng phát hiện qua các lớp và ngưỡng đánh giá |
| NMS | Non-Maximum Suppression, bước loại các hộp dự đoán trùng lặp |
| YOLO | You Only Look Once, tên của một họ mô hình phát hiện đối tượng |

---

## DANH MỤC TỪ TIẾNG ANH CHUYÊN NGÀNH

| Từ tiếng Anh | Giải thích dễ hiểu |
|---|---|
| Annotation / Label | Đánh dấu lớp và vị trí đối tượng trên ảnh. |
| Backbone / Neck / Head | Các phần lần lượt rút, kết hợp đặc điểm và tạo dự đoán. |
| Batch size | Số ảnh xử lý trong một lần cập nhật trọng số. |
| Bounding box | Hộp chữ nhật bao quanh đối tượng. |
| Checkpoint | Tệp lưu trọng số mô hình tại một thời điểm. |
| Class / Class ID | Loại đối tượng cần tìm / mã số của loại đó. |
| Confidence | Mức tin cậy của một dự đoán. |
| Data augmentation | Tạo biến thể ảnh phù hợp để mô hình học thêm điều kiện. |
| Dataset | Tập ảnh và nhãn; có thể chia thành training, validation và test set. |
| Detection / Object detection | Tìm đối tượng, vị trí và lớp của chúng trong ảnh. |
| Epoch | Một lượt mô hình học qua toàn bộ training set. |
| Feature map | Bản đồ thể hiện dấu hiệu mạng nhận ra trong ảnh. |
| Fine-tuning / Transfer learning | Điều chỉnh mô hình đã học cho nhiệm vụ mới / dùng kiến thức cũ làm điểm bắt đầu. |
| Ground truth | Nhãn chuẩn để so sánh với dự đoán. |
| Hyperparameter / Model parameter | Thiết lập do người chạy chọn / trọng số mô hình tự học. |
| Image size | Kích thước ảnh đưa vào mô hình. |
| Learning rate | Mức thay đổi trọng số ở mỗi bước học. |
| Log | Bản ghi quá trình huấn luyện hoặc đánh giá. |
| Loss / Metric | Giá trị sai số được tối ưu / chỉ số tóm tắt chất lượng mô hình. |
| Optimizer | Thuật toán cập nhật trọng số theo sai số. |
| Overfitting | Học quá sát ảnh huấn luyện nhưng xử lý kém ảnh mới. |
| Pretrained weights | Trọng số mô hình đã học trước trên dữ liệu khác. |
| Precision / Recall | Tỷ lệ dự đoán đúng / tỷ lệ đối tượng thật được phát hiện. |

---

## DANH MỤC CÁC BẢNG BIỂU, HÌNH VẼ, ĐỒ THỊ, CÔNG THỨC

Danh mục bảng biểu có số trang được cập nhật tự động trong bản Word.

---

# LỜI MỞ ĐẦU

Thị giác máy tính (Computer Vision, CV) giúp máy tính phân tích nội dung trong ảnh hoặc video. Một nhiệm vụ phổ biến là phát hiện đối tượng (object detection), chẳng hạn xác định vật thể xuất hiện ở đâu trong ảnh. Để mô hình dự đoán đúng, người làm AI cần chuẩn bị ảnh phù hợp và tạo nhãn (label) chính xác.

Trong thời gian làm việc tại FPT Smart Cloud, em tham gia gán nhãn dữ liệu và tinh chỉnh các mô hình YOLO cho bài toán thị giác máy tính. Qua công việc này, em nhận thấy việc huấn luyện không chỉ là chạy một lệnh. Người thực hiện cần hiểu yêu cầu của bài toán, kiểm tra nhãn, chọn dữ liệu phù hợp, theo dõi quá trình học và xem các trường hợp mô hình dự đoán sai.

Mục tiêu của báo cáo là trình bày kiến thức cơ bản về dữ liệu ảnh, gán nhãn dữ liệu và fine-tuning YOLO; mô tả cách các công việc này hỗ trợ quá trình huấn luyện; đồng thời nêu những kỹ năng em học được. Để bảo vệ thông tin của đơn vị, báo cáo không nêu tên khách hàng, số lượng ảnh, tên lớp đối tượng hoặc cấu hình huấn luyện nội bộ khi chưa có xác nhận công bố.

Báo cáo gồm ba phần. Phần I giới thiệu khái quát về FPT Smart Cloud dựa trên tài liệu hội nhập nhân viên được cung cấp. Phần II trình bày lý thuyết và công việc gán nhãn, tinh chỉnh mô hình YOLO. Phần III tự đánh giá quá trình thực tập và đưa ra một số đề xuất. Các chỉ số chỉ được nêu khi có nguồn rõ ràng và được phép sử dụng.

---

# PHẦN I. KHÁI QUÁT VỀ ĐƠN VỊ THỰC TẬP

## 1.1. Giới thiệu chung về FPT Smart Cloud

FPT Smart Cloud hoạt động trong các lĩnh vực điện toán đám mây, trí tuệ nhân tạo và dữ liệu thuộc hệ sinh thái FPT. Theo tài liệu hội nhập nhân viên tháng 10 năm 2026, đơn vị phát triển nền tảng và dịch vụ công nghệ phục vụ khách hàng doanh nghiệp, đồng thời chú trọng nghiên cứu, phát triển và vận hành sản phẩm [1].

Tài liệu hội nhập ghi FPT Smart Cloud ra mắt ngày 13/08/2020 [1]. Báo cáo sử dụng tên đơn vị theo hồ sơ thực tập là Công ty TNHH FPT Smart Cloud; cách ghi cuối cùng cần được đối chiếu với hướng dẫn của nhà trường và người phụ trách tại đơn vị.

Trong doanh nghiệp công nghệ, công việc thường cần sự phối hợp giữa nhiều nhóm như phát triển sản phẩm, kỹ thuật, kinh doanh, vận hành và hỗ trợ khách hàng. Nhân viên cần trao đổi rõ ràng, tuân thủ quy trình và chú ý đến chất lượng cũng như an toàn thông tin. Những nội dung này cũng được nhắc đến trong tài liệu hội nhập [1].

## 1.2. Lĩnh vực hoạt động và sản phẩm, dịch vụ

Tài liệu hội nhập giới thiệu các nhóm dịch vụ điện toán đám mây, nền tảng AI, nền tảng dữ liệu và AI Factory. Có thể hiểu đơn giản như sau:

| Nhóm hoạt động | Cách hiểu đơn giản |
|---|---|
| Điện toán đám mây | Cung cấp tài nguyên máy tính và lưu trữ qua mạng. |
| Trí tuệ nhân tạo | Cung cấp công cụ giúp phần mềm phân tích, nhận dạng hoặc tạo nội dung. |
| Nền tảng dữ liệu | Hỗ trợ thu thập, lưu trữ và khai thác dữ liệu. |
| AI Factory | Môi trường và dịch vụ hỗ trợ phát triển, thử nghiệm và vận hành ứng dụng AI. |

*Bảng 1.1. Lĩnh vực hoạt động và sản phẩm, dịch vụ - Nhóm hoạt động*


Trong nhóm AI, tài liệu giới thiệu nền tảng AI, công cụ tạo ứng dụng và sản phẩm phục vụ giao tiếp, xử lý tài liệu, nhận diện và vận hành. Báo cáo chỉ trình bày theo nhóm để tránh dùng sai tên sản phẩm hoặc thông tin chưa được phép công bố [1].

## 1.3. Cơ cấu tổ chức và chức năng các đơn vị

Tài liệu hội nhập đề cập đến ban điều hành, các mảng Cloud Technology, AI Product, sản phẩm/dịch vụ, chất lượng và an toàn thông tin. Báo cáo mô tả ở mức khái quát, không nêu tên cá nhân hoặc chi tiết cơ cấu chưa được cho phép.

| Nhóm chức năng | Vai trò khái quát |
|---|---|
| Phát triển sản phẩm và kỹ thuật | Xây dựng, kiểm thử và duy trì sản phẩm, nền tảng hoặc dịch vụ. |
| Kinh doanh và tư vấn giải pháp | Tìm hiểu nhu cầu khách hàng và phối hợp đề xuất giải pháp. |
| Vận hành và hỗ trợ | Theo dõi hoạt động dịch vụ, tiếp nhận và xử lý vấn đề theo quy trình. |
| Các bộ phận hỗ trợ | Hỗ trợ nhân sự, tài chính, chất lượng, an toàn thông tin và hoạt động chung. |

*Bảng 1.2. Cơ cấu tổ chức và chức năng các đơn vị - Nhóm chức năng*


Tài liệu hội nhập nhấn mạnh văn hóa đổi mới, học hỏi và phối hợp. Tài liệu cũng giới thiệu nguyên tắc “Quality from me” và “Security from Code”. Đây là nội dung được trích từ tài liệu hội nhập, không phải kết quả đánh giá độc lập [1].

## 1.4. Bộ phận và nội dung thực tập của sinh viên

Trong thời gian thực tập tại Trung tâm Sản phẩm Vision thuộc Khối Sản phẩm AI, em tham gia gán nhãn dữ liệu và tinh chỉnh các mô hình YOLO cho bài toán thị giác máy tính. Công việc yêu cầu hiểu nhãn cần gán, tuân theo quy tắc dữ liệu và trao đổi với nhóm khi gặp trường hợp chưa rõ.

| Thông tin | Nội dung |
|---|---|
| Bộ phận | Trung tâm Sản phẩm Vision, Khối Sản phẩm AI. |
| Vị trí hoặc vai trò | AI Engineer Intern (Computer Vision), theo hồ sơ thực tập đã cung cấp. |
| Công việc chính | Gán nhãn dữ liệu và tham gia tinh chỉnh mô hình YOLO cho bài toán thị giác máy tính. |
| Công cụ và quy trình | Làm theo công cụ, hướng dẫn và quy trình được bộ phận giao; tên cụ thể chỉ nêu khi được phép công bố. |

*Bảng 1.3. Bộ phận và nội dung thực tập của sinh viên - Thông tin*


Phần II trình bày kiến thức và quy trình liên quan đến hai nhóm nhiệm vụ này. Các ví dụ được viết ở mức khái quát để không làm lộ dữ liệu, tên dự án hoặc thông tin khách hàng của công ty.

## 1.5. Tình hình hoạt động trong hai năm gần nhất

Mẫu báo cáo yêu cầu giới thiệu hoạt động của đơn vị trong hai năm gần nhất. Tài liệu hội nhập không phải báo cáo tài chính nên không có số liệu doanh thu theo từng năm. Phần này bổ sung thông tin pháp lý và dữ liệu công khai; số liệu ước tính hoặc chưa được công bố được ghi rõ.

Website của FPT Smart Cloud ghi tên Công ty TNHH FPT Smart Cloud, mã số đăng ký kinh doanh 0109307938, cấp ngày 13/08/2020 [7]. Apps Run The World ước tính doanh thu công ty năm 2024 khoảng 20 triệu USD [8]. FPT cho biết doanh thu lũy kế của FPT Smart Cloud đến hết tháng 7/2026 đã vượt doanh thu cả năm 2025, nhưng thông báo không nêu số tiền cụ thể [9]. Báo cáo thường niên FPT năm 2025 công bố doanh thu thực nhận từ các giải pháp AI và Cloud của toàn Tập đoàn đạt 913 tỷ đồng, tăng 48,4% so với năm 2024 [10]. Đây là số liệu của nhóm giải pháp AI và Cloud trong phạm vi FPT, không phải doanh thu riêng của FPT Smart Cloud.

| Kỳ báo cáo | Thông tin được cung cấp | Nhận xét |
|---|---|---|
| Năm 2024 | Apps Run The World ước tính doanh thu FPT Smart Cloud khoảng 20 triệu USD [8]. | Ước tính từ cơ sở dữ liệu doanh nghiệp; không phải số liệu tài chính kiểm toán do công ty công bố. |
| Năm 2025 | FPT cho biết doanh thu lũy kế đến hết tháng 7/2026 đã vượt doanh thu cả năm 2025 [9]. | Nguồn chính thức không nêu số tiền cụ thể nên báo cáo không tự suy ra giá trị. |

*Bảng 1.4. Tình hình hoạt động trong hai năm gần nhất - Kỳ báo cáo*


Phần này có thể được cập nhật khi đơn vị cung cấp số liệu đã xác nhận hoặc nguồn công khai được phép sử dụng.

---

# PHẦN II. GÁN NHÃN DỮ LIỆU VÀ TINH CHỈNH MÔ HÌNH YOLO

## Bối cảnh và phạm vi chuyên đề

Chuyên đề tập trung vào hai công việc em tham gia tại FPT: gán nhãn dữ liệu và tinh chỉnh mô hình YOLO cho bài toán thị giác máy tính. Nội dung đi theo quá trình từ xác định quy tắc nhãn, kiểm tra dữ liệu, fine-tune mô hình đến xem lại dự đoán. Báo cáo không đưa cấu hình nội bộ hoặc dữ liệu công ty chưa được xác nhận để công bố.

## CHƯƠNG 1. CƠ SỞ LÝ THUYẾT

### 1.1. Thị giác máy tính và dữ liệu ảnh

Thị giác máy tính là lĩnh vực giúp máy tính xử lý ảnh hoặc video để tìm thông tin cần thiết. Con người nhìn ảnh và nhận ra vật thể nhờ kinh nghiệm; máy tính nhận ảnh dưới dạng các ma trận số. Mỗi điểm ảnh có giá trị màu hoặc độ sáng. Mô hình dùng các giá trị này để học đặc điểm có ích cho nhiệm vụ.

Chất lượng đầu vào ảnh ảnh hưởng trực tiếp đến việc học. Ảnh quá mờ, thiếu sáng, bị che hoặc có độ phân giải thấp có thể khiến đối tượng khó nhận ra. Vì vậy, khi chuẩn bị dữ liệu, người thực hiện cần kiểm tra không chỉ nhãn mà cả ảnh gốc và điều kiện chụp.

### 1.2. Học có giám sát

Học có giám sát là cách huấn luyện trong đó mỗi dữ liệu đầu vào đi cùng một nhãn đúng. Với bài toán phát hiện đối tượng, nhãn thường gồm tên lớp và vị trí đối tượng trong ảnh. Mô hình dự đoán từ ảnh, sau đó so sánh dự đoán với nhãn đúng để tính sai số. Quá trình học điều chỉnh trọng số để giảm sai số đó.

Nếu nhãn sai hoặc không nhất quán, mô hình sẽ nhận tín hiệu học không chính xác. Ví dụ, cùng một loại vật thể nhưng ảnh này được gán nhãn còn ảnh khác bị bỏ sót sẽ làm mô hình khó học quy tắc ổn định. Đây là lý do việc gán nhãn cần được xem là một phần của quá trình xây dựng AI, không chỉ là công việc chuẩn bị dữ liệu.

### 1.3. Phát hiện đối tượng

Phát hiện đối tượng (object detection) trả lời ba câu hỏi: trong ảnh có đối tượng nào, đối tượng nằm ở đâu và mô hình tin vào dự đoán đó ở mức nào. Kết quả thường gồm hộp giới hạn (bounding box), tên lớp (class) và độ tin cậy (confidence).

Phát hiện khác với phân loại ảnh. Phân loại thường gán một hoặc một vài nhãn cho toàn bộ ảnh. Phát hiện có thể tìm nhiều đối tượng và vị trí riêng của từng đối tượng trong cùng ảnh. Vì vậy, dữ liệu phát hiện cần có nhãn vị trí chứ không chỉ tên lớp.

### 1.4. Gán nhãn dữ liệu ảnh

Gán nhãn dữ liệu (data labeling hay annotation) là việc đánh dấu đối tượng theo hướng dẫn của bài toán. Với phát hiện đối tượng, người gán nhãn thường vẽ một hình chữ nhật quanh đối tượng và gán lớp tương ứng. Các nhãn đã kiểm tra trở thành ground truth để mô hình học và để người đánh giá so sánh với kết quả dự đoán.

Trong định dạng YOLO phổ biến, mỗi đối tượng được biểu diễn bằng mã lớp và bốn giá trị vị trí đã chuẩn hóa theo kích thước ảnh: tâm hộp theo trục ngang, tâm hộp theo trục dọc, chiều rộng và chiều cao. Các giá trị đã chuẩn hóa nằm trong khoảng từ 0 đến 1. Định dạng cụ thể cần theo đúng công cụ và phiên bản được sử dụng [3].

Nguyên tắc gán nhãn thường cần thống nhất các điểm sau:

| Nội dung cần thống nhất | Câu hỏi cần trả lời |
|---|---|
| Định nghĩa lớp | Đối tượng nào thuộc lớp này và đối tượng nào không thuộc lớp? |
| Ranh giới hộp | Hộp bao sát toàn bộ đối tượng hay chỉ phần nhìn thấy? |
| Đối tượng bị che | Khi bị che một phần, có gán nhãn không và theo quy tắc nào? |
| Đối tượng nhỏ hoặc mờ | Có gán nhãn, bỏ qua hay chuyển sang người có kinh nghiệm rà soát? |
| Nhiều đối tượng gần nhau | Vẽ từng hộp riêng hay gộp theo quy tắc của bài toán? |
| Trường hợp khó phân biệt | Ghi chú và hỏi người phụ trách thay vì tự suy đoán. |

*Bảng 2.1. Gán nhãn dữ liệu ảnh - Nội dung cần thống nhất*


Không có một quy tắc hộp phù hợp cho mọi bài toán. Điều quan trọng là quy tắc được mô tả rõ, áp dụng đồng đều và được cập nhật khi nhóm thống nhất cách xử lý trường hợp khó.

Nhãn hộp thường được lưu cùng mã lớp và tọa độ. Một cách biểu diễn phổ biến của YOLO gồm `class_id`, tâm hộp theo chiều ngang, tâm hộp theo chiều dọc, chiều rộng và chiều cao. Tọa độ được chia cho kích thước ảnh để đưa về cùng thang đo. Ví dụ minh họa, nếu tâm hộp nằm chính giữa ảnh thì tọa độ tâm theo cả hai chiều bằng 0,5; đây chỉ là ví dụ toán học, không phải dữ liệu của công ty. Cách lưu tương đối này giúp mô hình sử dụng nhãn trên ảnh có kích thước khác nhau [3].

Khi rà soát một nhãn, cần xem đồng thời ảnh gốc, lớp được chọn và vị trí hộp. Một hộp quá rộng có thể chứa cả nền; hộp quá hẹp có thể cắt mất phần quan trọng của vật thể. Với trường hợp bị che, mờ hoặc nằm sát mép ảnh, người gán nhãn cần làm theo hướng dẫn thống nhất thay vì tự đặt thêm quy tắc. Việc kiểm tra chéo một số nhãn giúp nhóm phát hiện sớm cách hiểu khác nhau.

Chất lượng nhãn có thể nhìn qua bốn điểm: đúng lớp, đúng vị trí, không bỏ sót đối tượng cần đánh dấu và áp dụng cùng quy tắc cho các ảnh tương tự. Các lỗi này tạo ra những tín hiệu học khác nhau:

| Lỗi nhãn | Mô hình có thể học sai điều gì |
|---|---|
| Chọn nhầm class | Mô hình nhận ví dụ của một lớp như thể đó là lớp khác. |
| Hộp lệch hoặc cắt mất đối tượng | Mục tiêu vị trí không còn khớp với hình ảnh. |
| Bỏ sót đối tượng | Mô hình có thể hiểu nhầm rằng vùng có vật thể là nền. |
| Cùng tình huống nhưng gán theo hai cách | Mô hình nhận các ví dụ mâu thuẫn, khó học một quy tắc ổn định. |

*Bảng 2.2. Gán nhãn dữ liệu ảnh - Lỗi nhãn*


Vì vậy, sửa một lỗi được phát hiện đôi khi cần rà soát thêm các ảnh cùng loại. Nếu chỉ sửa đúng một ảnh mà giữ nguyên các nhãn tương tự đang sai, bộ dữ liệu vẫn chứa những hướng dẫn không thống nhất.

### 1.5. Mạng nơ-ron tích chập

Mạng nơ-ron tích chập (CNN) thường được dùng trong xử lý ảnh. Các phép tích chập giúp mô hình nhận ra đặc điểm cục bộ như cạnh, góc hoặc vùng màu. Qua nhiều lớp, mô hình kết hợp các đặc điểm nhỏ thành đặc điểm phức tạp hơn.

Các bộ lọc trong mạng không được người lập trình viết tay cho từng ảnh. Mô hình điều chỉnh trọng số của chúng trong quá trình huấn luyện. Khi fine-tune, một phần hoặc toàn bộ trọng số đã học được điều chỉnh bằng dữ liệu mới để phù hợp hơn với bài toán đang làm.

Có thể hình dung một lớp tích chập như nhiều bộ lọc nhỏ trượt qua ảnh hoặc bản đồ đặc trưng. Mỗi bộ lọc phản hồi mạnh với một kiểu dấu hiệu nhất định. Ở các lớp đầu, dấu hiệu thường đơn giản như đường viền hoặc vùng sáng tối; ở các lớp sâu hơn, mạng kết hợp chúng thành hình dạng có ý nghĩa hơn. Đầu ra của một lớp được gọi là bản đồ đặc trưng (feature map), cho biết dấu hiệu nào xuất hiện và ở vị trí nào.

Trong một CNN, lớp tích chập thường đi cùng phép chuẩn hóa và hàm kích hoạt. Chuẩn hóa giúp các giá trị trong mạng ổn định hơn; hàm kích hoạt giúp mạng học được quan hệ phức tạp thay vì chỉ cộng nhân tuyến tính. Một số khối còn giảm kích thước bản đồ đặc trưng để tiết kiệm tính toán và mở rộng vùng ảnh mà mô hình xem xét. Cấu trúc cụ thể phụ thuộc vào phiên bản, vì vậy báo cáo không gán một số lớp hay số tham số chung cho tất cả mô hình YOLO.

### 1.6. Mô hình YOLO

YOLO là họ mô hình phát hiện đối tượng theo hướng xử lý ảnh trong một lần chạy để dự đoán vị trí và lớp của nhiều đối tượng. Cách làm này thường phù hợp với các ứng dụng cần kết quả nhanh, nhưng tốc độ và chất lượng còn phụ thuộc vào biến thể mô hình, kích thước ảnh, thiết bị và dữ liệu [2].

Điểm khác dễ hiểu giữa YOLO và cách phát hiện hai giai đoạn là cách tạo dự đoán. Với phương pháp hai giai đoạn, hệ thống thường tìm các vùng có thể chứa vật thể rồi phân tích từng vùng. YOLO dự đoán nhiều hộp và lớp trong một lượt xử lý mạng. Cách một lượt có thể thuận lợi khi cần xử lý liên tục, nhưng lựa chọn mô hình vẫn cần dựa vào yêu cầu thực tế như loại đối tượng, tốc độ cần thiết, bộ nhớ và mức độ khó của ảnh; không thể kết luận một họ mô hình luôn phù hợp nhất.

Để dễ hình dung, có thể chia một mô hình phát hiện thành ba phần khái niệm:

| Phần | Vai trò dễ hiểu |
|---|---|
| Backbone | Rút ra đặc điểm từ ảnh, từ cạnh đơn giản đến cấu trúc phức tạp hơn. |
| Neck | Kết hợp đặc điểm ở nhiều kích thước để hỗ trợ phát hiện vật thể lớn và nhỏ. |
| Head | Dự đoán vị trí hộp, lớp đối tượng và độ tin cậy. |

*Bảng 2.3. Mô hình YOLO - Phần*


Đây là cách giải thích khái quát. Tên lớp, số khối và cách kết nối thay đổi theo phiên bản YOLO. Vì thế, khi báo cáo một mô hình cụ thể cần ghi rõ tên biến thể và nguồn cấu hình thay vì dùng một sơ đồ chung cho mọi phiên bản.

Các biến thể nhỏ thường được cân nhắc khi tài nguyên hoặc tốc độ là ưu tiên; biến thể lớn hơn có thể cần nhiều bộ nhớ và thời gian hơn. Đây là xu hướng chung chứ không phải quy tắc cho mọi trường hợp. Tài liệu Ultralytics phân biệt các tác vụ như phát hiện, phân đoạn, phân loại hoặc ước lượng tư thế [2]. Trong công việc, em học được rằng cần xác định đúng tác vụ và kiểm tra biến thể đang dùng trước khi chuẩn bị nhãn.

### 1.7. Học chuyển giao và fine-tuning

Học chuyển giao bắt đầu từ mô hình đã được huấn luyện trên một tập dữ liệu lớn. Fine-tuning tiếp tục điều chỉnh trọng số bằng dữ liệu của nhiệm vụ mới. Cách này thường tiết kiệm thời gian hơn khởi tạo toàn bộ trọng số ngẫu nhiên, nhất là khi dữ liệu riêng chưa lớn.

| Cách bắt đầu | Mô hình nhận được gì | Điểm cần cân nhắc |
|---|---|---|
| Khởi tạo ngẫu nhiên | Trọng số ban đầu chưa học từ ảnh. | Có thể cần nhiều dữ liệu và thời gian hơn để học các đặc điểm cơ bản. |
| Fine-tuning từ pretrained weights | Mô hình bắt đầu từ những đặc điểm đã học trước đó. | Cần kiểm tra mức độ phù hợp giữa dữ liệu cũ và nhiệm vụ mới. |

*Bảng 2.4. Học chuyển giao và fine-tuning - Cách bắt đầu*


Fine-tuning được chọn khi có một mô hình ban đầu phù hợp và muốn điều chỉnh mô hình đó cho dữ liệu cụ thể. Đây không phải cách bảo đảm kết quả tốt hơn trong mọi trường hợp. Nếu dữ liệu mới khác biệt nhiều, lớp cần phát hiện khác hoặc nhãn chưa tốt, mô hình vẫn cần được kiểm tra kỹ.

Fine-tuning không bảo đảm mô hình sẽ tốt hơn trong mọi tình huống. Nếu dữ liệu mới khác nhiều so với dữ liệu ban đầu, nhãn không tốt hoặc cấu hình học chưa phù hợp, mô hình vẫn có thể dự đoán sai. Người thực hiện cần kiểm tra cả dữ liệu, tiến trình học và các ảnh dự đoán sau huấn luyện.

Một lý do thường dùng mô hình đã huấn luyện trước là mô hình đã học được một số đặc điểm ảnh phổ biến. Việc tinh chỉnh giúp điều chỉnh các đặc điểm đó theo lớp và điều kiện của bài toán mới. Tùy quy mô dữ liệu và cấu hình, người thực hiện có thể cập nhật nhiều phần của mạng hoặc tạm giữ một số lớp; lựa chọn này phải dựa trên thí nghiệm và tài nguyên, không thể suy ra chỉ từ tên YOLO.

Trong thực tế, fine-tuning là một vòng lặp: kiểm tra dữ liệu, chạy huấn luyện, xem kết quả trên validation, xem các ảnh dự đoán và quyết định có cần sửa nhãn hoặc cấu hình hay không. Nếu lỗi xuất phát từ nhãn thì chỉ thay mô hình có thể không giải quyết được. Nếu mô hình học chậm hoặc không ổn định, cần xem log và cấu hình trước khi chạy lại.

### 1.8. Các thông số huấn luyện thường gặp

| Thông số | Giải thích đơn giản | Ảnh hưởng thường gặp |
|---|---|---|
| Trọng số khởi tạo | Bộ trọng số đã học trước dùng làm điểm bắt đầu. | Ảnh hưởng kiến thức ban đầu của mô hình. |
| Image size | Kích thước ảnh đưa vào mô hình. | Ảnh lớn giữ được chi tiết nhỏ nhưng tốn tài nguyên hơn. |
| Epoch | Số lượt mô hình học qua toàn bộ ảnh huấn luyện. | Quá ít có thể chưa học đủ; quá nhiều có thể học thuộc dữ liệu. |
| Batch size | Số ảnh trong một lần cập nhật trọng số. | Ảnh hưởng bộ nhớ và độ ổn định của quá trình học. |
| Learning rate | Mức độ thay đổi trọng số ở mỗi bước. | Quá lớn có thể làm học không ổn định; quá nhỏ có thể học chậm. |
| Optimizer | Cách cập nhật trọng số từ sai số. | Các lựa chọn khác nhau có thể tạo quá trình học khác nhau. |
| Data augmentation | Tạo biến thể ảnh như thay đổi sáng hoặc lật ảnh khi phù hợp. | Giúp mô hình gặp nhiều tình huống hơn nhưng cần tránh biến đổi sai ý nghĩa. |

*Bảng 2.5. Các thông số huấn luyện thường gặp - Thông số*


Các giá trị tối ưu không giống nhau cho mọi bài toán. Báo cáo này không tự điền epoch, learning rate hoặc batch size của công việc tại FPT vì các thông tin đó chưa được cung cấp để công bố.

Các thông số liên quan với nhau. Chẳng hạn, ảnh đầu vào lớn hơn có thể giữ nhiều chi tiết của vật thể nhỏ nhưng cần nhiều bộ nhớ hơn. Batch size lớn cần nhiều bộ nhớ và có thể làm thay đổi độ ổn định của cập nhật. Learning rate quá cao có thể khiến trọng số thay đổi mạnh, còn quá thấp có thể làm quá trình học kéo dài. Vì vậy, không nên thay nhiều giá trị cùng lúc nếu muốn hiểu nguyên nhân kết quả thay đổi.

Số lớp mạng và số tham số thuộc về kiến trúc của một biến thể cụ thể, còn epoch, batch size và learning rate là các cấu hình của lần huấn luyện. Hai loại thông tin này không nên nhầm lẫn. Nếu báo cáo cần nêu số lớp hoặc số tham số, cần lấy từ đúng tệp cấu hình hoặc phần tóm tắt mô hình đã dùng, ghi phiên bản và không suy đoán từ tên gọi của biến thể.

### 1.9. Chia dữ liệu và tránh học thuộc

Tập huấn luyện (training set) dùng để cập nhật mô hình. Tập validation (validation set) dùng để theo dõi mô hình trên dữ liệu không dùng trực tiếp để cập nhật trọng số. Khi có đủ dữ liệu, có thể giữ một tập test (test set) riêng để đánh giá cuối cùng.

Ảnh gần như trùng nhau không nên bị chia ngẫu nhiên sang nhiều tập nếu điều đó khiến validation quá giống train. Khi đó mô hình có thể đạt kết quả tốt trên validation nhưng kém hơn trên ảnh mới. Việc chia tập cần xét nguồn ảnh, thời gian chụp, đối tượng hoặc nhóm cảnh để hạn chế rò rỉ dữ liệu.

Overfitting xảy ra khi mô hình học quá sát các ví dụ đã thấy nhưng khó xử lý dữ liệu mới. Dấu hiệu thường gặp là kết quả trên train tiếp tục tốt lên trong khi kết quả validation không cải thiện hoặc xấu đi. Có thể xử lý bằng cách kiểm tra dữ liệu, giảm số vòng học, điều chỉnh augmentation hoặc chọn checkpoint phù hợp.

Chia dữ liệu cần tránh để ảnh gần như giống nhau xuất hiện ở cả train và validation. Ví dụ, nhiều khung hình liền nhau từ cùng một video có thể rất giống nhau; nếu chia ngẫu nhiên từng khung hình, mô hình đã nhìn thấy một cảnh tương tự trong lúc học. Khi đó, validation chưa phản ánh tốt khả năng xử lý cảnh mới. Tùy nguồn dữ liệu, có thể chia theo video, phiên thu thập, thiết bị hoặc nhóm đối tượng để giảm sự trùng lặp giữa các tập.

### 1.10. Đánh giá mô hình ở mức cơ bản

Các chỉ số là cách tóm tắt một phần chất lượng mô hình, không thay thế việc xem ảnh dự đoán. Với phát hiện đối tượng, có thể dùng ba khái niệm cơ bản:

| Chỉ số | Cách hiểu ngắn |
|---|---|
| Precision | Trong các đối tượng mô hình dự đoán, tỷ lệ dự đoán đúng là bao nhiêu. |
| Recall | Trong các đối tượng thực sự có trong ảnh, mô hình tìm được bao nhiêu. |
| mAP | Tóm tắt chất lượng phát hiện qua nhiều mức tin cậy và điều kiện khớp hộp. |

*Bảng 2.6. Đánh giá mô hình ở mức cơ bản - Chỉ số*


Chỉ số cao trên một tập thử không tự chứng minh mô hình hoạt động tốt ở môi trường khác. Cần xem ảnh mô hình bỏ sót, dự đoán nhầm, hộp quá rộng hoặc quá hẹp. Precision, Recall và mAP cần được đọc cùng với ảnh dự đoán và tập dữ liệu đã dùng [5]. Với báo cáo thực tập, chỉ ghi số liệu khi có log gốc, biết rõ tập dữ liệu và được phép công bố.

### 1.11. Bảo vệ dữ liệu và vai trò con người

Ảnh có thể chứa thông tin cá nhân, địa điểm, tài sản hoặc quy trình nội bộ. Người thực hiện cần tuân thủ quyền truy cập, mục đích sử dụng và quy định lưu trữ của đơn vị. Không sao chép dữ liệu công ty vào báo cáo, thiết bị hoặc dịch vụ ngoài quy trình được phép.

Mô hình chỉ đưa ra dự đoán dựa trên dữ liệu đã học. Người phụ trách vẫn cần xem lại các trường hợp khó và xác nhận kết quả trước khi đưa ra quyết định nghiệp vụ. Việc giữ nhật ký thay đổi nhãn, cấu hình và phiên bản mô hình giúp nhóm hiểu vì sao kết quả thay đổi.

## CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ QUY TRÌNH

### 2.1. Bài toán và mục tiêu

Bài toán chung là dùng ảnh để tìm một hay nhiều nhóm đối tượng đã được xác định trước. Đầu ra cần cho biết đối tượng được tìm thấy ở đâu và thuộc lớp nào. Để giải quyết bài toán, nhóm cần có ảnh đủ phù hợp, hướng dẫn gán nhãn rõ ràng và cách kiểm tra chất lượng trước khi huấn luyện.

Mục tiêu của quy trình gồm:

- hiểu yêu cầu và định nghĩa lớp trước khi gán nhãn;
- tạo nhãn nhất quán với quy tắc đã thống nhất;
- kiểm tra và sửa lỗi nhãn trước khi đưa vào huấn luyện;
- tinh chỉnh mô hình YOLO theo tập dữ liệu của nhiệm vụ;
- đánh giá bằng ảnh chưa dùng để cập nhật trọng số;
- ghi lại phiên bản dữ liệu, mô hình và kết quả được phép công bố.

### 2.2. Dữ liệu đầu vào và đầu ra

| Thành phần | Mô tả |
|---|---|
| Ảnh đầu vào | Ảnh hoặc khung hình được cung cấp cho bài toán theo quyền truy cập được cấp. |
| Danh sách lớp | Tên và định nghĩa của từng loại đối tượng cần phát hiện. |
| Nhãn | Vị trí hộp và mã lớp của đối tượng trong ảnh. |
| Mô hình | Mô hình YOLO được chọn để fine-tune. |
| Kết quả dự đoán | Hộp, lớp và độ tin cậy cho mỗi đối tượng được phát hiện. |
| Kết quả kiểm tra | Ảnh dự đoán, lỗi ghi nhận và kết luận theo quy trình của nhóm. |

*Bảng 2.7. Dữ liệu đầu vào và đầu ra - Thành phần*


### 2.3. Thiết kế quy tắc gán nhãn

Trước khi bắt đầu, cần đọc mô tả bài toán và xác nhận ý nghĩa từng lớp. Với mỗi lớp, hướng dẫn nên có ví dụ phù hợp, ví dụ không phù hợp và cách xử lý trường hợp biên. Nếu hai người hiểu định nghĩa lớp khác nhau, nhãn của họ có thể không đồng nhất dù cùng dùng một công cụ.

Một quy tắc gán nhãn nên trả lời được các câu hỏi sau: đối tượng nào cần đánh dấu; hộp bao quanh phần nào; xử lý thế nào khi đối tượng bị che hoặc cắt khỏi mép ảnh; khi nào đánh dấu ảnh không hợp lệ; và người gán nhãn cần làm gì khi không chắc chắn.

| Tình huống | Cách xử lý cần được thống nhất |
|---|---|
| Đối tượng nhìn rõ | Gán đúng lớp và vẽ hộp theo quy tắc. |
| Đối tượng bị che một phần | Làm theo hướng dẫn của bài toán; không tự đặt quy tắc riêng. |
| Đối tượng nằm sát mép ảnh | Kiểm tra hộp không vượt ra ngoài ảnh và áp dụng quy tắc của nhóm. |
| Đối tượng quá nhỏ hoặc quá mờ | Đánh dấu theo hướng dẫn hoặc gửi người phụ trách rà soát. |
| Không phân biệt được lớp | Không đoán; ghi nhận trường hợp chưa rõ để xin quyết định. |

*Bảng 2.8. Thiết kế quy tắc gán nhãn - Tình huống*


### 2.4. Kiểm tra chất lượng nhãn

Kiểm tra chất lượng có thể thực hiện theo mẫu hoặc theo toàn bộ dữ liệu tùy yêu cầu. Những lỗi cần chú ý gồm bỏ sót đối tượng, chọn sai lớp, hộp quá rộng hoặc quá hẹp, hai hộp chồng không đúng, ảnh trùng và nhãn không hợp lệ.

| Bước kiểm tra | Việc cần xem | Kết quả |
|---|---|---|
| Kiểm tra ảnh | Ảnh đọc được, đúng thư mục và không trùng ngoài quy tắc. | Danh sách ảnh có thể sử dụng hoặc cần xử lý. |
| Kiểm tra lớp | Mã lớp tồn tại và khớp danh sách lớp. | Nhãn không có lớp sai hoặc thiếu. |
| Kiểm tra hộp | Hộp nằm trong ảnh và bao đúng đối tượng. | Vị trí nhãn hợp lệ. |
| Rà soát trường hợp khó | Đối chiếu hướng dẫn với ảnh mờ, che khuất hoặc gần mép. | Các trường hợp chưa rõ được thống nhất. |
| Kiểm tra chéo | Một người khác xem lại mẫu nhãn nếu quy trình cho phép. | Lỗi lặp lại được phát hiện sớm. |

*Bảng 2.9. Kiểm tra chất lượng nhãn - Bước kiểm tra*


### 2.5. Chuẩn bị tập dữ liệu

Sau khi rà soát, dữ liệu cần được chia thành các tập phù hợp. Tập train được dùng để học, còn validation giúp theo dõi khả năng tổng quát. Nếu có tập test, tập này chỉ nên dùng cho đánh giá cuối sau khi đã chốt lựa chọn mô hình.

Việc chia tập nên được thực hiện có chủ đích. Không nên chỉ chia ngẫu nhiên nếu ảnh liên tiếp hoặc cùng một cảnh có thể xuất hiện ở cả train và validation. Tên lớp, cấu trúc thư mục, đường dẫn và định dạng nhãn cần được kiểm tra trước khi bắt đầu chạy mô hình.

### 2.6. Quy trình tinh chỉnh mô hình

| Bước | Hoạt động | Câu hỏi kiểm tra |
|---:|---|---|
| 1 | Xác nhận mục tiêu và lớp cần phát hiện. | Đầu ra mong muốn đã được mô tả rõ chưa? |
| 2 | Kiểm tra ảnh và nhãn. | Nhãn có nhất quán, đúng lớp và đúng vị trí không? |
| 3 | Chia dữ liệu và cấu hình đường dẫn. | Train và validation có tách hợp lý không? |
| 4 | Chọn mô hình YOLO và trọng số khởi tạo. | Mô hình có phù hợp với tài nguyên và yêu cầu không? |
| 5 | Cấu hình thông số rồi huấn luyện. | Log có lỗi, quá khớp hoặc dấu hiệu học không ổn định không? |
| 6 | Đánh giá trên validation và xem ảnh dự đoán. | Mô hình bỏ sót hay dự đoán nhầm ở tình huống nào? |
| 7 | Chọn phiên bản và lưu thông tin lần chạy. | Có thể truy lại dữ liệu, cấu hình và checkpoint không? |

*Bảng 2.10. Quy trình tinh chỉnh mô hình - Bước*


### 2.7. Luồng trao đổi giữa dữ liệu và mô hình

| Bước | Người/Thành phần | Công việc | Kết quả chuyển tiếp |
|---:|---|---|---|
| 1 | Người phụ trách bài toán | Mô tả lớp và điều kiện cần phát hiện. | Hướng dẫn dữ liệu. |
| 2 | Người gán nhãn | Đánh dấu đối tượng theo hướng dẫn. | Ảnh kèm nhãn. |
| 3 | Người rà soát | Kiểm tra nhãn và thống nhất trường hợp khó. | Tập dữ liệu đã kiểm tra. |
| 4 | Người huấn luyện | Cấu hình và fine-tune YOLO. | Checkpoint và log huấn luyện. |
| 5 | Người đánh giá | Chạy mô hình trên ảnh kiểm tra, xem lỗi. | Ghi nhận kết quả và hướng cải thiện. |
| 6 | Nhóm dự án | Chấp nhận, điều chỉnh hoặc chạy thử tiếp theo quy trình. | Phiên bản được theo dõi. |

*Bảng 2.11. Luồng trao đổi giữa dữ liệu và mô hình - Bước*


Đây là luồng khái quát để giải thích kiến thức. Thứ tự và người chịu trách nhiệm thực tế cần được đối chiếu với quy trình của bộ phận trước khi nộp báo cáo.

### 2.8. Yêu cầu chất lượng và rủi ro

| Rủi ro | Ảnh hưởng | Cách hạn chế |
|---|---|---|
| Quy tắc lớp chưa rõ | Người gán nhãn tạo nhãn khác nhau. | Thống nhất định nghĩa và ví dụ trước khi làm số lượng lớn. |
| Bỏ sót hoặc sai hộp | Mô hình học từ mục tiêu sai. | Rà soát mẫu và sửa nhãn trước khi huấn luyện. |
| Dữ liệu train và validation quá giống | Kết quả validation có thể quá lạc quan. | Chia theo nguồn ảnh, cảnh hoặc nhóm phù hợp. |
| Huấn luyện quá lâu | Mô hình có thể học thuộc dữ liệu. | Theo dõi validation và chọn checkpoint phù hợp. |
| Dữ liệu công ty bị chia sẻ sai nơi | Có thể vi phạm quy định bảo mật. | Chỉ dùng công cụ, thiết bị và thư mục được đơn vị cho phép. |
| Chỉ nhìn một chỉ số | Không thấy kiểu lỗi cụ thể. | Xem ảnh dự đoán và phân loại lỗi bên cạnh chỉ số. |

*Bảng 2.12. Yêu cầu chất lượng và rủi ro - Rủi ro*


### 2.9. Công cụ sử dụng

Tên công cụ gán nhãn, môi trường huấn luyện và phiên bản thư viện phụ thuộc vào nhiệm vụ của đơn vị. Báo cáo chỉ nêu công cụ khi người viết xác nhận tên và được phép công bố.

| Nhóm công cụ | Mục đích | Cách trình bày trong báo cáo |
|---|---|---|
| Công cụ gán nhãn | Vẽ hộp, chọn lớp và lưu nhãn. | Sử dụng công cụ theo hướng dẫn của bộ phận; không nêu tên chưa được xác nhận để công bố. |
| Môi trường huấn luyện | Cấu hình dữ liệu và chạy fine-tuning. | Tuân thủ môi trường được cấp; không ghi cấu hình hạ tầng nội bộ. |
| Công cụ rà soát | Xem ảnh dự đoán, log và lỗi. | Trình bày thao tác và kiến thức, không đưa ảnh hoặc log chưa được phép sử dụng. |

*Bảng 2.13. Công cụ sử dụng - Nhóm công cụ*


## CHƯƠNG 3. THỰC HIỆN GÁN NHÃN VÀ TINH CHỈNH MÔ HÌNH

### 3.1. Nhiệm vụ được tham gia

Trong thời gian làm việc, em tham gia gán nhãn dữ liệu và tinh chỉnh mô hình YOLO cho các bài toán thị giác máy tính. Hai công việc có liên quan trực tiếp: nhãn cho biết mô hình cần học điều gì, còn fine-tuning giúp mô hình điều chỉnh theo dữ liệu của nhiệm vụ.

| Nhóm công việc | Nội dung tham gia | Kiến thức áp dụng |
|---|---|---|
| Gán nhãn dữ liệu | Đánh dấu đối tượng và lớp theo hướng dẫn được giao. | Định nghĩa lớp, bounding box và định dạng nhãn. |
| Kiểm tra nhãn | Xem lại các trường hợp chưa rõ hoặc có khả năng sai. | Tính nhất quán và chất lượng dữ liệu. |
| Fine-tune YOLO | Chạy hoặc hỗ trợ quá trình điều chỉnh mô hình theo dữ liệu bài toán. | Học chuyển giao, epoch, learning rate và validation. |
| Xem kết quả | Đối chiếu dự đoán với ảnh và ghi nhận lỗi cần xem lại. | Precision, recall, mAP và phân tích lỗi bằng hình ảnh. |

*Bảng 2.14. Nhiệm vụ được tham gia - Nhóm công việc*


Tên bộ dữ liệu, đối tượng cần phát hiện và cấu hình cụ thể không được nêu trong báo cáo. Nếu đơn vị cho phép công bố, các thông tin này có thể được bổ sung sau khi người hướng dẫn xác nhận.

### 3.2. Cách thực hiện gán nhãn

Trước khi gán nhãn, em cần hiểu đối tượng nào cần đánh dấu và cách phân biệt các lớp. Khi đã nắm hướng dẫn, em xem ảnh, vẽ hộp quanh đối tượng, chọn lớp phù hợp và lưu nhãn theo định dạng được yêu cầu. Đây là công việc đòi hỏi sự tập trung vì một lỗi nhỏ có thể lặp lại trên nhiều ảnh nếu chưa được phát hiện.

Trong quá trình làm, em chú ý các lỗi dễ gặp như hộp không bao đúng đối tượng, chọn nhầm lớp, bỏ sót đối tượng nhỏ hoặc xử lý không thống nhất đối tượng bị che. Nếu gặp ảnh không rõ hoặc quy tắc chưa đủ cụ thể, cần ghi nhận và hỏi người phụ trách thay vì tự suy đoán.

| Bước | Việc thực hiện | Điều em rút ra |
|---:|---|---|
| 1 | Đọc hướng dẫn lớp và xem ví dụ đã được duyệt. | Cần hiểu định nghĩa trước khi bắt đầu làm nhiều ảnh. |
| 2 | Kiểm tra ảnh và xác định đối tượng cần đánh dấu. | Ảnh đầu vào cũng cần được xem xét, không chỉ nhãn. |
| 3 | Vẽ hộp và chọn lớp theo quy tắc. | Cách đánh dấu phải nhất quán giữa các ảnh. |
| 4 | Xem lại các nhãn đã tạo và sửa lỗi được phát hiện. | Lỗi nhỏ lặp lại nhiều lần có thể ảnh hưởng đến cả tập dữ liệu. |
| 5 | Gửi hoặc bàn giao dữ liệu theo quy trình của nhóm. | Tên tệp, thư mục và phiên bản cần dễ kiểm tra. |

*Bảng 2.15. Cách thực hiện gán nhãn - Bước*


Qua các bước này, em học được rằng gán nhãn không chỉ là vẽ hộp nhanh. Người gán nhãn cần hiểu mục tiêu của mô hình, chú ý phần nào được tính là đối tượng và áp dụng cùng một quy tắc cho các ảnh tương tự. Khi có góp ý từ người rà soát, cần xem lại cả những nhãn cùng loại thay vì chỉ sửa riêng ví dụ được chỉ ra.

Một điểm quan trọng khác là lưu nhãn đúng với ảnh và đúng cấu trúc dữ liệu mà công cụ huấn luyện yêu cầu. Nếu tên tệp ảnh và nhãn không khớp, mã lớp vượt ngoài danh sách đã khai báo hoặc tọa độ không hợp lệ, quá trình huấn luyện có thể báo lỗi hoặc học từ dữ liệu sai. Kiểm tra dữ liệu trước khi huấn luyện giúp tiết kiệm thời gian và tránh nhầm lỗi dữ liệu với lỗi mô hình.

### 3.3. Cách tinh chỉnh YOLO

Fine-tuning bắt đầu từ trọng số đã được huấn luyện trước, sau đó tiếp tục học trên dữ liệu và lớp của bài toán mới. Công việc thường gồm kiểm tra dữ liệu, khai báo danh sách lớp, chọn cấu hình, chạy huấn luyện, theo dõi log và đánh giá trên validation [4].

| Giai đoạn | Việc thực hiện | Nội dung cần theo dõi |
|---|---|---|
| Chuẩn bị | Kiểm tra ảnh, nhãn, đường dẫn và danh sách lớp. | Nhãn lỗi, ảnh trùng và sai cấu trúc thư mục. |
| Cấu hình | Chọn trọng số khởi tạo, kích thước ảnh và thông số học. | Phù hợp với dữ liệu, yêu cầu và tài nguyên. |
| Huấn luyện | Chạy các epoch theo cấu hình. | Loss, lỗi phần mềm và dấu hiệu mô hình học không ổn định. |
| Đánh giá | Chạy trên validation và xem ảnh dự đoán. | Bỏ sót, dự đoán nhầm, hộp lệch và lớp dễ nhầm. |
| Chọn checkpoint | Chọn phiên bản theo tiêu chí đã thống nhất. | Không chỉ dựa vào một chỉ số đơn lẻ. |
| Lưu hồ sơ | Ghi phiên bản dữ liệu, cấu hình và mô hình. | Có thể truy lại nguồn gốc kết quả. |

*Bảng 2.16. Cách tinh chỉnh YOLO - Giai đoạn*


Thông số như số epoch, learning rate, batch size, kích thước ảnh và tên checkpoint của nhiệm vụ tại FPT không được nêu trong bản này vì chưa có xác nhận công bố. Khi được phép, có thể thêm bảng ngắn gồm thông số, giá trị và lý do chọn. Cần phân biệt các thông số này với số lớp mạng và số parameters: thông số huấn luyện mô tả cách chạy, còn số lớp và parameters thuộc kiến trúc cụ thể.

Trong phạm vi bài toán phát hiện đối tượng, YOLO là lựa chọn thuận tiện để tìm vị trí và lớp của nhiều vật thể trong một lượt xử lý ảnh. Họ mô hình có các biến thể với quy mô khác nhau, nên nhóm có thể cân nhắc sự cân bằng giữa tốc độ, độ chi tiết và tài nguyên tính toán. Đây là lý do chung về mặt kỹ thuật, không khẳng định rằng mọi nhiệm vụ của đơn vị dùng cùng một biến thể hoặc cùng một cấu hình.

Khi bắt đầu một lần fine-tuning, người thực hiện cần xác định phiên bản trọng số ban đầu, danh sách lớp, đường dẫn dữ liệu và các thiết lập của lần chạy. Trong quá trình huấn luyện, log giúp theo dõi tiến triển và phát hiện lỗi; sau khi chạy, checkpoint là tệp lưu trọng số tại một thời điểm. Cần biết checkpoint nào được đánh giá và tránh ghi kết quả của một lần chạy cho một mô hình khác.

Các giá trị cấu hình cần được xem trong mối liên hệ với nhau. Nếu đổi đồng thời kích thước ảnh, learning rate và số epoch, sẽ khó biết thay đổi nào ảnh hưởng đến kết quả. Vì vậy, cách làm có thể kiểm soát là giữ nguyên dữ liệu và cách đánh giá, thay đổi từng nhóm cấu hình có lý do, rồi so sánh kết quả trên cùng điều kiện. Đây là nguyên tắc thí nghiệm, không phải cam kết về một mức cải thiện cụ thể.

### 3.4. Xem lỗi và cải thiện dữ liệu

Sau khi huấn luyện, chỉ số tổng hợp chưa cho biết rõ mô hình sai ở ảnh nào. Vì vậy, cần mở ảnh dự đoán và nhóm lỗi theo nguyên nhân. Một lỗi có thể đến từ ảnh chất lượng kém, nhãn chưa thống nhất, dữ liệu ít đại diện hoặc mô hình chưa học đủ đặc điểm.

| Dấu hiệu | Nguyên nhân có thể | Hướng kiểm tra |
|---|---|---|
| Bỏ sót đối tượng | Đối tượng nhỏ, bị che hoặc ít xuất hiện trong dữ liệu. | Kiểm tra ảnh và nhãn của trường hợp tương tự. |
| Dự đoán nhầm lớp | Hai lớp có đặc điểm giống nhau hoặc định nghĩa chưa rõ. | Xem hướng dẫn lớp và rà soát nhãn. |
| Hộp bao chưa sát | Nhãn không nhất quán hoặc ảnh khó nhìn. | So sánh cách gán nhãn giữa nhiều ảnh. |
| Kết quả tốt trên train nhưng yếu ở ảnh mới | Mô hình học thuộc hoặc tập chưa đại diện. | Kiểm tra cách chia dữ liệu và validation. |

*Bảng 2.17. Xem lỗi và cải thiện dữ liệu - Dấu hiệu*


Việc sửa dữ liệu nên dựa trên ảnh và quy tắc, không chỉ thay thông số mô hình. Nếu nguồn lỗi là nhãn sai thì tăng epoch không giải quyết được nguyên nhân.

### 3.5. Ghi nhận và so sánh các lần fine-tuning

Một lần chạy huấn luyện cần được gắn với phiên bản dữ liệu và cấu hình cụ thể. Nếu không lưu lại các thông tin này, người thực hiện khó biết sự thay đổi trong dự đoán đến từ nhãn mới, trọng số khởi tạo hay thông số huấn luyện. Việc ghi nhận không cần dùng cách trình bày phức tạp; chỉ cần đủ để truy lại cách tạo ra checkpoint và tập kết quả.

| Thông tin cần ghi | Ý nghĩa khi xem lại |
|---|---|
| Phiên bản dataset và danh sách class | Biết mô hình đã học từ bộ ảnh, nhãn và lớp nào. |
| Trọng số khởi tạo và biến thể YOLO | Biết điểm bắt đầu và kiến trúc được dùng. |
| Image size, batch size, epoch, learning rate và optimizer | Biết các thiết lập chính của lần huấn luyện. |
| Log và checkpoint được chọn | Theo dõi quá trình học và xác định đúng tệp mô hình được kiểm tra. |
| Tập validation và ảnh dự đoán | So sánh các lần chạy trên cùng căn cứ và xem dạng lỗi cụ thể. |

*Bảng 2.18. Ghi nhận và so sánh các lần fine-tuning - Thông tin cần ghi*


Khi muốn so sánh hai lần fine-tuning, nên giữ cách đánh giá như nhau và thay đổi cấu hình có chủ đích. Nếu cùng lúc đổi dữ liệu, kích thước ảnh và learning rate thì khó xác định yếu tố nào tạo ra khác biệt. Kết quả được ghi nhận cần gồm cả chỉ số phù hợp và ảnh dự đoán, nhưng không nên rút ra kết luận vượt quá những gì tập đánh giá thể hiện.

Quy trình này giúp nối công việc gán nhãn với huấn luyện. Khi ảnh dự đoán sai, người thực hiện có thể kiểm tra nhãn tham chiếu trước, sau đó mới xem dữ liệu có đại diện không, cấu hình có phù hợp không và checkpoint nào nên giữ. Nhờ vậy, việc sửa lỗi tập trung vào nguyên nhân thay vì chỉ chạy mô hình nhiều lần.

## CHƯƠNG 4. KẾT QUẢ, KIỂM THỬ VÀ ĐÁNH GIÁ

### 4.1. Kết quả công việc

Trong phạm vi thông tin có thể sử dụng, kết quả thực tập được trình bày theo nhóm công việc và kiến thức thu nhận được. Báo cáo không tự đưa số lượng ảnh, tỷ lệ hoàn thành hoặc kết quả mô hình của công ty khi chưa có nguồn được phép công bố.

| Nhóm việc | Điều em học được |
|---|---|---|
| Gán nhãn | Nhãn biến yêu cầu bài toán thành ví dụ mà mô hình có thể học; tính nhất quán quan trọng hơn thao tác nhanh. |
| Kiểm tra nhãn | Cần xem đồng thời ảnh, lớp và hộp để phát hiện trường hợp bỏ sót, sai lớp hoặc lệch ranh giới. |
| Fine-tuning | Trọng số có sẵn là điểm bắt đầu; dữ liệu và cấu hình quyết định cách mô hình thích nghi với nhiệm vụ. |
| Đánh giá | Chỉ số giúp tóm tắt, còn ảnh dự đoán giúp hiểu nguyên nhân bỏ sót hoặc nhận nhầm. |

*Bảng 2.19. Kết quả công việc - Nhóm việc*


### 4.2. Các trường hợp cần kiểm tra mô hình

Các tình huống dưới đây là danh sách tham khảo khi kiểm tra detector, không phải kết quả chạy trên dữ liệu công ty. Chúng giúp người đánh giá xem mô hình có xử lý được nhiều điều kiện ảnh khác nhau hay không.

| Kịch bản | Điều cần xem |
|---|---|
| Đối tượng rõ, nằm trọn trong ảnh | Hộp có bao đúng và lớp có chính xác không. |
| Đối tượng nhỏ hoặc ở xa | Mô hình có bỏ sót không. |
| Đối tượng bị che một phần | Mô hình có phát hiện theo yêu cầu không. |
| Nhiều đối tượng gần nhau | Hộp có bị gộp, lệch hoặc bỏ sót không. |
| Ảnh không có đối tượng mục tiêu | Mô hình có dự đoán nhầm không. |
| Thay đổi ánh sáng hoặc nền | Kết quả có thay đổi đáng kể không. |

*Bảng 2.20. Các trường hợp cần kiểm tra mô hình - Kịch bản*


Khi kiểm thử, nên lưu phiên bản mô hình, tập ảnh được phép sử dụng, thiết bị chạy và cấu hình. Nếu có dự đoán sai, cần giữ ảnh và nhãn tham chiếu theo chính sách của đơn vị để người phụ trách phân tích.

### 4.3. Cách đọc kết quả đánh giá

Kết quả kiểm thử nên được gắn với đúng mô hình, phiên bản dữ liệu và tập đánh giá. Các chỉ số như Precision, Recall và mAP đã được giải thích ở Chương 1; trong phần này, trọng tâm là đối chiếu kết quả với ảnh thật để hiểu mô hình đang làm tốt ở đâu và còn sai ở trường hợp nào.

Tài liệu công việc hiện có chưa bao gồm log huấn luyện tại đơn vị đã được xác nhận để công bố. Vì vậy, phần kết quả không tự đưa ra số lượng ảnh, cấu hình hay metric của mô hình. Nội dung được trình bày qua các thao tác đã tham gia, cách kiểm tra chất lượng dữ liệu và kiến thức thu nhận; số liệu chỉ được bổ sung khi có nguồn gốc rõ ràng và được phép sử dụng.

### 4.4. Đánh giá chung

Qua công việc, em hiểu rằng mô hình phụ thuộc nhiều vào dữ liệu và nhãn. Một tập ảnh lớn nhưng thiếu nhất quán vẫn có thể khiến mô hình học sai. Ngược lại, quy tắc rõ và bước rà soát tốt giúp nhóm giảm lỗi trước khi tốn thời gian chạy huấn luyện.

Fine-tuning giúp tận dụng trọng số đã học trước, nhưng người thực hiện vẫn cần lựa chọn dữ liệu, theo dõi validation và xem ảnh dự đoán. Một chỉ số không thể mô tả hết chất lượng; cần xem mô hình phát hiện được gì, bỏ sót gì và có phù hợp với điều kiện sử dụng không.

Do chưa có bộ số liệu công việc tại công ty được phép đưa vào báo cáo, phần đánh giá công việc tập trung vào quy trình và kiến thức học được. Đánh giá chính thức về số lượng dữ liệu, chất lượng mô hình hoặc mức cải thiện cần do đơn vị xác nhận.

### 4.5. Hạn chế và hướng cải thiện

- Bổ sung ví dụ gán nhãn đã ẩn thông tin nhạy cảm để người đọc hiểu rõ công việc.
- Lưu hướng dẫn lớp và cách xử lý trường hợp khó để người gán nhãn làm thống nhất.
- Kiểm tra tập train và validation nhằm hạn chế ảnh trùng hoặc quá giống nhau.
- Xem ảnh dự đoán sai cùng các chỉ số cơ bản trước khi thay đổi cấu hình.
- Ghi phiên bản dữ liệu, cấu hình và checkpoint theo quy định của đơn vị.
- Chỉ đưa số liệu hoặc ảnh công ty vào báo cáo sau khi có xác nhận.

---

# PHẦN III. NHẬN XÉT VÀ ĐỀ XUẤT

## 3.1. Kiến thức và kỹ năng thu nhận được

Qua công việc gán nhãn, em hiểu rõ hơn cách yêu cầu nghiệp vụ được chuyển thành lớp và vị trí đối tượng. Em học được rằng mỗi nhãn là một ví dụ dạy mô hình. Nếu cùng một trường hợp nhưng được đánh dấu theo nhiều cách, mô hình sẽ nhận tín hiệu không nhất quán.

Qua quá trình tinh chỉnh YOLO, em hiểu thêm về trọng số khởi tạo, epoch, batch size, learning rate và validation. Những thông số này không phải các con số chọn tùy ý; chúng liên quan đến dữ liệu, tài nguyên và mục tiêu của bài toán. Em cũng hiểu rằng cần xem ảnh dự đoán để nhận ra lỗi mà một chỉ số tổng hợp không thể hiện.

Một bài học quan trọng là cần bắt đầu từ yêu cầu và quy tắc dữ liệu trước khi thay đổi mô hình. Nếu định nghĩa lớp chưa rõ, hai người có thể đánh dấu cùng một đối tượng khác nhau. Khi đó, mô hình nhận các ví dụ mâu thuẫn và việc tăng thời gian huấn luyện không tự sửa được vấn đề. Em học cách dừng lại, kiểm tra hướng dẫn và hỏi người phụ trách khi gặp trường hợp chưa thống nhất.

Em cũng hiểu rõ hơn mối liên hệ giữa dữ liệu huấn luyện và khả năng áp dụng cho ảnh mới. Tập huấn luyện giúp mô hình cập nhật trọng số, còn validation giúp theo dõi xem mô hình có tiến bộ trên ảnh chưa dùng để cập nhật hay không. Nếu hai tập quá giống nhau, kết quả kiểm tra có thể tạo cảm giác tốt hơn thực tế. Vì vậy, cách chọn và chia dữ liệu là một quyết định quan trọng, không chỉ là thao tác kỹ thuật.

Với YOLO, em học được cách nhìn fine-tuning như quá trình điều chỉnh một mô hình đã có kiến thức ban đầu, thay vì bắt đầu từ đầu. Kích thước mô hình, kích thước ảnh và các thông số huấn luyện cần phù hợp với bài toán và tài nguyên. Không có một bộ thông số đúng cho mọi dữ liệu; người thực hiện cần ghi lại cấu hình, theo dõi quá trình học và so sánh các lần chạy theo cùng một cách.

Cuối cùng, em nhận ra đánh giá mô hình cần kết hợp số liệu với việc xem dự đoán trên từng ảnh. Chỉ số tổng hợp giúp so sánh nhanh, nhưng không giải thích nguyên nhân mô hình bỏ sót hoặc nhận nhầm. Khi phân loại lỗi theo ảnh, người thực hiện có thể xác định vấn đề nằm ở nhãn, dữ liệu, cấu hình hay giới hạn của mô hình, rồi trao đổi với nhóm về bước cải thiện tiếp theo.

Em rèn luyện khả năng đọc hướng dẫn, ghi nhận trường hợp chưa rõ, trao đổi với người phụ trách và tuân thủ quy định dữ liệu. Đây là những kỹ năng quan trọng khi làm việc với dữ liệu thật trong môi trường doanh nghiệp.

Qua kỳ thực tập, em dần nhìn công việc theo một chuỗi thay vì các thao tác tách rời. Yêu cầu bài toán quyết định lớp cần nhận diện; quy tắc gán nhãn chuyển yêu cầu thành dữ liệu; mô hình dùng dữ liệu đó để học; bước validation giúp kiểm tra khả năng áp dụng lên ảnh khác; còn việc xem lỗi giúp xác định cần sửa ở dữ liệu hay cấu hình. Hiểu mối liên hệ này giúp em giải thích được vì sao chất lượng mô hình không chỉ phụ thuộc vào kiến trúc mạng.

Em cũng học cách phân biệt cấu hình của mô hình với thiết lập của một lần huấn luyện. Tên biến thể, số lớp mạng và số tham số mô tả kiến trúc; epoch, batch size và learning rate mô tả cách chạy huấn luyện. Khi đọc tài liệu kỹ thuật, em chú ý ghi lại phiên bản và nguồn thay vì ghi nhớ một con số không gắn với mô hình cụ thể. Cách học này giúp tránh áp dụng máy móc thông số từ một bài toán sang bài toán khác.

Một thay đổi trong cách làm của em là không vội quy mọi kết quả chưa tốt cho mô hình. Em học cách kiểm tra từng bước: yêu cầu đã rõ chưa, ảnh có phù hợp không, nhãn có nhất quán không, tập validation có đại diện không và log huấn luyện có dấu hiệu bất thường không. Việc đặt câu hỏi theo trình tự giúp trao đổi với người hướng dẫn cụ thể hơn và làm cho việc cải thiện có căn cứ.

Những kiến thức này là nền tảng để em tiếp tục học sâu hơn về phát hiện và phân đoạn đối tượng, cách thiết kế thí nghiệm, phân tích lỗi và triển khai mô hình. Em nhận thấy kỹ năng chuyên môn cần đi cùng sự cẩn thận, trung thực khi báo cáo kết quả và ý thức bảo vệ dữ liệu của đơn vị.

## 3.2. Khó khăn và cách khắc phục

Khó khăn đầu tiên là hiểu đúng cách phân biệt các lớp và cách xử lý ảnh khó. Em giải quyết bằng cách xem hướng dẫn, so sánh ví dụ đã duyệt và hỏi lại người phụ trách khi chưa chắc chắn. Cách này giúp tránh việc tự tạo quy tắc khác với nhóm.

Khó khăn tiếp theo là hiểu mối liên hệ giữa dữ liệu và kết quả mô hình. Khi dự đoán chưa tốt, không thể kết luận ngay rằng cần đổi mô hình. Cần xem nhãn, ảnh, cách chia tập và log để tìm nguyên nhân. Qua đó, em học cách phân tích từng bước thay vì chỉ nhìn một con số.

## 3.3. Đề xuất

1. **Đối với sinh viên:** Ghi lại nhiệm vụ, kiến thức mới và câu hỏi phát sinh theo từng tuần; xác nhận với người hướng dẫn trước khi đưa thông tin công ty vào báo cáo.
2. **Đối với quy trình gán nhãn:** Duy trì hướng dẫn ngắn có ví dụ về lớp, hộp và trường hợp khó; cập nhật hướng dẫn khi nhóm thống nhất quy tắc mới.
3. **Đối với huấn luyện mô hình:** Lưu cấu hình, phiên bản dữ liệu và checkpoint theo quy định để có thể truy lại các lần chạy.
4. **Đối với đánh giá:** Kết hợp chỉ số với việc xem ảnh dự đoán sai, không kết luận chất lượng chỉ từ một giá trị.

---

# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Báo cáo đã giới thiệu khái quát FPT Smart Cloud dựa trên tài liệu hội nhập được cung cấp, đồng thời trình bày kiến thức và công việc gán nhãn dữ liệu, tinh chỉnh mô hình YOLO. Nội dung tập trung vào cách nhãn hướng dẫn mô hình học, cách fine-tune sử dụng trọng số đã có và cách kiểm tra lỗi bằng cả ảnh lẫn chỉ số.

Qua kỳ thực tập, em hiểu rằng chất lượng mô hình bắt đầu từ yêu cầu và dữ liệu. Quy tắc gán nhãn rõ, dữ liệu được rà soát và cách chia tập hợp lý giúp việc huấn luyện có ý nghĩa hơn. Kết quả mô hình cần được xem trong bối cảnh dữ liệu và điều kiện sử dụng; không nên chỉ dựa vào một chỉ số.

Trong thời gian tới, em muốn tiếp tục học về xử lý ảnh, thiết kế tập dữ liệu, phân tích lỗi và triển khai mô hình. Báo cáo có thể được hoàn thiện thêm bằng ví dụ công việc và kết quả đã được đơn vị xác nhận, đồng thời tiếp tục bảo vệ dữ liệu nội bộ.

---

# TÀI LIỆU THAM KHẢO

1. FPT Smart Cloud. *FCI Onboard Training - October 2026*. Tài liệu hội nhập nhân viên; chỉ sử dụng nội dung được phép công bố.
2. Ultralytics. *Object Detection with Ultralytics YOLO*. https://docs.ultralytics.com/tasks/detect/ (truy cập ngày 23/10/2026).
3. Ultralytics. *Object Detection Datasets Overview*. https://docs.ultralytics.com/datasets/detect/ (truy cập ngày 23/10/2026).
4. Ultralytics. *Train Mode*. https://docs.ultralytics.com/modes/train/ (truy cập ngày 23/10/2026).
5. Ultralytics. *YOLO Performance Metrics*. https://docs.ultralytics.com/guides/yolo-performance-metrics/ (truy cập ngày 23/10/2026).
6. OpenAI. ChatGPT/Codex, công cụ AI được sử dụng để hỗ trợ lập cấu trúc, soạn và biên tập bản nháp ở Phần I, Phần II và Phần III; diễn giải thuật ngữ thị giác máy tính; và rà soát cách diễn đạt. Người viết đối chiếu nội dung kỹ thuật với tài liệu gốc. Công cụ được sử dụng trong phạm vi nhà trường cho phép (truy cập ngày 23/10/2026).
7. FPT Smart Cloud. Thông tin chủ sở hữu website. https://microsoft.fptcloud.com/thong-tin-chu-so-huu-website/ (truy cập ngày 24/10/2026).
8. Apps Run The World. FPT Smart Cloud company profile (ước tính doanh thu năm 2024). https://www.appsruntheworld.com/customers-database/customers/view/fpt-smart-cloud-vietnam (truy cập ngày 24/10/2026).
9. FPT. FPT Appoints New Deputy CEO of FPT Smart Cloud and CEO of FPT Online. https://fpt.com/en/news/fpt-appoints-new-deputy-ceo-of-fpt-smart-cloud-and-ceo-of-fpt-online (truy cập ngày 24/10/2026).
10. FPT. Dịch vụ CNTT cho thị trường trong nước, Báo cáo thường niên 2025. https://bctn2025.fpt.com/vi/phan-tich-hoat-dong-kinh-doanh/khoi-cong-nghe/dich-vu-cntt-cho-thi-truong-trong-nuoc/ (truy cập ngày 24/10/2026).

---


