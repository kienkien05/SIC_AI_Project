# BÁO CÁO THỰC TẬP TỐT NGHIỆP

## Nội dung báo cáo — gán nhãn dữ liệu và tinh chỉnh YOLO tại FPT Smart Cloud

> **Lưu ý trước khi nộp:** Các phần trong ngoặc vuông cần được xác nhận và điền bằng thông tin thật. Nội dung chính phản ánh công việc người viết mô tả tại FPT: gán nhãn dữ liệu và tinh chỉnh các mô hình YOLO cho bài toán thị giác máy tính. Báo cáo không nêu tên dự án, dữ liệu, thông số hoặc kết quả nội bộ chưa được phép công bố. SPAS chỉ được nhắc như một dự án liên quan do nhóm thực hiện trong cùng giai đoạn, không gộp kết quả của dự án này với công việc tại công ty.
>
> Không có sơ đồ được tạo trong tài liệu này. Các quy trình được trình bày bằng bảng để người viết có thể tự vẽ lại nếu biểu mẫu yêu cầu.

---

## BÌA

**[TÊN TRƯỜNG / CƠ SỞ ĐÀO TẠO]**  
**[KHOA / BỘ MÔN]**

### BÁO CÁO THỰC TẬP TỐT NGHIỆP

**Đơn vị thực tập:** FPT Smart Cloud  
**Nội dung thực tập:** Gán nhãn dữ liệu và tinh chỉnh mô hình YOLO cho bài toán thị giác máy tính

**Sinh viên:** [Họ và tên]  
**Mã sinh viên:** [Mã sinh viên]  
**Lớp:** [Tên lớp]  
**Người hướng dẫn tại đơn vị:** [Họ tên, chức vụ — bổ sung khi được phép]  
**Giảng viên hướng dẫn:** [Họ và tên]

**[Địa điểm], [tháng/năm]**

## BÌA PHỤ

**[TÊN TRƯỜNG / CƠ SỞ ĐÀO TẠO]**  
**[KHOA / BỘ MÔN]**

### BÁO CÁO THỰC TẬP TỐT NGHIỆP

**Đơn vị thực tập:** FPT Smart Cloud  
**Chuyên đề:** Gán nhãn dữ liệu và tinh chỉnh mô hình YOLO cho bài toán thị giác máy tính

**Sinh viên:** [Họ và tên]  
**Mã sinh viên:** [Mã sinh viên]  
**Lớp:** [Tên lớp]  
**Giảng viên hướng dẫn:** [Họ và tên]  
**Người hướng dẫn tại đơn vị:** [Họ tên, chức vụ nếu được phép ghi]

**[Địa điểm], [năm]**

---

## LỜI CẢM ƠN

Em xin cảm ơn **[tên trường/cơ sở đào tạo]** và giảng viên hướng dẫn đã tạo điều kiện để em hoàn thành kỳ thực tập và báo cáo này. Em cũng xin cảm ơn các anh, chị tại FPT Smart Cloud đã hỗ trợ em tìm hiểu môi trường làm việc, quy trình phối hợp và các yêu cầu về tác phong trong doanh nghiệp.

Trong thời gian làm việc tại FPT, em được tham gia gán nhãn dữ liệu và tinh chỉnh mô hình YOLO để giải quyết các bài toán thị giác máy tính. Công việc giúp em hiểu rõ hơn mối liên hệ giữa dữ liệu, cách gán nhãn và kết quả mô hình. Em xin cảm ơn các anh, chị và các thành viên trong nhóm đã hướng dẫn, trao đổi kinh nghiệm và hỗ trợ em trong quá trình làm việc.

Do thời gian và kinh nghiệm còn hạn chế, báo cáo có thể còn thiếu sót. Em mong nhận được góp ý từ thầy cô và đơn vị để tiếp tục hoàn thiện kiến thức và kỹ năng của mình.

**[Họ và tên sinh viên]**

---

## MỤC LỤC

> Cập nhật số trang tự động sau khi chuyển nội dung sang Word theo mẫu PDF.

1. Đặt vấn đề ................................................................ [trang]
2. Phần I. Tổng quan về đơn vị thực tập ........................ [trang]
   1. Giới thiệu chung về FPT Smart Cloud ...................... [trang]
   2. Lĩnh vực hoạt động và sản phẩm, dịch vụ .................. [trang]
   3. Cơ cấu tổ chức và chức năng các đơn vị ................... [trang]
   4. Bộ phận và nội dung thực tập của sinh viên ............... [trang]
   5. Tình hình hoạt động trong hai năm gần nhất ............... [trang]
3. Phần II. Nội dung thực tập: Gán nhãn dữ liệu và tinh chỉnh YOLO ... [trang]
   Chương 1. Cơ sở lý thuyết .................................. [trang]
   Chương 2. Phân tích và thiết kế hệ thống .................... [trang]
   Chương 3. Huấn luyện mô hình và tích hợp hệ thống .......... [trang]
   Chương 4. Kết quả, kiểm thử và đánh giá hệ thống ........... [trang]
4. Phần III. Tự đánh giá và đề xuất ........................... [trang]
5. Kết luận và hướng phát triển ............................... [trang]
6. Tài liệu tham khảo .......................................... [trang]
7. Phụ lục .................................................... [trang]

---

## DANH MỤC BẢNG BIỂU VÀ CÔNG THỨC

Danh mục bảng biểu và công thức được tạo tự động trong bản Word sau khi cập nhật trường mục lục. Báo cáo không có sơ đồ hoặc hình minh họa.

---

## DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Giải thích |
|---|---|
| AI | Trí tuệ nhân tạo |
| API | Giao diện để các phần mềm trao đổi dữ liệu |
| CNN | Mạng nơ-ron tích chập, thường dùng để xử lý ảnh |
| Epoch | Một lượt mô hình học qua toàn bộ dữ liệu huấn luyện |
| Fine-tuning | Tinh chỉnh mô hình đã được huấn luyện trước bằng dữ liệu của bài toán mới |
| Learning rate | Tốc độ điều chỉnh trọng số trong mỗi bước học |
| SPAS | Smart Passive Attendance System — dự án hỗ trợ điểm danh bằng camera và AI |
| YOLO | Họ mô hình phát hiện đối tượng trong ảnh |
| Batch size | Số ảnh được đưa vào mô hình trong một lượt cập nhật trọng số |
| Bounding box | Hình chữ nhật bao quanh đối tượng cần phát hiện |
| CNN | Mạng nơ-ron tích chập, thường dùng để xử lý ảnh |

---

# ĐẶT VẤN ĐỀ

Thị giác máy tính giúp máy tính phân tích nội dung trong ảnh hoặc video. Để mô hình nhận biết đúng đối tượng, người làm AI cần chuẩn bị dữ liệu phù hợp, xác định quy tắc gán nhãn nhất quán và kiểm tra kết quả sau huấn luyện. Nếu nhãn không đúng hoặc cách gán nhãn giữa các ảnh không thống nhất, mô hình có thể học sai ngay cả khi dùng một kiến trúc tốt.

Trong thời gian làm việc tại FPT Smart Cloud, em tham gia gán nhãn dữ liệu và tinh chỉnh các mô hình YOLO cho một số bài toán thị giác máy tính. Vì tên dự án, loại dữ liệu và cấu hình cụ thể chưa được xác nhận để công bố, báo cáo tập trung giải thích quy trình và kiến thức em học được, không tự nêu tên khách hàng, số lượng dữ liệu hoặc kết quả nội bộ. Dự án SPAS được nhắc riêng như một ví dụ học tập có liên quan, không dùng thay cho kết quả công việc tại công ty.

Báo cáo gồm ba phần. Phần I giới thiệu FPT Smart Cloud dựa trên tài liệu hội nhập nhân viên được cung cấp. Phần II trình bày cơ sở lý thuyết, cách phân tích dữ liệu, quy trình gán nhãn và tinh chỉnh YOLO, cùng cách kiểm tra mô hình. Phần III tự đánh giá kiến thức, kỹ năng và khó khăn trong quá trình thực tập. Các kết quả định lượng chỉ được đưa vào khi có nguồn rõ ràng và được phép công bố.

---

# PHẦN I. TỔNG QUAN VỀ ĐƠN VỊ THỰC TẬP

## 1.1. Giới thiệu chung về FPT Smart Cloud

FPT Smart Cloud là đơn vị hoạt động trong các lĩnh vực điện toán đám mây, trí tuệ nhân tạo và dữ liệu thuộc hệ sinh thái FPT. Theo tài liệu đào tạo nhân viên FCI tháng 10 năm 2026, đơn vị phát triển các nền tảng và dịch vụ công nghệ phục vụ khách hàng doanh nghiệp, đồng thời chú trọng hoạt động nghiên cứu, phát triển và vận hành sản phẩm.

Tài liệu đào tạo nhân viên tháng 10/2026 ghi FPT Smart Cloud ra mắt ngày 13/08/2020. Tài liệu cũng giới thiệu quy mô khoảng 870 nhân viên, khoảng 100 cộng tác viên/thực tập sinh và năm văn phòng tại Việt Nam và Nhật Bản tại thời điểm tài liệu được lập. Các con số này là thông tin khái quát trong tài liệu hội nhập, cần được xác nhận là được phép đưa vào báo cáo trước khi nộp [1]. Khi hoàn thiện, cần kiểm tra tên pháp nhân và cách ghi tên đơn vị theo hướng dẫn của người phụ trách thực tập.

Trong môi trường doanh nghiệp công nghệ, công việc thường cần sự phối hợp giữa nhiều nhóm như phát triển sản phẩm, kỹ thuật, kinh doanh, vận hành và hỗ trợ khách hàng. Nhân viên cần tuân thủ quy trình làm việc, trao đổi rõ ràng và quan tâm đến chất lượng cũng như an toàn thông tin. Các nội dung này được nhắc đến trong tài liệu hội nhập nhân viên của đơn vị.

## 1.2. Lĩnh vực hoạt động và sản phẩm, dịch vụ

