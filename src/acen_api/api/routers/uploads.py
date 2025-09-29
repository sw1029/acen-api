"""이미지 업로드 API."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ...schemas import ErrorResponse
from ..deps import get_storage, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    401: {"model": ErrorResponse, "description": "인증 필요"},
}


router = APIRouter(prefix="/uploads", tags=["uploads"], responses=error_responses)


@router.post("", dependencies=[Depends(require_api_key)])
async def upload_image(file: UploadFile = File(...), storage=Depends(get_storage)) -> dict:
    # 파일명과 내용 검증 및 저장
    try:
        data = await file.read()
        result = storage.save_bytes(data, filename=file.filename)
    except Exception as exc:  # StorageError 메시지 위임
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "path": str(result.path),
        "relative_path": str(result.relative_path),
        "content_type": result.content_type,
    }

