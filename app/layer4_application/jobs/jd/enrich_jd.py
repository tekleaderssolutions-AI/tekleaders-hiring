class JDEnricher:
    @staticmethod
    def classify_responsibilities(responsibilities: list[str]) -> dict:
        """
        Step 9: Responsibility Processing
        Classify into: development, leadership, operations
        """
        categorized = {"development": [], "leadership": [], "operations": []}
        
        dev_kws = ["build", "develop", "code", "implement", "design", "architect", "engineer"]
        lead_kws = ["lead", "mentor", "manage", "guide", "strategy", "roadmap", "hiring"]
        ops_kws = ["deploy", "monitor", "maintain", "support", "infrastructure", "on-call"]

        for resp in responsibilities:
            r_lower = resp.lower()
            if any(kw in r_lower for kw in lead_kws):
                categorized["leadership"].append(resp)
            elif any(kw in r_lower for kw in ops_kws):
                categorized["operations"].append(resp)
            else:
                categorized["development"].append(resp)
                
        return categorized

    @staticmethod
    def detect_seniority(hints: list[str], exp_min: int) -> str:
        """
        Step 11: Seniority Detection
        """
        hints_lower = [h.lower() for h in hints]
        
        if "lead" in hints_lower or "architect" in hints_lower or exp_min >= 8:
            return "lead"
        if "senior" in hints_lower or exp_min >= 5:
            return "senior"
        if "junior" in hints_lower or exp_min <= 2:
            return "junior"
            
        return "mid"

    @staticmethod
    def calculate_quality_score(data: dict) -> float:
        """
        Step 12: JD Quality Scoring
        Simple completeness score (0-100)
        """
        score = 0
        total_fields = 7
        
        if data.get("role"): score += 1
        if data.get("primary_skills"): score += 1
        if data.get("experience", {}).get("min") is not None: score += 1
        if data.get("salary", {}).get("min"): score += 1
        if data.get("responsibilities"): score += 1
        if data.get("location"): score += 1
        if data.get("summary"): score += 1
        
        return (score / total_fields) * 100