Tài liệu hội nhập giới thiệu các nhóm dịch vụ điện toán đám mây, nền tảng AI, nền tảng dữ liệu và AI Factory. Có thể giải thích đơn giản như sau:

| Nhóm hoạt động | Cách hiểu đơn giản |
|---|---|
| Điện toán đám mây | Cung cấp tài nguyên máy tính và lưu trữ qua mạng để khách hàng không phải tự xây toàn bộ hạ tầng. |
| Trí tuệ nhân tạo | Cung cấp công cụ hoặc giải pháp giúp phần mềm xử lý các việc như nhận dạng, phân tích hoặc hỗ trợ giao tiếp. |
| Nền tảng dữ liệu | Hỗ trợ thu thập, lưu trữ và khai thác dữ liệu phục vụ vận hành hoặc ra quyết định. |
| AI Factory | Môi trường và dịch vụ hỗ trợ phát triển, thử nghiệm và vận hành các ứng dụng AI. |

Trong nhóm AI, tài liệu giới thiệu nền tảng AI toàn diện, gồm các mô hình nền tảng, công cụ tạo ứng dụng AI và các sản phẩm phục vụ giao tiếp, xử lý tài liệu, nhận diện và hỗ trợ vận hành. Tài liệu cũng nêu dịch vụ cloud, nền tảng dữ liệu và hạ tầng AI Factory như những nhóm giải pháp liên quan. Báo cáo chỉ trình bày ở mức nhóm sản phẩm để dễ hiểu; tên từng sản phẩm cần được xác nhận quyền công bố và phiên bản hiện hành trước khi nộp [1].

Danh mục sản phẩm có thể thay đổi theo thời gian. Vì vậy, bản nộp cuối cần dùng đúng tên sản phẩm và mô tả được đơn vị cho phép công bố tại thời điểm nộp báo cáo.

## 1.3. Cơ cấu tổ chức và chức năng các đơn vị

Tài liệu hội nhập có nội dung về ban điều hành, cơ cấu tổ chức và các mảng Cloud Technology, AI Product, sản phẩm/dịch vụ, chất lượng và an toàn thông tin. Vì yêu cầu của người viết là không chèn sơ đồ vào bản báo cáo này, nội dung được trình bày dưới dạng bảng chức năng ở mức khái quát, không nêu tên cá nhân hoặc dựng lại cơ cấu chi tiết.

Nếu biểu mẫu bắt buộc có sơ đồ, sinh viên tự vẽ lại bằng tay dựa trên sơ đồ chính thức đã được người hướng dẫn tại FPT cho phép. Có thể dùng bảng dưới đây để mô tả các nhóm liên quan ở mức khái quát:

| Nhóm chức năng | Vai trò khái quát |
|---|---|
| Phát triển sản phẩm và kỹ thuật | Xây dựng, kiểm thử và duy trì sản phẩm, nền tảng hoặc dịch vụ. |
| Kinh doanh và tư vấn giải pháp | Tìm hiểu nhu cầu khách hàng và phối hợp đề xuất giải pháp phù hợp. |
| Vận hành và hỗ trợ | Theo dõi hoạt động dịch vụ, tiếp nhận và xử lý vấn đề theo quy trình. |
| Các bộ phận hỗ trợ | Hỗ trợ nhân sự, tài chính, pháp chế, chất lượng và các hoạt động chung. |

Tài liệu hội nhập nhấn mạnh văn hóa đổi mới, học hỏi, phối hợp và tinh thần cùng hướng tới mục tiêu chung. Phần chất lượng và an toàn thông tin nhắc đến nguyên tắc “Quality from me” và “Security from Code”, cùng một số chứng nhận, tiêu chuẩn được đơn vị giới thiệu trong tài liệu. Trong báo cáo thực tập, nội dung này được dùng để mô tả thông tin hội nhập; không xem là kết quả đánh giá độc lập và chỉ giữ lại nếu được phép công bố [1].

## 1.4. Bộ phận và nội dung thực tập của sinh viên

Trong thời gian làm việc tại FPT Smart Cloud, em tham gia hai nhóm công việc chính: gán nhãn dữ liệu ảnh và tinh chỉnh mô hình YOLO cho các bài toán thị giác máy tính. Gán nhãn giúp mô hình biết đối tượng cần học nằm ở đâu và thuộc lớp nào. Tinh chỉnh giúp mô hình đã học trước điều chỉnh theo dữ liệu và yêu cầu của bài toán.

| Thông tin cần điền | Nội dung xác nhận |
|---|---|
| Thời gian thực tập/làm việc | [Từ ngày… đến ngày…] |
| Bộ phận | [Tên bộ phận được phép ghi] |
| Vị trí hoặc vai trò | [Ghi đúng chức danh/vai trò được đơn vị xác nhận] |
| Người hướng dẫn | [Tên/chức vụ nếu được phép công bố] |
| Công việc đã thực hiện | Gán nhãn dữ liệu và tham gia tinh chỉnh các mô hình YOLO cho bài toán thị giác máy tính. Bổ sung ví dụ cụ thể nếu được phép. |
| Công cụ/quy trình đã tiếp cận | [Ghi tên công cụ, phiên bản và quy trình nếu được phép công bố] |

Nếu đưa SPAS vào báo cáo, cần mô tả đây là dự án liên quan được nhóm thực hiện trong cùng giai đoạn và ghi riêng phần đóng góp cá nhân. Không gộp dữ liệu, mô hình hoặc kết quả của SPAS với nhiệm vụ tại FPT.

## 1.5. Tình hình hoạt động trong hai năm gần nhất

Mẫu báo cáo yêu cầu giới thiệu kết quả hoạt động của đơn vị trong hai năm gần nhất. Tài liệu hội nhập nhân viên được cung cấp không phải báo cáo tài chính và không có bảng số liệu theo từng năm. Tài liệu nêu một số chỉ số quy mô ở thời điểm tháng 10/2026 như hơn 80 dịch vụ cloud, hơn 20 sản phẩm AI, hơn 30 đối tác toàn cầu và trên 3.000 khách hàng tại 15 quốc gia [1]. Đây là chỉ số quy mô được trình bày trong tài liệu đào tạo, không phải doanh thu hoặc kết quả riêng của từng năm.

| Kỳ / nguồn | Thông tin được nêu | Cách sử dụng trong báo cáo |
|---|---|---|
| Tài liệu hội nhập, tháng 10/2026 | Hơn 80 dịch vụ cloud; hơn 20 sản phẩm AI; hơn 30 đối tác toàn cầu; trên 3.000 khách hàng tại 15 quốc gia. | Chỉ mô tả quy mô tổng quát theo tài liệu; cần xác nhận quyền công bố và phạm vi số liệu trước khi nộp. |
| Hai năm gần nhất theo yêu cầu mẫu | Tài liệu hiện có không nêu số liệu hoặc kết quả theo từng năm. | Không tự ước tính doanh thu, lợi nhuận hay tăng trưởng; bổ sung báo cáo công khai được phép hoặc ghi rõ “không công bố”. |

| Năm | Chỉ tiêu được phép công bố | Nguồn xác nhận |
|---|---|---|
| [Năm gần nhất] | [Bổ sung số liệu/tóm tắt chính thức hoặc ghi “không công bố”] | [Báo cáo công khai hoặc người phụ trách cho phép] |
| [Năm liền trước] | [Bổ sung số liệu/tóm tắt chính thức hoặc ghi “không công bố”] | [Báo cáo công khai hoặc người phụ trách cho phép] |

Nếu không được phép sử dụng số liệu kinh doanh, sinh viên nên trình bày khái quát lĩnh vực hoạt động và sản phẩm đã được công bố, đồng thời ghi rõ đơn vị không cung cấp số liệu chi tiết cho báo cáo thực tập.

---

# PHẦN II. NỘI DUNG THỰC TẬP: XÂY DỰNG HỆ THỐNG HỖ TRỢ ĐIỂM DANH SPAS

## Bối cảnh và phạm vi chuyên đề

SPAS là tên viết tắt của Smart Passive Attendance System. Dự án dùng camera và AI để phát hiện, nhận diện khuôn mặt trong buổi học. Hệ thống đề xuất danh tính và lưu bằng chứng; giảng viên có thể kiểm tra lại những trường hợp chưa rõ.

Nhóm thực hiện SPAS trong giai đoạn người viết làm việc tại FPT. Báo cáo tập trung vào mục tiêu của hệ thống, cách các thành phần phối hợp và kết quả thử nghiệm của dự án. Phần nhiệm vụ cá nhân cần được bổ sung theo đúng công việc người viết đảm nhận. Các ảnh và dữ liệu dùng trong huấn luyện, kiểm thử thuộc phạm vi tài liệu dự án được nhóm cho phép sử dụng; báo cáo không đưa dữ liệu nội bộ của FPT vào nội dung.

## CHƯƠNG 1. CƠ SỞ LÝ THUYẾT

### 1.1. Trí tuệ nhân tạo và xử lý ảnh

Trí tuệ nhân tạo (AI) là cách xây dựng phần mềm có thể học từ dữ liệu để thực hiện một số nhiệm vụ như phân loại, dự đoán hoặc nhận dạng. Trong dự án SPAS, dữ liệu đầu vào là ảnh khuôn mặt lấy từ camera. Máy tính không “nhìn” ảnh như con người; ảnh được biểu diễn thành các giá trị số để mô hình xử lý.

Xử lý ảnh bằng máy tính có thể chia thành hai câu hỏi. Câu hỏi thứ nhất là trong ảnh có khuôn mặt nào và chúng nằm ở đâu. Câu hỏi thứ hai là khuôn mặt đã tìm thấy có thể thuộc về người nào trong danh sách đã đăng ký. SPAS dùng hai bước AI riêng để trả lời hai câu hỏi này.

### 1.2. Phát hiện khuôn mặt

