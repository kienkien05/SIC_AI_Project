import fitz,json
p=fitz.open(r"C:/Users/dangv/Downloads/Hướng Dẫn Định Dạng Tài Liệu KLTN_ Sửa Style và Thiết Lập Trang - Studocu.pdf")
out={str(i+1):p[i].get_text() for i in [1,2,11,12,13] if i<len(p)}
open(r"tmp/guide_table_pages.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=2))
