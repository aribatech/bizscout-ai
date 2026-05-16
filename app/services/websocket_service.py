from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, campaign_id: str, ws: WebSocket):
        await ws.accept()
        if campaign_id not in self.connections:
            self.connections[campaign_id] = []
        self.connections[campaign_id].append(ws)

    def disconnect(self, campaign_id: str, ws: WebSocket):
        if campaign_id in self.connections:
            try:
                self.connections[campaign_id].remove(ws)
            except ValueError:
                pass

    async def broadcast(self, campaign_id: str, message: dict):
        if campaign_id not in self.connections:
            return
        dead = []
        for ws in self.connections[campaign_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(campaign_id, ws)


manager = ConnectionManager()
