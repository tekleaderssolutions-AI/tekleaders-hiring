from openai import OpenAI
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate vector embedding using OpenAI text-embedding-3-small
        """
        response = self.client.embeddings.create(
            input=[text],
            model=self.model
        )
        return response.data[0].embedding

    def build_embedding_text(self, jd_data: dict) -> str:
        """
        Rule: "{title} | {location} | skills: {primary_skills CSV} | experience: {min}-{max} | summary: {one-line summary}"
        """
        title = jd_data.get("role", "N/A")
        location = jd_data.get("location", "N/A")
        skills = ", ".join(jd_data.get("primary_skills", []))
        
        exp = jd_data.get("experience", {}) or {}
        exp_str = f"{exp.get('min', '0')}-{exp.get('max', 'any')}"
        
        summary = jd_data.get("summary", "")
        # Take the first line or first 200 chars for the 'one-line summary' part of the embedding
        one_line_summary = summary.split('\n')[0][:200]
        
        return f"{title} | {location} | skills: {skills} | experience: {exp_str} | summary: {one_line_summary}"
