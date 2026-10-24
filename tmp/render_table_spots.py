import fitz
d=fitz.open(r"deliverables/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.pdf")
for n in [12,13,19,20,24,25,30,31,32]:
 if n<=len(d): d[n-1].get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(f"tmp/table_spot_{n}.png")
