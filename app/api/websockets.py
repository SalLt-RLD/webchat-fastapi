import json
from typing import AsyncGenerator
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_access_token
from app.db.requests_db import add_message, get_messages_stream, get_user_by_id
from app.db.session import get_temp_session
from app.models.models import Message, User
from app.websockets.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


async def send_online_count(session: AsyncSession, room_id: int):
    users_id: list[int] = manager.get_online_users(room_id)
    usernames: set[str] = set()
    for user_id in users_id:
        user: User = await get_user_by_id(session, user_id)
        usernames.add(user.username)
    await manager.broadcast(room_id=room_id, message=json.dumps({
        "type": "users_online",
        "users": sorted(usernames)
    }))


def message_to_json(message: Message, username: str) -> str:
    return json.dumps({
        "id": message.id,
        "user_id": message.user_id,
        "username": username,
        "room_id": message.room_id,
        "content": message.content,
        "timestamp": message.timestamp.isoformat(),
    })


def get_user_id_from_token(token: str) -> int | None:
    try:
        payload: dict | None = decode_access_token(token)
        return int(payload.get("sub"))
    except (ValueError, Exception):
        return None


@router.websocket("/{room_id}")
async def ws_connection(room_id: int, websocket: WebSocket):
    cookies: dict[str, str] = websocket.cookies
    token = cookies.get("access_token")

    if not token:
        await websocket.close(code=1008)
        return
    user_id: int | None = get_user_id_from_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    async with get_temp_session() as session:
        user: User = await get_user_by_id(session=session, user_id=user_id)
        username: str = user.username
        await manager.connect(websocket=websocket, room_id=room_id, user_id=user_id)
        await send_online_count(session=session, room_id=room_id)

        messages: AsyncGenerator[Message] = get_messages_stream(session=session, room_id=room_id)
        async for msg in messages:
            user: User = await get_user_by_id(session=session, user_id=msg.user_id)
            await websocket.send_text(message_to_json(message=msg, username=user.username))

        await manager.broadcast(room_id, json.dumps({
            "type": "system",
            "content": f"🟢 {username} вошёл в чат"
        }))

        try:
            while True:
                text = await websocket.receive_text()
                user: User = await get_user_by_id(session=session, user_id=user_id)
                new_message: Message = await add_message(session, text, user_id, room_id)
                await manager.broadcast(room_id, message_to_json(new_message, user.username))

        except WebSocketDisconnect:
            await manager.disconnect(websocket=websocket, room_id=room_id, user_id=user_id)
            await send_online_count(session=session, room_id=room_id)
            await manager.broadcast(room_id, json.dumps({
                "type": "system",
                "content": f"🔴 {username} покинул чат"
            }))
