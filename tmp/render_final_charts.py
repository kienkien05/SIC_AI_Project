import fitz,json
d=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_refreshed.pdf")
hits=[]
for i,p in enumerate(d):
 t=p.get_text()
 if "Hình 1.1. Sơ đồ tổ chức FPT Smart Cloud năm 2026 [11]" in t:
  p.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save("tmp/final_org_chart_page.png")
  hits.append({"page":i+1,"text":t[:600]})
 if "Hình 1.1. Sơ đồ tổ chức FPT Smart Cloud năm 2026" in t and "Hình 1.2. Cơ cấu tổ chức Khối Sản phẩm AI năm 2026" in t and "[11]" not in t:
  p.get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(f"tmp/final_figure_list_{i+1}.png")
open(r"tmp/final_charts_check.json","w",encoding="utf-8").write(json.dumps({"pages":len(d),"chart_pages":hits},ensure_ascii=False,indent=2))
