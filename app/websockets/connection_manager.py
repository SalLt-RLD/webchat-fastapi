from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[int, WebSocket]] = defaultdict(dict)

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        self.active_connections[room_id][user_id] = websocket

    async def broadcast(self, room_id: int, message: str):
        room = self.active_connections.get(room_id, {})
        for ws in room.values():
            await ws.send_text(message)

    async def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        room = self.active_connections.get(room_id)
        if room and user_id in room and room[user_id] is websocket:
            del room[user_id]
            if not room:
                del self.active_connections[room_id]

    def get_online_users(self, room_id: int) -> int:
        return len(list(self.active_connections.get(room_id, {}).keys()))
