from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # user_id -> WebSocket bağlantıları
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Kullanıcıyı WebSocket'e bağla"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"Kullanıcı {user_id} WebSocket'e bağlandı")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Kullanıcıyı WebSocket'ten ayır"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"Kullanıcı {user_id} WebSocket'ten ayrıldı")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Belirli bir kullanıcıya mesaj gönder"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Mesaj gönderilirken hata: {e}")
                    disconnected.add(connection)
            
            # Bağlantısı kopanları temizle
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """Kullanıcının tüm bağlantılarına mesaj gönder"""
        await self.send_personal_message(message, user_id)

manager = ConnectionManager()

