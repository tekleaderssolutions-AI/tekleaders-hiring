import re

class SkillOntology:
    # 8.2 Alias Resolution Dictionary
    ALIASES = {
        "js": "javascript",
        "node": "nodejs",
        "node.js": "nodejs",
        "react.js": "react",
        "reactjs": "react",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "py": "python",
        "ts": "typescript",
        "k8s": "kubernetes",
        "sql server": "mssql",
        "postgres": "postgresql"
    }

    # 8.4 Skill Categorization
    CATEGORIES = {
        "frontend": ["react", "vue", "angular", "html", "css", "javascript", "typescript", "tailwind"],
        "backend": ["nodejs", "python", "java", "go", "golang", "ruby", "php", "c#", "dotnet"],
        "ml": ["pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "opencv"],
        "devops": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd", "github actions"],
        "data_engineering": ["spark", "hadoop", "airflow", "kafka", "etl", "snowflake", "databricks"]
    }

    # 8.5 Skill Relationships
    RELATIONSHIPS = {
        "tensorflow": ["keras", "pytorch", "deep learning"],
        "pytorch": ["tensorflow", "jax", "deep learning"],
        "react": ["nextjs", "redux", "frontend"],
        "nodejs": ["express", "backend", "javascript"],
        "aws": ["azure", "gcp", "cloud"]
    }

    @classmethod
    def normalize_skills(cls, raw_skills_data: list[dict]) -> list[dict]:
        """
        8.7 Final Skill Pipeline
        Accepts list of {name: str, importance: "must-have"|"preferred"}
        """
        if not raw_skills_data:
            return []

        processed_skills = []
        seen_canonical = set()

        for skill_entry in raw_skills_data:
            name = skill_entry.get("name", "")
            importance = skill_entry.get("importance", "preferred")
            
            # Clean & Lowercase
            skill_clean = name.strip().lower()
            
            # Alias Resolution
            canonical = cls.ALIASES.get(skill_clean, skill_clean)
            
            if canonical in seen_canonical:
                continue
            seen_canonical.add(canonical)
            
            # 8.6 Skill Weighting (HYBRID)
            # LLM detected importance + Backend numeric conversion
            weight = 0.9 if importance == "must-have" else 0.6
            
            # Category Tagging
            category = "general"
            for cat, skills in cls.CATEGORIES.items():
                if canonical in skills:
                    category = cat
                    break
            
            processed_skills.append({
                "name": canonical,
                "original": name,
                "category": category,
                "weight": weight,
                "related": cls.RELATIONSHIPS.get(canonical, [])
            })
            
        return processed_skills