Phát hiện khuôn mặt là tìm vị trí khuôn mặt trong ảnh. Kết quả thường là một hình chữ nhật bao quanh khuôn mặt cùng một điểm tin cậy. Trong SPAS, YOLO11n đảm nhận công việc này.

Detector không tự biết tên người trong hình chữ nhật. Nó chỉ báo “có một khuôn mặt ở vùng này”. Việc xác định danh tính được chuyển cho mô hình nhận diện ở bước tiếp theo. Tách hai nhiệm vụ giúp mỗi thành phần có một công việc rõ ràng và có thể được đánh giá riêng.

### 1.3. Mạng nơ-ron tích chập và học chuyển giao

Mạng nơ-ron tích chập (CNN) thường được dùng với ảnh vì có thể học các đặc điểm từ đơn giản đến phức tạp. Ở các lớp đầu, mô hình có thể học cạnh hoặc vùng sáng tối. Ở các phần sâu hơn, mô hình kết hợp các đặc điểm để nhận ra hình dạng và cấu trúc khuôn mặt.

Học chuyển giao là bắt đầu từ một mô hình đã học trên dữ liệu lớn, sau đó điều chỉnh mô hình bằng dữ liệu của bài toán đang làm. Cách này giúp nhóm không phải bắt đầu từ số 0. Tuy nhiên, kết quả còn phụ thuộc vào chất lượng dữ liệu, cách chia tập và mức độ giống nhau giữa dữ liệu thử nghiệm với ảnh thực tế. Inception-ResNet là ví dụ kết hợp các nhánh trích xuất đặc điểm với kết nối dư để việc học sâu ổn định hơn [4].

### 1.4. Vector đặc trưng khuôn mặt

Sau khi phát hiện và căn chỉnh khuôn mặt, mô hình nhận diện chuyển ảnh thành một dãy số gọi là vector đặc trưng. Có thể xem vector như một “mã số” mô tả các đặc điểm mà mô hình đã học từ khuôn mặt. Trong cấu hình của dự án, vector có 512 giá trị.

Các ảnh khác nhau của cùng một người được kỳ vọng tạo ra vector gần nhau hơn các ảnh của hai người khác nhau. Hệ thống lưu vector của những người đã đăng ký trong một tập dữ liệu gọi là gallery. Khi có ảnh mới, hệ thống tạo vector rồi tìm vector gần nhất trong gallery.

### 1.5. ArcFace

ArcFace là phương pháp dùng trong lúc huấn luyện để giúp mô hình phân biệt các danh tính rõ hơn. Có thể hiểu đơn giản rằng ArcFace khuyến khích ảnh của cùng một người nằm gần nhau trong không gian đặc trưng, đồng thời khuyến khích ảnh của những người khác nhau cách xa nhau hơn [3].

ArcFace không tự tìm vị trí khuôn mặt và cũng không trực tiếp ghi nhận điểm danh. Nó góp phần dạy mô hình nhận diện tạo ra vector hữu ích cho việc so sánh. Sau huấn luyện, hệ thống sử dụng phần tạo vector để so sánh ảnh mới với gallery.

Trong lúc huấn luyện, mỗi embedding được chuẩn hóa rồi so với các trọng số đại diện cho các danh tính trong tập train. Với danh tính đúng, ArcFace cộng một khoảng góc `m` vào góc hiện tại trước khi tính logit; các logit sau đó được nhân với hệ số `s` và đưa vào hàm mất mát phân loại. Có thể viết logit của lớp đúng ở dạng `s × cos(θ + m)`. Cách này làm bài toán phân lớp khó hơn một chút: mô hình phải tạo vector có hướng rõ ràng hơn để phân biệt danh tính. Trong notebook, `m = 0,35` và `s = 32`; công thức này mô tả nhánh huấn luyện, không phải công thức threshold ở runtime [3, 8].

### 1.6. Cosine similarity và quyết định danh tính

Cosine similarity là một cách đo mức độ cùng hướng của hai vector. Khi hai vector chỉ hướng gần giống nhau, điểm cosine cao hơn; khi hướng khác nhau, điểm thấp hơn. Dự án sử dụng phép đo này để xếp hạng các khuôn mặt trong gallery.

Quy trình ra quyết định không chỉ nhìn vào ứng viên đứng đầu. Hệ thống kiểm tra điểm có vượt ngưỡng chấp nhận hay không. Trong phiên bản hiện tại, nếu điểm thấp hơn ngưỡng hoặc không tìm thấy vector phù hợp, AI Service trả `UNKNOWN`; giáo viên có thể kiểm tra trường hợp này thay vì hệ thống tự gán tên.

L2 normalization đưa vector về độ dài bằng 1. Khi cả hai vector đã được chuẩn hóa, tích vô hướng của chúng bằng cosine similarity. Việc chuẩn hóa giúp việc so sánh tập trung vào hướng của vector thay vì độ lớn có thể thay đổi do điều kiện ảnh.

Cosine similarity được tính theo công thức:

**cos(A, B) = (A · B) / (||A|| × ||B||)**

Khi A và B đã được L2-normalize, độ dài của mỗi vector bằng 1 nên công thức rút gọn thành tích vô hướng A · B. Ví dụ A = [1, 0], B = [0,8; 0,6]: tích vô hướng là (1 × 0,8) + (0 × 0,6) = 0,8; hai vector đều có độ dài 1 nên cosine cũng bằng 0,8. Ví dụ này chỉ minh họa phép tính bằng vector hai chiều; trong hệ thống, mỗi embedding có 512 chiều.

Ví dụ minh họa với các vector ngắn hơn vector 512 chiều của hệ thống:

| So sánh | Vector A | Vector B | Cosine | Cách hiểu |
|---|---|---|---:|---|
| Hai hướng gần nhau | [1, 0] | [0,8; 0,6] | 0,8 | Hai vector cùng hướng ở mức khá cao. |
| Hai hướng vuông góc | [1, 0] | [0, 1] | 0,0 | Hai vector không cùng hướng. |

Với vector đã chuẩn hóa, khoảng cách Euclidean và cosine cho cùng thứ tự xếp hạng vì bình phương khoảng cách Euclidean bằng 2 trừ hai lần cosine. Tuy nhiên, cosine biểu diễn trực tiếp mức độ cùng hướng nên phù hợp để giải thích điểm tương đồng của embedding. Điều đó không có nghĩa cosine luôn tốt hơn mọi phép đo; cách chọn cần dựa trên mô hình và dữ liệu thực tế.

| Phép đo | Cách so sánh | Khi nào có thể phù hợp |
|---|---|---|
| Cosine similarity | So góc giữa hai vector; ít bị ảnh hưởng bởi độ dài vector. | Khi embedding đã chuẩn hóa và cần xếp hạng theo hướng đặc trưng. |
| Euclidean distance | Đo khoảng cách thẳng giữa hai điểm trong không gian vector. | Khi độ lớn và cấu trúc khoảng cách đã được kiểm soát trong quá trình huấn luyện. |
| Manhattan distance | Cộng độ chênh tuyệt đối trên từng chiều. | Có thể dùng khi bài toán phù hợp với cách cộng chênh lệch theo từng tọa độ; cần thử nghiệm trước khi chọn. |

Trong prototype, nhóm dùng cosine trên embedding đã L2-normalize để phép so sánh ngắn gọn và nhất quán với vector gallery. Muốn kết luận phép đo này tốt hơn lựa chọn khác cần chạy thử các cách đo trên cùng một tập kiểm thử, cùng cách tạo gallery và cùng quy tắc chọn ngưỡng.

Các số trên chỉ giải thích phép tính, không phải ngưỡng nhận diện của hệ thống. Điểm cosine cũng không phải phần trăm chính xác. Ngưỡng cần được chọn bằng dữ liệu đánh giá phù hợp; nếu hai ứng viên đầu có điểm gần nhau, hệ thống nên chuyển kết quả sang trạng thái cần rà soát.

### 1.7. Các chỉ số đánh giá

Các chỉ số giúp mô tả một phần chất lượng mô hình, nhưng mỗi chỉ số trả lời một câu hỏi khác nhau:

| Chỉ số | Giải thích dễ hiểu |
|---|---|
| Precision | Trong các khuôn mặt mô hình đã tìm thấy, có bao nhiêu kết quả là đúng. |
| Recall | Trong tất cả khuôn mặt cần tìm, mô hình tìm được bao nhiêu. |
| mAP | Chỉ số tổng hợp để đánh giá chất lượng vị trí và xếp hạng các hộp khuôn mặt. |
| Top-1 | Danh tính đúng đứng đầu danh sách ứng viên bao nhiêu lần. |
| Top-5 | Danh tính đúng nằm trong năm ứng viên đầu bao nhiêu lần. |
| Cosine similarity | Mức tương đồng giữa vector ảnh mới và vector đã lưu. |

Metric trong notebook chỉ mô tả kết quả trên tập dữ liệu và cách đánh giá của lần chạy đó. Chúng không tự động chứng minh hệ thống đạt cùng mức chính xác khi chạy với camera lớp học.

### 1.8. Bảo vệ dữ liệu và vai trò con người

Ảnh khuôn mặt và vector đặc trưng đều cần được xem là dữ liệu nhạy cảm. Hệ thống cần giới hạn người được xem, lưu hoặc chỉnh sửa thông tin; chỉ giữ dữ liệu cần thiết; và có quy định về thời gian lưu trữ, xóa dữ liệu.

AI có thể mắc lỗi khi ảnh tối, mặt nhỏ, bị che khuất hoặc quay nghiêng. Do đó, trong phạm vi prototype, quyết định cuối cùng nên có khả năng được giảng viên xem lại. Kết quả AI là gợi ý, không phải bằng chứng tuyệt đối về danh tính.

## CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 2.1. Bài toán và mục tiêu

Bài toán của SPAS là hỗ trợ ghi nhận người có mặt trong một buổi học thông qua hình ảnh camera. Hệ thống cần tìm được khuôn mặt, so sánh với danh sách đã đăng ký, trả về kết quả có thể kiểm tra và không tự gán danh tính khi bằng chứng còn yếu.

