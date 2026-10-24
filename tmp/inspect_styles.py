from docx import Document
import json
d=Document(r"deliverables/Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.docx")
styles=[]
for name in ["Normal","DoanVB","Caption","Table of Figures","TableofFigures","Heading 1","Heading 2"]:
 try:
  s=d.styles[name];styles.append({"name":name,"font":s.font.name,"size":s.font.size.pt if s.font.size else None,"bold":s.font.bold,"italic":s.font.italic,"alignment":str(s.paragraph_format.alignment),"line_spacing":str(s.paragraph_format.line_spacing),"space_after":str(s.paragraph_format.space_after)})
 except KeyError: pass
def rinfo(p):
 return {"style":p.style.name,"align":str(p.alignment),"runs":[{"text":r.text[:60],"font":r.font.name,"size":r.font.size.pt if r.font.size else None,"bold":r.bold,"italic":r.italic} for r in p.runs if r.text.strip()][:2]}
samples={}
for i,p in enumerate(d.paragraphs):
 if p.text.startswith(("FPT Smart Cloud thuộc","PHẦN I.","CHƯƠNG 1.","Bảng 1.1.")):samples[p.text[:40]]=rinfo(p)
out={"styles":styles,"paragraph_samples":samples}
open(r"tmp/styles_info.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=2))
