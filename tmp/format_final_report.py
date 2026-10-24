from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from pathlib import Path
import re,sys,json
src=Path(sys.argv[1]);out=Path(sys.argv[2])
doc=Document(src)
removed_chapter_breaks=[]
paras=doc.paragraphs
for i,p in enumerate(paras):
 if p.text.strip():
  continue
 has_page=any(b.get(qn("w:type"))=="page" for b in p._p.iter(qn("w:br")))
 if not has_page:
  continue
 next_heading=next((q.text.strip() for q in paras[i+1:] if q.text.strip()),"")
 if next_heading.startswith("CHƯƠNG "):
  parent=p._p.getparent()
  parent.remove(p._p)
  removed_chapter_breaks.append(next_heading)
for p in doc.paragraphs:
 if p.text.strip().startswith("CHƯƠNG "):
  p.paragraph_format.page_break_before=False
meta="Phần II trình bày kiến thức và quy trình gắn với hai nhiệm vụ này, tập trung vào cách thực hiện và bài học chuyên môn."
removed_meta=0
for p in list(doc.paragraphs):
 if p.text.strip()==meta:
  p._p.getparent().remove(p._p)
  removed_meta+=1
# Apply the supplied formatting guide consistently: TNR 13, 1.2 spacing,
# centered bold blue headers, readable body alignment, and repeated header rows.
def set_font(run, bold=None):
 run.font.name="Times New Roman"
 run.font.size=Pt(13)
 rpr=run._element.get_or_add_rPr()
 fonts=rpr.rFonts
 if fonts is None:
  fonts=OxmlElement("w:rFonts");rpr.insert(0,fonts)
 for key in ["w:ascii","w:hAnsi","w:eastAsia","w:cs"]:
  fonts.set(qn(key),"Times New Roman")
 if bold is not None:run.bold=bold
def set_shading(cell,fill="DCE6F1"):
 tcpr=cell._tc.get_or_add_tcPr()
 shd=tcpr.find(qn("w:shd"))
 if shd is None:shd=OxmlElement("w:shd");tcpr.append(shd)
 shd.set(qn("w:fill"),fill);shd.set(qn("w:val"),"clear")
def set_vertical_center(cell):
 tcpr=cell._tc.get_or_add_tcPr()
 valign=tcpr.find(qn("w:vAlign"))
 if valign is None:valign=OxmlElement("w:vAlign");tcpr.append(valign)
 valign.set(qn("w:val"),"center")
numeric=re.compile(r"^[0-9\s.,%+\-–−]+$")
for table in doc.tables:
 table.alignment=WD_TABLE_ALIGNMENT.CENTER
 if table.rows:
  trpr=table.rows[0]._tr.get_or_add_trPr()
  if trpr.find(qn("w:tblHeader")) is None:
   repeat=OxmlElement("w:tblHeader");repeat.set(qn("w:val"),"true");trpr.append(repeat)
  for cell in table.rows[0].cells:set_shading(cell)
 for ri,row in enumerate(table.rows):
  header=(ri==0)
  for cell in row.cells:
   set_vertical_center(cell)
   text=cell.text.strip()
   for p in cell.paragraphs:
    p.paragraph_format.space_before=Pt(6)
    p.paragraph_format.space_after=Pt(6)
    p.paragraph_format.line_spacing=1.2
    if header:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    else:p.alignment=WD_ALIGN_PARAGRAPH.RIGHT if text and numeric.fullmatch(text) else WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:set_font(run,bold=True if header else False)
doc.save(out)
# Validate structural changes and table formatting before returning success.
check=Document(out)
chapter_breaks=[]
for i,p in enumerate(check.paragraphs):
 if not p.text.strip() and any(b.get(qn("w:type"))=="page" for b in p._p.iter(qn("w:br"))):
  nxt=next((q.text.strip() for q in check.paragraphs[i+1:] if q.text.strip()),"")
  if nxt.startswith("CHƯƠNG "):chapter_breaks.append(nxt)
figs=[p for p in check.paragraphs if p.text.strip().startswith(("Hình 1.1. Sơ đồ tổ chức","Hình 1.2. Cơ cấu tổ chức"))]
result={"tables":len(check.tables),"inline_images":len(check.inline_shapes),"removed_chapter_breaks":removed_chapter_breaks,"remaining_chapter_breaks":chapter_breaks,"removed_meta_paragraphs":removed_meta,"figure_captions":len(figs)}
assert len(check.tables)==26,result
assert len(removed_chapter_breaks)==4,result
assert not chapter_breaks,result
assert removed_meta==1,result
assert len(check.inline_shapes)==2,result
open(str(out.with_suffix(".validation.json")),"w",encoding="utf-8").write(json.dumps(result,ensure_ascii=False,indent=2))
print("Applied and validated report layout and table formatting.")