Mục tiêu của phiên bản prototype gồm:

- hỗ trợ giáo viên mở buổi học và quan sát quá trình điểm danh;
- phát hiện nhiều khuôn mặt trong ảnh;
- so sánh khuôn mặt với danh sách người đã đăng ký;
- ghi nhận người phù hợp và đánh dấu người chưa xác định;
- lưu bằng chứng để giáo viên xem lại;
- cho phép giáo viên rà soát hoặc điều chỉnh kết quả khi cần.

### 2.2. Người dùng chính

| Người dùng | Nhu cầu chính |
|---|---|
| Giáo viên | Tạo buổi học, theo dõi danh sách, xem ảnh bằng chứng và rà soát kết quả. |
| Sinh viên | Đăng ký khuôn mặt và được ghi nhận trong buổi học. |
| Quản trị viên | Quản lý tài khoản, lớp, quyền truy cập và cấu hình chung. |
| AI Service | Nhận ảnh, phát hiện và so khớp khuôn mặt, trả kết quả cho Backend. |

### 2.3. Chức năng và phạm vi

Các chức năng trong phạm vi dự án gồm đăng nhập và phân quyền, quản lý lớp và danh sách, đăng ký khuôn mặt, mở phiên điểm danh, nhận ảnh từ camera, nhận diện người đã đăng ký, trả về người chưa xác định, lưu bằng chứng và cho giáo viên rà soát.

Prototype không tuyên bố giải quyết đầy đủ các vấn đề như chống giả mạo chuyên sâu, hoạt động ổn định ở mọi loại camera, xử lý lớp học quy mô lớn hoặc thay thế hoàn toàn quyết định của giảng viên. Các tính năng đó cần thiết kế và kiểm thử riêng.

### 2.4. Các thành phần của hệ thống

| Thành phần | Vai trò |
|---|---|
| Giao diện người dùng | Cho giáo viên thao tác với lớp, camera, phiên điểm danh và kết quả. |
| Backend | Kiểm tra quyền, quản lý phiên, gọi AI Service và lưu nghiệp vụ điểm danh. |
| AI Service | Nạp mô hình, xử lý ảnh, tạo vector, so sánh với gallery và trả kết quả. |
| Cơ sở dữ liệu | Lưu người dùng, lớp học, phiên, kết quả điểm danh và trạng thái rà soát. |
| Gallery | Lưu vector của người đã đăng ký để hệ thống so sánh. |
| Nơi lưu bằng chứng | Lưu ảnh hoặc crop được dùng để người phụ trách kiểm tra lại. |

### 2.5. Bảng luồng hoạt động điểm danh

| Bước | Thành phần thực hiện | Hoạt động | Kết quả |
|---:|---|---|---|
| 1 | Giáo viên | Mở phiên điểm danh và chọn lớp. | Phiên được tạo hoặc kích hoạt. |
| 2 | Giao diện | Lấy khung hình từ camera và gửi lên Backend. | Backend nhận ảnh của phiên. |
| 3 | Backend | Kiểm tra phiên, quyền và dữ liệu đầu vào. | Ảnh hợp lệ được chuyển đến AI Service. |
| 4 | AI Service | YOLO11n tìm vị trí từng khuôn mặt. | Một hoặc nhiều vùng khuôn mặt. |
| 5 | AI Service | Cắt và căn chỉnh từng khuôn mặt. | Ảnh khuôn mặt ở dạng phù hợp cho mô hình nhận diện. |
| 6 | AI Service | InceptionResnetV1 tạo vector đặc trưng. | Vector đại diện cho từng khuôn mặt. |
| 7 | AI Service | So sánh vector với gallery của lớp bằng cosine similarity. | Danh sách ứng viên cùng điểm tương đồng. |
| 8 | AI Service | So điểm ứng viên cao nhất với ngưỡng cấu hình của dịch vụ. | Trả danh tính phù hợp hoặc `UNKNOWN` nếu điểm thấp hơn ngưỡng. |
| 9 | Backend | Lưu kết quả, thời điểm và bằng chứng theo chính sách của hệ thống. | Bản ghi điểm danh có thể kiểm tra lại. |
| 10 | Giáo viên | Xem và rà soát trường hợp cần thiết. | Kết quả được xác nhận hoặc điều chỉnh. |

### 2.6. Luồng đăng ký khuôn mặt

| Bước | Hoạt động | Ghi chú |
|---:|---|---|
| 1 | Người dùng đăng nhập đúng tài khoản. | Hệ thống kiểm tra quyền đăng ký. |
| 2 | Camera thu một số ảnh khuôn mặt. | Ảnh cần đủ rõ và có góc nhìn phù hợp. |
| 3 | AI phát hiện, căn chỉnh và tạo vector cho từng ảnh. | Ảnh quá mờ hoặc không có mặt hợp lệ nên được yêu cầu chụp lại. |
| 4 | Hệ thống kiểm tra chất lượng và dấu hiệu trùng theo quy tắc hiện có. | Kết quả không chắc chắn cần được xử lý cẩn thận. |
| 5 | Các vector hợp lệ được tổng hợp thành dữ liệu đăng ký. | Gallery được cập nhật sau khi đăng ký thành công. |

### 2.7. Yêu cầu về an toàn và độ tin cậy

- Chỉ tài khoản có quyền mới được mở phiên hoặc xem dữ liệu của lớp.
- Ảnh không hợp lệ không được âm thầm ghi thành lượt điểm danh.
- Không gán một danh tính khi điểm tương đồng chưa đạt điều kiện.
- Kết quả cần gắn với phiên và thời điểm để người dùng kiểm tra.
- Giáo viên cần có cách rà soát trường hợp AI chưa chắc chắn.
- Việc thu thập và lưu ảnh cần được thông báo, giới hạn quyền truy cập và tuân theo chính sách áp dụng.

### 2.8. Yêu cầu chức năng và chất lượng

Yêu cầu chức năng mô tả những việc người dùng có thể làm. Yêu cầu chất lượng mô tả điều kiện để hệ thống có thể được sử dụng an toàn và dễ kiểm tra. Các bảng dưới đây là phạm vi thiết kế của prototype, không thay thế quy trình nghiệm thu của một hệ thống thương mại.

| Mã | Yêu cầu chức năng | Kết quả mong đợi |
|---|---|---|
| F01 | Đăng nhập và phân quyền | Người dùng chỉ thấy chức năng phù hợp với vai trò. |
| F02 | Quản lý lớp và danh sách người học | Giáo viên chọn được lớp và kiểm tra roster của phiên. |
| F03 | Đăng ký khuôn mặt | Ảnh hợp lệ được chuyển thành dữ liệu đặc trưng gắn với tài khoản phù hợp. |
| F04 | Mở phiên điểm danh | Phiên có lớp, thời điểm và trạng thái để Backend kiểm tra. |
| F05 | Nhận ảnh và tìm khuôn mặt | Một ảnh có thể trả về nhiều vùng khuôn mặt để xử lý riêng. |
| F06 | Nhận diện hoặc trả chưa xác định | Hệ thống không tự gán tên khi điểm thấp hơn ngưỡng cấu hình. |
| F07 | Lưu và xem bằng chứng | Người có quyền có thể truy ngược kết quả đến phiên tương ứng. |
| F08 | Rà soát kết quả | Giáo viên xem lại trường hợp chưa rõ và điều chỉnh theo quyền được cấp. |

| Nhóm yêu cầu chất lượng | Mô tả áp dụng trong prototype |
|---|---|
| Tính đúng đắn | Không biến kết quả AI thành quyết định cuối cùng nếu chưa qua quy tắc nghiệp vụ. |
| Khả năng kiểm tra | Lưu thời điểm, phiên và bằng chứng liên quan để người phụ trách rà soát. |
| Bảo vệ dữ liệu | Hạn chế quyền xem ảnh và vector; chỉ sử dụng dữ liệu được phép. |
| Khả năng bảo trì | Tách giao diện, Backend và AI Service để kiểm tra hoặc thay từng phần. |
| Khả năng chịu lỗi | Khi dịch vụ AI lỗi, giao diện cần báo lỗi và Backend không ghi kết quả nhận diện giả. |

### 2.9. Dữ liệu logic của hệ thống

Để giải thích quan hệ dữ liệu mà không phụ thuộc vào tên bảng cụ thể trong mã nguồn, có thể xem hệ thống qua các nhóm thông tin logic sau:

| Nhóm dữ liệu | Thông tin chính | Mối liên hệ |
|---|---|---|
| Tài khoản | Mã người dùng, thông tin đăng nhập, vai trò | Xác định quyền thao tác của giáo viên, sinh viên hoặc quản trị viên. |
| Lớp và danh sách | Mã lớp, thông tin môn học và các tài khoản được xếp vào lớp | Là phạm vi người cần được điểm danh trong phiên. |
| Phiên điểm danh | Mã phiên, lớp, thời điểm mở/đóng và trạng thái | Gom các lượt ghi nhận thuộc cùng một buổi học. |
| Dữ liệu đăng ký khuôn mặt | Mã người dùng và vector đặc trưng đã chuẩn hóa | Giúp AI Service so ảnh mới với người đã đăng ký. |
| Bản ghi điểm danh | Mã phiên, kết quả nhận diện, thời điểm và trạng thái rà soát | Ghi lại kết quả nghiệp vụ mà Backend quản lý. |
| Bằng chứng | Ảnh hoặc vùng ảnh liên quan đến một lượt xử lý | Hỗ trợ người được phân quyền kiểm tra lại khi cần. |

Luồng xử lý đi qua các nhóm dữ liệu này theo thứ tự: tài khoản và roster xác định phạm vi; phiên tạo ngữ cảnh điểm danh; AI Service dùng vector để đề xuất danh tính; Backend đối chiếu quy tắc và ghi bản ghi; bằng chứng được liên kết với kết quả theo chính sách lưu trữ. Đây là mô hình giải thích ở mức khái niệm. Tên trường, bảng dữ liệu và cách lưu cụ thể cần đối chiếu với phiên bản mã nguồn được nộp.

