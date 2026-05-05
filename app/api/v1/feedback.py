from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List

from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User
from app.layer6_data.models.feedback_model import ApplicationFeedbackModel, FeedbackOutcome
import uuid

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackCreate(BaseModel):
    application_id: str
    outcome: FeedbackOutcome
    recruiter_score: Optional[float] = None
    recruiter_notes: Optional[str] = None
    feedback_tags: Optional[List[str]] = None

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
