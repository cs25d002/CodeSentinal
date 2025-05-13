from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from parser import ASTParser
from analyzer import CodeAnalyzer
import sqlite3
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
parser = ASTParser()
analyzer = CodeAnalyzer()

# SQLite DB
conn = sqlite3.connect('activity.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS edits (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        content   TEXT,
        language  TEXT,
        is_ai     BOOLEAN
    )
''')
conn.commit()

class AnalysisRequest(BaseModel):
    code: Optional[str] = None
    lines: Optional[List[str]] = None
    language: str

@app.post("/analyze")
async def analyze_code(request: AnalysisRequest):
    try:
        logging.info("\ud83d\ude80 /analyze endpoint triggered")
        logging.info(f"Language received: {request.language}")
        logging.info(f"Received lines: {len(request.lines) if request.lines else 'None'}")

        # Prepare content
        if request.lines:
            content = "\n".join(request.lines)
        elif request.code:
            content = request.code
        else:
            return {"error": "Either 'code' or 'lines' must be provided."}

        logging.info("\u2705 Code content prepared")

        # Parse (AST)
        try:
            ast_tree = parser.parse(content, request.language)
            logging.info("\u2705 AST parsed successfully")
        except Exception as e:
            logging.warning(f"\u26a0\ufe0f AST parse failed: {e}")
            ast_tree = None

        # Analyze overall
        result = analyzer.analyze(content, ast_tree)
        logging.info(f"\u2705 Analyzer complete, isAI: {result.get('isAI')}, Probability: {result.get('probability'):.2f}")

        # Log into DB
        is_ai = bool(result.get("isAI", False))
        cursor.execute(
            "INSERT INTO edits (timestamp, content, language, is_ai) VALUES (?, ?, ?, ?)",
            (int(time.time()), content, request.language, is_ai)
        )
        conn.commit()
        logging.info("\ud83d\udcc5 Logged analysis into SQLite")

        # Line-level analysis
        if request.lines:
            logging.info("\ud83d\udcca Starting per-line analysis")
            line_scores = []
            for idx, line in enumerate(request.lines):
                try:
                    sub_ast = parser.parse(line, request.language)
                except Exception:
                    sub_ast = None
                sub_result = analyzer.analyze(line, sub_ast)
                prob = sub_result.get("probability", 1.0 if sub_result.get("isAI") else 0.0)
                logging.debug(f"Line {idx + 1}: Prob = {prob:.2f}")
                line_scores.append(prob)
            result["line_scores"] = line_scores

        return result

    except Exception as e:
        logging.error("\u274c Exception during analysis", exc_info=True)
        return {"error": f"Analysis failed: {str(e)}"}
