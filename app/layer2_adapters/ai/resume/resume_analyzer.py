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
            "description": "Extract structured candidate information from a resume",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "current_title": {"type": "string"},
                    "location": {"type": "string"},
                    "total_experience_years": {"type": "number"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "work_experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "company": {"type": "string"},
                                "duration": {"type": "string"},
                                "responsibilities": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "summary": {"type": "string"}
                },
                "required": ["candidate_name"]
            }
        }

    @ai_retry(max_retries=3)
    async def analyze(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": "You are an expert recruitment assistant. Extract highly accurate structured data."},
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
        """
        ELITE RERANKER: Performs a deep-dive comparison between JD and Resume.
        Looks for depth of experience, leadership, and cultural alignment.
        """
        messages = [
            {"role": "system", "content": """You are an Elite Technical Recruiter. 
            Analyze the fit between the Job Description and the Candidate Resume. 
            Look past keywords; evaluate the depth of impact, seniority, and project complexity.
            Return a JSON object with:
            - relevance_score: float (0.0 to 1.0)
            - reasoning: string (detailed explanation of the score)
            - critical_gaps: list (what is missing?)
            - top_strengths: list (why they are a great fit?)"""},
            {"role": "user", "content": f"JOB DESCRIPTION:\n{jd_text}\n\nCANDIDATE RESUME:\n{resume_text}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