## CHƯƠNG 3. HUẤN LUYỆN MÔ HÌNH VÀ TÍCH HỢP HỆ THỐNG

### 3.1. Vì sao dùng hai mô hình

SPAS tách việc “tìm khuôn mặt ở đâu” và “khuôn mặt này giống ai” thành hai nhiệm vụ. YOLO11n phù hợp với bước phát hiện vị trí. InceptionResnetV1 được dùng để tạo vector khuôn mặt; ArcFace là phương pháp giúp huấn luyện vector phân biệt danh tính tốt hơn.

Nếu gộp mọi việc vào một kết quả duy nhất, sẽ khó biết lỗi nằm ở việc không tìm thấy mặt hay tìm thấy rồi nhưng nhận diện sai. Tách bước cho phép nhóm xem xét và đánh giá từng phần độc lập.

### 3.2. Mô hình phát hiện: YOLO11n

YOLO11n là mô hình nhỏ trong họ YOLO. Trong dự án, mô hình được huấn luyện để nhận một loại đối tượng là khuôn mặt. Nhóm chọn mô hình này vì nó có thể tìm nhiều khuôn mặt trong một ảnh và có thể trả kết quả đủ nhanh cho một prototype.

Notebook detector ghi nhận lần huấn luyện dùng 25 epoch trên tập WIDER Face đã được chuyển sang định dạng YOLO, gồm 12.880 ảnh huấn luyện và 3.226 ảnh validation [5, 7]. Mỗi epoch là một lượt mô hình học qua tập huấn luyện. Những con số này mô tả lần chạy trong notebook, không phải cam kết về tốc độ hoặc chất lượng khi triển khai ở mọi thiết bị.

Ở mức dễ hiểu, YOLO11n có ba phần: phần đầu trích xuất đặc điểm từ ảnh, phần giữa kết hợp đặc điểm ở nhiều kích thước, và phần cuối dự đoán vị trí khuôn mặt. Không cần xem đây là ba mô hình riêng; chúng phối hợp bên trong một detector. Kết quả tổng kết của notebook ghi 100 layer, 2.582.347 tham số sau khi gộp một số phép chuẩn hóa vào lớp tích chập, và khoảng 6,4 GFLOPs ở cấu hình đánh giá. Log trước bước gộp ghi 2.624.080 tham số; hai cách đếm thuộc hai trạng thái triển khai khác nhau của cùng detector.

| Thông số huấn luyện YOLO11n | Giá trị trong notebook |
|---|---|
| Trọng số khởi tạo | `yolo11n.pt` đã huấn luyện trước |
| Nhiệm vụ | Phát hiện một lớp: khuôn mặt |
| Kích thước ảnh | 640 × 640 |
| Batch size | 8 |
| Số epoch | 25 |
| Ảnh train / validation | 12.880 / 3.226 |
| Tham số ở log model ban đầu | 2.624.080 |
| Layer / tham số sau fusion / phép tính | 100 / 2.582.347 / 6,4 GFLOPs |

Nhóm chọn YOLO11n vì đây là biến thể nhỏ, có thể tìm nhiều khuôn mặt trong một khung hình và tách rõ kết quả định vị khỏi bước nhận dạng. Quyết định dùng biến thể “n” ưu tiên thời gian xử lý và tài nguyên vừa phải cho prototype; đổi lại, Recall vẫn cần được theo dõi vì mô hình có thể bỏ sót khuôn mặt nhỏ hoặc bị che [2].

### 3.3. Mô hình nhận diện: InceptionResnetV1 và ArcFace

InceptionResnetV1 nhận một ảnh khuôn mặt đã được chuẩn bị và trả về vector 512 giá trị. Model được khởi tạo bằng trọng số đã học trên VGGFace2 rồi fine-tune trên một phần WebFace-112x112 gồm 1.500 danh tính được chọn, với 37.501 ảnh train và 9.383 ảnh validation. Lần huấn luyện được ghi nhận chạy 20 epoch [6, 8].

ArcFace được dùng trong lúc huấn luyện để tăng khả năng phân biệt danh tính. Khi hệ thống chạy điểm danh, phần tạo vector của InceptionResnetV1 cung cấp biểu diễn để so sánh với gallery. Hệ thống không cần huấn luyện lại toàn bộ mô hình mỗi khi thêm một sinh viên mới; thay vào đó, sau khi đăng ký hợp lệ, vector của người đó được thêm vào gallery.

InceptionResnetV1 có phần đầu trích xuất đặc điểm, sau đó là các khối Inception-ResNet lặp lại: Block35 lặp 5 lần, Block17 lặp 10 lần, Block8 lặp 5 lần và một Block8 cuối. Tiếp theo là gộp trung bình, lớp tuyến tính từ 1.792 xuống 512 chiều và chuẩn hóa. Mỗi khối có nhiều nhánh tích chập, vì vậy một con số “tổng số layer” có thể khác nhau tùy cách đếm; báo cáo dùng cấu trúc khối và số tham số do notebook ghi lại để tránh gây hiểu nhầm [6].

Notebook ghi 27.910.327 tham số trong phần tạo embedding. Khi huấn luyện, ArcMarginProduct bổ sung một ma trận 1.500 × 512, tương đương 768.000 tham số; tổng phần tạo embedding và đầu phân lớp là 28.678.327 tham số. Khi chạy nhận diện, đầu ArcMarginProduct không cần dùng; hệ thống chỉ cần phần tạo vector 512 chiều.

| Thông số recognizer | Giá trị trong notebook |
|---|---|
| Kiến trúc | InceptionResnetV1, khởi tạo từ VGGFace2 |
| Kích thước ảnh đầu vào | 160 × 160 RGB |
| Vector đầu ra | 512 chiều |
| Tham số phần tạo embedding | 27.910.327 |
| ArcMarginProduct | 1.500 lớp × 512 chiều = 768.000 tham số |
| Tổng tham số khi huấn luyện | 28.678.327 |
| Epoch / batch size | 20 / 64 |
| Optimizer / learning rate đầu | AdamW / 0,0001 |
| Weight decay / lịch giảm learning rate | 0,0001 / Cosine Annealing đến 0,000001 |
| Số danh tính và ảnh train / validation | 1.500; 37.501 / 9.383 |
| Kích thước gallery khi đánh giá | 1.500 vector, mỗi vector 512 chiều |

Đầu phân lớp ArcFace dùng scale 32 và angular margin 0,35. Loss là cross-entropy với label smoothing 0,05. Toàn bộ phần tạo embedding và đầu phân lớp được đưa vào optimizer; notebook lưu checkpoint tốt nhất dựa trên validation Top-1. Đây là lý do checkpoint embedding dùng khi inference không cần chứa đầu phân lớp 1.500 danh tính.

Quy trình fine-tune có thể đọc theo các bước sau:

| Bước | Hoạt động trong lần huấn luyện | Mục đích |
|---:|---|---|
| 1 | Nạp trọng số InceptionResnetV1 đã học trước và chuẩn bị danh sách danh tính train. | Có điểm khởi đầu tốt hơn so với khởi tạo ngẫu nhiên. |
| 2 | Chia ảnh thành train và validation theo cấu hình notebook. | Học trên train và theo dõi khả năng khái quát trên dữ liệu chưa dùng để cập nhật trọng số. |
| 3 | Resize, chuẩn hóa và áp dụng augmentation cho ảnh train. | Giảm khác biệt nhỏ về ánh sáng, vị trí và góc nhìn. |
| 4 | Tạo embedding 512 chiều, đưa embedding qua đầu ArcFace và tính cross-entropy. | Đo mức độ mô hình phân biệt danh tính trong tập huấn luyện. |
| 5 | Lan truyền ngược gradient và cập nhật trọng số bằng AdamW. | Điều chỉnh mô hình để giảm loss. |
| 6 | Đánh giá trên validation và lưu checkpoint có Top-1 tốt nhất. | Theo dõi quá trình học và chọn checkpoint theo tiêu chí đã đặt. |
| 7 | Bỏ đầu phân lớp danh tính khi dùng cho tìm kiếm trong gallery. | Cho phép đăng ký danh tính mới mà không cần huấn luyện lại classifier cho từng người. |

Notebook ghi nhận cấu hình `AdamW`, learning rate ban đầu `1e-4`, weight decay `1e-4`, lịch learning rate cosine với mức cuối `1e-6`, batch size 64 và 20 epoch [8]. Đây là cấu hình của lần chạy được báo cáo, không khẳng định đã tìm được cấu hình tối ưu. Muốn so sánh cấu hình cần giữ nguyên cách chia dữ liệu và thay đổi từng yếu tố có kiểm soát.

Ảnh train và validation cần được chia hợp lý để ảnh gần như trùng lặp không cùng xuất hiện ở cả hai phía. Nếu cùng một cảnh hoặc chuỗi ảnh liên tiếp lọt vào cả train và validation, metric có thể cao hơn khả năng nhận diện ảnh mới. Khi hoàn thiện thực nghiệm, nhóm nên lưu lại quy tắc chia dữ liệu, seed và danh sách danh tính của mỗi tập để kết quả có thể kiểm tra lại.

### 3.4. Chuẩn bị ảnh và tạo gallery

Các bước chuẩn bị ảnh thường được gọi là tiền xử lý. YOLO11n trước tiên cung cấp bounding box. Dịch vụ cắt vùng mặt; MTCNN tìm năm điểm mốc; OpenCV ước lượng phép biến đổi affine để đưa các điểm mốc về mẫu chuẩn. Hàm căn chỉnh thử ảnh gốc và các hướng xoay 90 độ, 180 độ, rồi chọn kết quả có xác suất landmark cao nhất. Ảnh sau đó được đổi sang RGB, resize về 160 × 160 và chuẩn hóa theo cách mà mô hình nhận diện cần. Nếu không tìm được landmark hoặc phép căn chỉnh hợp lệ, dịch vụ dùng vùng mặt đã cắt làm phương án dự phòng. Đây là luồng trong mã nguồn hiện tại, không phải một bước tự động của notebook [9].

