"""
Database setup and initialization
データベースのセットアップと初期化
"""
import logging
from .models import Base
from .connection import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """全てのテーブルを作成"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def drop_tables():
    """全てのテーブルを削除"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped!")


def reset_database():
    """データベースをリセット（削除→再作成）"""
    drop_tables()
    create_tables()


if __name__ == "__main__":
    # スクリプトとして実行された場合はテーブルを作成
    create_tables()
