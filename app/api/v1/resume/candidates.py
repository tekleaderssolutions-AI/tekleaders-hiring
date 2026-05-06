from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies import get_db, get_current_user
from app.layer4_application.resume.parse_resume import ParseResumeUseCase
from app.layer5_domain.entities.user import User
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository

router = APIRouter(prefix="/candidates", tags=["Candidates"])

async def process_bulk_resumes(content: bytes, user_id: str):
    """Background task to process ZIP resumes with a fresh session"""
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        use_case = ParseResumeUseCase(db)
        await use_case.execute_bulk(content, user_id)
        await db.commit()

@router.post(
    "/upload",
    summary="Smart Upload: Handles single PDF/DOCX or Bulk ZIP files"
)
async def upload_resumes(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    use_case = ParseResumeUseCase(db)
    content = await file.read()
    filename = file.filename.lower()
    
    # 1. Check if it's a Bulk ZIP -> Run in Background
    if filename.endswith(".zip"):
        background_tasks.add_task(process_bulk_resumes, content, current_user.id)
        return {
            "mode": "bulk",
            "status": "processing",
            "message": "Your resumes are being processed in the background. Check back in a few minutes."
        }
    
    # 2. Otherwise process as a Single File
    result = await use_case.execute_single(content, file.filename, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "mode": "single",
        "data": result
    }

@router.get(
    "",
    summary="List all candidates"
)
async def list_candidates(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresCandidateRepository(db)
    candidates = await repo.list_candidates(limit=limit, offset=offset)
    return candidates

@router.get(
    "/{candidate_id}",
    summary="Get candidate details by ID"
)
async def get_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresCandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
