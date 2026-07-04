import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_client import make_asgi_app, Counter, Histogram
import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
import time
import re

from app.api.documents import router as document_router
from app.api.history import router as history_router
from app.api.search import router as search_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.elastic import close_elasticsearch, init_elasticsearch

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

# Счётчик запросов (method, endpoint, status)
REQUESTS = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Гистограмма времени ответа (method, endpoint)
DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)  # настраиваемые бакеты
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Определяем эндпоинт: убираем динамические части (ID, параметры)
        # Например, /api/v1/documents/123 -> /api/v1/documents/{id}
        path = request.url.path
        # Сначала заменяем UUID (формат 8-4-4-4-12 шестнадцатеричных символов)
        endpoint = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        # Затем заменяем цифровые ID (если они есть)
        endpoint = re.sub(r'/\d+', '/{id}', endpoint)

        start_time = time.time()
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            # Обновляем счётчик и гистограмму
            REQUESTS.labels(method=request.method, endpoint=endpoint, status=status).inc()
            DURATION.labels(method=request.method, endpoint=endpoint).observe(duration)


app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(document_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Корневой эндпоинт API",
    description="Проверка доступности API поисковой системы.",
)
async def root():
    return {"message": "API поисковой системы успешно запущено"}


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Проверка состояния системы",
    description="Возвращает статус 'ok' для мониторинга работоспособности сервиса.",
)
async def health_check():
    return {"status": "ok"}
