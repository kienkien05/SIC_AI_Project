from docx import Document
from docx.oxml.ns import qn
d=Document(r"deliverables/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.docx")
sdt=next(e for e in d.element.body if e.tag==qn("w:sdt") and any("Bảng" in (x.text or "") for x in e.iter(qn("w:instrText"))))
arr=[]
for p in sdt.iter(qn("w:p")):
 t="".join(x.text or "" for x in p.iter(qn("w:t")))
 if t.startswith("Bảng 1.1") or t.startswith("Bảng 2.10"):
  arr.append({"text":t,"xml":p.xml})
open("tmp/figure_row_samples.json","w",encoding="utf-8").write(__import__("json").dumps(arr,ensure_ascii=False,indent=2))
