"""
Step 16: Seniority Enrichment
Detects candidate seniority level from job titles and responsibilities,
independent of the exact title the candidate gave themselves.
"""


class SeniorityEnricher:
    # Keywords that signal seniority level based on title or responsibilities
    SENIORITY_SIGNALS = {
        "executive": [
            "cto", "ceo", "vp", "vice president", "chief", "head of",
            "director of", "c-suite", "c-level"
        ],
        "lead": [
            "lead", "principal", "staff", "architect", "engineering manager",
            "tech lead", "team lead", "technical lead"
        ],
        "senior": [
            "senior", "sr.", "sr ", "specialist", "expert", "consultant",
            "mentor", "designed", "architected", "drove", "spearheaded", "owned",
            "led a team", "managed a team", "scaled"
        ],
        "mid": [
            "mid", "ii", "level 2", "developer", "engineer", "analyst",
            "implemented", "developed", "built", "collaborated", "contributed"
        ],
        "junior": [
            "junior", "jr.", "jr ", "associate", "entry", "intern", "trainee",
            "fresher", "graduate", "assisted", "supported", "learned"
        ]
    }

    @classmethod
    def detect_seniority(
        cls,
        current_title: str = "",
        total_years: float = 0.0,
        work_experience: list = None
    ) -> dict:
        """
        Step 16: Enrichment — detect seniority from:
        1. Current job title keywords
        2. Total years of experience
        3. Responsibility keywords from work history

        Returns: {"level": str, "confidence": float, "signals": list[str]}
        """
        signals_found = []
        scores = {k: 0 for k in cls.SENIORITY_SIGNALS}

        # --- Signal 1: Scan current title ---
        if current_title:
            title_lower = current_title.lower()
            for level, keywords in cls.SENIORITY_SIGNALS.items():
                for kw in keywords:
                    if kw in title_lower:
                        scores[level] += 3  # Strong signal from title
                        signals_found.append(f"title:{kw}")

        # --- Signal 2: Years of experience ---
        yrs = float(total_years or 0)
        if yrs >= 10:
            scores["executive"] += 1
            scores["lead"] += 2
            scores["senior"] += 2
        elif yrs >= 5:
            scores["senior"] += 3
        elif yrs >= 3:
            scores["mid"] += 3
        elif yrs >= 1:
            scores["junior"] += 2
            scores["mid"] += 1
        else:
            scores["junior"] += 3

        # --- Signal 3: Responsibilities keyword scan ---
        if work_experience:
            for job in work_experience:
                responsibilities = job.get("responsibilities") or []
                job_title = (job.get("title") or "").lower()

                # Scan responsibilities text
                for responsibility in responsibilities:
                    resp_lower = responsibility.lower()
                    for level, keywords in cls.SENIORITY_SIGNALS.items():
                        for kw in keywords:
                            if kw in resp_lower:
                                scores[level] += 1
                                signals_found.append(f"responsibility:{kw}")

                # Also scan individual job titles
                for level, keywords in cls.SENIORITY_SIGNALS.items():
                    for kw in keywords:
                        if kw in job_title:
                            scores[level] += 2
                            signals_found.append(f"past_title:{kw}")

        # --- Determine winner ---
        best_level = max(scores, key=scores.get)
        best_score = scores[best_level]
        total_score = sum(scores.values()) or 1
        confidence = round(min(best_score / total_score, 1.0), 2)

        # Map to human-readable label
        label_map = {
            "executive": "Executive / Director",
            "lead": "Lead / Principal",
            "senior": "Senior",
            "mid": "Mid-Level",
            "junior": "Junior / Entry-Level"
        }

        return {
            "level": label_map[best_level],
            "raw_level": best_level,
            "confidence": confidence,
            "signals": list(set(signals_found))[:10]  # Cap at 10 signals
        }
