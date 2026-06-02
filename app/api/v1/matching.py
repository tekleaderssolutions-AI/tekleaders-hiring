from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User
from app.layer4_application.matching.fetch_and_align import FetchAndAlignUseCase

router = APIRouter(prefix="/matching", tags=["Matching"])

@router.get(
    "/fetch-and-align/{job_id}",
    summary="Elite Matching Engine: Vector + Business Rules + LLM Reranking"
)
async def fetch_and_align(
    job_id: str,
    top_k: int = Query(10, ge=1, le=50),
    rerank_threshold: float = Query(60.0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triggers the high-level decision engine.
    Returns Top candidates with explainable strengths, gaps, and reasoning.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")

    # Scope AI scan to the current recruiter's own submissions; admins see all
    role = (current_user.role or "").lower().strip()
    recruiter_id = None if role == "admin" else current_user.id

    use_case = FetchAndAlignUseCase(db)
    try:
        results = await use_case.execute(
            job_id=job_id,
            company_id=current_user.company_id,
            top_k=top_k,
            rerank_threshold=rerank_threshold,
            recruiter_id=recruiter_id,
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI scan error: {str(e)}")
