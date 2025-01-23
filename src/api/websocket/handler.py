from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import asyncio
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_channels: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, channels: Set[str] = None):
        """
        Connect a client and subscribe to specified channels
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        if channels:
            self.connection_channels[websocket] = channels
        else:
            self.connection_channels[websocket] = {"system"}  # Default channel

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a client and clean up subscriptions
        """
        self.active_connections.remove(websocket)
        if websocket in self.connection_channels:
            del self.connection_channels[websocket]

    async def subscribe(self, websocket: WebSocket, channels: Set[str]):
        """
        Subscribe a client to additional channels
        """
        if websocket in self.connection_channels:
            self.connection_channels[websocket].update(channels)

    async def unsubscribe(self, websocket: WebSocket, channels: Set[str]):
        """
        Unsubscribe a client from specified channels
        """
        if websocket in self.connection_channels:
            self.connection_channels[websocket] = self.connection_channels[websocket] - channels

    async def broadcast(self, message: Dict[str, Any], channel: str = "system"):
        """
        Broadcast a message to all clients subscribed to the specified channel
        """
        message_data = {
            "type": "update",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat(),
            "data": message
        }
        
        for connection, channels in self.connection_channels.items():
            if channel in channels:
                try:
                    await connection.send_json(message_data)
                except Exception as e:
                    print(f"Error sending message to client: {str(e)}")
                    await self.disconnect(connection)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send a message to a specific client
        """
        try:
            await websocket.send_json({
                "type": "personal",
                "timestamp": datetime.utcnow().isoformat(),
                "data": message
            })
        except Exception as e:
            print(f"Error sending personal message: {str(e)}")
            await self.disconnect(websocket)

# Create a global WebSocket manager instance
manager = WebSocketManager()

# Example usage of different update types
async def send_token_update(token_data: Dict[str, Any]):
    """
    Send token-related updates (mentions, launches, etc.)
    """
    await manager.broadcast(
        message=token_data,
        channel="tokens"
    )

async def send_trade_update(trade_data: Dict[str, Any]):
    """
    Send trade-related updates
    """
    await manager.broadcast(
        message=trade_data,
        channel="trades"
    )

async def send_system_update(status_data: Dict[str, Any]):
    """
    Send system status updates
    """
    await manager.broadcast(
        message=status_data,
        channel="system"
    )

async def send_error_alert(error_data: Dict[str, Any]):
    """
    Send error alerts
    """
    await manager.broadcast(
        message=error_data,
        channel="alerts"
    )

# WebSocket message handler
async def handle_websocket_message(websocket: WebSocket, message: str):
    """
    Handle incoming WebSocket messages
    """
    try:
        data = json.loads(message)
        message_type = data.get("type")

        if message_type == "subscribe":
            channels = set(data.get("channels", []))
            await manager.subscribe(websocket, channels)
            await manager.send_personal_message(
                {"message": f"Subscribed to channels: {channels}"},
                websocket
            )

        elif message_type == "unsubscribe":
            channels = set(data.get("channels", []))
            await manager.unsubscribe(websocket, channels)
            await manager.send_personal_message(
                {"message": f"Unsubscribed from channels: {channels}"},
                websocket
            )

        else:
            await manager.send_personal_message(
                {"error": "Unknown message type"},
                websocket
            )

    except json.JSONDecodeError:
        await manager.send_personal_message(
            {"error": "Invalid JSON message"},
            websocket
        )
    except Exception as e:
        await manager.send_personal_message(
            {"error": f"Error processing message: {str(e)}"},
            websocket
        )