Trong notebook, augmentation trên ảnh train gồm lật ngang, thay đổi nhẹ độ sáng/độ tương phản/màu và dịch/xoay nhỏ; ảnh validation chỉ resize và chuẩn hóa để kết quả không bị ngẫu nhiên [8]. Cần phân biệt hai luồng: metric notebook được tính theo phép chuẩn bị dữ liệu notebook, còn dịch vụ đang chạy có thêm căn chỉnh landmark và xử lý hướng ảnh. Khác biệt này là một lý do nữa để không suy ra chất lượng triển khai trực tiếp từ metric notebook.

Trong dự án, “trích xuất đặc trưng” không có nghĩa nhóm tự viết thủ công các quy tắc như khoảng cách giữa hai mắt. CNN tự học cách chuyển pixel thành vector trong quá trình fine-tune. Phần con người thiết kế là cách chuẩn bị ảnh, chọn mô hình và cách so sánh vector; phần đặc trưng chi tiết được học từ dữ liệu.

Khi đăng ký, hệ thống tạo vector từ các ảnh hợp lệ. Notebook đánh giá dùng 5 ảnh train cho mỗi danh tính để tạo vector gallery, lấy trung bình rồi chuẩn hóa lại. Gallery lưu vector cùng mã định danh của người đã đăng ký. Khi mở phiên, hệ thống có thể giới hạn gallery theo danh sách lớp để tránh so sánh với người không thuộc phạm vi phiên học.

#### Tìm ứng viên bằng phép nhân ma trận

Có thể xem gallery là một ma trận có `N` hàng và 512 cột; mỗi hàng là một vector khuôn mặt đã chuẩn hóa. Vector của ảnh mới được xem như ma trận một hàng kích thước `1 × 512`. Nhân vector query với chuyển vị của gallery tạo ra `N` điểm cosine cùng lúc: `scores = query × galleryᵀ`. Sau đó hệ thống lấy điểm cao nhất, tìm mã người tương ứng và so với ngưỡng runtime. Nếu gallery của notebook có 1.500 danh tính thì phép nhân trả 1.500 điểm để xếp hạng; trong phiên thật, danh sách có thể nhỏ hơn nếu chỉ so với roster của lớp.

Ví dụ dưới đây dùng hai chiều để nhìn rõ phép tính. Đây là số minh họa, không phải embedding thực tế của sinh viên:

| Thành phần | Giá trị minh họa |
|---|---|
| Query | `Q = [1, 0]` |
| Gallery của hai người | `G = [[0,8; 0,6], [0, 1]]` |
| Tính điểm | `Q × Gᵀ = [0,8; 0]` |
| Xếp hạng | Người thứ nhất đứng đầu với điểm 0,8; người thứ hai có điểm 0. |
| Quyết định minh họa | Nếu dùng ngưỡng runtime 0,60 thì ví dụ này vượt ngưỡng; đây không phải phép đo thật hoặc bằng chứng chọn ngưỡng tối ưu. |

Ưu điểm của cách biểu diễn ma trận là các phép nhân trên nhiều vector có cùng số chiều có thể được thực hiện bằng một phép toán vector hóa, thay vì viết vòng lặp riêng cho từng thành viên. Ma trận không tự làm cho hai khuôn mặt “giống nhau”; nó chỉ giúp tính điểm và xếp hạng nhiều ứng viên một cách gọn, nhất quán và thuận tiện cho phần cứng tăng tốc.

| Bước xử lý ảnh | Dữ liệu vào / ra | Vì sao cần |
|---|---|---|
| Nhận khung hình | Ảnh màu từ camera | Tạo đầu vào cho detector. |
| Phát hiện | Ảnh → bounding box và confidence | Tìm vị trí từng khuôn mặt. |
| Cắt và căn chỉnh | Bounding box và landmark → ảnh mặt chuẩn | Giảm ảnh hưởng của vị trí và góc nghiêng. |
| Resize và chuẩn hóa | Ảnh mặt → tensor 160 × 160 | Đưa dữ liệu về định dạng model được huấn luyện. |
| Trích xuất embedding | Tensor → vector 512 chiều | Tóm tắt đặc trưng khuôn mặt thành dãy số. |
| L2-normalize và so sánh | Vector chuẩn hóa × gallery | Tính cosine và xếp hạng ứng viên. |
| Trả quyết định | Match hoặc unknown | Tránh bắt buộc gán tên khi bằng chứng yếu. |

### 3.5. Tích hợp với Backend

AI Service và Backend có nhiệm vụ khác nhau. AI Service xử lý ảnh và đưa ra gợi ý nhận diện; Backend quản lý phiên, quyền, lớp và dữ liệu điểm danh. Cách chia này giúp phần xử lý AI có thể thay đổi mà không cần chuyển toàn bộ nghiệp vụ lớp học vào trong mô hình.

| Trao đổi | Nội dung chính |
|---|---|
| Backend gửi AI Service | Ảnh hoặc khung hình, mã phiên và danh sách người được phép so sánh khi cần. |
| AI Service trả về | Vị trí khuôn mặt, danh tính đề xuất, điểm tương đồng và trạng thái nhận diện. |
| Backend xử lý tiếp | Kiểm tra nghiệp vụ, ghi nhận kết quả, lưu bằng chứng và trả dữ liệu cho giao diện. |
| Giao diện hiển thị | Danh sách đã nhận diện, trường hợp chưa xác định và công cụ rà soát. |

Có thể tóm tắt trao đổi giữa các phần bằng bảng luồng sau, không cần xem model như nơi quyết định toàn bộ nghiệp vụ:

| Bước | Thành phần | Việc thực hiện | Kết quả chuyển tiếp |
|---:|---|---|---|
| 1 | Frontend | Chụp frame và gửi yêu cầu điểm danh. | Ảnh cùng thông tin phiên. |
| 2 | Backend | Kiểm tra người dùng, quyền, phiên và roster; chuyển ảnh sang AI Service. | Yêu cầu AI hợp lệ. |
| 3 | AI Service | Detect → crop/align → resize/normalize → tạo embedding → so cosine với gallery. | Box, identity đề xuất, score và trạng thái. |
| 4 | Backend | Áp dụng quy tắc attendance; lưu sự kiện và evidence theo quyền. | Bản ghi điểm danh có thể truy vết. |
| 5 | Frontend / giáo viên | Hiển thị kết quả và cho phép rà soát trường hợp chưa rõ. | Kết quả được xác nhận hoặc chỉnh sửa. |

Đối với một ảnh có nhiều khuôn mặt, mỗi bounding box được xử lý riêng. Vector của từng mặt được so với gallery; Backend nhận kết quả theo từng người rồi áp dụng roster và quy tắc của phiên. Vì vậy, “nhận dạng được một khuôn mặt” và “được ghi nhận có mặt trong lớp” là hai bước khác nhau.

Trong cấu hình dịch vụ hiện hành, ngưỡng phát hiện của YOLO11n là 0,35 và ngưỡng so khớp khuôn mặt là 0,60. Khi điểm cao nhất thấp hơn ngưỡng nhận diện, AI Service trả `UNKNOWN` thay vì gán tên. Đây là giá trị cấu hình đang dùng trong prototype, không phải ngưỡng tối ưu đã được chứng minh cho mọi camera hoặc nhóm dữ liệu. Ngưỡng này cũng không phải giá trị 0,7742 được báo cáo ở phép đánh giá notebook: 0,7742 là cosine trung bình của các cặp cùng danh tính trên validation; 0,60 là điều kiện quyết định ở runtime. Muốn thay đổi ngưỡng cần đo lại trên tập validation độc lập và ghi nhận cả nhận nhầm lẫn bỏ sót [9].

### 3.6. Phân biệt kết quả notebook và mô hình trong hệ thống

Các metric trong báo cáo này được lấy từ notebook huấn luyện mới nhất. Chúng phản ánh mô hình và tập validation trong notebook. Hệ thống đang chạy có thể sử dụng checkpoint và tiền xử lý khác. Vì vậy, không được gộp metric notebook với kết quả hệ thống thành một con số duy nhất.

Trước khi thay checkpoint trong hệ thống bằng một checkpoint mới, nhóm cần kiểm tra đúng kiến trúc, cách đọc trọng số, kích thước ảnh, chuẩn hóa, gallery và kết quả kiểm thử. Chỉ đổi tên file model không đủ để chứng minh hai checkpoint tương thích.

## CHƯƠNG 4. KẾT QUẢ, KIỂM THỬ VÀ ĐÁNH GIÁ HỆ THỐNG

### 4.1. Kết quả detector trong notebook

| Chỉ số | Kết quả notebook | Diễn giải |
|---|---:|---|
| Precision | 0,8253 | Trong các vùng được mô hình đánh dấu, phần lớn là vùng khuôn mặt đúng. |
| Recall | 0,5618 | Mô hình còn bỏ sót một số khuôn mặt trong tập đánh giá. |
| mAP50 | 0,6437 | Kết quả tổng hợp ở mức tiêu chuẩn IoU 0,50. |
| mAP50–95 | 0,3397 | Chỉ số nghiêm ngặt hơn vì kiểm tra ở nhiều mức khớp hộp. |

Precision cao hơn Recall cho thấy mô hình có thể đánh dấu tương đối đúng những khuôn mặt đã phát hiện, nhưng vẫn còn nguy cơ bỏ sót. Đây là điểm cần tiếp tục cải thiện nếu ảnh có nhiều người hoặc khuôn mặt nhỏ.

### 4.2. Kết quả recognizer trong notebook

