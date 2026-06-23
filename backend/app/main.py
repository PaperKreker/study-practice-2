from fastapi import FastAPI

from app.api.documents import router as document_router

app = FastAPI(
    title="Интеллектуальная поисковая система по внутренней базе знаний университета",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(document_router)

@app.get("/")
async def root():
    return {
        "message": "API поисковой системы успешно запущено"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }
