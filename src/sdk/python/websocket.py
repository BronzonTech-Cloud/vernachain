"""Websocket implementation for real-time events in Vernachain SDK."""

import json
import asyncio
import websockets
from typing import Dict, Any, Callable, Set, Optional
from dataclasses import dataclass, field
from .errors import NetworkError, ValidationError

@dataclass
class WebsocketEvent:
    """Websocket event data structure."""
    type: str
    data: Dict[str, Any]
    timestamp: float

@dataclass
class WebsocketClient:
    """Websocket client for handling real-time events."""
    
    url: str
    handlers: Dict[str, Set[Callable]] = field(default_factory=dict)
    _ws: Optional[websockets.WebSocketClientProtocol] = None
    _task: Optional[asyncio.Task] = None
    _running: bool = False

    async def connect(self) -> None:
        """Connect to websocket server."""
        try:
            self._ws = await websockets.connect(self.url)
            self._running = True
            self._task = asyncio.create_task(self._message_handler())
        except Exception as e:
            raise NetworkError(f"Failed to connect to websocket: {e}")

    async def disconnect(self) -> None:
        """Disconnect from websocket server."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def subscribe(self, event_type: str, handler: Callable[[WebsocketEvent], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function for handling events
        """
        if not self._ws:
            raise NetworkError("Not connected to websocket server")
            
        # Register handler
        if event_type not in self.handlers:
            self.handlers[event_type] = set()
        self.handlers[event_type].add(handler)
        
        # Send subscription message
        try:
            await self._ws.send(json.dumps({
                "type": "subscribe",
                "event": event_type
            }))
        except Exception as e:
            raise NetworkError(f"Failed to subscribe to event: {e}")

    async def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self.handlers:
            self.handlers[event_type].discard(handler)
            if not self.handlers[event_type]:
                del self.handlers[event_type]
                if self._ws:
                    try:
                        await self._ws.send(json.dumps({
                            "type": "unsubscribe",
                            "event": event_type
                        }))
                    except Exception as e:
                        raise NetworkError(f"Failed to unsubscribe from event: {e}")

    async def _message_handler(self) -> None:
        """Handle incoming websocket messages."""
        if not self._ws:
            return
            
        while self._running:
            try:
                message = await self._ws.recv()
                data = json.loads(message)
                
                # Validate message format
                if not isinstance(data, dict) or 'type' not in data:
                    continue
                    
                event_type = data['type']
                
                # Call registered handlers
                if event_type in self.handlers:
                    event = WebsocketEvent(
                        type=event_type,
                        data=data.get('data', {}),
                        timestamp=data.get('timestamp', 0)
                    )
                    for handler in self.handlers[event_type]:
                        try:
                            await handler(event)
                        except Exception as e:
                            # Log handler error but continue processing
                            print(f"Error in event handler: {e}")
                            
            except websockets.ConnectionClosed:
                self._running = False
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error handling websocket message: {e}")
                continue

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect() 