"""
FastAPI application entry point
FastAPIアプリケーションのエントリーポイント
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import time

from ..config import settings
from .routes import items, listings, statistics, profit_calculator

# ロギング設定
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(
    title="Star Resonance Market Analyzer API",
    description="ブループロトコル:スターレゾナンス 取引所解析API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエスト処理時間ログミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# ルーター登録
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(listings.router, prefix="/api/v1", tags=["listings"])
app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])
app.include_router(profit_calculator.router, prefix="/api/v1", tags=["calculator"])

# リアルタイム機能
try:
    from .routes import realtime
    app.include_router(realtime.router, prefix="/api/v1", tags=["realtime"])
    logger.info("Real-time capture routes enabled")
except ImportError as e:
    logger.warning(f"Real-time capture not available: {e}")

# 静的ファイルとテンプレート
try:
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    templates = Jinja2Templates(directory="web/templates")
except Exception as e:
    logger.warning(f"Could not mount static files or templates: {e}")
    templates = None

# ルートエンドポイント
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """ホームページ"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse(content="""
        <html>
            <head><title>Star Resonance Market Analyzer</title></head>
            <body>
                <h1>Star Resonance Market Analyzer</h1>
                <p>API Documentation: <a href="/api/docs">/api/docs</a></p>
            </body>
        </html>
    """)

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
