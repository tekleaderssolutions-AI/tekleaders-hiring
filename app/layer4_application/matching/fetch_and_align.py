import re
import uuid
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.layer6_data.models.resume.resume_model import ResumeModel
from app.layer6_data.models.jd.job_model import JobModel
from app.layer6_data.models.jd.job_version_model import JobVersionModel
from app.layer6_data.models.memory_model import MemoryModel
from app.layer6_data.models.application_model import ApplicationModel, ApplicationStage
from app.layer6_data.models.evaluation_model import CandidateEvaluationModel
from app.layer7_crosscutting.jd.skill_ontology import SkillOntology
from app.config import settings

# Performance optimization / tuning signals
_OPTIMIZATION_PATTERNS = [
    r'\b(?:performance\s+tuning|query\s+tuning|query\s+optimization)\b',
    r'\b(?:etl|ssis|pipeline)\s+(?:optimization|tuning|performance)\b',
    r'\b(?:index(?:ing)?\s+(?:strategy|optimization|tuning))\b',
    r'\b(?:execution\s+plan|query\s+plan|explain\s+plan)\b',
    r'\b(?:bottleneck|latency\s+reduction|throughput\s+improvement)\b',
    r'\b(?:partition(?:ing)?|parallel\s+(?:processing|execution|loading))\b',
    r'\b(?:performance\s+(?:improvement|enhancement|optimization|monitoring))\b',
    r'\boptimize[d]?\s+(?:queries|sql|stored\s+proc(?:edure)?|etl|pipeline|data\s+load)\b',
    r'\b(?:sla|service\s+level\s+agreement)\s+(?:compliance|adherence|met|maintained)\b',
]

# Ownership / production / leadership signals
_OWNERSHIP_PATTERNS = [
    r'\b(?:independently|autonomously|end[-\s]to[-\s]end)\b',
    r'\b(?:client|stakeholder)\s+(?:interaction|communication|management|facing|presentation)\b',
    r'\b(?:architect(?:ed|ing)?|designed\s+(?:the\s+)?(?:system|architecture|solution|pipeline))\b',
    r'\b(?:production\s+support|on[-\s]call|oncall|incident\s+(?:management|response|handling))\b',
    r'\b(?:owner(?:ship)?|own(?:ed|ing)\s+the\s+(?:system|pipeline|process|delivery))\b',
    r'\b(?:led|lead(?:ing)?|mentored?|guided?)\s+(?:a\s+)?(?:team|group|developers?)\b',
    r'\b(?:delivered|drove|spearheaded|championed|established)\b',
    r'\b(?:remote\s+work|work(?:ing)?\s+(?:independently|remotely|with\s+minimal\s+supervision))\b',
]

# Quantified business-impact / achievement signals (distinct from optimization patterns)
_ACHIEVEMENT_PATTERNS = [
    r'\b(?:reduced|improved|increased|decreased|accelerated)\b.{0,80}\b\d+\s*%',
    r'\b\d+\s*%\s*(?:reduction|improvement|increase|decrease|faster|gain|drop|rise)\b',
    r'\b(?:saved|generated|processed|migrated|handled)\b.{0,60}(?:\$\s*[\d,]+[km]?|\d+[km+]?\s*(?:records?|transactions?|requests?|rows?|files?|users?))',
    r'\b\d+[xX]\s*(?:faster|speedup|improvement|reduction|increase)\b',
    r'\bfrom\b.{0,40}\b\d+\s*(?:hours?|minutes?|seconds?|days?)\b.{0,40}\bto\b.{0,20}\b\d+\s*(?:hours?|minutes?|seconds?|days?)\b',
    r'\b(?:zero\s+downtime|no\s+(?:incidents?|failures?|outages?|data\s+loss))\b',
    r'\b(?:sla|slo)\s+(?:compliance|adherence|met|achieved|maintained)\b',
    r'\b(?:revenue|cost|time|effort)\s+(?:savings?|reduction|increase|optimization)\b.{0,60}\d+',
    r'\bcut\b.{0,40}\b(?:time|cost|runtime|latency|errors?|defects?)\b.{0,30}\d+\s*%',
    r'\b(?:award|recognition|top\s+performer|employee\s+of\s+the)\b',
]

# Title → seniority level for career progression analysis
_TITLE_LEVEL_MAP = [
    (["intern", "trainee", "fresher", "graduate"],         0),
    (["junior", "jr.", "jr ", "associate", "entry"],       1),
    (["senior", "sr.", "sr ", "principal", "staff"],       3),
    (["tech lead", "team lead", "lead"],                   4),
    (["architect"],                                        5),
    (["manager", "head of"],                               4),
    (["director", "vp", "vice president"],                 6),
    (["cto", "ceo", "ciso", "chief"],                      7),
]

SENIORITY_LEVELS = ["junior", "mid", "senior", "lead", "executive"]

JD_LEVEL_MAP = {
    "entry level": "junior", "entry-level": "junior", "entry": "junior",
    "mid level": "mid", "mid-level": "mid", "mid": "mid",
    "senior": "senior", "lead": "lead", "principal": "lead",
    "director": "executive", "executive": "executive", "manager": "lead",
}

# Dynamic weights per job cluster — skills matter most in technical roles,
# experience matters most in management, education in finance/legal etc.
WEIGHT_PROFILES = {
    "engineering":      {"skills": 45, "experience": 30, "projects": 15, "education":  5, "seniority":  5},
    "data_science":     {"skills": 40, "experience": 30, "projects": 20, "education":  5, "seniority":  5},
    "management":       {"skills": 20, "experience": 40, "projects": 10, "education": 15, "seniority": 15},
    "marketing":        {"skills": 30, "experience": 35, "projects": 20, "education": 10, "seniority":  5},
    "sales":            {"skills": 25, "experience": 40, "projects": 15, "education": 10, "seniority": 10},
    "hr":               {"skills": 25, "experience": 35, "projects": 15, "education": 15, "seniority": 10},
    "finance":          {"skills": 35, "experience": 35, "projects": 10, "education": 15, "seniority":  5},
    "legal":            {"skills": 25, "experience": 35, "projects": 10, "education": 25, "seniority":  5},
    "customer_service": {"skills": 30, "experience": 35, "projects": 15, "education": 10, "seniority": 10},
    "other":            {"skills": 40, "experience": 35, "projects": 15, "education":  5, "seniority":  5},
}

