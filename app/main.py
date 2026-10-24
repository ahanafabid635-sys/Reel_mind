from fastapi import FastAPI
from app.models import AnalyzeRequest, AnalyzeResponse
from app.service import analyze_transcript

app = FastAPI(
    title="ReelMind API",
    description="Prototype API for user-controlled short-form content intelligence.",
    version="0.1.0",
)

@app.get("/health")
def health():
    return {"status": "ok", "project": "ReelMind", "version": "0.1.0"}

@app.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a user-provided transcript. Prototype only; not a truth detector."""
    return analyze_transcript(request)
