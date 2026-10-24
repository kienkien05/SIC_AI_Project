import fitz
d=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_refreshed.pdf")
checks=[("Nhóm hoạt động","Điện toán đám mây","table_final_1.png"),("Nội dung cần thống nhất","Định nghĩa lớp","table_final_2.png"),("Thông số","Giải thích đơn giản","table_final_3.png"),("Bước","Người/Thành phần","table_final_4.png")]
for a,b,name in checks:
 for i,p in enumerate(d):
  t=p.get_text()
  if a in t and b in t and "Bảng " in t and "Hình " not in t:
   p.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save("tmp/"+name)
   break