| Chỉ số | Kết quả notebook | Diễn giải |
|---|---:|---|
| Validation Top-1 | 0,8896 | Danh tính đúng đứng đầu trong khoảng 89 trên 100 ảnh validation. |
| Validation Top-5 | 0,9208 | Danh tính đúng nằm trong năm ứng viên đầu trong khoảng 92 trên 100 ảnh. |
| Gallery Top-1 | 0,8801 | Khi so ảnh với gallery, danh tính đúng đứng đầu trong khoảng 88 trên 100 ảnh được đánh giá. |
| Gallery Top-5 | 0,9141 | Danh tính đúng nằm trong năm ứng viên đầu trong khoảng 91 trên 100 ảnh được đánh giá. |
| Mean true cosine | 0,7742 | Cosine trung bình giữa query validation và vector gallery của đúng danh tính. |
| Mean top-1 margin | 0,3713 | Chênh lệch trung bình giữa điểm ứng viên đứng đầu và đứng thứ hai. |

Đây là phép đánh giá trên tập dữ liệu của notebook, với cách tạo gallery được mô tả trong notebook. Các tỷ lệ này không đồng nghĩa với độ chính xác thực tế của điểm danh tại lớp học.

Giá trị cosine trung bình 0,7742 có thể được làm tròn thành 0,77 hoặc 0,78 tùy cách làm tròn. Nó được tính bằng cách lấy cosine similarity giữa mỗi ảnh validation và vector gallery của đúng danh tính, sau đó tính trung bình trên 9.383 ảnh. Đây không phải accuracy, không phải threshold và không có nghĩa hệ thống nhận diện đúng 77,42% số ảnh. Accuracy Top-1 của phép đánh giá gallery là 0,8801.

#### Cách đọc và giới hạn của các chỉ số

Trong đánh giá phát hiện, một vùng dự đoán được tính là đúng khi nó khớp với vùng khuôn mặt thật theo tiêu chuẩn giao trên hợp (IoU) và ngưỡng confidence của lần đánh giá. Gọi TP là số vùng đúng, FP là số vùng dự đoán nhầm và FN là số khuôn mặt bị bỏ sót, ta có:

| Chỉ số | Công thức hoặc cách tính | Điều cần lưu ý |
|---|---|---|
| Precision | TP / (TP + FP) | Tăng khi giảm dự đoán nhầm, nhưng không cho biết số mặt bị bỏ sót. |
| Recall | TP / (TP + FN) | Tăng khi tìm được nhiều mặt thật, nhưng có thể đi kèm nhiều dự đoán nhầm hơn. |
| F1-score | 2 × Precision × Recall / (Precision + Recall) | Cân bằng Precision và Recall tại một điểm hoạt động; notebook hiện báo cáo chính các metric detector theo Ultralytics. |
| mAP50 | Diện tích trung bình dưới đường Precision–Recall ở IoU 0,50. | Hộp dự đoán được xem là khớp khi mức giao trên hợp đạt ngưỡng 0,50. |
| mAP50–95 | Trung bình mAP trên nhiều ngưỡng IoU từ 0,50 đến 0,95. | Nghiêm ngặt hơn mAP50 vì kiểm tra cả độ chặt của hộp. |

Với nhận diện, Top-1 đếm số ảnh mà danh tính thật đứng đầu danh sách so khớp chia cho tổng số ảnh query; Top-5 đếm số ảnh mà danh tính thật nằm trong năm ứng viên đầu. Đây là các phép đánh giá theo tập danh tính đã có trong gallery. Chúng không đo trực tiếp khả năng từ chối người hoàn toàn mới.

#### Cần đo thêm khả năng từ chối người lạ

Trong ứng dụng thực tế, tập so khớp có thể chứa người không được đăng ký. Khi đó, chỉ số Top-1 trên các danh tính đã biết chưa trả lời được câu hỏi hệ thống có gán nhầm người lạ thành sinh viên hay không. Cần tạo tập kiểm thử có cả cặp cùng người, cặp khác người và người không có trong gallery; việc thu thập ảnh phải có sự đồng ý phù hợp.

| Chỉ số mở rộng | Cách hiểu | Mục đích |
|---|---|---|
| FAR (False Accept Rate) | Tỷ lệ trường hợp khác người hoặc người lạ bị chấp nhận nhầm. | Theo dõi rủi ro gán nhầm danh tính. |
| FRR (False Reject Rate) | Tỷ lệ ảnh của người đã đăng ký bị từ chối hoặc trả `UNKNOWN`. | Theo dõi trường hợp người hợp lệ bị bỏ qua. |
| ROC / EER | So sánh FAR và FRR ở nhiều ngưỡng; EER là điểm hai tỷ lệ bằng nhau. | Hỗ trợ lựa chọn ngưỡng theo mức chấp nhận rủi ro. |

Ngưỡng 0,60 trong cấu hình dịch vụ là giá trị đang dùng, không phải kết quả được suy ra từ cosine trung bình 0,7742. Muốn kết luận ngưỡng phù hợp cần đo FAR và FRR trên dữ liệu độc lập, chọn ngưỡng theo mục tiêu sử dụng, rồi kiểm tra lại trên một tập chưa dùng để chọn ngưỡng. Notebook hiện không cung cấp đầy đủ phép đo FAR/FRR đối với người ngoài gallery; báo cáo vì vậy không khẳng định hệ thống đã được kiểm định khả năng từ chối người lạ.

### 4.3. Kịch bản kiểm thử hệ thống

Các tình huống dưới đây dựa trên chức năng được mô tả trong báo cáo và slide SPAS. Cột kết quả thực tế cần được điền sau khi người viết chạy lại phiên bản sẽ trình bày; không đánh dấu “Đạt” nếu chưa có bằng chứng kiểm thử.

| Mã | Tình huống | Kết quả mong đợi | Kết quả thực tế |
|---|---|---|---|
| TC01 | Giáo viên đăng nhập | Vào đúng màn hình theo quyền. | [Bổ sung] |
| TC02 | Đăng ký khuôn mặt hợp lệ | Lưu dữ liệu sau khi ảnh đủ rõ và đủ điều kiện. | [Bổ sung] |
| TC03 | Điểm danh người đã đăng ký | Đề xuất đúng người khi kết quả đủ chắc chắn. | [Bổ sung] |
| TC04 | Người ngoài danh sách lớp xuất hiện | Không tự gán tên của một sinh viên trong lớp. | [Bổ sung] |
| TC05 | Kết quả nhận diện chưa rõ | Trả trạng thái cần rà soát hoặc chưa xác định. | [Bổ sung] |
| TC06 | Giáo viên mở ảnh bằng chứng | Hiển thị được bằng chứng tương ứng với lượt nhận diện. | [Bổ sung] |
| TC07 | Giáo viên sửa kết quả | Lưu kết quả chỉnh sửa theo quyền được cấp. | [Bổ sung] |
| TC08 | Dịch vụ AI không hoạt động | Hiển thị lỗi phù hợp, không tạo lượt điểm danh giả. | [Bổ sung] |

Để kiểm thử có thể lặp lại, mỗi lần chạy nên ghi phiên bản mã nguồn, checkpoint, cấu hình ngưỡng, thiết bị camera, điều kiện ánh sáng, số khuôn mặt trong ảnh và trạng thái của từng ca. Kết quả “đạt” chỉ được ghi khi đã chạy đúng phiên bản dùng để demo hoặc nộp; bảng hiện giữ chỗ vì tài liệu hiện có chưa kèm nhật ký chạy đầy đủ cho các tình huống trên.

| Nhóm lỗi cần phân biệt | Dấu hiệu | Cách ghi nhận khi kiểm thử |
|---|---|---|
| Lỗi phát hiện | Không tạo bounding box cho một khuôn mặt có trong ảnh, hoặc đánh dấu vùng không phải mặt. | Ghi số khuôn mặt thật, số vùng tìm được và điều kiện ảnh. |
| Lỗi căn chỉnh / tiền xử lý | Có vùng mặt nhưng crop sai, landmark không hợp lệ hoặc hướng ảnh không phù hợp. | Lưu mã ca thử và ảnh bằng chứng được phép sử dụng. |
| Lỗi nhận diện | Có embedding nhưng đề xuất sai người hoặc trả `UNKNOWN` cho người đã đăng ký. | Ghi danh tính thật, ứng viên đầu, cosine score và ngưỡng runtime. |
| Lỗi nghiệp vụ | AI có kết quả nhưng phiên, roster hoặc trạng thái điểm danh xử lý sai. | Kiểm tra dữ liệu phiên, kết quả AI và bản ghi cuối ở Backend. |
| Lỗi dịch vụ / kết nối | Backend không nhận được kết quả AI hoặc gặp lỗi khi lưu. | Ghi mã lỗi và xác nhận không tạo bản ghi thành công giả. |

Việc tách nhóm lỗi giúp nhóm không quy mọi vấn đề cho mô hình nhận diện. Chẳng hạn, sinh viên ngoài roster có thể được AI nhận ra trong gallery toàn cục nhưng Backend vẫn phải áp dụng quy tắc lớp; ngược lại, AI trả `UNKNOWN` là kết quả nhận diện chưa đủ chắc chắn, không tự động chứng minh người đó vắng mặt.

### 4.4. Đánh giá chung

Kết quả notebook cho thấy hai mô hình có thể thực hiện được các bước cơ bản của bài toán: tìm khuôn mặt và tạo đặc trưng phục vụ nhận diện. Kiến trúc tách detector và recognizer giúp việc giải thích, kiểm thử và thay đổi từng phần dễ hơn.

Hệ thống cũng có luồng nghiệp vụ để giáo viên theo dõi kết quả thay vì chỉ trả tên người từ mô hình. Các trạng thái chưa xác định và giao diện rà soát giúp hạn chế việc hệ thống buộc phải đoán trong mọi tình huống.

Tuy nhiên, các metric hiện có chủ yếu là kết quả thực nghiệm trong notebook. Chưa có đủ bằng chứng từ tập dữ liệu camera lớp học độc lập để kết luận độ chính xác ngoài môi trường thử nghiệm. Detector còn có thể bỏ sót mặt; recognizer có thể nhầm khi mặt nhỏ, tối, bị che hoặc góc quay khác ảnh đăng ký. Ngưỡng cosine đang được dùng như cấu hình của hệ thống, chưa nên xem là ngưỡng tối ưu cho mọi lớp.

