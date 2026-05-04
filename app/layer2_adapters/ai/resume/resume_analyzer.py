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
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "location": {"type": "string"},
                    "summary": {"type": "string", "description": "A brief 2-3 sentence professional summary"},
                    "total_years_experience": {"type": "number"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "company": {"type": "string"},
                                "role": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "description": {"type": "string"},
                                "is_current": {"type": "boolean"}
                            }
                        }
                    },
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "institution": {"type": "string"},
                                "degree": {"type": "string"},
                                "field_of_study": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["first_name", "last_name", "email", "skills"]
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
