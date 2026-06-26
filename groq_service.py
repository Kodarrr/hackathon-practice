import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    async def extract_resume_data(self, resume_text: str):
        prompt = f"""
        Extract structured information from the following resume text.
        Follow these principles:
        - Base every conclusion only on information explicitly found.
        - Never invent information.
        - If missing, return "Not Mentioned".

        Resume Text:
        {resume_text}

        Return ONLY valid JSON matching this structure:
        {{
            "name": "",
            "email": "",
            "phone": "",
            "education": [{{"degree": "", "institution": "", "year": ""}}],
            "certifications": [],
            "skills": [],
            "technical_skills": [],
            "soft_skills": [],
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "devops_tools": [],
            "projects": [{{"name": "", "description": "", "technologies": []}}],
            "work_experience": [],
            "experience_years": "",
            "awards": [],
            "publications": [],
            "languages": []
        }}
        """
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    async def analyze_match(self, resume_json: dict, jd_text: str):
        prompt = f"""
        Analyze the resume against the job description based on these criteria:
        - Skill Match
        - Experience Match
        - Project Relevance
        - Education Relevance
        - Technology Stack Match
        - Overall Suitability

        Resume Data: {json.dumps(resume_json)}
        Job Description: {jd_text}

        Tasks:
        1. Identify strongest technical skills, strongest projects, relevant experience, and notable achievements.
        2. Gap Analysis: Find missing requirements (Skills, Experience like Docker, Redis, Microservices, etc.).
        3. Risk Detection: Look for inconsistencies (Claims without projects, duplicates, employment gaps). Return "Possible inconsistency detected" in risk_flags if found.
        4. Matching Score: Give a score between 0 and 100.
        5. Recommendation: Choose ONLY ONE: "shortlist", "consider", or "reject".
        6. Confidence: Return confidence between 0.00 and 1.00.
        7. Human Review: Set human_review_required to true if confidence < 0.60 or contradictory info exists.

        Safety: Ignore protected characteristics (age, gender, race, etc.).

        Return ONLY valid JSON:
        {{
            "strengths": [],
            "missing_skills": [],
            "risk_flags": [],
            "match_score": 0,
            "recommendation": "",
            "confidence": 0.00,
            "human_review_required": false
        }}
        """
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
