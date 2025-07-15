from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        self.active_connections.setdefault(room_id, []).append(websocket)

    async def broadcast(self, room_id: int, message: str):
        for ws in self.active_connections.get(room_id, []):
            await ws.send_text(message)

    async def disconnect(self, websocket: WebSocket, room_id: int):
        connections = self.active_connections.get(room_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            if not connections:
                del self.active_connections[room_id]