### 4.5. Hạn chế và hướng cải thiện

- Bổ sung tập kiểm thử độc lập từ camera, nhiều điều kiện ánh sáng, kích thước và góc mặt; chỉ dùng ảnh khi có sự đồng ý phù hợp.
- Ghi phiên bản checkpoint, cách chia dữ liệu, tiền xử lý, ngưỡng và thiết bị cho mỗi lần đo.
- Đo riêng nhận đúng, bỏ sót, FAR và FRR; chọn ngưỡng trên tập validation độc lập rồi kiểm tra lại trên tập khác.
- Hoàn thiện phân quyền, thời gian lưu/xóa ảnh và nhật ký rà soát; giữ bước giáo viên xem lại kết quả có độ tin cậy thấp.

---

# PHẦN III. TỰ ĐÁNH GIÁ VÀ ĐỀ XUẤT

## 3.1. Kiến thức và kỹ năng thu nhận được

Qua thời gian học tập và làm việc, em hiểu rõ hơn cách một dự án công nghệ được chia thành nhiều phần: làm rõ nhu cầu, thiết kế cách xử lý, xây dựng thành phần, kiểm thử và ghi lại giới hạn. Dự án SPAS giúp em liên hệ kiến thức AI với quy trình phần mềm thực tế.

Về AI, em hiểu rằng một hệ thống nhận diện không chỉ có một mô hình. Detector tìm vị trí khuôn mặt; recognizer chuyển khuôn mặt thành vector; bước so sánh tìm ứng viên phù hợp; Backend mới áp dụng quy tắc điểm danh và lưu kết quả. Việc đọc metric cũng giúp em nhận ra rằng chỉ số trên tập validation không thể thay thế kiểm thử trong môi trường sử dụng thật.

Về kỹ năng làm việc, em có thêm kinh nghiệm [bổ sung kỹ năng thực tế như phối hợp nhóm, quản lý thời gian, viết tài liệu, sử dụng công cụ phát triển hoặc báo cáo tiến độ]. Mỗi kỹ năng nên gắn với một công việc cụ thể đã thực hiện tại FPT hoặc trong dự án SPAS.

## 3.2. Khó khăn và cách khắc phục

Một khó khăn của dự án là phải phân biệt metric huấn luyện với kết quả tích hợp. Mô hình có thể cho kết quả tốt trong notebook nhưng cần kiểm tra thêm khi thay đổi checkpoint, cách căn chỉnh ảnh hoặc gallery. Nhóm xử lý vấn đề này bằng cách ghi nguồn của từng metric và không gộp các kết quả khác môi trường.

Khó khăn khác là các thuật ngữ như embedding, cosine similarity và threshold có thể gây khó hiểu cho người mới. Trong báo cáo, các thuật ngữ được giải thích bằng ví dụ đơn giản và đặt trong đúng bước xử lý thay vì chỉ liệt kê định nghĩa.

**[Bổ sung thêm khó khăn thực tế của sinh viên tại FPT và cách đã xử lý.]**

## 3.3. Đề xuất

1. **Đối với sinh viên:** Nên ghi chép nhiệm vụ và kết quả công việc theo tuần; trước khi đưa thông tin của doanh nghiệp vào báo cáo cần xác nhận nội dung nào được phép công bố.
2. **Đối với dự án học tập:** Nên lưu lại dữ liệu kiểm thử, phiên bản mô hình và cách đo metric để người khác có thể hiểu nguồn gốc của kết quả.
3. **Đối với hệ thống SPAS:** Nên kiểm thử với tập ảnh độc lập, đo riêng trường hợp nhận nhầm và trường hợp bỏ sót, đồng thời giữ bước giáo viên rà soát.

---

# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Báo cáo đã giới thiệu khái quát FPT Smart Cloud từ tài liệu hội nhập nhân viên được cung cấp và trình bày quá trình nhóm thực hiện dự án SPAS trong giai đoạn người viết làm việc tại FPT. Nội dung tập trung vào công việc của dự án và cần được bổ sung bằng phần đóng góp cá nhân đã được xác nhận.

SPAS kết hợp phát hiện khuôn mặt, tạo vector đặc trưng, so sánh với gallery và xử lý kết quả bằng Backend. Các notebook cho thấy mô hình có thể học được đặc trưng từ dữ liệu thử nghiệm. Dù vậy, kết quả notebook chưa thay thế kiểm thử độc lập trên camera lớp học. Việc sử dụng trong thực tế cần có dữ liệu phù hợp, đánh giá kỹ hơn, bảo vệ thông tin khuôn mặt và cho phép con người rà soát kết quả.

Trong tương lai, dự án có thể được cải thiện bằng cách xây dựng tập kiểm thử thực tế có sự đồng ý, hiệu chỉnh ngưỡng theo dữ liệu, giảm bỏ sót khuôn mặt, đo thời gian xử lý, tăng khả năng giải thích và hoàn thiện chính sách lưu/xóa bằng chứng. Đối với báo cáo thực tập, người viết cần bổ sung nhiệm vụ và kết quả thực tế tại FPT, cùng những số liệu hoạt động được đơn vị cho phép sử dụng.

---

# TÀI LIỆU THAM KHẢO

1. FPT Smart Cloud. *FCI Onboard Training — October 2026*. Tài liệu hội nhập nhân viên; chỉ sử dụng nội dung được phép công bố.
2. Ultralytics. *YOLO11 Documentation*. https://docs.ultralytics.com/models/yolo11/ (truy cập ngày 23/10/2026).
3. Deng, J., Guo, J., Xue, N., & Zafeiriou, S. “ArcFace: Additive Angular Margin Loss for Deep Face Recognition.” CVPR, 2019, tr. 4690–4699. https://openaccess.thecvf.com/content_CVPR_2019/html/Deng_ArcFace_Additive_Angular_Margin_Loss_for_Deep_Face_Recognition_CVPR_2019_paper.html.
4. Szegedy, C., Ioffe, S., Vanhoucke, V., & Alemi, A. “Inception-v4, Inception-ResNet and the Impact of Residual Connections on Learning.” AAAI, 2017. https://doi.org/10.1609/aaai.v31i1.11231.
5. Yang, S., Luo, P., Loy, C.-C., & Tang, X. “WIDER FACE: A Face Detection Benchmark.” CVPR, 2016, tr. 5525–5533. https://openaccess.thecvf.com/content_cvpr_2016/html/Yang_WIDER_FACE_A_CVPR_2016_paper.html.
6. timesler. *facenet-pytorch: Inception Resnet (V1) models in PyTorch*. https://github.com/timesler/facenet-pytorch (truy cập ngày 23/10/2026).
7. Nhóm dự án SPAS. Notebook `face-attendance-yolo11n-detector.ipynb` — cấu hình huấn luyện và kết quả validation của detector.
8. Nhóm dự án SPAS. Notebook `face-attendance-arcface-recognition (1).ipynb` — cấu hình huấn luyện và kết quả validation của recognizer.
9. Nhóm dự án SPAS. Mã nguồn và tài liệu tích hợp AI Service với Backend.
10. OpenAI. ChatGPT/Codex, công cụ AI được sử dụng để hỗ trợ lập cấu trúc, soạn và biên tập bản nháp ở Phần I, Phần II và Phần III; giải thích thuật ngữ AI và rà soát cách diễn đạt. Người viết đối chiếu nội dung kỹ thuật và số liệu với tài liệu gốc. Công cụ được sử dụng trong phạm vi nhà trường cho phép (truy cập ngày 23/10/2026).

---

# PHỤ LỤC A. CHECKLIST HOÀN THIỆN BẢN NỘP

| Hạng mục | Trạng thái |
|---|---|
| Họ tên, mã sinh viên, lớp, trường, giảng viên | [Bổ sung] |
| Thời gian thực tập/làm việc và bộ phận tại FPT | [Bổ sung theo thông tin thật] |
| Nhiệm vụ cá nhân tại FPT và phần việc trong dự án SPAS | [Bổ sung riêng từng nội dung; nêu đúng phần cá nhân phụ trách] |
| Người hướng dẫn và xác nhận của đơn vị | [Bổ sung nếu mẫu yêu cầu] |
| Số liệu hoạt động hai năm gần nhất | [Dùng nguồn công khai hoặc số liệu được phép; không tự ước lượng] |
| Sơ đồ tổ chức | [Chỉ tự vẽ từ nguồn chính thức được phép; bản MD này không tạo sơ đồ] |
| Trạng thái thực tế của các ca kiểm thử | [Chạy và ghi lại trước khi nộp] |
| Xác nhận quyền sử dụng tài liệu đào tạo FCI | [Xin phép hoặc thay bằng nguồn công khai] |
| Xác nhận quyền sử dụng ảnh khuôn mặt và dữ liệu | [Bổ sung theo quy định của dự án] |
| Số trang, mục lục, font và lề theo mẫu PDF | [Dàn trang và kiểm tra trong Word] |

# PHỤ LỤC B. PHÂN BỔ TRANG DỰ KIẾN

| Phần | Số trang dự kiến |
|---|---:|
| Bìa, lời cảm ơn, mục lục và danh mục | 3–4 |
| Đặt vấn đề | 1 |
| Phần I — Tổng quan đơn vị | 3–5 |
| Phần II — Chuyên đề SPAS | 20–24 |
| Phần III — Tự đánh giá và đề xuất | 2–3 |
| Kết luận, tài liệu tham khảo, phụ lục | 1–3 |
| **Tổng dự kiến** | **30–40** |

Để giữ tổng báo cáo trong khoảng 30–40 trang, nên giới hạn phần đầu và phụ lục, phần I không vượt quá giới hạn trong mẫu, và điều chỉnh số trang Phần II theo hướng dẫn của trường. Số trang thực tế chỉ xác định sau khi dàn trang Word theo đúng khổ giấy, font, cỡ chữ, giãn dòng và lề của mẫu PDF.
