import fitz,json,re
pdf=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_refreshed.pdf")
targets=["PHẦN I. KHÁI QUÁT VỀ ĐƠN VỊ THỰC TẬP","PHẦN II. GÁN NHÃN DỮ LIỆU VÀ TINH CHỈNH MÔ HÌNH YOLO","CHƯƠNG 1. CƠ SỞ LÝ THUYẾT","CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ QUY TRÌNH","CHƯƠNG 3. THỰC HIỆN GÁN NHÃN VÀ TINH CHỈNH MÔ HÌNH","CHƯƠNG 4. KẾT QUẢ, KIỂM THỬ VÀ ĐÁNH GIÁ","PHẦN III. NHẬN XÉT VÀ ĐỀ XUẤT"]
hits=[]
for i,p in enumerate(pdf):
 t=p.get_text()
 for target in targets:
  if target in t:
   r=p.search_for(target)
   hits.append({"heading":target,"pdfPage":i+1,"y":round(r[0].y0,1) if r else None,"pageTextStart":t[:1400]})
for key in ["Bảng 1.1.","Bảng 1.2.","Bảng 2.1.","Hình 1.1.","Hình 1.2."]:
 for i,p in enumerate(pdf):
  t=p.get_text()
  if key in t:
   p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(f"tmp/final_layout_{re.sub(r'[^a-zA-Z0-9]','_',key)}_page_{i+1}.png")
   break
open(r"tmp/final_layout_check.json","w",encoding="utf-8").write(json.dumps({"pages":len(pdf),"hits":hits},ensure_ascii=False,indent=2))
