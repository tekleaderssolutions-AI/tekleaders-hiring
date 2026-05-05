import re


class SkillOntology:
    # Step 11: Alias Resolution Dictionary
    ALIASES = {
        # JavaScript ecosystem
        "js": "javascript", "javascript": "javascript",
        "ts": "typescript", "typescript": "typescript",
        "node": "nodejs", "node.js": "nodejs", "nodejs": "nodejs",
        "react.js": "react", "reactjs": "react", "react": "react",
        "vue.js": "vue", "vuejs": "vue",
        "next.js": "nextjs", "nextjs": "nextjs",
        # Python
        "py": "python", "python3": "python",
        # Cloud
        "aws": "aws", "amazon web services": "aws",
        "gcp": "gcp", "google cloud": "gcp", "google cloud platform": "gcp",
        "azure": "azure", "microsoft azure": "azure",
        # Databases
        "postgres": "postgresql", "postgresql": "postgresql",
        "mongo": "mongodb", "mongodb": "mongodb",
        "sql server": "mssql", "ms sql": "mssql",
        # AI/ML
        "ml": "machine learning", "ai": "artificial intelligence",
        "llm": "large language models",
        "scikit": "scikit-learn", "sklearn": "scikit-learn",
        # DevOps
        "k8s": "kubernetes", "kube": "kubernetes",
        "ci/cd": "ci/cd", "cicd": "ci/cd",
        # Misc
        "c#": "csharp", "dotnet": ".net", ".net": ".net",
    }

    # Step 13: Skill Categorization buckets
    CATEGORIES = {
        "frontend": ["react", "vue", "angular", "html", "css", "javascript", "typescript", "tailwind", "nextjs", "svelte", "sass"],
        "backend": ["nodejs", "python", "java", "go", "golang", "ruby", "php", "csharp", ".net", "fastapi", "django", "flask", "spring"],
        "database": ["postgresql", "mysql", "mongodb", "redis", "mssql", "sqlite", "elasticsearch", "cassandra"],
        "cloud": ["aws", "gcp", "azure", "heroku", "vercel", "render"],
        "ml_ai": ["pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "opencv", "hugging face", "langchain", "large language models", "machine learning", "artificial intelligence"],
        "devops": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd", "github actions", "gitlab ci"],
        "data_engineering": ["spark", "hadoop", "airflow", "kafka", "etl", "snowflake", "databricks", "dbt"],
        "mobile": ["react native", "flutter", "swift", "kotlin", "android", "ios"],
    }

    # Skill Relationships for embedding enrichment
    RELATIONSHIPS = {
        "tensorflow": ["keras", "pytorch", "deep learning"],
        "pytorch": ["tensorflow", "jax", "deep learning"],
        "react": ["nextjs", "redux", "frontend"],
        "nodejs": ["express", "backend", "javascript"],
        "aws": ["azure", "gcp", "cloud"]
    }

    @classmethod
    def _resolve_canonical(cls, skill_str: str) -> str:
        """Step 10 & 11: Normalize + resolve alias for a single skill string."""
        cleaned = skill_str.strip().lower()
        cleaned = re.sub(r'[^\w\s.#+/-]', '', cleaned).strip()
        return cls.ALIASES.get(cleaned, cleaned)

    @classmethod
    def _get_category(cls, canonical: str) -> str:
        """Step 13: Categorize a canonical skill."""
        for cat, skills in cls.CATEGORIES.items():
            if canonical in skills:
                return cat
        return "general"

    @classmethod
    def normalize_skills_from_list(cls, raw_skills: list) -> list:
        """
        Steps 10-13: Process a plain list of skill strings (from Resume AI output).
        - Step 10/11: Alias resolution
        - Step 12: Deduplication
        - Step 13: Categorization
        - Weight = 0.7 (neutral, no JD context to compare against)
        """
        if not raw_skills:
            return []

        processed = []
        seen = set()

        for skill in raw_skills:
            if not skill or not isinstance(skill, str):
                continue
            canonical = cls._resolve_canonical(skill)
            if not canonical or canonical in seen:
                continue  # Step 12: Deduplication
            seen.add(canonical)

            processed.append({
                "name": canonical,
                "original": skill.strip(),
                "category": cls._get_category(canonical),  # Step 13
                "weight": 0.7,  # Neutral weight
                "related": cls.RELATIONSHIPS.get(canonical, [])
            })

        return processed

    @classmethod
    def normalize_skills(cls, raw_skills_data: list) -> list:
        """
        Steps 10-14: Process skill dicts from JD AI output: [{name, importance}]
        - Step 10/11: Alias resolution
        - Step 12: Deduplication
        - Step 13: Categorization
        - Step 14: Skill Weighting (must-have=0.9, preferred=0.6)
        """
        if not raw_skills_data:
            return []

        processed = []
        seen = set()

        for skill_entry in raw_skills_data:
            if isinstance(skill_entry, str):
                name = skill_entry
                importance = "preferred"
            else:
                name = skill_entry.get("name", "")
                importance = skill_entry.get("importance", "preferred")

            canonical = cls._resolve_canonical(name)
            if not canonical or canonical in seen:
                continue  # Step 12: Deduplication
            seen.add(canonical)

            # Step 14: Skill Weighting
            weight = 0.9 if importance == "must-have" else 0.6

            processed.append({
                "name": canonical,
                "original": name.strip(),
                "category": cls._get_category(canonical),  # Step 13
                "weight": weight,                            # Step 14
                "related": cls.RELATIONSHIPS.get(canonical, [])
            })

        return processed
