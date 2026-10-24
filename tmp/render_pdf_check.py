import fitz
d=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_final.pdf")
for n in [9,10]:d[n-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(f"tmp/pdf_check_{n}.png")
