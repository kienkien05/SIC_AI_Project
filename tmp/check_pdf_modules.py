import importlib.util,json
mods={m:bool(importlib.util.find_spec(m)) for m in ["fitz","pypdf","PIL"]}
open("tmp/pdf_modules.json","w",encoding="utf-8").write(json.dumps(mods))
