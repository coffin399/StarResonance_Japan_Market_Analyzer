"""
Real-time API routes
リアルタイムデータ配信のAPIルート
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import asyncio
import json
import logging

from ...database import get_db
from ...packet_decoder.realtime_capture import (
    RealtimePacketCapture,
    RealtimeCaptureCallback
)
from ...packet_decoder.packet_types import TradingPacket, ItemListing

logger = logging.getLogger(__name__)
router = APIRouter()

# グローバルキャプチャインスタンス
capture_instance: RealtimePacketCapture = None
websocket_clients: List[WebSocket] = []


class WebSocketCallback(RealtimeCaptureCallback):
    """WebSocketクライアントに通知するコールバック"""
    
    async def on_listing_found_async(self, listings: List[ItemListing]):
        """新しい出品情報をWebSocketクライアントに送信"""
        if not websocket_clients:
            return
        
        # リスティングデータをシリアライズ
        data = {
            "type": "new_listings",
            "timestamp": listings[0].timestamp.isoformat() if listings else None,
            "count": len(listings),
            "listings": [
                {
                    "listing_id": listing.listing_id,
                    "item_id": listing.item_id,
                    "item_name": listing.item_name,
                    "quantity": listing.quantity,
                    "price": listing.price,
                    "seller_name": listing.seller_name,
                }
                for listing in listings
            ]
        }
        
        # すべてのWebSocketクライアントに送信
        disconnected_clients = []
        for client in websocket_clients:
            try:
                await client.send_json(data)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket client: {e}")
                disconnected_clients.append(client)
        
        # 切断されたクライアントを削除
        for client in disconnected_clients:
            if client in websocket_clients:
                websocket_clients.remove(client)
    
    def on_listing_found(self, listings: List[ItemListing]):
        """同期メソッドから非同期メソッドを呼び出し"""
        # イベントループで実行
        try:
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                self.on_listing_found_async(listings),
                loop
            )
        except Exception as e:
            logger.error(f"Failed to schedule async callback: {e}")


websocket_callback = WebSocketCallback()


@router.post("/realtime/start")
async def start_realtime_capture(
    game_server_ip: str = None,
    game_server_port: int = None,
    db: Session = Depends(get_db)
):
    """
    リアルタイムキャプチャを開始
    
    - **game_server_ip**: ゲームサーバーのIPアドレス（オプション）
    - **game_server_port**: ゲームサーバーのポート（オプション）
    """
    global capture_instance
    
    if capture_instance and capture_instance.is_running:
        raise HTTPException(status_code=400, detail="Capture is already running")
    
    try:
        # データベースコールバックも追加
        from ...database import SessionLocal
        from ...packet_decoder.realtime_capture import DatabaseCallback
        
        db_session = SessionLocal()
        db_callback = DatabaseCallback(db_session)
        
        # キャプチャインスタンスを作成
        capture_instance = RealtimePacketCapture(
            callback=websocket_callback,
            game_server_ip=game_server_ip,
            game_server_port=game_server_port
        )
        
        # データベースコールバックも登録
        original_on_listing = capture_instance.callback.on_listing_found
        
        def combined_callback(listings):
            original_on_listing(listings)
            db_callback.on_listing_found(listings)
        
        capture_instance.callback.on_listing_found = combined_callback
        
        # キャプチャ開始
        capture_instance.start()
        
        return {
            "status": "started",
            "game_server_ip": game_server_ip,
            "game_server_port": game_server_port,
        }
    
    except Exception as e:
        logger.error(f"Failed to start capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/realtime/stop")
async def stop_realtime_capture():
    """リアルタイムキャプチャを停止"""
    global capture_instance
    
    if not capture_instance or not capture_instance.is_running:
        raise HTTPException(status_code=400, detail="Capture is not running")
    
    try:
        stats = capture_instance.get_stats()
        capture_instance.stop()
        capture_instance = None
        
        return {
            "status": "stopped",
            "stats": stats,
        }
    
    except Exception as e:
        logger.error(f"Failed to stop capture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime/status")
async def get_realtime_status():
    """リアルタイムキャプチャの状態を取得"""
    global capture_instance
    
    if not capture_instance:
        return {
            "is_running": False,
            "connected_clients": len(websocket_clients),
        }
    
    return {
        "is_running": capture_instance.is_running,
        "stats": capture_instance.get_stats(),
        "connected_clients": len(websocket_clients),
    }


@router.websocket("/realtime/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocketエンドポイント
    リアルタイムで新しい出品情報を受信
    """
    await websocket.accept()
    websocket_clients.append(websocket)
    
    logger.info(f"WebSocket client connected. Total clients: {len(websocket_clients)}")
    
    try:
        # 接続確認メッセージを送信
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to real-time market data stream"
        })
        
        # クライアントからのメッセージを待機
        while True:
            try:
                data = await websocket.receive_text()
                # Pingメッセージへの応答
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(websocket_clients)}")


@router.get("/realtime/recent")
async def get_recent_listings(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    最近キャプチャされた出品情報を取得（リアルタイムキャプチャからではなくDBから）
    
    - **limit**: 取得する件数
    """
    from ...database.models import Listing, Item
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    
    # 過去5分以内のリスティングを取得
    recent_time = datetime.utcnow() - timedelta(minutes=5)
    
    listings = db.query(Listing).filter(
        Listing.captured_at >= recent_time
    ).order_by(
        desc(Listing.captured_at)
    ).limit(limit).all()
    
    result = []
    for listing in listings:
        item = db.query(Item).filter(Item.id == listing.item_id).first()
        result.append({
            "listing_id": listing.id,
            "item_id": listing.item_id,
            "item_name": item.name if item else "Unknown",
            "quantity": listing.quantity,
            "price": listing.price,
            "unit_price": listing.unit_price,
            "seller_name": listing.seller_name,
            "captured_at": listing.captured_at.isoformat(),
        })
    
    return {
        "count": len(result),
        "listings": result,
    }
