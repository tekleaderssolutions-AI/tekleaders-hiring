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
            "description": "Extract structured fields, strategic weights, and functional cluster from a job description",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": ["string", "null"]},
                    "job_cluster": {
                        "type": "string", 
                        "enum": ["engineering", "management", "data_science", "marketing", "sales", "hr", "finance", "legal", "customer_service", "other"],
                        "description": "The functional category this job belongs to."
                    },
                    "experience": {
                        "type": ["object", "null"],
                        "properties": {
                            "min": {"type": ["integer", "null"]},
                            "max": {"type": ["integer", "null"]},
                        },
                    },
                    "primary_skills": {"type": "array", "items": {"type": "string"}},
                    "scoring_weights": {
                        "type": "object",
                        "properties": {
                            "semantic_weight": {"type": "number"},
                            "skills_weight": {"type": "number"},
                            "experience_multiplier": {"type": "number"}
                        }
                    },
                    "summary": {"type": "string"}
                },
                "required": ["role", "job_cluster", "scoring_weights"]
            },
        }

    async def extract_structured_jd(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": """You are an Elite Recruitment Strategist. 
            Analyze the JD and categorize it into one of the following functional clusters:
            engineering, management, data_science, marketing, sales, hr, finance, legal, customer_service.
            Also define the scoring plan."""},
            {"role": "user", "content": f"Analyze this JD:\n\n{text}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.get_function_schema()],
            function_call={"name": "extract_jd"},
            temperature=0.0
        )

        return json.loads(response.choices[0].message.function_call.arguments)
