from fastapi import APIRouter, UploadFile, File, status
from app.services.document_service import validate_file
from app.schemas.document import UploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload", 
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse
)
async def upload(file: UploadFile = File(...)):
    result, file_bytes = await validate_file(file)
    return result