# ATS 7-component weights — 47 specific cluster profiles + broad fallbacks
# Skill | Experience | Semantic | Evidence | Impact | Domain | Seniority
# skill_depth and project_complexity are computed as informational signals (not weighted)
ATS_WEIGHTS_BY_CLUSTER: dict = {
    # ── AI / ML ───────────────────────────────────────────────────────────
    "ai_ml_engineer":            {"skill_match": 0.28, "experience_relevance": 0.25, "semantic_similarity": 0.20, "evidence_score": 0.10, "impact": 0.07, "domain_match": 0.05, "seniority_fit": 0.05},
    "data_science":              {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.20, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.05, "seniority_fit": 0.05},
    "nlp_engineer":              {"skill_match": 0.28, "experience_relevance": 0.25, "semantic_similarity": 0.22, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.05, "seniority_fit": 0.05},
    "computer_vision_engineer":  {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.18, "evidence_score": 0.10, "impact": 0.07, "domain_match": 0.05, "seniority_fit": 0.05},
    "mlops_engineer":            {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.15, "impact": 0.10, "domain_match": 0.05, "seniority_fit": 0.05},
    "research_engineer":         {"skill_match": 0.25, "experience_relevance": 0.20, "semantic_similarity": 0.25, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "data_engineer":             {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "analytics_engineer":        {"skill_match": 0.25, "experience_relevance": 0.25, "semantic_similarity": 0.15, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "data_analyst":              {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "database_engineer":         {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    # ── Software Engineering ──────────────────────────────────────────────
    "backend_engineer":          {"skill_match": 0.30, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "frontend_engineer":         {"skill_match": 0.35, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "fullstack_engineer":        {"skill_match": 0.28, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.07, "domain_match": 0.10, "seniority_fit": 0.05},
    "mobile_engineer":           {"skill_match": 0.35, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "devops_engineer":           {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "site_reliability_engineer": {"skill_match": 0.20, "experience_relevance": 0.35, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "platform_engineer":         {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.15, "impact": 0.10, "domain_match": 0.05, "seniority_fit": 0.05},
    "cloud_engineer":            {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "cybersecurity":             {"skill_match": 0.25, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.20, "seniority_fit": 0.05},
    "network_engineer":          {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.05, "domain_match": 0.15, "seniority_fit": 0.05},
    "system_administrator":      {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.05, "domain_match": 0.15, "seniority_fit": 0.05},
    "qa_automation":             {"skill_match": 0.30, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "manual_tester":             {"skill_match": 0.30, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    # ── Architects & Leads ────────────────────────────────────────────────
    "solution_architect":        {"skill_match": 0.20, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.10},
    "software_architect":        {"skill_match": 0.20, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.10},
    "enterprise_architect":      {"skill_match": 0.15, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.05, "impact": 0.10, "domain_match": 0.20, "seniority_fit": 0.10},
    "technical_lead":            {"skill_match": 0.20, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.05, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.15},
    "engineering_manager":       {"skill_match": 0.15, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.15, "domain_match": 0.15, "seniority_fit": 0.15},
    # ── Product & Programme ───────────────────────────────────────────────
    "product_manager":           {"skill_match": 0.18, "experience_relevance": 0.32, "semantic_similarity": 0.08, "evidence_score": 0.05, "impact": 0.12, "domain_match": 0.15, "seniority_fit": 0.10},
    "program_manager":           {"skill_match": 0.15, "experience_relevance": 0.35, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.15, "domain_match": 0.15, "seniority_fit": 0.10},
    "project_manager":           {"skill_match": 0.18, "experience_relevance": 0.35, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.12, "domain_match": 0.15, "seniority_fit": 0.10},
    "scrum_master":              {"skill_match": 0.15, "experience_relevance": 0.35, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.10, "domain_match": 0.20, "seniority_fit": 0.10},
    "business_analyst":          {"skill_match": 0.20, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.05, "impact": 0.10, "domain_match": 0.20, "seniority_fit": 0.05},
    # ── Design ────────────────────────────────────────────────────────────
    "ui_ux_designer":            {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    "product_designer":          {"skill_match": 0.25, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.15, "domain_match": 0.10, "seniority_fit": 0.05},
    # ── ERP / CRM / Platform ──────────────────────────────────────────────
    "erp_specialist":            {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.25, "seniority_fit": 0.05},
    "crm_specialist":            {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.25, "seniority_fit": 0.05},
    "salesforce_developer":      {"skill_match": 0.25, "experience_relevance": 0.30, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.15, "seniority_fit": 0.05},
    "sap_consultant":            {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.25, "seniority_fit": 0.05},
    "oracle_consultant":         {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.25, "seniority_fit": 0.05},
    # ── Support & Sales ───────────────────────────────────────────────────
    "technical_support":         {"skill_match": 0.25, "experience_relevance": 0.35, "semantic_similarity": 0.05, "evidence_score": 0.15, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "pre_sales_engineer":        {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.20, "domain_match": 0.20, "seniority_fit": 0.05},
    "sales_engineer":            {"skill_match": 0.20, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.05, "impact": 0.25, "domain_match": 0.15, "seniority_fit": 0.05},
    # ── Specialized / Emerging ────────────────────────────────────────────
    "embedded_engineer":         {"skill_match": 0.35, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.15, "seniority_fit": 0.05},
    "iot_engineer":              {"skill_match": 0.30, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.15, "seniority_fit": 0.05},
    "blockchain_engineer":       {"skill_match": 0.35, "experience_relevance": 0.25, "semantic_similarity": 0.10, "evidence_score": 0.10, "impact": 0.05, "domain_match": 0.10, "seniority_fit": 0.05},
    "game_developer":            {"skill_match": 0.35, "experience_relevance": 0.25, "semantic_similarity": 0.05, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    # ── Broad fallbacks (for coarse JD classifier output) ─────────────────
    "engineering":               {"skill_match": 0.30, "experience_relevance": 0.28, "semantic_similarity": 0.12, "evidence_score": 0.10, "impact": 0.07, "domain_match": 0.08, "seniority_fit": 0.05},
    "management":                {"skill_match": 0.15, "experience_relevance": 0.32, "semantic_similarity": 0.07, "evidence_score": 0.05, "impact": 0.15, "domain_match": 0.16, "seniority_fit": 0.10},
    "marketing":                 {"skill_match": 0.22, "experience_relevance": 0.25, "semantic_similarity": 0.13, "evidence_score": 0.10, "impact": 0.15, "domain_match": 0.10, "seniority_fit": 0.05},
    "sales":                     {"skill_match": 0.18, "experience_relevance": 0.25, "semantic_similarity": 0.07, "evidence_score": 0.05, "impact": 0.25, "domain_match": 0.15, "seniority_fit": 0.05},
    "hr":                        {"skill_match": 0.20, "experience_relevance": 0.28, "semantic_similarity": 0.12, "evidence_score": 0.10, "impact": 0.12, "domain_match": 0.12, "seniority_fit": 0.06},
    "finance":                   {"skill_match": 0.22, "experience_relevance": 0.25, "semantic_similarity": 0.08, "evidence_score": 0.08, "impact": 0.15, "domain_match": 0.15, "seniority_fit": 0.07},
    "legal":                     {"skill_match": 0.18, "experience_relevance": 0.25, "semantic_similarity": 0.07, "evidence_score": 0.05, "impact": 0.05, "domain_match": 0.30, "seniority_fit": 0.10},
    "customer_service":          {"skill_match": 0.22, "experience_relevance": 0.30, "semantic_similarity": 0.10, "evidence_score": 0.13, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
    # ── Default ────────────────────────────────────────────────────────────
    "other":                     {"skill_match": 0.25, "experience_relevance": 0.25, "semantic_similarity": 0.15, "evidence_score": 0.10, "impact": 0.10, "domain_match": 0.10, "seniority_fit": 0.05},
}

# Role-aware experience normalization: years at which a candidate is "fully experienced"
DOMAIN_EXP_NORMS: dict = {
    # AI / ML
    "ai_ml_engineer": 5.0, "data_science": 5.0, "nlp_engineer": 5.0,
    "computer_vision_engineer": 5.0, "mlops_engineer": 5.0, "research_engineer": 6.0,
    "data_engineer": 5.0, "analytics_engineer": 4.0, "data_analyst": 4.0, "database_engineer": 5.0,
    # Engineering
    "backend_engineer": 6.0, "frontend_engineer": 5.0, "fullstack_engineer": 6.0,
    "mobile_engineer": 5.0, "devops_engineer": 5.0, "site_reliability_engineer": 7.0,
    "platform_engineer": 7.0, "cloud_engineer": 5.0, "cybersecurity": 6.0,
    "network_engineer": 6.0, "system_administrator": 5.0, "qa_automation": 5.0, "manual_tester": 4.0,
    # Architects & Leads
    "solution_architect": 10.0, "software_architect": 10.0, "enterprise_architect": 12.0,
    "technical_lead": 8.0, "engineering_manager": 8.0,
    # Product & Programme
    "product_manager": 6.0, "program_manager": 8.0, "project_manager": 7.0,
    "scrum_master": 5.0, "business_analyst": 5.0,
    # Design
    "ui_ux_designer": 5.0, "product_designer": 5.0,
    # ERP / CRM / Platform
    "erp_specialist": 6.0, "crm_specialist": 5.0, "salesforce_developer": 5.0,
    "sap_consultant": 7.0, "oracle_consultant": 7.0,
    # Support & Sales
    "technical_support": 4.0, "pre_sales_engineer": 5.0, "sales_engineer": 5.0,
    # Specialized / Emerging
    "embedded_engineer": 6.0, "iot_engineer": 5.0, "blockchain_engineer": 4.0, "game_developer": 5.0,
    # Broad fallbacks
    "engineering": 6.0, "management": 8.0, "marketing": 5.0, "sales": 5.0,
    "hr": 5.0, "finance": 6.0, "legal": 7.0, "customer_service": 4.0, "other": 6.0,
}


def _optimization_score(raw_text: str) -> int:
    """Detect performance/optimization signal strength from resume text. Returns 0-100."""
    if not raw_text:
        return 0
    text_lower = raw_text.lower()
    hits = sum(1 for p in _OPTIMIZATION_PATTERNS if re.search(p, text_lower))
    return min(100, hits * 20)


def _ownership_score(raw_text: str) -> int:
    """Detect ownership/leadership/production signal strength. Returns 0-100."""
    if not raw_text:
        return 0
    text_lower = raw_text.lower()
    hits = sum(1 for p in _OWNERSHIP_PATTERNS if re.search(p, text_lower))
    return min(100, hits * 20)


def _achievement_score(raw_text: str) -> int:
    """Detect quantified business-impact signals (%, $, Nx speedup). Returns 0-100."""
    if not raw_text:
        return 0
    text_lower = raw_text.lower()
    hits = sum(1 for p in _ACHIEVEMENT_PATTERNS if re.search(p, text_lower))
    return min(100, hits * 15)


def _title_level(title: str) -> int:
    """Map a job title to a seniority integer (0=intern … 7=C-suite). Default 2=mid."""
    t = (title or "").lower()
    for keywords, level in _TITLE_LEVEL_MAP:
        if any(kw in t for kw in keywords):
            return level
    return 2


def _job_stability_analysis(exp_json: list) -> dict:
    """
    Analyze tenure patterns across all roles.
    Penalizes frequent short-tenure changes (retention risk signal).
    Returns: score 0-100, avg_tenure, short_stints count, flag string or None.
    """
    if not exp_json:
        return {"score": 70, "avg_tenure": 0.0, "short_stints": 0, "flag": None}

    tenures = [t for t in (_role_years(job) for job in exp_json) if t > 0]
    if not tenures:
        return {"score": 70, "avg_tenure": 0.0, "short_stints": 0, "flag": None}

    avg = sum(tenures) / len(tenures)
    short = sum(1 for t in tenures if t < 1.5)

    if avg >= 3.5:    score = 100
    elif avg >= 2.5:  score = 90
    elif avg >= 2.0:  score = 80
    elif avg >= 1.5:  score = 65
    elif avg >= 1.0:  score = 50
    else:             score = 30

    if short >= 4:    score = max(15, score - 30)
    elif short >= 3:  score = max(25, score - 20)
    elif short >= 2:  score = max(35, score - 10)

    flag = None
    if avg < 1.5 and len(tenures) >= 3:
        flag = f"High turnover risk: avg {avg:.1f}y tenure across {len(tenures)} roles"
    elif short >= 3:
        flag = f"{short} roles under 18 months — assess retention risk"

    return {"score": round(score), "avg_tenure": round(avg, 1), "short_stints": short, "flag": flag}


def _career_progression_analysis(exp_json: list) -> dict:
    """
    Detect upward/stable/descending career trajectory from title seniority levels.
    Compares first-half vs second-half of career chronologically.
    Returns: trend ('ascending'|'stable'|'descending'|'unknown'), peak_level, flag or None.
    """
    if not exp_json:
        return {"trend": "unknown", "peak_level": 2, "flag": None}

    def _start_yr(job):
        m = re.search(r'\d{4}', str(job.get("start_date") or ""))
        return int(m.group()) if m else 0

    sorted_jobs = [j for j in sorted(exp_json, key=_start_yr) if _role_years(j) > 0]
    levels = [_title_level(j.get("title") or "") for j in sorted_jobs]

    if not levels:
        return {"trend": "unknown", "peak_level": 2, "flag": None}

    peak = max(levels)
    if len(levels) == 1:
        return {"trend": "stable", "peak_level": peak, "flag": None}

    mid = max(1, len(levels) // 2)
    early_avg = sum(levels[:mid]) / mid
    late_avg  = sum(levels[mid:]) / len(levels[mid:])
    delta = late_avg - early_avg

    if delta >= 1.0:
        trend, flag = "ascending", None
    elif delta <= -1.0:
        trend, flag = "descending", "Career trajectory appears downward — verify context"
    else:
        trend, flag = "stable", None

    return {"trend": trend, "peak_level": peak, "flag": flag}


def _skill_role_depth(skill_canonical: str, exp_json: list) -> int:
    """Count how many distinct work roles explicitly mention this skill. Returns role count."""
    if not exp_json:
        return 0
    count = 0
    for job in exp_json:
        skills_raw = [s.lower() for s in (job.get("skills_used") or [])]
        skills_norm = {_normalize_skill(s) for s in skills_raw}
        if skill_canonical in skills_norm:
            count += 1
    return count


def _match_label(score: float) -> str:
    if score >= 80:
        return "Strong Match"
    if score >= 65:
        return "Good Match"
    if score >= 50:
        return "Fair Match"
    return "Weak Match"


def _seniority_score(cand_raw: str, jd_experience_level: str) -> int:
    jd_raw = JD_LEVEL_MAP.get((jd_experience_level or "mid").lower(), "mid")
    try:
        ci = SENIORITY_LEVELS.index(cand_raw)
    except ValueError:
        ci = 1
    try:
        ji = SENIORITY_LEVELS.index(jd_raw)
    except ValueError:
        ji = 2
    return [100, 80, 60, 40, 20][min(abs(ci - ji), 4)]


def _normalize_skill(s: str) -> str:
    return SkillOntology._resolve_canonical(s)



def _skill_match(
    jd_skills_raw: list,
    cand_skills: set,
    raw_text: str = "",
    skill_weights: dict = None,
    exp_json: list = None,
) -> Tuple[list, list, int, dict]:
    """
    Four-tier skill matching with optional per-skill JD weights and role-depth tracking.

    Tier 1 — exact canonical match
    Tier 2 — substring / partial match on normalized skills
    Tier 3 — raw resume text fallback
    Tier 4 — parent/child ontology: parent skill → 0.6 partial credit

    skill_weights: {canonical_skill: 0.5–1.0} from JD — critical skills count more.
                   Defaults to 0.7 for any skill not listed.
    exp_json: work_experience list — used to count how many roles mention each skill.

    Returns (matched_list, missing_list, score_0_to_100, depth_info)
    depth_info: {skill: role_count} for matched must-have skills
    """
    if not jd_skills_raw:
        return [], [], 0, {}

    jd_normalized = {_normalize_skill(s) for s in jd_skills_raw if s}
    weights = skill_weights or {}

    matched = set()
    partial = set()

    # Tier 1: exact canonical
    matched.update(jd_normalized & cand_skills)

    # Tier 2: substring / shared-word on normalized skills
    for jd_s in jd_normalized - matched:
        jd_words = set(jd_s.split())
        for cand_s in cand_skills:
            cand_words = set(cand_s.split())
            if (jd_s in cand_s or cand_s in jd_s or
                    (jd_words & cand_words and max((len(w) for w in jd_words & cand_words), default=0) >= 4)):
                matched.add(jd_s)
                break

    # Tier 3: raw resume text fallback
    text_lower = raw_text.lower() if raw_text else ""
    if text_lower:
        for jd_s in jd_normalized - matched:
            if jd_s in text_lower:
                matched.add(jd_s)
                continue
            words = [w for w in jd_s.split() if len(w) >= 4]
            if words and all(w in text_lower for w in words):
                matched.add(jd_s)

    # Tier 4: parent/child ontology → partial credit
    parent_of = SkillOntology.PARENT_OF
    for jd_s in jd_normalized - matched:
        for parent, children in parent_of.items():
            if jd_s in children and parent in cand_skills:
                partial.add(jd_s)
                break

    missing = sorted(jd_normalized - matched - partial)
    matched_list = sorted(matched | partial)

    # Weighted score: critical skills penalize more when missing, reward more when present
    DEFAULT_W = 0.7
    total_w = sum(weights.get(s, DEFAULT_W) for s in jd_normalized) or len(jd_normalized)
    matched_w = sum(weights.get(s, DEFAULT_W) for s in matched)
    partial_w = sum(weights.get(s, DEFAULT_W) * 0.6 for s in partial)
    score = round(min(1.0, (matched_w + partial_w) / total_w) * 100)

    # Depth: how many distinct roles mention each matched skill
    depth_info: dict = {}
    if exp_json:
        for s in matched:
            depth_info[s] = _skill_role_depth(s, exp_json)

    return matched_list, missing, score, depth_info


def _years_from_text(raw_text: str) -> float:
    """
    Extract declared total years of experience from resume text.
    Finds ALL pattern matches and returns the maximum — avoids being fooled
    by "5 years in Python" appearing before "20 years of IT experience".
    """
    if not raw_text:
        return 0.0
    patterns = [
        r'(\d{1,2})\s*\+\s*years',
        r'(\d{1,2})\+\s*years',
        r'over\s+(\d{1,2})\s+years',
        r'(\d{1,2})\s+years\s+of\s+(?:experience|expertise|exp)',
        r'(\d{1,2})\s+years\s+(?:in|of)\s+(?:IT|Information Technology|software)',
        r'(\d{1,2})\s+years\s+(?:of\s+)?(?:total|overall|professional)',
    ]
    found = []
    for pattern in patterns:
        for m in re.finditer(pattern, raw_text, re.IGNORECASE):
            yrs = float(m.group(1))
            if 1 <= yrs <= 40:
                found.append(yrs)
    return max(found) if found else 0.0


def _role_years(job: dict) -> float:
    """Return years duration for a single work experience entry."""
    now_year = datetime.now().year
    start_str = str(job.get("start_date") or "")
    end_str   = str(job.get("end_date")   or "")
    m_start = re.search(r'\d{4}', start_str)
    m_end   = re.search(r'\d{4}', end_str)
    start_yr = int(m_start.group()) if m_start else None
    if not end_str or "present" in end_str.lower() or "current" in end_str.lower():
        end_yr = now_year
    else:
        end_yr = int(m_end.group()) if m_end else None
    if start_yr and end_yr and end_yr >= start_yr:
        return float(end_yr - start_yr)
    return 0.0


def _years_from_experience_json(exp_json: list) -> float:
    """Compute total experience years from structured experience_json entries."""
    if not exp_json or not isinstance(exp_json, list):
        return 0.0
    return round(sum(_role_years(job) for job in exp_json), 1)



_SENIOR_KW  = ["senior", "sr.", "sr ", "lead", "principal", "architect", "manager", "staff", "head", "director"]
_JUNIOR_KW  = ["junior", "jr.", "associate", "trainee", "intern", "entry", "fresher", "graduate"]
_DEPTH_KW   = ["designed", "architected", "built", "optimized", "implemented", "led", "owned",
                "established", "drove", "created", "developed", "managed", "delivered", "spearheaded"]
_SHALLOW_KW = ["worked on", "assisted", "supported", "helped", "exposure to", "familiar with"]


def _weighted_relevant_experience(exp_json: list, jd_skills_normalized: set) -> dict:
    """
    Compute WEIGHTED relevant experience using the full formula:
      Role Contribution = duration × skill_ratio × recency_weight × seniority_weight × depth_weight

    Recency decay: roles ending 0-2 years ago = 1.0, 13+ years ago = 0.25
    Seniority:     Senior/Lead/Architect = 1.2×, Junior/Entry = 0.75×
    Depth:         "Designed", "architected", "optimized" = 1.1×; "worked on", "assisted" = 0.85×
    Skill ratio:   fraction of JD skills present in each role (partial match = partial credit)

    Returns:
      relevant_years    — weighted effective years used in scoring
      raw_domain_years  — raw calendar years in primarily-relevant roles (for display)
      relevance_ratio   — what fraction of the candidate's career aligns with the JD
      role_breakdown    — per-role detail list for transparency
    """
    now_year = datetime.now().year

    if not exp_json or not isinstance(exp_json, list) or not jd_skills_normalized:
        return {"relevant_years": 0.0, "raw_domain_years": 0.0, "relevance_ratio": 0.0, "role_breakdown": []}

    total_calendar = 0.0
    relevant_years = 0.0
    raw_domain_years = 0.0
    role_breakdown: list = []

    for job in exp_json:
        role_yrs = _role_years(job)
        if role_yrs == 0:
            continue
        total_calendar += role_yrs

        # ── Skill match ratio for this role ─────────────────────────────
        role_skills_raw  = [s.lower() for s in (job.get("skills_used") or [])]
        role_skills_norm = {_normalize_skill(s) for s in role_skills_raw}
        role_header_text = " ".join([
            str(job.get("title")  or ""),
            str(job.get("domain") or ""),
        ]).lower()

        # Tier 1: exact matches in role's structured skill list
        tier1 = jd_skills_normalized & role_skills_norm
        # Tier 2: skills found in title/domain text only (half credit)
        tier2 = set()
        for jd_s in jd_skills_normalized - tier1:
            words = [w for w in jd_s.split() if len(w) >= 4]
            if jd_s in role_header_text or (words and any(w in role_header_text for w in words)):
                tier2.add(jd_s)

        matched_weight = len(tier1) + len(tier2) * 0.5
        skill_ratio = min(1.0, matched_weight / len(jd_skills_normalized))

        if skill_ratio == 0.0:
            role_breakdown.append({"title": job.get("title", ""), "years": role_yrs,
                                   "skill_ratio": 0.0, "contribution": 0.0})
            continue

        # ── Recency weight ────────────────────────────────────────────────
        end_str = str(job.get("end_date") or "")
        m_end   = re.search(r'\d{4}', end_str)
        if not end_str or "present" in end_str.lower() or "current" in end_str.lower():
            end_yr = now_year
        else:
            end_yr = int(m_end.group()) if m_end else now_year
        gap = now_year - end_yr
        if gap <= 2:   recency_w = 1.0
        elif gap <= 5: recency_w = 0.85
        elif gap <= 9: recency_w = 0.65
        elif gap <= 13: recency_w = 0.45
        else:          recency_w = 0.25

        # ── Seniority weight (from role title) ────────────────────────────
        title_lower = (job.get("title") or "").lower()
        if any(kw in title_lower for kw in _SENIOR_KW):
            seniority_w = 1.2
        elif any(kw in title_lower for kw in _JUNIOR_KW):
            seniority_w = 0.75
        else:
            seniority_w = 1.0

        # ── Depth weight (how substantively they worked in the skill) ─────
        all_role_text = " ".join([
            role_header_text,
            " ".join(str(r) for r in (job.get("responsibilities") or [])),
            " ".join(str(s) for s in (job.get("skills_used") or [])),
        ]).lower()
        has_depth   = any(kw in all_role_text for kw in _DEPTH_KW)
        has_shallow = any(kw in all_role_text for kw in _SHALLOW_KW)
        depth_w = 1.1 if has_depth else (0.85 if has_shallow else 1.0)

        # ── Role contribution ─────────────────────────────────────────────
        contribution = role_yrs * skill_ratio * recency_w * seniority_w * depth_w
        relevant_years += contribution
        if skill_ratio >= 0.25:
            raw_domain_years += role_yrs

        role_breakdown.append({
            "title":            job.get("title", ""),
            "years":            role_yrs,
            "end_year":         end_yr,
            "skill_ratio":      round(skill_ratio, 2),
            "recency_weight":   recency_w,
            "seniority_weight": seniority_w,
            "depth_weight":     round(depth_w, 2),
            "contribution":     round(contribution, 2),
            "matched_skills":   sorted(tier1 | tier2),
        })

    relevance_ratio = min(1.0, relevant_years / total_calendar) if total_calendar > 0 else 0.0

    return {
        "relevant_years":   round(relevant_years, 1),
        "raw_domain_years": round(raw_domain_years, 1),
        "relevance_ratio":  round(relevance_ratio, 2),
        "role_breakdown":   role_breakdown,
    }


def _generate_candidate_brief(
    matched: list,
    missing: list,
    total_years: float,
    domain_years: float,
    min_exp: float,
    opt_score: int,
    own_score: int,
    achieve_score: int,
    stability: dict,
    progression: dict,
    exp_score: int,
    depth_info: dict,
    nice_matched: list = None,
) -> dict:
    """
    Produce exactly 4 human-readable bullets per section:
    Why Shortlisted / Key Strengths / Gaps & Risks.
    Each bullet is always generated — conditional logic picks the most
    informative variant, with a sensible fallback when data is absent.
    """
    reasons: list = []
    strengths: list = []
    gaps: list = []

    total_skills = len(matched) + len(missing)
    deep_skills  = [s for s, d in depth_info.items() if d >= 2]
    short_stints = stability.get("short_stints", 0)
    avg_tenure   = stability.get("avg_tenure", 0)

    # ── REASONS (always 4) ────────────────────────────────────────────────
    # 1. Experience
    if total_years >= 1:
        if domain_years > 0 and domain_years < total_years:
            reasons.append(f"{int(domain_years)}+ years of relevant domain experience ({int(total_years)}y total)")
        else:
            reasons.append(f"{int(total_years)}+ years of professional experience")
    else:
        reasons.append("Early-career profile — assess via technical interview")

    # 2. Core skill match
    if matched:
        skill_str = ", ".join(matched[:4]) + (" ..." if len(matched) > 4 else "")
        reasons.append(f"Proficient in required skills: {skill_str}")
    else:
        reasons.append("Skill alignment needs further validation in interview")

    # 3. Coverage breadth
    if total_skills > 0 and matched:
        pct = int(len(matched) / total_skills * 100)
        reasons.append(f"Covers {len(matched)} of {total_skills} required skills ({pct}% match rate)")
    elif matched:
        reasons.append(f"Matches {len(matched)} required skill{'s' if len(matched) > 1 else ''}")
    else:
        reasons.append("Resume submitted for manual skill review")

    # 4. Best available signal
    if nice_matched:
        reasons.append(f"Bonus skills: {', '.join(nice_matched[:3])}")
    elif achieve_score >= 60:
        reasons.append("Quantified business impact demonstrated in prior roles")
    elif own_score >= 60:
        reasons.append("Senior-level production ownership and responsibility shown")
    elif opt_score >= 60:
        reasons.append("Performance tuning and optimisation experience evident")
    elif avg_tenure >= 2.0:
        reasons.append(f"Consistent employment history — avg {avg_tenure}y per role")
    elif progression["trend"] == "ascending":
        reasons.append("Strong upward career progression across roles")
    else:
        reasons.append("Background warrants closer review against JD requirements")

    # ── STRENGTHS (always 4) ──────────────────────────────────────────────
    # 1. Skill depth / breadth
    if deep_skills:
        strengths.append(f"Deep multi-role expertise in: {', '.join(deep_skills[:3])}")
    elif len(matched) >= 5:
        strengths.append(f"Broad coverage across {len(matched)} required skills")
    elif matched:
        strengths.append(f"Relevant proficiency in {', '.join(matched[:3])}")
    else:
        strengths.append("Demonstrates foundational technical knowledge")

    # 2. Ownership / achievement / optimisation signal
    if achieve_score >= 60:
        strengths.append("Measurable business outcomes documented in resume")
    elif own_score >= 60:
        strengths.append("Proven ownership of production systems and stakeholder delivery")
    elif opt_score >= 60:
        strengths.append("Strong performance optimisation and ETL capability")
    elif achieve_score >= 30:
        strengths.append("Some evidence of impact — quantify further in interview")
    else:
        strengths.append("Technical depth to be validated through assessment")

    # 3. Career trajectory / stability
    if progression["trend"] == "ascending":
        strengths.append(f"Upward career trajectory — peak level: {progression.get('peak_level', 'N/A')}")
    elif avg_tenure >= 2.5:
        strengths.append(f"Highly stable employment history ({avg_tenure}y average tenure)")
    elif avg_tenure >= 1.5:
        strengths.append(f"Reasonable job stability ({avg_tenure}y avg tenure per role)")
    else:
        strengths.append("Career breadth across multiple organisations and contexts")

    # 4. Experience vs requirement
    if min_exp > 0:
        if exp_score >= 80:
            strengths.append(f"Experience significantly exceeds the {int(min_exp)}y requirement")
        elif exp_score >= 60:
            strengths.append(f"Experience meets the {int(min_exp)}y requirement")
        else:
            strengths.append(f"Experience partially meets the {int(min_exp)}y requirement — verify scope")
    elif domain_years > 0:
        strengths.append(f"{int(domain_years)}y of domain-specific experience confirmed")
    elif total_years >= 5:
        strengths.append(f"{int(total_years)}y of overall experience — assess domain relevance")
    else:
        strengths.append("Experience level to be assessed against role complexity")

    # ── GAPS (always 4) ───────────────────────────────────────────────────
    # 1. Skill gaps
    if missing:
        gaps.append(f"Missing required skills: {', '.join(missing[:4])}")
    else:
        gaps.append("All required skills present — verify depth and recency in interview")

    # 2. Experience / domain gap
    if min_exp > 0 and 0 < total_years < min_exp:
        gaps.append(f"Total experience ({int(total_years)}y) is below the {int(min_exp)}y requirement")
    elif domain_years == 0 and total_years > 0 and matched:
        gaps.append("Domain-specific experience not explicitly confirmed in resume")
    elif domain_years > 0 and total_years > 0 and (domain_years / total_years) < 0.4:
        pct = int(domain_years / total_years * 100)
        gaps.append(f"Only {pct}% of experience is domain-relevant ({int(domain_years)}y of {int(total_years)}y)")
    else:
        gaps.append("Validate depth and recency of domain-specific experience")

    # 3. Evidence / impact gap
    if achieve_score < 30:
        gaps.append("No quantified impact statements — request metrics during interview")
    elif own_score < 30:
        gaps.append("Limited ownership signals — probe decision-making scope in interview")
    elif short_stints >= 2:
        gaps.append(f"{short_stints} short-tenure roles detected — assess retention risk")
    else:
        gaps.append("Confirm project scale, team size, and individual contribution scope")

    # 4. Stability / progression / seniority gap
    if short_stints >= 2 and achieve_score >= 30:
        gaps.append(f"{short_stints} roles under 1 year — evaluate commitment and fit")
    elif progression["trend"] == "descending":
        gaps.append("Career trajectory appears downward — understand context and motivation")
    elif own_score < 40 and total_years >= 4:
        gaps.append("Limited leadership or ownership evidence for the seniority level expected")
    else:
        gaps.append("Assess motivation, cultural fit, and long-term growth alignment")

    return {"reasons": reasons[:4], "strengths": strengths[:4], "gaps": gaps[:4]}


def _match_summary(
    match_label: str,
    matched: list,
    missing: list,
    total_years: float,
    domain_years: float,
    min_exp: float,
    composite: float,
    relevance_ratio: float = 0.0,
) -> str:
    parts = []

    # Skills narrative
    total_skills = len(matched) + len(missing)
    if total_skills:
        if matched:
            skill_names = ", ".join(matched[:3]) + ("..." if len(matched) > 3 else "")
            parts.append(f"Matches {len(matched)}/{total_skills} required skills ({skill_names})")
        else:
            missing_names = ", ".join(missing[:3]) + ("..." if len(missing) > 3 else "")
            parts.append(f"Missing required skills: {missing_names}")

    # Experience narrative — distinguish relevant vs total
    active_years = domain_years if domain_years > 0 else total_years
    if active_years > 0:
        if domain_years > 0 and total_years > domain_years:
            pct = int(relevance_ratio * 100) if relevance_ratio > 0 else int(domain_years / total_years * 100)
            exp_label = f"{int(domain_years)}y relevant / {int(total_years)}y total ({pct}% relevant)"
        else:
            exp_label = f"{int(active_years)}y experience"

        if min_exp > 0:
            if active_years >= min_exp * 1.5:
                parts.append(f"{exp_label} — well above the {int(min_exp)}y requirement")
            elif active_years >= min_exp:
                parts.append(f"{exp_label} — meets the {int(min_exp)}y requirement")
            else:
                parts.append(f"{exp_label} — below the {int(min_exp)}y requirement")
        else:
            parts.append(exp_label)

    if parts:
        return ". ".join(parts) + "."
    return f"{match_label} based on overall semantic alignment with the role."


def _domain_alignment_score(jd_cluster: str, resume_meta: dict, exp_json: list) -> int:
    """
    Score 0-100: how well the candidate's career domain aligns with the JD cluster.
    Uses resume cluster metadata first, then falls back to job title keyword matching.
    """
    seniority_meta = (resume_meta or {}).get("seniority") or {}
    resume_cluster = seniority_meta.get("job_cluster") or ""

    if jd_cluster and resume_cluster:
        if jd_cluster == resume_cluster:
            return 92
        COMPATIBLE = {
            "data_science": {"engineering", "data_science"},
            "engineering":  {"engineering", "data_science"},
            "management":   {"management", "engineering", "hr"},
            "hr":           {"hr", "management"},
            "finance":      {"finance", "management"},
        }
        if resume_cluster in COMPATIBLE.get(jd_cluster, set()):
            return 75

    DOMAIN_KW: dict = {
        "data_science": ["data", "ml", "machine learning", "ai ", "analyst", "scientist", "nlp",
                         "deep learning", "llm", "analytics", "intelligence", "research", "engineer"],
        "engineering":  ["engineer", "developer", "devops", "backend", "frontend", "sre", "cloud",
                         "architect", "software", "sde", "swe", "platform"],
        "management":   ["manager", "head", "lead", "director", "vp", "chief"],
        "hr":           ["hr", "recruiter", "talent", "people", "human resources"],
        "marketing":    ["marketing", "growth", "brand", "content", "seo", "digital"],
        "sales":        ["sales", "account executive", "business development", "bdr", "sdr"],
        "finance":      ["finance", "accountant", "cfo", "controller", "treasury"],
    }
    kws = DOMAIN_KW.get(jd_cluster or "other", [])
    if not kws:
        return 50

    matching_roles = sum(
        1 for job in (exp_json or [])
        if any(kw in (job.get("title") or "").lower() for kw in kws)
    )
    if matching_roles >= 2:
        return 88
    if matching_roles == 1:
        return 68
    return 40


def _skill_depth_score(depth_info: dict) -> int:
    """
    Score 0-100: how deeply each matched skill is embedded in the candidate's career.
    Based on role-count confidence tiers from the evidence confidence table.
    """
    if not depth_info:
        return 40  # No depth data — skills-section mention only
    scores = []
    for role_count in depth_info.values():
        if role_count >= 3:
            scores.append(100)  # Multi-role + production deployment
        elif role_count == 2:
            scores.append(80)   # Experience + measurable impact
        elif role_count == 1:
            scores.append(65)   # Mentioned in at least one work experience role
        else:
            scores.append(40)   # Skills section only
    return round(sum(scores) / len(scores))


async def _llm_ats_evaluate(
    jd_title: str,
    must_have_skills: list,
    nice_to_have_skills: list,
    jd_description: str,
    jd_exp_level: str,
    candidate_title: str,
    candidate_skills: set,
    exp_json: list,
    raw_text_snippet: str,
    total_years: float,
) -> Optional[dict]:
    """
    GPT-4o-mini semantic ATS evaluation across 4 dimensions.
    Handles skill synonyms (GPT-4→LLM, LangChain→GenAI framework, etc.).
    Returns scored dict or None on failure.
    """
    skills_str = ", ".join(must_have_skills[:15]) if must_have_skills else "Not specified"
    nice_str   = ", ".join(nice_to_have_skills[:8]) if nice_to_have_skills else "None"

    exp_lines = []
    for job in (exp_json or [])[:4]:
        skills_used = ", ".join((job.get("skills_used") or [])[:6])
        exp_lines.append(
            f"- {job.get('title','')} @ {job.get('company','')} "
            f"({job.get('start_date','')}–{job.get('end_date','Present')}): {skills_used}"
        )
    exp_summary = "\n".join(exp_lines) or "Not provided"

    cand_skills_str = ", ".join(sorted(candidate_skills)[:20]) or "Not listed"
    text_snippet    = (raw_text_snippet or "")[:600]

    prompt = f"""You are an expert ATS (Applicant Tracking System) evaluator. Score this candidate.

JOB: {jd_title} [{jd_exp_level or 'mid'} level]
REQUIRED SKILLS: {skills_str}
NICE TO HAVE: {nice_str}
JD DESCRIPTION: {jd_description[:350] if jd_description else 'N/A'}

CANDIDATE: {candidate_title or 'Unknown'} | {total_years:.1f}y experience
SKILLS DETECTED: {cand_skills_str}
WORK HISTORY:
{exp_summary}
RESUME EXCERPT: {text_snippet}

CRITICAL: Apply semantic normalization when scoring skills:
- "GPT-4", "GPT", "ChatGPT", "Claude", "Gemini" → counts for "LLMs" or "generative AI"
- "LangChain", "LlamaIndex", "CrewAI" → counts for "GenAI frameworks" / "AI pipelines"
- "Hugging Face", "Transformers", "BERT", "T5" → counts for "NLP" / "deep learning"
- "PyTorch", "TensorFlow", "Keras" → counts for "deep learning" / "ML frameworks"
- "RAG", "vector DB", "Pinecone", "Chroma", "Weaviate" → counts for "AI/ML engineering"
- "AI Engineer", "ML Engineer" → counts for "data science" domain
- "Power BI", "Tableau", "Looker" → counts for "data analysis" / "BI"

Return ONLY valid JSON (no markdown, no explanation):
{{
  "skill_match": <0-100: % of required skills covered counting semantic equivalents>,
  "experience_relevance": <0-100: relevance and depth of actual work experience for THIS role>,
  "impact_quality": <0-100: quantified achievements, production deployments, ownership signals>,
  "domain_alignment": <0-100: career domain fit with the JD>,
  "matched_skills": [<up to 8 skills from required list found semantically in candidate>],
  "missing_skills": [<up to 5 required skills clearly absent>],
  "key_strength": "<one sentence: biggest strength for this role>",
  "key_gap": "<one sentence: most important gap, or empty string if strong match>"
}}"""

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=600,
        )
        result = json.loads(resp.choices[0].message.content)
        for key in ("skill_match", "experience_relevance", "impact_quality", "domain_alignment"):
            if key in result:
                result[key] = max(0, min(100, int(result[key])))
        return result
    except Exception as e:
        print(f"[llm_ats] evaluation failed: {e}")
        return None


# ── Cross-Encoder: lazy-loaded singleton ─────────────────────────────────────
_ce_model = None


def _load_cross_encoder():
    """Load cross-encoder/ms-marco-MiniLM-L-6-v2 once per process (CPU-friendly, ~85 MB)."""
    global _ce_model
    if _ce_model is None:
        try:
            from sentence_transformers import CrossEncoder
            _ce_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
            print("[CrossEncoder] Loaded: cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            print(f"[CrossEncoder] Load failed ({e}) — re-ranking will be skipped")
            _ce_model = False  # sentinel: don't retry
    return _ce_model if _ce_model else None


def _cross_encoder_rerank(
    jd_query: str,
    candidate_signals: list,
    top_n: int,
    loop,
) -> list:
    """
    Score each (jd_query, candidate_snippet) pair with the cross-encoder.
    Returns candidate_signals reordered by score; top_n candidates are flagged
    for expensive LLM evaluation, the rest get rule-based-only scoring.
    Runs the CPU-bound inference in a thread pool to keep the event loop free.
    """
    ce = _load_cross_encoder()
    if ce is None:
        # No cross-encoder available — send all to LLM (unchanged behaviour)
        for sig in candidate_signals:
            sig["llm_eligible"] = True
        return candidate_signals

    pairs = [
        (jd_query, sig.get("ce_snippet", ""))
        for sig in candidate_signals
    ]

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        import asyncio
        scores = loop.run_until_complete(
            asyncio.get_event_loop().run_in_executor(ex, ce.predict, pairs)
        ) if False else ce.predict(pairs)   # synchronous — called from sync context

    for sig, score in zip(candidate_signals, scores):
        sig["ce_score"] = float(score)

    reranked = sorted(candidate_signals, key=lambda x: x.get("ce_score", 0.0), reverse=True)
    for i, sig in enumerate(reranked):
        sig["llm_eligible"] = i < top_n
    return reranked


class FetchAndAlignUseCase:
    """
    ELITE MATCHING ENGINE v10 — Hybrid Search + Cross-Encoder + 7-Component ATS
    Pipeline: Hybrid(Vector+BM25 RRF) → Cross-Encoder Re-rank → LLM ATS Eval
    - Vector search (top 200) + PostgreSQL BM25 → Reciprocal Rank Fusion → top 50
    - Cross-encoder/ms-marco-MiniLM-L-6-v2 re-ranks top 50 → selects top 20 for LLM
    - Remaining candidates scored rule-based only (no LLM cost)
    - 7-component dynamic weights across 53 cluster profiles
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _bm25_search(self, query_text: str, company_id: str, allowed_ids: list, limit: int = 200) -> list:
        """
        PostgreSQL full-text search (BM25-style ts_rank_cd) over resume raw_text.
        Scoped to allowed_ids (resumes submitted for the active job).
        Returns list of (resume_id, bm25_score) tuples, best first.
        Falls back to empty list if query is too short or FTS fails.
        """
        if not query_text or len(query_text.strip()) < 3 or not allowed_ids:
            return []
        try:
            bm25_sql = text("""
                SELECT r.id AS resume_id,
                       ts_rank_cd(
                           to_tsvector('english', COALESCE(r.raw_text, '')),
                           plainto_tsquery('english', :query)
                       ) AS bm25_score
                FROM resumes r
                JOIN memories m ON m.resume_id = r.id
                WHERE m.company_id  = :company_id
                  AND r.is_active   = TRUE
                  AND m.is_active   = TRUE
                  AND r.id          = ANY(:allowed_ids)
                  AND to_tsvector('english', COALESCE(r.raw_text, ''))
                      @@ plainto_tsquery('english', :query)
                GROUP BY r.id
                ORDER BY bm25_score DESC
                LIMIT :limit
            """)
            result = await self.db.execute(bm25_sql, {
                "query": query_text,
                "company_id": company_id,
                "allowed_ids": allowed_ids,
                "limit": limit,
            })
            return [(row[0], float(row[1])) for row in result.all()]
        except Exception as e:
            print(f"[BM25] Search failed: {e}")
            return []

    async def execute(self, job_id: str, company_id: str, top_k: int = 10, rerank_threshold: float = 60.0) -> List[Dict]:
        # ── 0. Resolve allowed resume IDs for this job (job-scoped scan) ──
        from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel, SubmissionStatus
        sub_res = await self.db.execute(
            select(CandidateSubmissionModel.resume_id)
            .where(
                CandidateSubmissionModel.job_id == job_id,
                CandidateSubmissionModel.resume_id != None,
                CandidateSubmissionModel.status != SubmissionStatus.WITHDRAWN,
            )
        )
        allowed_resume_ids: list = [row[0] for row in sub_res.all()]
        if not allowed_resume_ids:
            return []   # No resumes submitted for this job yet

        # ── 1. Active JD version ──────────────────────────────────────────
        res = await self.db.execute(
            select(JobVersionModel)
            .where(JobVersionModel.job_id == job_id, JobVersionModel.is_active == True)
            .order_by(JobVersionModel.version.desc()).limit(1)
        )
        job_version = res.scalar_one_or_none()
        if not job_version:
            raise ValueError("No active job version found")

        reqs            = job_version.requirements_json or {}
        jd_title        = job_version.title or ""
        jd_description  = job_version.description or ""

        must_have_skills    = reqs.get("must_have_skills")    or reqs.get("primary_skills") or []
        nice_to_have_skills = reqs.get("nice_to_have_skills") or []

        raw_skill_weights = reqs.get("must_have_skill_weights") or {}
        skill_weights = {_normalize_skill(k): float(v) for k, v in raw_skill_weights.items() if k and v}

        jd_scoring      = job_version.scoring_weights or {}
        exp_multiplier  = max(0.7, min(1.4, float(jd_scoring.get("experience_multiplier") or 1.0)))
        min_exp         = float((reqs.get("experience") or {}).get("min") or 0)
        jd_exp_level    = reqs.get("experience_level") or ""

        # ── 2. JD embedding ───────────────────────────────────────────────
        res = await self.db.execute(
            select(MemoryModel.embedding, MemoryModel.cluster)
            .where(MemoryModel.job_version_id == job_version.id, MemoryModel.chunk_type == "job_summary")
            .limit(1)
        )
        jd_memory = res.first()
        if not jd_memory:
            raise ValueError("JD embedding missing — please re-upload the JD.")
        jd_embedding, jd_cluster = jd_memory

        jd_vector_list = jd_embedding.tolist() if hasattr(jd_embedding, "tolist") else jd_embedding
        jd_vector_str  = f"[{','.join(map(str, jd_vector_list))}]"

        # ── 3. Hybrid Retrieval: Vector + BM25 → Reciprocal Rank Fusion ─────
        VECTOR_POOL  = max(200, top_k * 20)   # large vector pool for high recall
        BM25_POOL    = 200
        RRF_K        = 60                      # standard RRF constant
        CE_TOP_N     = min(30, VECTOR_POOL)    # candidates sent to cross-encoder
        LLM_TOP_N    = 20                      # candidates sent to LLM after CE rerank

        vector_query = text("""
            SELECT * FROM (
                SELECT DISTINCT ON (r.id)
                    r.id              AS resume_id,
                    r.candidate_id,
                    r.skills_json,
                    r.education_json,
                    r.experience_json,
                    r.raw_text,
                    r.title           AS current_role,
                    r.metadata_json   AS resume_metadata,
                    c.first_name, c.last_name, c.email, c.phone, c.linkedin_url,
                    (1 - (m.embedding <=> :jd_vector)) AS best_similarity
                FROM memories m
                JOIN resumes r ON m.resume_id = r.id
                JOIN candidates c ON r.candidate_id = c.id
                WHERE m.entity_type = 'resume_chunk'
                  AND m.company_id  = :company_id
                  AND r.is_active   = True
                  AND m.is_active   = True
                  AND r.id          = ANY(:allowed_ids)
                ORDER BY r.id, best_similarity DESC
            ) best_chunks
            ORDER BY best_similarity DESC
            LIMIT :limit
        """)

        # Build BM25 query string from JD skills + title
        bm25_query_text = " ".join(
            [jd_title] + must_have_skills[:12] + nice_to_have_skills[:5]
        ).strip()

        # Run vector search and BM25 in parallel — both scoped to allowed_resume_ids
        vector_result, bm25_results = await asyncio.gather(
            self.db.execute(vector_query, {
                "jd_vector": jd_vector_str,
                "company_id": company_id,
                "allowed_ids": allowed_resume_ids,
                "limit": VECTOR_POOL,
            }),
            self._bm25_search(bm25_query_text, company_id, allowed_resume_ids, BM25_POOL),
        )
        vector_rows = vector_result.mappings().all()

        # Build lookup maps for RRF
        vector_rank_map: Dict[str, int] = {
            row["resume_id"]: rank for rank, row in enumerate(vector_rows)
        }
        bm25_rank_map: Dict[str, int] = {
            rid: rank for rank, (rid, _) in enumerate(bm25_results)
        }

        # Collect all unique resume_ids across both lists
        all_ids = list(dict.fromkeys(
            [r["resume_id"] for r in vector_rows] +
            [rid for rid, _ in bm25_results]
        ))

        # RRF score: 1/(k+rank_vector) + 1/(k+rank_bm25)
        rrf_scores: Dict[str, float] = {}
        for rid in all_ids:
            score = 0.0
            if rid in vector_rank_map:
                score += 1.0 / (RRF_K + vector_rank_map[rid] + 1)
            if rid in bm25_rank_map:
                score += 1.0 / (RRF_K + bm25_rank_map[rid] + 1)
            rrf_scores[rid] = score

        # Reorder vector rows by RRF score; BM25-only rows need a separate fetch
        vector_row_map: Dict[str, any] = {r["resume_id"]: r for r in vector_rows}
        bm25_only_ids = [rid for rid, _ in bm25_results if rid not in vector_row_map]

        # Fetch BM25-only candidates (not retrieved by vector search)
        extra_rows: list = []
        if bm25_only_ids:
            extra_sql = text("""
                SELECT DISTINCT ON (r.id)
                    r.id AS resume_id, r.candidate_id,
                    r.skills_json, r.education_json, r.experience_json,
                    r.raw_text, r.title AS current_role,
                    r.metadata_json AS resume_metadata,
                    c.first_name, c.last_name, c.email, c.phone, c.linkedin_url,
                    0.0 AS best_similarity
                FROM resumes r
                JOIN candidates c ON r.candidate_id = c.id
                WHERE r.id = ANY(:ids) AND r.is_active = TRUE
            """)
            extra_result = await self.db.execute(extra_sql, {"ids": bm25_only_ids})
            extra_rows = extra_result.mappings().all()
            for row in extra_rows:
                vector_row_map[row["resume_id"]] = row

        # Final ordered candidate pool (by RRF score, descending)
        ordered_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        candidates = [vector_row_map[rid] for rid in ordered_ids if rid in vector_row_map]

        print(f"[Hybrid] vector={len(vector_rows)} bm25={len(bm25_results)} "
              f"bm25_only={len(extra_rows)} merged={len(candidates)}")

        norm_years = DOMAIN_EXP_NORMS.get(jd_cluster or "other", 6.0)
        w = ATS_WEIGHTS_BY_CLUSTER.get(jd_cluster or "other", ATS_WEIGHTS_BY_CLUSTER["other"])

        # JD query string for cross-encoder (richer than BM25 query)
        jd_ce_query = (
            f"{jd_title}. Required: {', '.join(must_have_skills[:10])}. "
            f"{jd_description[:200]}"
        ).strip()

        # ── 4. First pass: rule-based signal collection ───────────────────
        # Collect all signals without LLM so we can run LLM evals in parallel after.
        candidate_signals: List[dict] = []

        for cand in candidates:
            similarity       = float(cand["best_similarity"])
            semantic_boosted = (similarity ** 0.5) * 0.85 + 0.1
            semantic_score   = round(min(100, semantic_boosted * 100))

            raw_text       = cand.get("raw_text") or ""
            meta           = cand["resume_metadata"] or {}
            seniority_meta = meta.get("seniority") or {}

            source_a   = {s.lower() for s in (cand["skills_json"] or [])}
            source_b   = SkillOntology.extract_skills_from_text(raw_text)
            cand_skills = source_a | source_b

            exp_json = cand.get("experience_json") or []

            # Skills matching (4-tier + ontology)
            if must_have_skills:
                must_matched, must_missing, must_score, depth_info = _skill_match(
                    must_have_skills, cand_skills, raw_text,
                    skill_weights=skill_weights, exp_json=exp_json
                )
            else:
                must_matched, must_missing, must_score, depth_info = [], [], 0, {}

            if nice_to_have_skills:
                nice_matched, _, nice_score, _ = _skill_match(nice_to_have_skills, cand_skills, raw_text)
            else:
                nice_matched, nice_score = [], 0

            if must_have_skills:
                rule_skill_score = round(must_score * 0.80 + nice_score * 0.20)
                if must_score < 50:
                    rule_skill_score = min(35, rule_skill_score)
            elif nice_to_have_skills:
                rule_skill_score = nice_score
            else:
                rule_skill_score = round(semantic_boosted * 100)

            rule_matched = sorted(set(must_matched) | set(nice_matched))
            rule_missing = must_missing

            # Experience analysis
            meta_years  = float(seniority_meta.get("total_years") or 0)
            json_years  = _years_from_experience_json(exp_json)
            text_years  = _years_from_text(raw_text)
            total_years = max(meta_years, json_years, text_years)

            # Hard filter: clearly underqualified
            if min_exp > 0 and 0 < total_years < min_exp:
                continue

            jd_skills_norm = {_normalize_skill(s) for s in must_have_skills if s}
            exp_analysis   = _weighted_relevant_experience(exp_json, jd_skills_norm) if must_have_skills else {
                "relevant_years": 0.0, "raw_domain_years": 0.0,
                "relevance_ratio": 0.0, "role_breakdown": []
            }
            weighted_rel_years = exp_analysis["relevant_years"]
            domain_years       = exp_analysis["raw_domain_years"]
            relevance_ratio    = exp_analysis["relevance_ratio"]
            role_breakdown     = exp_analysis["role_breakdown"]
            scoring_years      = weighted_rel_years if weighted_rel_years > 0 else total_years

            # Experience score — role-aware normalization (fixes the /8.0 bug)
            if min_exp > 0 and scoring_years > 0:
                if domain_years == 0 and total_years >= min_exp:
                    rule_exp_score = 65
                else:
                    ratio = scoring_years / min_exp
                    rule_exp_score = round(min(100, 55 + ratio * 45)) if ratio >= 1 else round(ratio * 85)
            elif scoring_years > 0:
                # Role-aware: 0y→35, norm_years→100 (e.g. data_science norm=5y)
                rule_exp_score = round(min(100, 35 + (scoring_years / norm_years) * 65))
            else:
                rule_exp_score = min(75, round(semantic_boosted * 85))
            rule_exp_score = min(100, round(rule_exp_score * exp_multiplier))

            # Signal scores
            opt_score     = _optimization_score(raw_text)
            own_score     = _ownership_score(raw_text)
            achieve_score = _achievement_score(raw_text)

            stability   = _job_stability_analysis(exp_json)
            progression = _career_progression_analysis(exp_json)

            cand_raw_level  = seniority_meta.get("raw_level") or "mid"
            seniority_sc    = _seniority_score(cand_raw_level, jd_exp_level)
            rule_domain     = _domain_alignment_score(jd_cluster, meta, exp_json)
            # Evidence Score: quantified achievements + ownership (pattern-based)
            evidence_score_r    = round(achieve_score * 0.6 + own_score * 0.4)
            # Project Complexity: architectural depth + optimization + production signals
            project_cmplx_r     = round(own_score * 0.5 + opt_score * 0.3 + achieve_score * 0.2)
            # Skill Depth: role-count confidence tiers across matched skills
            skill_depth_sc      = _skill_depth_score(depth_info)

            # Review flags (pre-compute for final output)
            review_flags = []
            if domain_years == 0 and total_years > 0 and must_have_skills:
                review_flags.append("Domain-specific experience years not verified — using total career years")
            if source_b - source_a and any(s in rule_matched for s in source_b - source_a):
                review_flags.append("Some skills matched via resume text scan — confirm in resume document")
            if must_score < 50 and must_have_skills:
                review_flags.append(f"Missing {len(must_missing)} must-have skill(s): {', '.join(must_missing[:3])}")
            shallow = [s for s, d in depth_info.items() if d == 1]
            if len(shallow) >= 2:
                review_flags.append(f"Limited role depth on: {', '.join(shallow[:3])}")
            if stability["flag"]:
                review_flags.append(stability["flag"])
            if progression["flag"]:
                review_flags.append(progression["flag"])

            brief = _generate_candidate_brief(
                matched=must_matched, missing=must_missing, total_years=total_years,
                domain_years=domain_years, min_exp=min_exp, opt_score=opt_score,
                own_score=own_score, achieve_score=achieve_score, stability=stability,
                progression=progression, exp_score=rule_exp_score, depth_info=depth_info,
                nice_matched=nice_matched,
            )

            candidate_signals.append({
                "cand":              cand,
                "semantic_score":    semantic_score,
                "semantic_boosted":  semantic_boosted,
                "rule_skill_score":  rule_skill_score,
                "rule_exp_score":    rule_exp_score,
                "evidence_score_r":  evidence_score_r,
                "project_cmplx_r":   project_cmplx_r,
                "skill_depth_sc":    skill_depth_sc,
                "rule_domain":       rule_domain,
                "seniority_sc":      seniority_sc,
                "cand_raw_level":    cand_raw_level,
                "rule_matched":      rule_matched,
                "rule_missing":      rule_missing,
                "must_matched":      must_matched,
                "must_missing":      must_missing,
                "nice_matched":      nice_matched,
                "must_score":        must_score,
                "nice_score":        nice_score,
                "depth_info":        depth_info,
                "total_years":       total_years,
                "domain_years":      domain_years,
                "weighted_rel_years": weighted_rel_years,
                "relevance_ratio":   relevance_ratio,
                "role_breakdown":    role_breakdown,
                "opt_score":         opt_score,
                "own_score":         own_score,
                "achieve_score":     achieve_score,
                "stability":         stability,
                "progression":       progression,
                "cand_skills":       cand_skills,
                "exp_json":          exp_json,
                "raw_text":          raw_text,
                "review_flags":      review_flags,
                "brief":             brief,
                # Snippet for cross-encoder: title + skills + text excerpt
                "ce_snippet": (
                    f"{cand.get('current_role') or ''} | "
                    f"Skills: {', '.join(list(cand_skills)[:15])} | "
                    f"{raw_text[:400]}"
                ),
                "rrf_score":         rrf_scores.get(cand.get("resume_id"), 0.0),
            })

        # ── 5. Cross-Encoder Re-ranking ───────────────────────────────────
        # Score each (jd_query, candidate_snippet) pair with the cross-encoder.
        # Top LLM_TOP_N get full LLM evaluation; the rest are scored rule-only.
        if jd_ce_query and candidate_signals:
            import concurrent.futures
            import functools
            ce = _load_cross_encoder()
            if ce is not None:
                pairs = [(jd_ce_query, sig["ce_snippet"]) for sig in candidate_signals]
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    ce_scores = await loop.run_in_executor(
                        ex, functools.partial(ce.predict, pairs)
                    )
                for sig, score in zip(candidate_signals, ce_scores):
                    sig["ce_score"] = float(score)
                candidate_signals.sort(key=lambda x: x.get("ce_score", 0.0), reverse=True)
                print(f"[CrossEncoder] Re-ranked {len(candidate_signals)} candidates; "
                      f"top score={candidate_signals[0]['ce_score']:.3f}")
            else:
                for sig in candidate_signals:
                    sig["ce_score"] = sig["rrf_score"]

        # Mark which candidates get LLM evaluation (top LLM_TOP_N after CE rerank)
        for i, sig in enumerate(candidate_signals):
            sig["llm_eligible"] = i < LLM_TOP_N

        # ── 6. Parallel LLM ATS evaluation (LLM-eligible candidates only) ─
        # GPT-4o-mini evaluates top candidates; rest are scored rule-based only.
        llm_eligible = [sig for sig in candidate_signals if sig["llm_eligible"]]
        llm_tasks = [
            _llm_ats_evaluate(
                jd_title=jd_title,
                must_have_skills=must_have_skills,
                nice_to_have_skills=nice_to_have_skills,
                jd_description=jd_description,
                jd_exp_level=jd_exp_level,
                candidate_title=sig["cand"].get("current_role") or "",
                candidate_skills=sig["cand_skills"],
                exp_json=sig["exp_json"],
                raw_text_snippet=sig["raw_text"][:1000],
                total_years=sig["total_years"],
            )
            for sig in llm_eligible
        ]
        llm_results_eligible = await asyncio.gather(*llm_tasks, return_exceptions=True)

        # Build full llm_results list aligned with candidate_signals
        llm_result_map: Dict[int, any] = {}
        eligible_iter = iter(llm_results_eligible)
        for i, sig in enumerate(candidate_signals):
            if sig["llm_eligible"]:
                llm_result_map[i] = next(eligible_iter)
            else:
                llm_result_map[i] = None  # rule-based only

        print(f"[LLM] Evaluated {len(llm_eligible)}/{len(candidate_signals)} candidates")

        # ── 7. Second pass: blend LLM + rule-based → 7-component composite ──
        matches: List[dict] = []

        for i, sig in enumerate(candidate_signals):
            llm_raw = llm_result_map.get(i)
            cand = sig["cand"]
            llm  = llm_raw if isinstance(llm_raw, dict) else None

            # Component 1 — Skill Match (25%): LLM semantic 60% + rule-based 40%
            if llm and llm.get("skill_match") is not None:
                skill_component = round(llm["skill_match"] * 0.60 + sig["rule_skill_score"] * 0.40)
                matched = llm.get("matched_skills") or sig["rule_matched"]
                missing = llm.get("missing_skills") or sig["rule_missing"]
            else:
                skill_component = sig["rule_skill_score"]
                matched = sig["rule_matched"]
                missing = sig["rule_missing"]

            # Component 2 — Experience Relevance (20%): LLM 70% + rule 30%
            if llm and llm.get("experience_relevance") is not None:
                exp_component = round(llm["experience_relevance"] * 0.70 + sig["rule_exp_score"] * 0.30)
            else:
                exp_component = sig["rule_exp_score"]

            # Component 3 — Semantic Similarity (15%): pure vector similarity
            semantic_component = sig["semantic_score"]

            # Component 4 — Evidence Score (10%): quantified achievements + ownership (rule-based)
            evidence_component = sig["evidence_score_r"]

            # Component 5 — Skill Depth (10%): role-count confidence tiers (rule-based)
            depth_component = sig["skill_depth_sc"]

            # Component 6 — Project Complexity (7%): architecture/optimization/production (rule-based)
            complexity_component = sig["project_cmplx_r"]

            # Component 7 — Impact Quality (5%): LLM-evaluated business impact
            if llm and llm.get("impact_quality") is not None:
                impact_component = llm["impact_quality"]
            else:
                impact_component = sig["evidence_score_r"]

            # Component 8 — Domain Alignment (5%): LLM 70% + rule 30%
            if llm and llm.get("domain_alignment") is not None:
                domain_component = round(llm["domain_alignment"] * 0.70 + sig["rule_domain"] * 0.30)
            else:
                domain_component = sig["rule_domain"]

            # Component 9 — Seniority Fit (3%): rule-based only
            seniority_component = sig["seniority_sc"]

            # Weighted composite — 7-component ATS formula (weights by job cluster)
            # skill_depth and project_complexity are informational signals only
            composite = round(min(98.5, max(10.0,
                skill_component    * w["skill_match"]          +
                exp_component      * w["experience_relevance"] +
                semantic_component * w["semantic_similarity"]  +
                evidence_component * w["evidence_score"]       +
                impact_component   * w["impact"]               +
                domain_component   * w["domain_match"]         +
                seniority_component * w["seniority_fit"]
            )))

            # Enrich candidate brief with LLM insights
            brief = sig["brief"]
            if llm:
                if llm.get("key_strength"):
                    brief["reasons"] = [llm["key_strength"]] + (brief.get("reasons") or [])[:1]
                if llm.get("key_gap"):
                    brief["gaps"] = [llm["key_gap"]] + (brief.get("gaps") or [])[:1]

            avg_depth = (sum(sig["depth_info"].values()) / len(sig["depth_info"])) if sig["depth_info"] else 0
            if sig["must_score"] >= 70 and (avg_depth >= 2 or sig["total_years"] > 0):
                confidence = "high"
            elif sig["must_score"] >= 40 or avg_depth >= 1 or sig["total_years"] > 0:
                confidence = "medium"
            else:
                confidence = "low"

            review_flags = sig["review_flags"]
            if composite >= 65 and sig["must_score"] < 40:
                review_flags = ["High semantic alignment but low rule-based skill coverage — verify manually"] + review_flags

            summary = _match_summary(
                match_label=_match_label(composite),
                matched=sig["must_matched"],
                missing=sig["must_missing"],
                total_years=sig["total_years"],
                domain_years=sig["domain_years"],
                min_exp=min_exp,
                composite=composite,
                relevance_ratio=sig["relevance_ratio"],
            )

            matches.append({
                "resume_id":    cand["resume_id"],
                "candidate_id": cand["candidate_id"],
                "first_name":   cand["first_name"],
                "last_name":    cand["last_name"],
                "email":        cand["email"],
                "phone":        cand.get("phone"),
                "linkedin_url": cand.get("linkedin_url"),
                "role":         cand["current_role"] or "Applicant",
                "composite_score": composite,
                "match_label":  _match_label(composite),
                "match_summary": summary,
                "confidence":   confidence,
                "review_flags": review_flags,
                "candidate_brief": brief,
                "scoring_breakdown": {
                    "skills": {
                        "weight": round(w["skill_match"] * 100), "score": skill_component,
                        "matched": matched, "missing": missing,
                        "must_score": sig["must_score"], "nice_score": sig["nice_score"],
                        "skill_depth": sig["depth_info"],
                    },
                    "experience": {
                        "weight": round(w["experience_relevance"] * 100), "score": exp_component,
                        "years": sig["total_years"], "domain_years": sig["domain_years"],
                        "weighted_relevant_years": sig["weighted_rel_years"],
                        "relevance_ratio": sig["relevance_ratio"],
                        "role_breakdown": sig["role_breakdown"],
                    },
                    "semantic":            {"weight": round(w["semantic_similarity"] * 100), "score": semantic_component},
                    "evidence_score":      {"weight": round(w["evidence_score"] * 100), "score": evidence_component,
                                            "achievement": sig["achieve_score"], "ownership": sig["own_score"]},
                    "skill_depth":         {"weight": 0, "score": depth_component, "depth_map": sig["depth_info"]},
                    "project_complexity":  {"weight": 0, "score": complexity_component,
                                            "opt": sig["opt_score"], "ownership": sig["own_score"]},
                    "impact":              {"weight": round(w["impact"] * 100), "score": impact_component},
                    "domain_match":        {"weight": round(w["domain_match"] * 100), "score": domain_component},
                    "seniority":           {"weight": round(w["seniority_fit"] * 100), "score": seniority_component,
                                            "level": sig["cand_raw_level"]},
                    "stability":           {"score": sig["stability"]["score"],
                                            "avg_tenure": sig["stability"]["avg_tenure"],
                                            "short_stints": sig["stability"]["short_stints"]},
                    "progression":         {"trend": sig["progression"]["trend"],
                                            "peak_level": sig["progression"]["peak_level"]},
                    "retrieval":           {
                                            "rrf_score":     round(sig.get("rrf_score", 0.0), 4),
                                            "ce_score":      round(sig.get("ce_score", 0.0), 3),
                                            "llm_evaluated": sig.get("llm_eligible", False),
                                            "vector_rank":   vector_rank_map.get(cand["resume_id"]),
                                            "bm25_rank":     bm25_rank_map.get(cand["resume_id"]),
                                           },
                },
            })

        ranked   = sorted(matches, key=lambda x: x["composite_score"], reverse=True)
        total    = len(ranked)
        filtered = sum(1 for m in ranked if m["composite_score"] < rerank_threshold)
        strong   = sum(1 for m in ranked if m["composite_score"] >= rerank_threshold)

        return {
            "stats": {
                "total": total,
                "matched": strong,
                "filtered": filtered,
                "role": jd_cluster,
                "seniority": jd_exp_level,
                "weight_profile": {k: round(v * 100) for k, v in w.items()},
                "pipeline": {
                    "vector_pool":   len(vector_rows),
                    "bm25_pool":     len(bm25_results),
                    "after_rrf":     len(candidates),
                    "ce_evaluated":  len(candidate_signals),
                    "llm_evaluated": len(llm_eligible),
                },
            },
            "matches": ranked[:top_k],
        }
