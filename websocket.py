from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.poll_subscribers: dict = {}  # poll_id -> [websockets]
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Remove from poll subscribers
        for poll_id, connections in self.poll_subscribers.items():
            if websocket in connections:
                connections.remove(websocket)
    
    def subscribe_to_poll(self, poll_id: int, websocket: WebSocket):
        if poll_id not in self.poll_subscribers:
            self.poll_subscribers[poll_id] = []
        if websocket not in self.poll_subscribers[poll_id]:
            self.poll_subscribers[poll_id].append(websocket)
    
    async def broadcast_poll_update(self, poll_id: int, data: dict):
        if poll_id in self.poll_subscribers:
            disconnected = []
            for connection in self.poll_subscribers[poll_id]:
                try:
                    await connection.send_text(json.dumps(data))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.poll_subscribers[poll_id].remove(conn)

# Create a single instance to be imported by other modules
manager = ConnectionManager()