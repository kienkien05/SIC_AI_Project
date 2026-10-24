from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from copy import deepcopy
from pathlib import Path
import sys
src,out,img1,img2=map(Path,sys.argv[1:5])
d=Document(src)
def replace_text(old,new):
 matches=[p for p in d.paragraphs if old in p.text.strip()]
 if not matches: raise ValueError('Text to replace was not found: '+old[:100])
 p=next((p for p in matches if p.text.strip()==old),matches[0])
 updated=p.text.replace(old,new,1)
 if p.runs:
  p.runs[0].text=updated
  for r in p.runs[1:]:r.text=''
 else:p.add_run(updated)
 return p
changes=[
('Để bảo vệ thông tin của đơn vị, báo cáo không nêu tên khách hàng, số lượng ảnh, tên lớp đối tượng hoặc cấu hình huấn luyện nội bộ khi chưa có xác nhận công bố.','Báo cáo tập trung vào kiến thức, quy trình và kỹ năng thu nhận được. Nội dung được trình bày theo phạm vi thực tập và phù hợp với yêu cầu bảo mật của đơn vị.'),
('Báo cáo gồm ba phần. Phần I giới thiệu khái quát về FPT Smart Cloud dựa trên tài liệu hội nhập nhân viên được cung cấp. Phần II trình bày lý thuyết và công việc gán nhãn, tinh chỉnh mô hình YOLO. Phần III tự đánh giá quá trình thực tập và đưa ra một số đề xuất. Các chỉ số chỉ được nêu khi có nguồn rõ ràng và được phép sử dụng.','Báo cáo gồm ba phần. Phần I giới thiệu FPT Smart Cloud và đơn vị thực tập. Phần II trình bày cơ sở lý thuyết, phân tích quy trình gán nhãn và tinh chỉnh mô hình YOLO. Phần III tổng kết kiến thức, kỹ năng, khó khăn và đề xuất.'),
('FPT Smart Cloud hoạt động trong các lĩnh vực điện toán đám mây, trí tuệ nhân tạo và dữ liệu thuộc hệ sinh thái FPT. Theo tài liệu hội nhập nhân viên tháng 10 năm 2026, đơn vị phát triển nền tảng và dịch vụ công nghệ phục vụ khách hàng doanh nghiệp, đồng thời chú trọng nghiên cứu, phát triển và vận hành sản phẩm [1].','FPT Smart Cloud thuộc hệ sinh thái FPT, hoạt động trong các lĩnh vực điện toán đám mây, trí tuệ nhân tạo và dữ liệu. Đơn vị phát triển nền tảng và dịch vụ công nghệ phục vụ khách hàng doanh nghiệp [1].'),
('Tài liệu hội nhập ghi FPT Smart Cloud ra mắt ngày 13/08/2020 [1]. Báo cáo sử dụng tên đơn vị theo hồ sơ thực tập là Công ty TNHH FPT Smart Cloud; cách ghi cuối cùng cần được đối chiếu với hướng dẫn của nhà trường và người phụ trách tại đơn vị.','Công ty TNHH FPT Smart Cloud được thành lập vào tháng 8/2020 [1, 9]. Website công ty công bố mã số đăng ký kinh doanh 0109307938, cấp ngày 13/08/2020 [7].'),
('Tài liệu hội nhập giới thiệu các nhóm dịch vụ điện toán đám mây, nền tảng AI, nền tảng dữ liệu và AI Factory. Có thể hiểu đơn giản như sau:','Các nhóm hoạt động chính gồm điện toán đám mây, nền tảng AI, nền tảng dữ liệu và AI Factory [1]. Bảng 1.1 tóm tắt chức năng của từng nhóm:'),
('Trong nhóm AI, tài liệu giới thiệu nền tảng AI, công cụ tạo ứng dụng và sản phẩm phục vụ giao tiếp, xử lý tài liệu, nhận diện và vận hành. Báo cáo chỉ trình bày theo nhóm để tránh dùng sai tên sản phẩm hoặc thông tin chưa được phép công bố [1].','Trong lĩnh vực AI, FPT Smart Cloud phát triển nền tảng và dịch vụ phục vụ giao tiếp, xử lý tài liệu, nhận diện và vận hành doanh nghiệp [1].'),
('Tài liệu hội nhập đề cập đến ban điều hành, các mảng Cloud Technology, AI Product, sản phẩm/dịch vụ, chất lượng và an toàn thông tin. Báo cáo mô tả ở mức khái quát, không nêu tên cá nhân hoặc chi tiết cơ cấu chưa được cho phép.','FPT Smart Cloud có các khối chuyên môn về AI Product, Cloud Technology, kinh doanh và vận hành, cùng các đơn vị hỗ trợ. Khối Sản phẩm AI gồm nhiều trung tâm và nhóm sản phẩm, trong đó Trung tâm Sản phẩm Vision là nơi em thực tập [11]. Hai sơ đồ dưới đây minh họa cơ cấu toàn công ty và riêng Khối Sản phẩm AI.'),
('Tài liệu hội nhập nhấn mạnh văn hóa đổi mới, học hỏi và phối hợp. Tài liệu cũng giới thiệu nguyên tắc “Quality from me” và “Security from Code”. Đây là nội dung được trích từ tài liệu hội nhập, không phải kết quả đánh giá độc lập [1].','Văn hóa làm việc đề cao tinh thần đổi mới, học hỏi và phối hợp. Các nguyên tắc “Quality from me” và “Security from Code” thể hiện sự chú trọng đến chất lượng và an toàn thông tin [1].'),
('Phần II trình bày kiến thức và quy trình liên quan đến hai nhóm nhiệm vụ này. Các ví dụ được viết ở mức khái quát để không làm lộ dữ liệu, tên dự án hoặc thông tin khách hàng của công ty.','Phần II trình bày kiến thức và quy trình gắn với hai nhiệm vụ này, tập trung vào cách thực hiện và bài học chuyên môn.'),
('Mẫu báo cáo yêu cầu giới thiệu hoạt động của đơn vị trong hai năm gần nhất. Tài liệu hội nhập không phải báo cáo tài chính nên không có số liệu doanh thu theo từng năm. Phần này bổ sung thông tin pháp lý và dữ liệu công khai; số liệu ước tính hoặc chưa được công bố được ghi rõ.','Các thông tin công khai dưới đây khái quát hoạt động và các mốc doanh thu của FPT Smart Cloud trong giai đoạn gần đây.'),
('Thông tin công khai giúp xác nhận đơn vị hoạt động dưới tên pháp lý rõ ràng. Website của FPT Smart Cloud ghi tên Công ty TNHH FPT Smart Cloud, mã số đăng ký kinh doanh 0109307938, cấp ngày 13/08/2020 [7]. Apps Run The World ước tính doanh thu công ty năm 2024 khoảng 20 triệu USD [8]. FPT cho biết doanh thu lũy kế của FPT Smart Cloud đến hết tháng 7/2026 đã vượt doanh thu cả năm 2025, nhưng thông báo không nêu số tiền cụ thể [9]. Báo cáo thường niên FPT năm 2025 công bố doanh thu thực nhận từ các giải pháp AI và Cloud của toàn Tập đoàn đạt 913 tỷ đồng, tăng 48,4% so với năm 2024 [10]. Đây là số liệu của nhóm giải pháp AI và Cloud trong phạm vi FPT, không phải doanh thu riêng của FPT Smart Cloud.','Apps Run The World ước tính doanh thu FPT Smart Cloud năm 2024 khoảng 20 triệu USD [8]. FPT cho biết doanh thu lũy kế của công ty đến hết tháng 7/2026 đã vượt tổng doanh thu cả năm 2025 [9]. Ở cấp Tập đoàn, Báo cáo thường niên FPT ghi nhận doanh thu thực nhận từ các giải pháp AI và Cloud đạt 913 tỷ đồng trong năm 2025, tăng 48,4% so với năm 2024 [10].'),
('Phần này có thể được cập nhật khi đơn vị cung cấp số liệu đã xác nhận hoặc nguồn công khai được phép sử dụng.','Các mốc công khai này cho thấy quy mô hoạt động và đà tăng trưởng của FPT Smart Cloud trong giai đoạn gần đây.')
]
for a,b in changes:replace_text(a,b)
# Update the generic tool/process row in the company overview.
table=next(t for t in d.tables if t.cell(0,0).text.strip()=='Thông tin')
for ri in range(len(table.rows)):
 if table.cell(ri,0).text.strip()=='Công cụ và quy trình':
  cell=table.cell(ri,1);p=cell.paragraphs[0];p.runs[0].text='Thực hiện theo công cụ, hướng dẫn và quy trình của bộ phận.'
  for r in p.runs[1:]:r.text=''
