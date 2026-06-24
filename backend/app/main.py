import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.documents import router as document_router
from app.core.elastic import close_elasticsearch, init_elasticsearch
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_elasticsearch()
    yield
    await close_elasticsearch()

app = FastAPI(
    title="Интеллектуальная поисковая система по внутренней базе знаний университета",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API поисковой системы успешно запущено"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
