from docx import Document
from docx.text.paragraph import Paragraph
from copy import deepcopy
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
import sys
src, out = map(Path, sys.argv[1:3])
captions = [
'Bảng 1.1. Lĩnh vực hoạt động và sản phẩm, dịch vụ - Nhóm hoạt động',
'Bảng 1.2. Cơ cấu tổ chức và chức năng các đơn vị - Nhóm chức năng',
'Bảng 1.3. Bộ phận và nội dung thực tập của sinh viên - Thông tin',
'Bảng 1.4. Tình hình hoạt động trong hai năm gần nhất - Kỳ báo cáo',
'Bảng 2.1. Gán nhãn dữ liệu ảnh - Nội dung cần thống nhất',
'Bảng 2.2. Gán nhãn dữ liệu ảnh - Lỗi nhãn',
'Bảng 2.3. Mô hình YOLO - Phần',
'Bảng 2.4. Học chuyển giao và fine-tuning - Cách bắt đầu',
'Bảng 2.5. Các thông số huấn luyện thường gặp - Thông số',
'Bảng 2.6. Đánh giá mô hình ở mức cơ bản - Chỉ số',
'Bảng 2.7. Dữ liệu đầu vào và đầu ra - Thành phần',
'Bảng 2.8. Thiết kế quy tắc gán nhãn - Tình huống',
'Bảng 2.9. Kiểm tra chất lượng nhãn - Bước kiểm tra',
'Bảng 2.10. Quy trình tinh chỉnh mô hình - Bước',
'Bảng 2.11. Luồng trao đổi giữa dữ liệu và mô hình - Bước',
'Bảng 2.12. Yêu cầu chất lượng và rủi ro - Rủi ro',
'Bảng 2.13. Công cụ sử dụng - Nhóm công cụ',
'Bảng 2.14. Nhiệm vụ được tham gia - Nhóm công việc',
'Bảng 2.15. Cách thực hiện gán nhãn - Bước',
'Bảng 2.16. Cách tinh chỉnh YOLO - Giai đoạn',
'Bảng 2.17. Xem lỗi và cải thiện dữ liệu - Dấu hiệu',
'Bảng 2.18. Ghi nhận và so sánh các lần fine-tuning - Thông tin cần ghi',
'Bảng 2.19. Kết quả công việc - Nhóm việc',
'Bảng 2.20. Các trường hợp cần kiểm tra mô hình - Kịch bản',
]
d=Document(src); body=d.element.body
found=[]
for el in list(body):
 if el.tag==qn('w:p'):
  p=Paragraph(el,d)
  if p.text.strip().startswith('Bảng '): found.append((el,p))
assert len(found)==len(captions),(len(found),len(captions))
for (el,p),expected in zip(found,captions):
 assert p.text.strip()==expected,(p.text,expected)
 nxt=el.getnext()
 assert nxt is not None and nxt.tag==qn('w:tbl'),f'Caption is not directly before table: {expected}'
 nxt.addnext(el)
 p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 for r in p.runs:r.italic=True
paras=[Paragraph(el,d) for el in body if el.tag==qn('w:p')]
intro=next(p for p in paras if p.text.startswith('Mẫu báo cáo yêu cầu giới thiệu hoạt động của đơn vị trong hai năm gần nhất.'))
new=OxmlElement('w:p')
if intro._p.pPr is not None:new.append(deepcopy(intro._p.pPr))
r=OxmlElement('w:r'); t=OxmlElement('w:t'); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
t.text=('Thông tin công khai giúp xác nhận đơn vị hoạt động dưới tên pháp lý rõ ràng. Website của FPT Smart Cloud ghi tên Công ty TNHH FPT Smart Cloud, mã số đăng ký kinh doanh 0109307938, cấp ngày 13/08/2020 [7]. Apps Run The World ước tính doanh thu công ty năm 2024 khoảng 20 triệu USD [8]. FPT cho biết doanh thu lũy kế của FPT Smart Cloud đến hết tháng 7/2026 đã vượt doanh thu cả năm 2025, nhưng thông báo không nêu số tiền cụ thể [9]. Báo cáo thường niên FPT năm 2025 công bố doanh thu thực nhận từ các giải pháp AI và Cloud của toàn Tập đoàn đạt 913 tỷ đồng, tăng 48,4% so với năm 2024 [10]. Đây là số liệu của nhóm giải pháp AI và Cloud trong phạm vi FPT, không phải doanh thu riêng của FPT Smart Cloud.')
r.append(t); new.append(r); intro._p.addnext(new)
tab=next(t for t in d.tables if t.cell(0,0).text.strip()=='Kỳ báo cáo')
rows=[
('Năm 2024','Apps Run The World ước tính doanh thu FPT Smart Cloud khoảng 20 triệu USD [8].','Ước tính từ cơ sở dữ liệu doanh nghiệp; không phải số liệu tài chính kiểm toán do công ty công bố.'),
('Năm 2025','FPT cho biết doanh thu lũy kế đến hết tháng 7/2026 đã vượt doanh thu cả năm 2025 [9].','Nguồn chính thức không nêu số tiền cụ thể nên báo cáo không tự suy ra giá trị.')
]
def set_cell(cell,text):
 p=cell.paragraphs[0]
 if p.runs:
  p.runs[0].text=text
  for run in p.runs[1:]:run.text=''
 else:p.add_run(text)
 for extra in cell.paragraphs[1:]:
  for run in extra.runs:run.text=''
for ri,row in enumerate(rows,1):
 for ci,value in enumerate(row):set_cell(tab.cell(ri,ci),value)
refs=[
'7. FPT Smart Cloud. Thông tin chủ sở hữu website. https://microsoft.fptcloud.com/thong-tin-chu-so-huu-website/ (truy cập ngày 24/10/2026).',
'8. Apps Run The World. FPT Smart Cloud company profile (ước tính doanh thu năm 2024). https://www.appsruntheworld.com/customers-database/customers/view/fpt-smart-cloud-vietnam (truy cập ngày 24/10/2026).',
'9. FPT. FPT Appoints New Deputy CEO of FPT Smart Cloud and CEO of FPT Online. https://fpt.com/en/news/fpt-appoints-new-deputy-ceo-of-fpt-smart-cloud-and-ceo-of-fpt-online (truy cập ngày 24/10/2026).',
'10. FPT. Dịch vụ CNTT cho thị trường trong nước, Báo cáo thường niên 2025. https://bctn2025.fpt.com/vi/phan-tich-hoat-dong-kinh-doanh/khoi-cong-nghe/dich-vu-cntt-cho-thi-truong-trong-nuoc/ (truy cập ngày 24/10/2026).'
]
for text in refs:d.add_paragraph(text,style='Normal')
d.save(out)
v=Document(out); vb=v.element.body
capels=[el for el in vb if el.tag==qn('w:p') and Paragraph(el,v).text.strip().startswith('Bảng ')]
assert len(capels)==24
for el in capels:
 p=Paragraph(el,v); assert el.getprevious() is not None and el.getprevious().tag==qn('w:tbl'),p.text
 assert p.runs and all(run.italic is True for run in p.runs if run.text.strip()),p.text
assert len(v.tables)==26
assert any('20 triệu USD' in p.text for p in v.paragraphs)
assert all(any(p.text.startswith(prefix) for p in v.paragraphs) for prefix in ('7. FPT Smart Cloud.','8. Apps Run The World.','9. FPT.','10. FPT.'))
print('DOCX_OK captions=24 all_below_and_italic tables=24 references=7-10 revenue_summary=yes')
