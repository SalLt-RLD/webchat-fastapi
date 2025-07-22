from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)
        self.active_users: dict[int, list[int]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)
        self.active_users[room_id].append(user_id)

    async def broadcast(self, room_id: int, message: str):
        room: list[WebSocket] = self.active_connections.get(room_id, [])
        for ws in room:
            await ws.send_text(message)

    async def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        room = self.active_connections.get(room_id)
        if room and websocket in room:
            room.remove(websocket)
            if not room:
                del self.active_connections[room_id]

        room = self.active_users.get(room_id)
        if room and user_id in room:
            room.remove(user_id)
            if not room:
                del self.active_users[room_id]

    def get_online_users(self, room_id: int) -> list[int]:
        return list(self.active_users.get(room_id, {}))
