import os
import json
from openai import AsyncOpenAI
from app.config import settings

class JDAnalyzerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL

    def get_function_schema(self):
        return {
            "name": "extract_jd",
            "description": "Extract structured fields and functional cluster from a job description",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": ["string", "null"]},
                    "job_cluster": {
                        "type": "string",
                        "enum": ["engineering", "management", "data_science", "marketing", "sales", "hr", "finance", "legal", "customer_service", "other"],
                        "description": "The functional category this job belongs to."
                    },
                    "experience_level": {
                        "type": "string",
                        "enum": ["entry", "mid", "senior", "lead", "executive"],
                        "description": "Seniority level of the role."
                    },
                    "experience": {
                        "type": ["object", "null"],
                        "properties": {
                            "min": {"type": ["integer", "null"], "description": "Minimum years of experience required"},
                            "max": {"type": ["integer", "null"], "description": "Maximum years mentioned"},
                        },
                    },
                    "must_have_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Skills explicitly marked as required/mandatory/must-have in the JD. ONLY include skills literally written in the JD text."
                    },
                    "nice_to_have_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Skills marked as preferred/good-to-have/plus in the JD. ONLY include skills literally written in the JD text."
                    },
                    "must_have_skill_weights": {
                        "type": "object",
                        "description": "Map of must-have skill name → relative importance (1.0=primary/core technology, 0.7=standard requirement, 0.5=supporting skill). Only include skills from must_have_skills. Reflects how prominently each skill is emphasized in the JD.",
                        "additionalProperties": {"type": "number"}
                    },
                    "summary": {"type": "string", "description": "2-3 sentence summary of the role"},
                    "scoring_weights": {
                        "type": "object",
                        "properties": {
                            "semantic_weight":        {"type": "number"},
                            "skills_weight":          {"type": "number"},
                            "experience_multiplier":  {"type": "number"}
                        }
                    },
                },
                "required": ["role", "job_cluster", "scoring_weights"]
            },
        }

    async def extract_structured_jd(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": """You are an Elite Recruitment Strategist analyzing a Job Description.

CRITICAL RULES — read carefully:

1. must_have_skills: Extract ONLY skills/tools/technologies that are explicitly stated as REQUIRED, MANDATORY, or MUST HAVE in the JD text.
   - Use the JD's own language: words like "required", "must have", "essential", "mandatory" signal must-have.
   - If the JD lists skills without qualification, treat them as must-have.
   - DO NOT infer or add skills not literally written. If JD says "Python", do not add "Java".
   - Limit to top 6 most specific must-have skills.

2. nice_to_have_skills: Extract ONLY skills explicitly marked as "preferred", "nice to have", "good to have", "plus", "bonus", or "advantageous".
   - Leave empty if JD has no preferred section.

3. experience.min: Extract the TOTAL OVERALL years of professional experience required (e.g. "10+ years of experience" → min=10).
   - Use the highest/overall number, NOT years for a specific technology.
   - If JD says "10+ years overall with 3+ years SSIS", set min=10.
   - Do NOT guess if no total experience is stated.

4. experience_level: Infer from job title and responsibilities (entry/mid/senior/lead/executive).

5. job_cluster: Categorize into the most accurate functional cluster.

6. must_have_skill_weights: For each must-have skill, assign importance:
   - 1.0: Primary/core technology explicitly called out as the focus of the role
   - 0.7: Standard requirement listed without special emphasis
   - 0.5: Supporting or secondary required skill
   Use the exact skill name as it appears in must_have_skills.

Be conservative — it is better to extract fewer accurate skills than many inaccurate ones."""},
            {"role": "user", "content": f"Analyze this JD:\n\n{text}"}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.get_function_schema()],
            function_call={"name": "extract_jd"},
            temperature=0.0
        )

        return json.loads(response.choices[0].message.function_call.arguments)
