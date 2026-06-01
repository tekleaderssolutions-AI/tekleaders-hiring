import json
from openai import AsyncOpenAI
from app.config import settings
from app.layer7_crosscutting.ai.resilience import ai_retry

class ResumeAnalyzerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    def get_function_schema(self):
        return {
            "name": "extract_resume",
            "description": (
                "Extract professional information from a resume. "
                "Contact details (name, email, phone) have already been redacted — "
                "focus only on title, skills, experience, and functional cluster."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "current_title": {"type": "string"},
                    "job_cluster": {
                        "type": "string",
                        "enum": ["engineering", "management", "data_science", "marketing", "sales", "hr", "finance", "legal", "customer_service", "other"],
                        "description": "The functional category this candidate's experience belongs to."
                    },
                    "total_experience_years": {"type": "number"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "summary": {"type": "string"},
                    "work_experience": {
                        "type": "array",
                        "description": "Each job held by the candidate, in reverse chronological order.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title":       {"type": "string", "description": "Job title held"},
                                "company":     {"type": "string"},
                                "start_date":  {"type": "string", "description": "e.g. 'Jan 2018' or '2018'"},
                                "end_date":    {"type": "string", "description": "e.g. 'Mar 2022' or 'Present'"},
                                "skills_used": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "ONLY technologies, tools, languages explicitly mentioned for THIS role. Do not infer."
                                },
                                "domain": {
                                    "type": "string",
                                    "description": "Primary technical domain for this role, e.g. 'ETL/Data Integration', 'Web Development', 'Cloud Infrastructure', 'Data Analytics'"
                                }
                            },
                            "required": ["title", "start_date", "end_date", "skills_used"]
                        }
                    }
                },
                "required": ["job_cluster"]
            }
        }

    @ai_retry(max_retries=3)
    async def analyze(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": (
                "You are an expert recruiter. The resume text has been anonymised — "
                "personal contact details are redacted.\n\n"
                "Extract professional information with these CRITICAL RULES:\n"
                "1. work_experience: Extract EVERY job listed. For each job, extract skills_used "
                "from ONLY what is explicitly mentioned for that specific role — do NOT carry skills "
                "across roles or infer. This is critical for computing domain-specific experience.\n"
                "2. skills: the complete union of all skills across all roles.\n"
                "3. total_experience_years: sum of all role durations. If unclear, estimate from dates.\n"
                "4. domain: classify each role's primary technical focus area."
            )},
            {"role": "user", "content": f"Extract candidate info:\n\n{text}"}
        ]
        response = await self.client.chat.completions.create(
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

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
