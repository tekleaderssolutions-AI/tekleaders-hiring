from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import AsyncSessionLocal
from app.dependencies import get_db, get_current_user
from app.layer4_application.resume.parse_resume import ParseResumeUseCase
from app.layer5_domain.entities.user import User
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository

router = APIRouter(prefix="/candidates", tags=["Candidates"])

async def process_bulk_resumes(content: bytes, user_id: str, session_id: str = None):
    """Background task to process ZIP resumes with a fresh session and lively progress updates"""
    from app.database import AsyncSessionLocal
    from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
    from sqlalchemy import update
    
    async with AsyncSessionLocal() as db:
        use_case = ParseResumeUseCase(db)
        results = await use_case.execute_bulk(content, user_id)
        
        # ELITE UPDATE: Mark the tracking session as completed
        if session_id:
            success_count = len([r for r in results if r["status"] == "success"])
            await db.execute(
                update(BulkUploadModel)
                .where(BulkUploadModel.id == session_id)
                .values(processed_count=success_count, status="completed")
            )
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
        import zipfile
        import io
        import hashlib
        import uuid
        from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
        
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            filenames = [f for f in z.namelist() if f.lower().endswith(('.pdf', '.docx')) and not f.startswith('__MACOSX')]
            total_count = len(filenames)
            
            # Pre-scan for duplicates
            seen_hashes = set()
            unique_count = 0
            duplicate_count = 0
            for fname in filenames:
                with z.open(fname) as f:
                    f_hash = hashlib.md5(f.read()).hexdigest()
                    if f_hash in seen_hashes:
                        duplicate_count += 1
                    else:
                        seen_hashes.add(f_hash)
                        unique_count += 1
        
        # Create Tracking Session
        session_id = f"bulk_{str(uuid.uuid4())[:8]}"
        async with AsyncSessionLocal() as session:
            tracking = BulkUploadModel(
                id=session_id,
                user_id=current_user.id,
                total_files=total_count,
                unique_files=unique_count,
                duplicate_files=duplicate_count,
                status="processing"
            )
            session.add(tracking)
            await session.commit()

        background_tasks.add_task(process_bulk_resumes, content, current_user.id, session_id)
        return {
            "mode": "bulk",
            "session_id": session_id,
            "total_files": total_count,
            "unique_files": unique_count,
            "duplicate_files": duplicate_count,
            "message": f"Processing {unique_count} unique resumes. {duplicate_count} duplicates skipped."
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
    "/progress/{session_id}",
    summary="Get lively progress for a bulk upload session"
)
async def get_bulk_progress(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(BulkUploadModel).where(BulkUploadModel.id == session_id)
    )
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Bulk session not found")
        
    return {
        "session_id": tracking.id,
        "total": tracking.total_files,
        "unique": tracking.unique_files,
        "duplicates": tracking.duplicate_files,
        "processed": tracking.processed_count,
        "status": tracking.status
    }

@router.get(
    "/stats",
    summary="Get candidate processing stats"
)
async def get_candidate_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresCandidateRepository(db)
    count = await repo.count_candidates() # I will add this method to the repo
    return {"total_count": count}

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
