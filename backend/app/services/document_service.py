import os
import uuid
from fastapi import UploadFile, HTTPException, status

MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

async def validate_file(file: UploadFile) -> dict:
    filename = file.filename
    _, ext = os.path.splitext(filename.lower())
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимы только PDF и DOCX"
        )
        
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает 20 МБ"
        )
    
    document_id = str(uuid.uuid4())
    
    return {
        "document_id": document_id,
        "file_name": filename,
        "size_bytes": file_size,
        "message": "Файл успешно загружен"
    }, contents
