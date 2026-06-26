from fastapi import FastAPI
from pydantic import BaseModel


from fastapi import  UploadFile, File, Form, HTTPException
from groq_service import GroqService
from parser import extract_text_from_pdf
from schemas import AnalysisResult
import json

app = FastAPI(title="hackathon-practice")

groq_service = GroqService()


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    return EchoResponse(message=payload.message)

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...)
):
    try:
        # Step 1: Extract text from Resume
        if resume.content_type == "application/pdf":
            resume_content = await resume.read()
            resume_text = extract_text_from_pdf(resume_content)
        else:
            resume_text = (await resume.read()).decode("utf-8")

        # Step 2: Extract structured info from Resume
        resume_data = await groq_service.extract_resume_data(resume_text)

        # Step 3: Match and Analysis
        analysis = await groq_service.analyze_match(resume_data, jd)

        # Merge data for final output
        final_result = {
            "name": resume_data.get("name", "Not Mentioned"),
            "email": resume_data.get("email", "Not Mentioned"),
            "phone": resume_data.get("phone", "Not Mentioned"),
            "education": resume_data.get("education", []),
            "experience_years": resume_data.get("experience_years", "Not Mentioned"),
            "skills": resume_data.get("skills", []),
            "projects": resume_data.get("projects", []),
            "strengths": analysis.get("strengths", []),
            "missing_skills": analysis.get("missing_skills", []),
            "risk_flags": analysis.get("risk_flags", []),
            "match_score": analysis.get("match_score", 0),
            "recommendation": analysis.get("recommendation", "reject"),
            "human_review_required": analysis.get("human_review_required", False),
            "confidence": analysis.get("confidence", 0.0)
        }

        return final_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)