import re


class SkillOntology:
    # ── Alias Resolution: raw string → canonical form ────────────────────────
    ALIASES = {
        # Python
        "py": "python", "python3": "python", "python2": "python",
        "pandas": "pandas", "pd": "pandas",
        "numpy": "numpy", "np": "numpy",
        "fastapi": "fastapi", "fast api": "fastapi",
        "flask": "flask",
        "django": "django",
        "asyncio": "asyncio",
        "scikit-learn": "scikit-learn", "scikit": "scikit-learn", "sklearn": "scikit-learn",
        "scipy": "scipy",

        # Java
        "java": "java",
        "spring": "spring",
        "spring boot": "spring boot", "springboot": "spring boot",
        "hibernate": "hibernate",
        "maven": "maven",
        "gradle": "gradle",

        # JavaScript / TypeScript
        "js": "javascript", "javascript": "javascript",
        "ts": "typescript", "typescript": "typescript",
        "node": "nodejs", "node.js": "nodejs", "nodejs": "nodejs",
        "react.js": "react", "reactjs": "react",
        "next.js": "nextjs", "nextjs": "nextjs", "next js": "nextjs",
        "vue.js": "vue", "vuejs": "vue",
        "angular": "angular", "angularjs": "angular",
        "express": "express", "express.js": "express", "expressjs": "express",
        "tailwind": "tailwind", "tailwindcss": "tailwind",
        "redux": "redux",
        "svelte": "svelte",
        "webpack": "webpack",
        "sass": "sass", "scss": "sass",
        "graphql": "graphql",

        # Other Languages
        "golang": "go",
        "c++": "c++", "cpp": "c++",
        "c#": "csharp", "c sharp": "csharp",
        "dotnet": ".net", ".net": ".net", "asp.net": ".net", "dotnet core": ".net",
        "rust": "rust",
        "ruby": "ruby",
        "ruby on rails": "ruby on rails", "rails": "ruby on rails",
        "php": "php",
        "laravel": "laravel",
        "swift": "swift",
        "kotlin": "kotlin",
        "scala": "scala",
        "r": "r",
        "matlab": "matlab",
        "shell": "shell scripting", "bash": "bash", "bash scripting": "bash",
        "powershell": "powershell",
        "sql": "sql",

        # Data Science
        "statistics": "statistics", "stats": "statistics",
        "hypothesis testing": "hypothesis testing",
        "a/b testing": "a/b testing", "ab testing": "a/b testing",
        "regression": "regression",
        "probability": "probability",
        "data analysis": "data analysis",
        "feature engineering": "feature engineering",
        "data cleaning": "data cleaning",
        "data preprocessing": "data preprocessing",
        "eda": "eda", "exploratory data analysis": "eda",
        "time series": "time series",
        "forecasting": "forecasting",

        # Machine Learning
        "ml": "machine learning", "machine learning": "machine learning",
        "supervised learning": "supervised learning",
        "random forest": "random forest",
        "xgboost": "xgboost", "xgb": "xgboost",
        "lightgbm": "lightgbm", "lgbm": "lightgbm",
        "catboost": "catboost",
        "unsupervised learning": "unsupervised learning",
        "clustering": "clustering",
        "pca": "pca", "principal component analysis": "pca",
        "reinforcement learning": "reinforcement learning", "rl": "reinforcement learning",
        "model evaluation": "model evaluation",
        "hyperparameter tuning": "hyperparameter tuning",
        "model deployment": "model deployment",

        # Deep Learning
        "deep learning": "deep learning", "dl": "deep learning",
        "neural networks": "neural networks", "neural network": "neural networks", "ann": "neural networks",
        "cnn": "cnn", "convolutional neural network": "cnn",
        "rnn": "rnn", "recurrent neural network": "rnn",
        "lstm": "lstm", "long short-term memory": "lstm",
        "transformers": "transformers", "transformer": "transformers",
        "tensorflow": "tensorflow", "tf": "tensorflow",
        "pytorch": "pytorch", "torch": "pytorch",
        "keras": "keras",
        "onnx": "onnx",
        "bert": "bert",
        "hugging face": "hugging face", "huggingface": "hugging face",

        # NLP
        "nlp": "nlp", "natural language processing": "nlp",
        "nltk": "nltk",
        "spacy": "spacy",
        "text classification": "text classification",
        "sentiment analysis": "sentiment analysis",
        "ner": "ner", "named entity recognition": "ner",
        "summarization": "summarization", "text summarization": "summarization",
        "topic modeling": "topic modeling",
        "information extraction": "information extraction",
        "machine translation": "machine translation",

        # Generative AI
        "ai": "artificial intelligence", "artificial intelligence": "artificial intelligence",
        "genai": "generative ai", "generative ai": "generative ai", "gen ai": "generative ai",
        "llm": "llms", "llms": "llms", "large language models": "llms", "large language model": "llms",
        "gpt": "gpt", "gpt-4": "gpt", "gpt4": "gpt", "gpt-3": "gpt", "chatgpt": "gpt",
        "openai": "openai",
        "claude": "claude", "anthropic": "claude",
        "gemini": "gemini", "google gemini": "gemini", "bard": "gemini",
        "llama": "llama", "llama2": "llama", "llama3": "llama", "meta llama": "llama",
        "mistral": "mistral",
        "deepseek": "deepseek",
        "prompt engineering": "prompt engineering",
        "fine-tuning": "fine-tuning", "finetuning": "fine-tuning", "fine tuning": "fine-tuning",
        "lora": "lora", "low-rank adaptation": "lora",
        "qlora": "qlora",
        "peft": "peft",
        "rag": "rag", "retrieval augmented generation": "rag", "retrieval-augmented generation": "rag",
        "langchain": "langchain", "lang chain": "langchain",
        "llamaindex": "llamaindex", "llama index": "llamaindex",
        "haystack": "haystack",
        "dspy": "dspy",
        "graphrag": "graphrag", "graph rag": "graphrag",
        "langgraph": "langgraph", "lang graph": "langgraph",
        "crewai": "crewai", "crew ai": "crewai",
        "autogen": "autogen",
        "semantic kernel": "semantic kernel",
        "mcp": "mcp", "model context protocol": "mcp",
        "agentic ai": "agentic ai", "ai agents": "agentic ai",
        "ragas": "ragas",
        "deepeval": "deepeval",
        "trulens": "trulens",
        "structured outputs": "structured outputs",

        # Vector Databases
        "pinecone": "pinecone",
        "chromadb": "chromadb", "chroma": "chromadb",
        "faiss": "faiss",
        "weaviate": "weaviate",
        "qdrant": "qdrant",
        "milvus": "milvus",
        "elasticsearch": "elasticsearch", "elastic search": "elasticsearch",
        "opensearch": "opensearch",

        # Data Engineering
        "etl": "etl", "extract transform load": "etl",
        "elt": "elt",
        "data warehouse": "data warehousing", "data warehousing": "data warehousing",
        "data lake": "data lake",
        "spark": "apache spark", "apache spark": "apache spark",
        "pyspark": "pyspark",
        "dask": "dask",
        "kafka": "kafka", "apache kafka": "kafka",
        "airflow": "airflow", "apache airflow": "airflow",
        "databricks": "databricks",
        "snowflake": "snowflake",
        "hadoop": "hadoop", "apache hadoop": "hadoop",
        "ssis": "ssis", "sql server integration services": "ssis",
        "ssrs": "ssrs", "sql server reporting services": "ssrs",
        "ssas": "ssas", "sql server analysis services": "ssas",
        "dbt": "dbt",
        "fivetran": "fivetran",
        "flink": "apache flink", "apache flink": "apache flink",

        # Databases
        "postgres": "postgresql", "postgresql": "postgresql",
        "mysql": "mysql", "mariadb": "mysql",
        "sql server": "mssql", "ms sql": "mssql", "microsoft sql server": "mssql",
        "oracle": "oracle", "oracle db": "oracle",
        "mongo": "mongodb", "mongodb": "mongodb",
        "redis": "redis",
        "cassandra": "cassandra", "apache cassandra": "cassandra",
        "dynamodb": "dynamodb", "amazon dynamodb": "dynamodb",
        "neo4j": "neo4j",
        "sqlite": "sqlite",
        "clickhouse": "clickhouse",
        "hbase": "hbase",

        # MLOps
        "mlflow": "mlflow",
        "kubeflow": "kubeflow",
        "sagemaker": "sagemaker", "aws sagemaker": "sagemaker",
        "model registry": "model registry",
        "model monitoring": "model monitoring",
        "drift detection": "drift detection",
        "experiment tracking": "experiment tracking",
        "feature store": "feature store",
        "bentoml": "bentoml",
        "seldon": "seldon",

        # Cloud — AWS
        "aws": "aws", "amazon web services": "aws",
        "ec2": "ec2",
        "s3": "s3",
        "lambda": "aws lambda", "aws lambda": "aws lambda",
        "bedrock": "aws bedrock", "amazon bedrock": "aws bedrock",
        # Cloud — GCP
        "gcp": "gcp", "google cloud": "gcp", "google cloud platform": "gcp",
        "vertex ai": "vertex ai",
        "bigquery": "bigquery",
        "cloud run": "cloud run",
        "gke": "gke", "google kubernetes engine": "gke",
        # Cloud — Azure
        "azure": "azure", "microsoft azure": "azure",
        "azure openai": "azure openai",
        "azure ml": "azure ml", "azure machine learning": "azure ml",
        "blob storage": "azure blob storage", "azure blob storage": "azure blob storage",
        "azure functions": "azure functions",

        # DevOps
        "docker": "docker",
        "kubernetes": "kubernetes", "k8s": "kubernetes",
        "git": "git",
        "github": "github",
        "github actions": "github actions",
        "gitlab": "gitlab", "gitlab ci": "gitlab ci",
        "jenkins": "jenkins",
        "terraform": "terraform",
        "helm": "helm",
        "ci/cd": "ci/cd", "cicd": "ci/cd",
        "ansible": "ansible",
        "prometheus": "prometheus",
        "grafana": "grafana",

        # Backend / Architecture
        "rest": "rest api", "rest api": "rest api", "restful": "rest api", "rest apis": "rest api",
        "microservices": "microservices",
        "event driven": "event driven systems", "event-driven": "event driven systems",
        "distributed systems": "distributed systems",
        "system design": "system design",
        "grpc": "grpc",

        # Frontend
        "html": "html", "html5": "html",
        "css": "css", "css3": "css",

        # Security
        "oauth": "oauth", "oauth2": "oauth",
        "jwt": "jwt", "json web token": "jwt",
        "iam": "iam",
        "soc2": "soc2", "soc 2": "soc2",
        "encryption": "encryption",
        "penetration testing": "penetration testing", "pentesting": "penetration testing",
        "vulnerability assessment": "vulnerability assessment",

        # BI / Reporting
        "power bi": "power bi", "powerbi": "power bi",
        "tableau": "tableau",
        "looker": "looker",
        "qlik": "qlikview", "qlikview": "qlikview", "qliksense": "qliksense",
        "excel": "excel", "microsoft excel": "excel",
        "metabase": "metabase",
        "superset": "apache superset", "apache superset": "apache superset",

        # Product / Agile
        "agile": "agile", "scrum": "scrum", "kanban": "kanban",
        "jira": "jira", "confluence": "confluence",
        "product management": "product management",
        "roadmapping": "roadmapping",
        "product strategy": "product strategy",
        "user research": "user research",
        "stakeholder management": "stakeholder management",
        "okrs": "okrs", "okr": "okrs",

        # Sales / CRM
        "salesforce": "salesforce", "sfdc": "salesforce",
        "hubspot": "hubspot",
        "dynamics 365": "dynamics 365", "ms dynamics": "dynamics 365",
        "lead generation": "lead generation",
        "prospecting": "prospecting",
        "pipeline management": "pipeline management",
        "negotiation": "negotiation",
        "revenue growth": "revenue growth",

        # Finance
        "financial modeling": "financial modeling",
        "valuation": "valuation",
        "budgeting": "budgeting",
        "risk analysis": "risk analysis",
        "investment analysis": "investment analysis",
        "portfolio management": "portfolio management",

        # Management / Leadership
        "leadership": "leadership",
        "team management": "team management",
        "hiring": "hiring",
        "mentoring": "mentoring",
        "program management": "program management",
        "change management": "change management",
        "strategic planning": "strategic planning",
    }

    # ── Categorization buckets ───────────────────────────────────────────────
    CATEGORIES = {
        "python": [
            "python", "pandas", "numpy", "fastapi", "flask", "django", "asyncio", "scipy", "scikit-learn",
        ],
        "java": [
            "java", "spring", "spring boot", "hibernate", "maven", "gradle",
        ],
        "javascript": [
            "javascript", "typescript", "nodejs", "express", "react", "nextjs", "vue", "angular",
            "redux", "svelte", "webpack", "sass",
        ],
        "other_languages": [
            "go", "c++", "csharp", ".net", "rust", "ruby", "ruby on rails", "php", "laravel",
            "swift", "kotlin", "scala", "r", "matlab", "bash", "shell scripting", "powershell", "sql",
        ],
        "data_science": [
            "statistics", "hypothesis testing", "a/b testing", "regression", "probability",
            "data analysis", "feature engineering", "data cleaning", "data preprocessing",
            "eda", "time series", "forecasting",
        ],
        "machine_learning": [
            "machine learning", "supervised learning", "random forest", "xgboost", "lightgbm",
            "catboost", "unsupervised learning", "clustering", "pca", "reinforcement learning",
            "model evaluation", "hyperparameter tuning", "model deployment",
        ],
        "deep_learning": [
            "deep learning", "neural networks", "cnn", "rnn", "lstm", "transformers",
            "tensorflow", "pytorch", "keras", "onnx", "bert", "hugging face",
        ],
        "nlp": [
            "nlp", "nltk", "spacy", "text classification", "sentiment analysis", "ner",
            "summarization", "topic modeling", "information extraction", "machine translation",
        ],
        "generative_ai": [
            "generative ai", "llms", "gpt", "claude", "gemini", "llama", "mistral", "deepseek",
            "openai", "prompt engineering", "fine-tuning", "lora", "qlora", "peft",
            "rag", "langchain", "llamaindex", "haystack", "dspy", "graphrag",
            "langgraph", "crewai", "autogen", "semantic kernel", "mcp", "agentic ai",
            "ragas", "deepeval", "trulens", "structured outputs",
        ],
        "vector_databases": [
            "pinecone", "chromadb", "faiss", "weaviate", "qdrant", "milvus",
            "elasticsearch", "opensearch",
        ],
        "data_engineering": [
            "etl", "elt", "data warehousing", "data lake", "apache spark", "pyspark", "dask",
            "kafka", "airflow", "databricks", "snowflake", "hadoop", "ssis", "ssrs", "ssas",
            "dbt", "fivetran", "apache flink",
        ],
        "databases": [
            "postgresql", "mysql", "mssql", "oracle", "mongodb", "redis", "cassandra",
            "dynamodb", "neo4j", "sqlite", "clickhouse", "hbase",
        ],
        "mlops": [
            "mlflow", "kubeflow", "sagemaker", "model registry", "model monitoring",
            "drift detection", "experiment tracking", "feature store", "bentoml", "seldon",
        ],
        "cloud": [
            "aws", "ec2", "s3", "aws lambda", "aws bedrock",
            "gcp", "vertex ai", "bigquery", "cloud run", "gke",
            "azure", "azure openai", "azure ml", "azure blob storage", "azure functions",
        ],
        "devops": [
            "docker", "kubernetes", "git", "github", "github actions", "gitlab", "gitlab ci",
            "jenkins", "terraform", "helm", "ci/cd", "ansible", "prometheus", "grafana",
        ],
        "backend": [
            "rest api", "graphql", "microservices", "event driven systems",
            "distributed systems", "system design", "grpc",
        ],
        "frontend": [
            "html", "css", "react", "nextjs", "angular", "vue", "tailwind",
            "redux", "svelte", "sass", "webpack",
        ],
        "security": [
            "oauth", "jwt", "iam", "soc2", "encryption", "penetration testing",
            "vulnerability assessment",
        ],
        "bi_reporting": [
            "power bi", "tableau", "looker", "qlikview", "qliksense", "excel",
            "metabase", "apache superset",
        ],
        "product_management": [
            "agile", "scrum", "kanban", "jira", "confluence", "product management",
            "roadmapping", "product strategy", "user research", "stakeholder management", "okrs",
        ],
        "sales": [
            "salesforce", "hubspot", "dynamics 365", "lead generation", "prospecting",
            "pipeline management", "negotiation", "revenue growth",
        ],
        "finance": [
            "financial modeling", "valuation", "budgeting", "forecasting", "risk analysis",
            "investment analysis", "portfolio management",
        ],
        "management": [
            "leadership", "team management", "hiring", "mentoring", "stakeholder management",
            "program management", "change management", "strategic planning",
        ],
    }

    # ── Parent → child: parent skill gives PARTIAL credit for child requirement ──
    PARENT_OF = {
        # Language ecosystems
        "python":          ["pandas", "numpy", "fastapi", "flask", "django", "asyncio", "scikit-learn", "scipy"],
        "java":            ["spring", "spring boot", "hibernate"],
        "spring":          ["spring boot"],
        "javascript":      ["react", "vue", "angular", "nextjs", "nodejs", "typescript"],
        "nodejs":          ["express"],
        "react":           ["react native", "nextjs", "redux"],
        ".net":            ["csharp", "asp.net"],
        # SQL family
        "sql":             ["mssql", "postgresql", "mysql", "oracle", "sqlite"],
        "mssql":           ["ssis", "ssrs", "ssas"],
        # Cloud families
        "aws":             ["ec2", "s3", "aws lambda", "sagemaker", "aws bedrock"],
        "gcp":             ["vertex ai", "bigquery", "cloud run", "gke"],
        "azure":           ["azure openai", "azure ml", "azure blob storage", "azure functions"],
        # Data engineering
        "apache spark":    ["pyspark"],
        # AI / ML hierarchy
        "machine learning":  ["supervised learning", "unsupervised learning", "reinforcement learning",
                              "random forest", "xgboost", "lightgbm", "catboost",
                              "model evaluation", "hyperparameter tuning", "model deployment"],
        "deep learning":     ["neural networks", "cnn", "rnn", "lstm", "transformers"],
        "transformers":      ["bert", "llms", "gpt"],
        "hugging face":      ["bert", "transformers", "nlp"],
        "nlp":               ["nltk", "spacy", "text classification", "sentiment analysis", "ner",
                              "summarization", "topic modeling", "information extraction", "machine translation"],
        "llms":              ["gpt", "claude", "gemini", "llama", "mistral", "deepseek"],
        "generative ai":     ["llms", "rag", "agentic ai", "prompt engineering", "fine-tuning"],
        "rag":               ["langchain", "llamaindex", "haystack", "dspy", "graphrag"],
        "agentic ai":        ["langgraph", "crewai", "autogen", "semantic kernel", "mcp"],
        "fine-tuning":       ["lora", "qlora", "peft"],
        "langchain":         ["langgraph"],
        # Vector DBs
        "elasticsearch":     ["opensearch"],
    }

    # ── Skill relationships for embedding enrichment ─────────────────────────
    RELATIONSHIPS = {
        "tensorflow":    ["keras", "pytorch", "deep learning"],
        "pytorch":       ["tensorflow", "deep learning", "transformers", "hugging face"],
        "keras":         ["tensorflow", "deep learning"],
        "langchain":     ["llamaindex", "rag", "llms", "langgraph"],
        "llamaindex":    ["langchain", "rag", "llms"],
        "langgraph":     ["langchain", "crewai", "autogen", "agentic ai"],
        "crewai":        ["langgraph", "autogen", "agentic ai"],
        "openai":        ["gpt", "llms", "azure openai"],
        "gpt":           ["llms", "prompt engineering", "openai"],
        "rag":           ["langchain", "llamaindex", "pinecone", "chromadb", "llms"],
        "pinecone":      ["weaviate", "qdrant", "faiss", "chromadb", "rag"],
        "chromadb":      ["pinecone", "weaviate", "qdrant", "faiss"],
        "react":         ["nextjs", "redux", "frontend", "javascript"],
        "nodejs":        ["express", "backend", "javascript"],
        "aws":           ["gcp", "azure", "cloud"],
        "gcp":           ["aws", "azure", "cloud", "vertex ai", "bigquery"],
        "azure":         ["aws", "gcp", "cloud", "azure openai"],
        "mssql":         ["ssis", "ssrs", "ssas", "data warehousing"],
        "snowflake":     ["databricks", "data warehousing", "bigquery"],
        "databricks":    ["apache spark", "pyspark", "mlflow"],
        "kubernetes":    ["docker", "helm", "devops"],
        "docker":        ["kubernetes", "devops"],
        "apache spark":  ["pyspark", "databricks", "data engineering"],
        "kafka":         ["event driven systems", "data engineering"],
        "mlflow":        ["kubeflow", "experiment tracking", "model registry"],
        "machine learning": ["deep learning", "data science"],
        "python":        ["pandas", "numpy", "machine learning", "data science"],
        "salesforce":    ["hubspot", "dynamics 365"],
        "bert":          ["transformers", "nlp", "hugging face"],
        "hugging face":  ["transformers", "bert", "nlp", "pytorch"],
    }

    _ALL_KNOWN: set = None

    @classmethod
    def _all_known_skills(cls) -> set:
        """Lazy-build the union of all canonical skill tokens."""
        if cls._ALL_KNOWN is None:
            known = set(cls.ALIASES.values())
            for skills in cls.CATEGORIES.values():
                known.update(skills)
            cls._ALL_KNOWN = known
        return cls._ALL_KNOWN

    @classmethod
    def extract_skills_from_text(cls, raw_text: str) -> set:
        """
        Source B: scan raw resume text for ALL known canonical skills using
        word-boundary regex. Catches skills the LLM missed during structured extraction.
        Returns a set of canonical skill strings.
        """
        if not raw_text:
            return set()
        text_lower = raw_text.lower()
        found = set()

        # Check aliases first (covers abbreviations and multi-word variants)
        for alias, canonical in cls.ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.add(canonical)

        # Check category skills directly (catches any not in ALIASES)
        for cat_skills in cls.CATEGORIES.values():
            for skill in cat_skills:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found.add(skill)

        return found

    @classmethod
    def _resolve_canonical(cls, skill_str: str) -> str:
        """Normalize + resolve alias for a single skill string."""
        cleaned = skill_str.strip().lower()
        cleaned = re.sub(r'[^\w\s.#+/-]', '', cleaned).strip()
        return cls.ALIASES.get(cleaned, cleaned)

    @classmethod
    def _get_category(cls, canonical: str) -> str:
        """Return the category bucket for a canonical skill."""
        for cat, skills in cls.CATEGORIES.items():
            if canonical in skills:
                return cat
        return "general"

    @classmethod
    def normalize_skills_from_list(cls, raw_skills: list) -> list:
        """
        Process a plain list of skill strings (from Resume AI output).
        Alias resolution → deduplication → categorization.
        Weight = 0.7 (neutral, no JD context).
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
                continue
            seen.add(canonical)

            processed.append({
                "name": canonical,
                "original": skill.strip(),
                "category": cls._get_category(canonical),
                "weight": 0.7,
                "related": cls.RELATIONSHIPS.get(canonical, [])
            })

        return processed

    @classmethod
    def normalize_skills(cls, raw_skills_data: list) -> list:
        """
        Process skill dicts from JD AI output: [{name, importance}]
        Alias resolution → deduplication → categorization → weighting.
        must-have = 0.9, preferred = 0.6.
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
                continue
            seen.add(canonical)

            weight = 0.9 if importance == "must-have" else 0.6

            processed.append({
                "name": canonical,
                "original": name.strip(),
                "category": cls._get_category(canonical),
                "weight": weight,
                "related": cls.RELATIONSHIPS.get(canonical, [])
            })

        return processed
