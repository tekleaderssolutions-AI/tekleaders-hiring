import re

class JDNormalizer:
    @staticmethod
    def normalize_experience(exp_data: dict) -> dict:
        """
        7.1 Experience normalization
        "3+ years" -> {min: 3, max: null}
        "3-5 years" -> {min: 3, max: 5}
        """
        if not exp_data:
            return {"min": 0, "max": None}
            
        min_val = exp_data.get("min")
        max_val = exp_data.get("max")
        
        # If the LLM failed to give numbers but gave a string (in units or elsewhere)
        # we would do extra parsing here. But let's assume we want a safety check.
        if min_val is None: min_val = 0
            
        return {"min": int(min_val), "max": int(max_val) if max_val else None}

    @staticmethod
    def normalize_salary(salary_data: dict) -> dict:
        """
        7.2 Salary normalization
        """
        if not salary_data:
            return {"min": None, "max": None, "currency": "INR"}
            
        min_val = salary_data.get("min")
        max_val = salary_data.get("max")
        
        # Ensure we have numbers
        try:
            if min_val: min_val = float(min_val)
            if max_val: max_val = float(max_val)
        except:
            pass
            
        return {
            "min": min_val,
            "max": max_val,
            "currency": salary_data.get("currency", "INR").upper()
        }

    @staticmethod
    def normalize_location(location: str) -> str:
        """
        7.3 Location normalization
        "Bangalore" -> "Bengaluru"
        """
        if not location:
            return "Remote"
        
        loc = location.strip().lower()
        if "bangalore" in loc:
            return "Bengaluru"
        if "gurgaon" in loc:
            return "Gurugram"
            
        return location.strip()
