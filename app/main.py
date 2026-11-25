import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db, SessionLocal, ForecastLog
from app.schemas import ForecastRequest, ForecastResponse
from app.agent import run_forecast

app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Evidence-grounded TCS quarterly financial outlook agent.")

@app.on_event("startup")
def startup():
    Path(settings.documents_dir).mkdir(parents=True, exist_ok=True)
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest):
    base = Path(settings.documents_dir)
    financial_files = sorted([str(p) for p in base.glob("*") if p.suffix.lower() in {".pdf", ".html", ".htm", ".txt"} and "transcript" not in p.name.lower()])
    transcript_files = sorted([str(p) for p in base.glob("*transcript*") if p.suffix.lower() in {".pdf", ".html", ".htm", ".txt"}])
    if not financial_files:
        raise HTTPException(status_code=400, detail=f"No financial documents found in {base}. Run scripts/fetch_documents.py.")
    if len(transcript_files) < 2:
        raise HTTPException(status_code=400, detail="Add at least two transcript files with 'transcript' in their filenames.")
    db = SessionLocal()
    try:
        output = run_forecast(request.task, financial_files, transcript_files, request.quarters)
        db.add(ForecastLog(request_text=request.model_dump_json(),
                           response_json=json.dumps(output, ensure_ascii=False), status="success"))
        db.commit()
        return JSONResponse(content=output)
    except Exception as exc:
        db.rollback()
        db.add(ForecastLog(request_text=request.model_dump_json(),
                           response_json=json.dumps({"error": str(exc)}), status="error"))
        db.commit()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()
