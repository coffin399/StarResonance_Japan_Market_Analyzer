"""
Database connection management
データベース接続管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from ..config import settings

# データベースエンジンの作成
engine = create_engine(
    settings.database_url,
    # SQLiteの場合は接続チェックを有効化
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.api_debug,
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得する依存性注入用関数
    
    Yields:
        データベースセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
