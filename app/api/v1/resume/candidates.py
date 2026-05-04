from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_user
from app.layer4_application.resume.parse_resume import ParseResumeUseCase
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post(
    "/upload",
    summary="Smart Upload: Handles single PDF/DOCX or Bulk ZIP files"
)
async def upload_resumes(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    use_case = ParseResumeUseCase(db)
    content = await file.read()
    filename = file.filename.lower()
    
    # 1. Check if it's a Bulk ZIP
    if filename.endswith(".zip"):
        results = await use_case.execute_bulk(content, current_user.id)
        return {
            "mode": "bulk",
            "total_processed": len(results),
            "results": results
        }
    
    # 2. Otherwise process as a Single File
    result = await use_case.execute_single(content, file.filename, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "mode": "single",
        "data": result
    }
