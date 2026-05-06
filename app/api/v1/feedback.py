from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any

from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User
from app.layer6_data.models.feedback_model import ApplicationFeedbackModel, FeedbackOutcome
import uuid

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackCreate(BaseModel):
    application_id: str
    outcome: Any
    recruiter_score: Optional[float] = None
    recruiter_notes: Optional[str] = None
    feedback_tags: Optional[List[str]] = None

    @model_validator(mode='before')
    @classmethod
    def normalize_outcome(cls, data: Any) -> Any:
        if isinstance(data, dict) and "outcome" in data:
            val = data["outcome"]
            if isinstance(val, str):
                data["outcome"] = val.lower().strip()
                # Check if it's a valid Enum member after normalization
                try:
                    data["outcome"] = FeedbackOutcome(data["outcome"])
                except ValueError:
                    pass # Let validation fail later if truly invalid
        return data

@router.post(
    "/outcome",
    status_code=status.HTTP_201_CREATED,
    summary="Log recruiter decision and feedback"
)
async def log_feedback(
    payload: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Closes the loop by storing manual decisions and AI overrides.
    """
    feedback = ApplicationFeedbackModel(
        id=str(uuid.uuid4()),
        application_id=payload.application_id,
        recruiter_id=current_user.id,
        outcome=payload.outcome,
        recruiter_score=payload.recruiter_score,
        recruiter_notes=payload.recruiter_notes,
        feedback_tags=payload.feedback_tags
    )
    db.add(feedback)
    await db.commit()
    return {"status": "success", "message": "Feedback captured for model improvement"}
