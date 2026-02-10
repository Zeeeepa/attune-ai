"""WebSocket manager for nurse dashboard live updates.

Manages per-patient WebSocket subscriptions and broadcasts for
real-time patient monitoring. Nurses subscribe to specific patients
and receive assessment updates and alerts as they happen.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class NurseWebSocketManager:
    """Manages WebSocket connections for live patient monitoring.

    Features:
        - Per-patient subscription tracking
        - Broadcast to patient subscribers
        - Global alert broadcasting for high/critical risk
        - Safe disconnect handling with subscription cleanup

    Usage:
        manager = NurseWebSocketManager()
        await manager.connect(websocket)
        await manager.subscribe(websocket, ["patient-001", "patient-002"])
        await manager.broadcast_to_patient("patient-001", {"event": "new_assessment"})

    Attributes:
        active_connections: All currently connected WebSocket clients.
        subscriptions: Map of patient_id to set of subscribed WebSocket connections.
    """

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection.

        Args:
            websocket: The incoming WebSocket connection to accept.
        """
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection and clean up all its subscriptions.

        Args:
            websocket: The WebSocket connection to remove.
        """
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

            # Remove from all subscription sets
            empty_patient_ids: list[str] = []
            for patient_id, subscribers in self.subscriptions.items():
                subscribers.discard(websocket)
                if not subscribers:
                    empty_patient_ids.append(patient_id)

            # Clean up empty subscription sets
            for patient_id in empty_patient_ids:
                del self.subscriptions[patient_id]

        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def subscribe(self, websocket: WebSocket, patient_ids: list[str]) -> None:
        """Subscribe a WebSocket to updates for specific patients.

        Args:
            websocket: The WebSocket connection to subscribe.
            patient_ids: List of patient IDs to subscribe to.
        """
        async with self._lock:
            for pid in patient_ids:
                if pid not in self.subscriptions:
                    self.subscriptions[pid] = set()
                self.subscriptions[pid].add(websocket)

        logger.debug(
            f"WebSocket subscribed to {len(patient_ids)} patients: {patient_ids}"
        )

    async def broadcast_to_patient(
        self, patient_id: str, data: dict[str, Any]
    ) -> None:
        """Send data to all WebSockets subscribed to a specific patient.

        Failed sends (e.g., dropped connections) are handled gracefully
        by disconnecting the broken WebSocket.

        Args:
            patient_id: Patient whose subscribers should receive the message.
            data: Dict payload to send (will be JSON-serialized with patient_id).
        """
        subscribers = self.subscriptions.get(patient_id, set())
        if not subscribers:
            return

        message = json.dumps({"patient_id": patient_id, **data})
        disconnected: list[WebSocket] = []

        for ws in subscribers:
            try:
                await ws.send_text(message)
            except ConnectionError as e:
                logger.debug(f"WebSocket send failed (connection closed): {e}")
                disconnected.append(ws)
            except RuntimeError as e:
                logger.debug(f"WebSocket send failed (runtime error): {e}")
                disconnected.append(ws)

        for ws in disconnected:
            await self.disconnect(ws)

    async def broadcast_alert(self, alert_data: dict[str, Any]) -> None:
        """Broadcast an alert to ALL connected nurses.

        Used for high/critical risk alerts that need immediate attention
        regardless of which patients a nurse is monitoring.

        Args:
            alert_data: Alert payload dict (will be JSON-serialized with event="alert").
        """
        if not self.active_connections:
            return

        message = json.dumps({"event": "alert", **alert_data})
        disconnected: list[WebSocket] = []

        for ws in self.active_connections:
            try:
                await ws.send_text(message)
            except ConnectionError as e:
                logger.debug(f"WebSocket broadcast failed (connection closed): {e}")
                disconnected.append(ws)
            except RuntimeError as e:
                logger.debug(f"WebSocket broadcast failed (runtime error): {e}")
                disconnected.append(ws)

        for ws in disconnected:
            await self.disconnect(ws)

    @property
    def connection_count(self) -> int:
        """Number of active WebSocket connections."""
        return len(self.active_connections)

    @property
    def subscription_count(self) -> int:
        """Total number of active patient subscriptions across all connections."""
        return sum(len(subs) for subs in self.subscriptions.values())
