import logging
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.documents import router as document_router
from app.api.history import router as history_router
from app.api.search import router as search_router
from app.api.users import router as users_router
from app.core.config import settings

from app.core.elastic import close_elasticsearch, init_elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.core.database import close_db, init_db

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_elasticsearch()
    await init_db()
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="kb-cache")
    yield
    await close_elasticsearch()
    await close_db()


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
app.include_router(search_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API поисковой системы успешно запущено"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
