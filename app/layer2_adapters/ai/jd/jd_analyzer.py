import os
import json
from openai import OpenAI
from app.config import settings

class JDAnalyzerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    def get_function_schema(self):
        return {
            "name": "extract_jd",
            "description": "Extract structured fields from a job description",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": ["string", "null"]},
                    "summary": {"type": ["string", "null"], "description": "A 150-800 character human-readable summary of the job."},
                    "team": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "employment_type": {"type": ["string", "null"]},
                    "experience": {
                        "type": ["object", "null"],
                        "properties": {
                            "min": {"type": ["integer", "null"]},
                            "max": {"type": ["integer", "null"]},
                            "units": {"type": ["string", "null"]}
                        }
                    },
                    "salary": {
                        "type": ["object", "null"],
                        "properties": {
                            "min": {"type": ["number", "null"]},
                            "max": {"type": ["number", "null"]},
                            "currency": {"type": ["string", "null"]}
                        }
                    },
                    "primary_skills": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "importance": {"type": "string", "enum": ["must-have", "preferred"]}
                            }
                        }
                    },
                    "secondary_skills": {"type": "array", "items": {"type": "string"}},
                    "responsibilities": {"type": "array", "items": {"type": "string"}},
                    "education": {"type": "array", "items": {"type": "string"}},
                    "nice_to_have": {"type": "array", "items": {"type": "string"}},
                    "domain": {"type": ["string", "null"], "description": "e.g. Fintech, Healthcare, E-commerce"},
                    "seniority_hints": {"type": "array", "items": {"type": "string"}, "description": "Keywords like Lead, Senior, Architect found in text"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                }
            }
        }

    async def extract_structured_jd(self, text: str) -> dict:
        """
        Step 5: LLM Extraction - OpenAI Function Calling
        """
        messages = [
            {"role": "system", "content": "You are a precise JD parsing assistant. Extract structured fields from the job description."},
            {"role": "user", "content": f"Extract structured fields from this job description:\n\n{text}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.get_function_schema()],
            function_call={"name": "extract_jd"},
            temperature=0.0
        )

        function_args = response.choices[0].message.function_call.arguments
        return json.loads(function_args)
