# app/parser.py
from comex import Comex
import tempfile
import os

comex = Comex(language="python")

def extract_dfg(code: str):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    views = comex.generate_codeviews(tmp_path)
    os.unlink(tmp_path)
    return views.get("dfg", [])
q