from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    code = body.get("code", "")
    language = body.get("language", "python")
    
    try:
        is_ai, explanation = analyze_code(code, language)
        return {"isAI": is_ai, "explanation": explanation}
    except Exception as e:
        return {"error": str(e)}
