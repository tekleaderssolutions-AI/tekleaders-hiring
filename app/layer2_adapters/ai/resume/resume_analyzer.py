import json
from openai import OpenAI
from app.config import settings
from app.layer7_crosscutting.ai.resilience import ai_retry

class ResumeAnalyzerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    def get_function_schema(self):
        return {
            "name": "extract_resume",
            "description": "Extract structured candidate information and functional cluster from a resume",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "email": {"type": "string"},
                    "current_title": {"type": "string"},
                    "job_cluster": {
                        "type": "string", 
                        "enum": ["engineering", "management", "data_science", "marketing", "sales", "hr", "finance", "legal", "customer_service", "other"],
                        "description": "The functional category this candidate's experience belongs to."
                    },
                    "total_experience_years": {"type": "number"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "summary": {"type": "string"}
                },
                "required": ["candidate_name", "job_cluster"]
            }
        }

    @ai_retry(max_retries=3)
    async def analyze(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": "You are an expert recruiter. Extract data and categorize the candidate into a functional cluster (engineering, sales, etc)."},
            {"role": "user", "content": f"Extract candidate info:\n\n{text}"}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.get_function_schema()],
            function_call={"name": "extract_resume"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.function_call.arguments)

    @ai_retry(max_retries=3)
    async def evaluate_match(self, jd_text: str, resume_text: str) -> dict:
        messages = [
            {"role": "system", "content": """You are an Elite Technical Recruiter. 
            Analyze the fit between the Job Description and the Candidate Resume. 
            Return a JSON object with: relevance_score, reasoning, critical_gaps, top_strengths."""},
            {"role": "user", "content": f"JOB DESCRIPTION:\n{jd_text}\n\nCANDIDATE RESUME:\n{resume_text}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
