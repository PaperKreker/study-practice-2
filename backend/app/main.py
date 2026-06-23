from fastapi import FastAPI

app = FastAPI(
    title="Интеллектуальная поисковая система по внутренней базе знаний университета",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

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
