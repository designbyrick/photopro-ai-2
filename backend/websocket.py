"""
WebSocket handlers for real-time photo processing updates.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up empty user connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            # Send to all connections for this user
            connections_to_remove = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    connections_to_remove.append(websocket)
            
            # Remove failed connections
            for websocket in connections_to_remove:
                self.active_connections[user_id].remove(websocket)
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """Broadcast message to all connections of a user"""
        await self.send_personal_message(message, user_id)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


async def notify_photo_status_update(user_id: int, photo_id: int, status: str, message: str = ""):
    """Notify user about photo processing status update"""
    notification = {
        "type": "photo_status_update",
        "photo_id": photo_id,
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(user_id, notification)


async def notify_photo_completed(user_id: int, photo_id: int, processed_url: str, thumbnail_url: str):
    """Notify user when photo generation is completed"""
    notification = {
        "type": "photo_completed",
        "photo_id": photo_id,
        "processed_url": processed_url,
        "thumbnail_url": thumbnail_url,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(user_id, notification)


async def notify_photo_failed(user_id: int, photo_id: int, error_message: str):
    """Notify user when photo generation fails"""
    notification = {
        "type": "photo_failed",
        "photo_id": photo_id,
        "error": error_message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(user_id, notification)


async def notify_credits_updated(user_id: int, new_balance: int, transaction_type: str):
    """Notify user about credit balance update"""
    notification = {
        "type": "credits_updated",
        "new_balance": new_balance,
        "transaction_type": transaction_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_user(user_id, notification)
