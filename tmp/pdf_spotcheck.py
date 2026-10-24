import fitz,json
d=fitz.open(r"tmp/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO_final.pdf")
idx=[3,10,11,12,13,14,15,16,17,18]
out=[{"page":i+1,"text":d[i].get_text()[:2200]} for i in idx if i<len(d)]
open("tmp/pdf_spotcheck.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=2))