# Update the revenue table with direct, positively framed source notes.
revenue=next(t for t in d.tables if t.cell(0,0).text.strip()=='Kỳ báo cáo')
rows=[
('Năm 2024','Apps Run The World ước tính doanh thu FPT Smart Cloud khoảng 20 triệu USD [8].','Mức doanh thu được cơ sở dữ liệu doanh nghiệp ước tính.'),
('Năm 2025','FPT công bố doanh thu lũy kế đến hết tháng 7/2026 đã vượt tổng doanh thu cả năm 2025 [9].','Mốc tăng trưởng được FPT công bố.')
]
def set_cell(cell,text):
 p=cell.paragraphs[0]
 if p.runs:
  p.runs[0].text=text
  for r in p.runs[1:]:r.text=''
 else:p.add_run(text)
 for other in cell.paragraphs[1:]:
  for r in other.runs:r.text=''
for ri,row in enumerate(rows,1):
 for ci,text in enumerate(row):set_cell(revenue.cell(ri,ci),text)
# Add source-backed organization charts immediately after Table 1.2.
tablecap=next(p for p in d.paragraphs if p.text.strip().startswith('Bảng 1.2.'))
def insert_after(reference,style_name='DoanVB'):
 el=OxmlElement('w:p');reference._p.addnext(el);p=Paragraph(el,reference._parent);p.style=d.styles[style_name];return p
