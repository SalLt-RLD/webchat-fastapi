import json
from typing import AsyncGenerator
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.jwt import decode_access_token
from app.db.requests_db import add_message, get_messages_stream
from app.db.session import get_temp_session
from app.models.models import Message
from app.websockets.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/{room_id}")
async def ws_connection(room_id: int, websocket: WebSocket):
    token: str | None = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        payload: dict | None = decode_access_token(token)
        user_id: int = int(payload.get("sub"))
    except (ValueError, Exception):
        await websocket.close(code=1008)
        return

    await manager.connect(websocket=websocket, room_id=room_id)
    async with get_temp_session() as session:
        messages: AsyncGenerator[Message] = get_messages_stream(session=session, room_id=room_id)
        async for msg in messages:
            await websocket.send_text(f"{msg.user_id}: {msg.content}")

        try:
            while True:
                new_message: Message = await add_message(
                    session=session,
                    content=await websocket.receive_text(),
                    user_id=user_id,
                    room_id=room_id
                )
                await manager.broadcast(room_id, json.dumps({
                    "id": new_message.id,
                    "user_id": new_message.user_id,
                    "room_id": new_message.room_id,
                    "content": new_message.content,
                    "timestamp": new_message.timestamp.isoformat(),
                }))

        except WebSocketDisconnect:
            await manager.disconnect(websocket=websocket, room_id=room_id)
