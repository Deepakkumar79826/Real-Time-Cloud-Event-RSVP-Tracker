from collections import defaultdict
from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.rooms = defaultdict(set)

    async def connect(self, event_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms[event_id].add(websocket)

    def disconnect(self, event_id: int, websocket: WebSocket):
        self.rooms[event_id].discard(websocket)
        if not self.rooms[event_id]:
            self.rooms.pop(event_id, None)

    async def broadcast(self, event_id: int, payload: dict):
        dead = []
        for ws in list(self.rooms.get(event_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(event_id, ws)

manager = ConnectionManager()
