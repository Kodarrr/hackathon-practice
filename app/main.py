from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal
import re

app = FastAPI(title="Hackathon Practice API")


# ---------------------------
# Request / Response Schemas
# ---------------------------

class ATSRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    job_description: str = Field(..., min_length=1)


class ATSResponse(BaseModel):
    name: str
    email: str
    phone: str
    education: List[str]
    experience_years: str
    skills: List[str]
    projects: List[str]
    strengths: List[str]
    missing_skills: List[str]
    risk_flags: List[str]
    match_score: int
    recommendation: Literal["shortlist", "consider", "reject"]
    human_review_required: bool
    confidence: float


# ---------------------------
# Helpers (simple deterministic parsing)
# ---------------------------

TECH_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "fastapi", "django", "flask", "react", "node", "spring", "tensorflow",
    "pytorch", "pandas", "numpy", "sql", "postgresql", "mysql", "mongodb",
    "redis", "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
    "ci/cd", "jenkins", "github actions"
]

SOFT_KEYWORDS = [
    "communication", "leadership", "collaboration", "teamwork",
    "problem solving", "time management", "adaptability"
]


def find_email(text: str) -> str:
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else "Not Mentioned"


def find_phone(text: str) -> str:
    m = re.search(r"(\+?\d[\d\-\s]{8,}\d)", text)
    return m.group(0).strip() if m else "Not Mentioned"


def infer_name(text: str) -> str:
    # very light heuristic: first non-empty line without common headings
    headings = {"resume", "curriculum vitae", "profile", "summary", "education", "experience"}
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.lower() in headings:
            continue
        # avoid email/phone as name
        if "@" in clean or re.search(r"\d{3,}", clean):
            continue
        if len(clean.split()) <= 5:
            return clean
    return "Not Mentioned"


def extract_mentions(text: str, keywords: List[str]) -> List[str]:
    lower = text.lower()
    found = []
    for k in keywords:
        if k in lower:
            found.append(k)
    return sorted(set(found))


def split_lines_if_contains(text: str, markers: List[str]) -> List[str]:
    out = []
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        ll = l.lower()
        if any(m in ll for m in markers):
            out.append(l)
    return out


def estimate_experience_years(text: str) -> str:
    # look for patterns like "3 years", "5+ years"
    matches = re.findall(r"(\d+)\s*\+?\s*years?", text.lower())
    if not matches:
        return "Not Mentioned"
    nums = [int(x) for x in matches]
    return str(max(nums))


def calc_match_score(resume_skills: List[str], jd_skills: List[str], risk_flags_count: int) -> int:
    if not jd_skills:
        base = 50
    else:
        overlap = len(set(resume_skills).intersection(set(jd_skills)))
        base = int((overlap / max(len(set(jd_skills)), 1)) * 100)

    penalty = min(risk_flags_count * 5, 20)
    score = max(0, min(100, base - penalty))
    return score


def pick_recommendation(score: int) -> Literal["shortlist", "consider", "reject"]:
    if score >= 75:
        return "shortlist"
    if score >= 45:
        return "consider"
    return "reject"


# ---------------------------
# Routes
# ---------------------------

@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/ats/screen", response_model=ATSResponse)
def ats_screen(payload: ATSRequest):
    resume = payload.resume_text
    jd = payload.job_description

    name = infer_name(resume)
    email = find_email(resume)
    phone = find_phone(resume)

    tech_skills = extract_mentions(resume, TECH_KEYWORDS)
    soft_skills = extract_mentions(resume, SOFT_KEYWORDS)
    all_skills = sorted(set(tech_skills + soft_skills))

    jd_skills = extract_mentions(jd, TECH_KEYWORDS + SOFT_KEYWORDS)

    education = split_lines_if_contains(resume, ["b.tech", "b.e", "bsc", "b.s", "m.tech", "m.e", "msc", "phd", "university", "college"])
    projects = split_lines_if_contains(resume, ["project", "built", "developed", "implemented"])

    strengths = []
    if tech_skills:
        strengths.append(f"Technical skills found: {', '.join(tech_skills[:8])}")
    if projects:
        strengths.append("Project evidence present in resume")
    if estimate_experience_years(resume) != "Not Mentioned":
        strengths.append(f"Experience mentioned: {estimate_experience_years(resume)} years")

    missing_skills = sorted(set(jd_skills) - set(all_skills))

    risk_flags = []
    if email == "Not Mentioned":
        risk_flags.append("Possible inconsistency detected: Missing contact email.")
    if phone == "Not Mentioned":
        risk_flags.append("Possible inconsistency detected: Missing phone number.")
    if not projects:
        risk_flags.append("Possible inconsistency detected: Experience claims may lack supporting project evidence.")
    if not education:
        risk_flags.append("Possible inconsistency detected: Education details not clearly mentioned.")

    match_score = calc_match_score(all_skills, jd_skills, len(risk_flags))
    recommendation = pick_recommendation(match_score)

    # Confidence heuristic
    confidence = 0.85
    if len(risk_flags) >= 2:
        confidence -= 0.2
    if not jd_skills:
        confidence -= 0.1
    confidence = max(0.0, min(1.0, round(confidence, 2)))

    human_review_required = bool(confidence < 0.60 or len(risk_flags) > 0)

    return ATSResponse(
        name=name if name else "Not Mentioned",
        email=email,
        phone=phone,
        education=education if education else ["Not Mentioned"],
        experience_years=estimate_experience_years(resume),
        skills=all_skills if all_skills else ["Not Mentioned"],
        projects=projects if projects else ["Not Mentioned"],
        strengths=strengths if strengths else ["Not Mentioned"],
        missing_skills=missing_skills if missing_skills else [],
        risk_flags=risk_flags if risk_flags else [],
        match_score=match_score,
        recommendation=recommendation,
        human_review_required=human_review_required,
        confidence=confidence,
    )