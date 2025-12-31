from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket.manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint
    
    Query parametresi olarak token gönderilmeli:
    ws://localhost:8000/api/ws?token=YOUR_JWT_TOKEN
    """
    user_id = None
    try:
        if not token:
            logger.warning("WebSocket bağlantısı token olmadan reddedildi")
            await websocket.close(code=1008, reason="Token gerekli")
            return
        
        # Token'dan kullanıcıyı doğrula
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
        if not payload:
            logger.warning("WebSocket bağlantısı geçersiz token ile reddedildi")
            await websocket.close(code=1008, reason="Geçersiz token")
            return
        
        user_id = int(payload.get("sub"))
        if not user_id:
            logger.warning("WebSocket bağlantısı geçersiz kullanıcı ID ile reddedildi")
            await websocket.close(code=1008, reason="Geçersiz kullanıcı")
            return
        
        # Bağlantıyı kabul et
        await manager.connect(websocket, user_id)
        logger.info(f"Kullanıcı {user_id} WebSocket'e başarıyla bağlandı")
        
        # Bağlantı başarılı mesajı gönder
        try:
            await websocket.send_json({
                "type": "connection",
                "message": "Bağlantı başarılı",
                "user_id": user_id
            })
        except Exception as e:
            logger.error(f"Bağlantı mesajı gönderilemedi: {e}")
        
        # Mesajları dinle
        while True:
            try:
                data = await websocket.receive_text()
                # İsteğe bağlı: kullanıcıdan gelen mesajları işle
                logger.info(f"Kullanıcı {user_id}'den mesaj: {data}")
            except WebSocketDisconnect:
                logger.info(f"Kullanıcı {user_id} WebSocket'ten ayrıldı")
                break
            except Exception as e:
                logger.error(f"WebSocket mesaj alma hatası: {e}")
                break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket bağlantısı kesildi (user_id: {user_id})")
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}", exc_info=True)
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)

