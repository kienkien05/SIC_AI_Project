import fitz,json
d=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_final.pdf")
res=[]
for i,p in enumerate(d):
 t=p.get_text()
 if any(k in t for k in ["Hình 1.1","Hình 1.2","Bảng 1.2","MỤC LỤC","DANH MỤC CÁC BẢNG"]):res.append({"page":i+1,"text":t[:3000]})
open("tmp/pdf_page_hits.json","w",encoding="utf-8").write(json.dumps({"pages":len(d),"hits":res},ensure_ascii=False,indent=2))
for i,p in enumerate(d):
 t=p.get_text()
 if "Hình 1.1" in t or "Hình 1.2" in t:p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(f"tmp/orgchart_page_{i+1}.png")