lead=insert_after(tablecap)
lead.add_run('Hình 1.1 thể hiện cơ cấu toàn công ty; Hình 1.2 tập trung vào Khối Sản phẩm AI [11].')
last=lead
figure_specs=[
(img1,'Hình 1.1. Sơ đồ tổ chức FPT Smart Cloud năm 2026 [11]','Sơ đồ tổ chức tổng thể FPT Smart Cloud'),
(img2,'Hình 1.2. Cơ cấu tổ chức Khối Sản phẩm AI năm 2026 [11]','Sơ đồ tổ chức Khối Sản phẩm AI')
]
# Reuse the existing caption style and add page-reference bookmarks for the figure list.
all_ids=[int(x.get(qn('w:id'))) for x in d.element.body.iter(qn('w:bookmarkStart')) if x.get(qn('w:id')) and x.get(qn('w:id')).isdigit()]
bookmark_id=max(all_ids,default=0)+1
figure_bookmarks=[]
for ix,(image_path,caption_text,alt) in enumerate(figure_specs,1):
 pic=insert_after(last);pic.alignment=WD_ALIGN_PARAGRAPH.CENTER;pic.paragraph_format.keep_with_next=True
 inline=pic.add_run().add_picture(str(image_path),width=Inches(6.0))
 inline._inline.docPr.set('descr',alt)
 inline._inline.docPr.set('title',caption_text)
 cap=insert_after(pic);cap.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.paragraph_format.keep_together=True
 run=cap.add_run(caption_text);run.italic=True
 name='FPTOrg2026' if ix==1 else 'FPTAIOrg2026'
 start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(bookmark_id));start.set(qn('w:name'),name)
 end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(bookmark_id))
 cap._p.insert(1,start);cap._p.append(end)
 figure_bookmarks.append((caption_text,name))
 bookmark_id+=1
 last=cap
# Balance the two-page list and add figure entries cloned from the template's own TOF rows.
sdt=next(e for e in d.element.body if e.tag==qn('w:sdt') and any('Bảng' in (x.text or '') for x in e.iter(qn('w:instrText'))))
tof_paras=list(sdt.iter(qn('w:p')))
def ptext(el): return ''.join((x.text or '') for x in el.iter(qn('w:t')))
sample=next(p for p in tof_paras if ptext(p).startswith('Bảng 1.1.'))
split_row=next(p for p in tof_paras if ptext(p).startswith('Bảng 2.10.'))
ppr=split_row.find(qn('w:pPr'))
if ppr is None:
 ppr=OxmlElement('w:pPr');split_row.insert(0,ppr)
page_break=OxmlElement('w:pageBreakBefore');ppr.append(page_break)
fig_entries=[]
for caption,name in figure_bookmarks:
 p=deepcopy(sample)
 for child in list(p):
  if child.tag!=qn('w:pPr'):p.remove(child)
 link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),name);link.set(qn('w:history'),'1')
 run=OxmlElement('w:r');rpr=OxmlElement('w:rPr')
 for tag in ['w:i','w:iCs','w:noProof']:rpr.append(OxmlElement(tag))
 run.append(rpr);t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=caption.replace(' [11]','');run.append(t);link.append(run);p.append(link)
 tabrun=OxmlElement('w:r');tabrun.append(OxmlElement('w:tab'));p.append(tabrun)
 fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),f' PAGEREF {name} \\h ')
 page_run=OxmlElement('w:r');page_text=OxmlElement('w:t');page_text.text='3';page_run.append(page_text);fld.append(page_run);p.append(fld)
 fig_entries.append(p)
sdt.addnext(fig_entries[0]);fig_entries[0].addnext(fig_entries[1])
# Extend references with the supplied organization-chart source.
d.add_paragraph('11. FPT Smart Cloud. Sơ đồ tổ chức FPT Smart Cloud và Khối Sản phẩm AI năm 2026. Hình ảnh được cung cấp trong tài liệu thực tập của người viết.',style='Normal')
d.save(out)
v=Document(out)
assert len(v.inline_shapes)==2,len(v.inline_shapes)
assert all(any(p.text.strip()==cap for p in v.paragraphs) for cap,_ in figure_bookmarks)
assert all(any(p.text.startswith(prefix) for p in v.paragraphs) for prefix in ['11. FPT Smart Cloud.'])
assert any('ước tính doanh thu FPT Smart Cloud' in p.text for p in v.paragraphs)
assert any('cơ sở dữ liệu doanh nghiệp ước tính' in c.text for t in v.tables if t.cell(0,0).text.strip()=='Kỳ báo cáo' for row in t.rows for c in row.cells)
print('DOCX prepared: two organization charts, captions/bookmarks, figure-list entries, revised company text, reference 11.')
