from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_user
from app.layer4_application.resume.parse_resume import ParseResumeUseCase
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post(
    "/analyze",
    summary="Upload and analyze a single resume (PDF/DOCX)"
)
async def analyze_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    use_case = ParseResumeUseCase(db)
    content = await file.read()
    result = await use_case.execute_single(content, file.filename, current_user.id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post(
    "/bulk-analyze",
    summary="Upload a ZIP file containing multiple resumes"
)
async def bulk_analyze_resumes(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file for bulk analysis")
    
    use_case = ParseResumeUseCase(db)
    content = await file.read()
    results = await use_case.execute_bulk(content, current_user.id)
    
    return {
        "total_processed": len(results),
        "results": results
    }
