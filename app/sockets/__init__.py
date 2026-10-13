"""Quiz Royale WebSocket events package."""

from app.sockets.multiplayer import (
    handle_connect,
    handle_disconnect,
    handle_join_room,
    handle_toggle_ready,
    handle_start_battle,
    handle_submit_answer,
    handle_advance_question,
)

__all__ = [
    "handle_connect",
    "handle_disconnect",
    "handle_join_room",
    "handle_toggle_ready",
    "handle_start_battle",
    "handle_submit_answer",
    "handle_advance_question",
]
