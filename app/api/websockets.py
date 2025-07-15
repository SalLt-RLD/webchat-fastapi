from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websockets.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/{room_id}")
async def ws_connection(room_id: int, websocket: WebSocket):
    await manager.connect(websocket=websocket, room_id=room_id)
    try:
        while True:
            data: str = await websocket.receive_text()
            await manager.broadcast(room_id=room_id, message=data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket=websocket, room_id=room_id)
