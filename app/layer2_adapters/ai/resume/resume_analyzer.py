import json
from openai import OpenAI
from app.config import settings

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
                    "candidate_name": {"type": "string", "description": "Full name of the candidate"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "current_title": {"type": "string", "description": "Current or most recent job title"},
                    "location": {"type": "string", "description": "Current location (city, state, country)"},
                    "total_experience_years": {"type": "number", "description": "Total years of professional experience"},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "List of technical skills"},
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "degree": {"type": "string"},
                                "institution": {"type": "string"},
                                "year": {"type": "string"}
                            }
                        },
                        "description": "Educational background"
                    },
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
                        },
                        "description": "Work experience history"
                    },
                    "certifications": {"type": "array", "items": {"type": "string"}, "description": "Professional certifications"},
                    "summary": {"type": "string", "description": "Professional summary or objective"}
                },
                "required": ["candidate_name"]
            }
        }

    async def analyze(self, text: str) -> dict:
        """
        Uses OpenAI to extract structured candidate data from raw resume text
        """
        messages = [
            {"role": "system", "content": "You are an expert recruitment assistant. Extract highly accurate structured data from the provided resume text. If a field is missing, return null."},
            {"role": "user", "content": f"Extract candidate info from this resume:\n\n{text}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.get_function_schema()],
            function_call={"name": "extract_resume"},
            temperature=0.0
        )

        function_args = response.choices[0].message.function_call.arguments
        return json.loads(function_args)
