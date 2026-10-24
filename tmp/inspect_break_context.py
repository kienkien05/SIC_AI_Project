from docx import Document
from docx.oxml.ns import qn
import json
d=Document(r"deliverables/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.docx")
p=d.paragraphs
out=[]
for i,x in enumerate(p):
 ppr=x._p.find(qn("w:pPr"))
 breaks=[b for b in x._p.iter(qn("w:br")) if b.get(qn("w:type"))=="page"]
 pb=ppr is not None and ppr.find(qn("w:pageBreakBefore")) is not None
 sect=ppr is not None and ppr.find(qn("w:sectPr")) is not None
 if breaks or pb or sect:
  prev=next((p[j].text.strip() for j in range(i-1,-1,-1) if p[j].text.strip()),"")
  nxt=next((p[j].text.strip() for j in range(i+1,len(p)) if p[j].text.strip()),"")
  out.append({"index":i,"text":x.text.strip(),"pageBreak":len(breaks),"pageBefore":bool(pb),"sectionBreak":bool(sect),"previous":prev[:100],"next":nxt[:100]})
open(r"tmp/break_context.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=2))
