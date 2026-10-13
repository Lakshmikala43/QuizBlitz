from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app.extensions import socketio
from app.multiplayer.manager import room_manager


@socketio.on("connect")
def handle_connect():
    """Client connected to WebSocket."""
    emit("connected", {"status": "ok", "sid": request.sid})


@socketio.on("disconnect")
def handle_disconnect():
    """Client disconnected; clean up room presence."""
    room_code = room_manager.leave_room(request.sid)
    if room_code:
        leaderboard = room_manager.get_room_leaderboard(room_code)
        emit(
            "player_left",
            {
                "user_id": current_user.id if current_user.is_authenticated else None,
                "leaderboard": leaderboard,
            },
            room=room_code,
        )


@socketio.on("join_room")
def handle_join_room(data):
    """Player enters multiplayer room."""
    room_code = data.get("room_code", "").strip().upper()
    if not current_user.is_authenticated:
        emit("error", {"message": "Authentication required to enter battle room."})
        return

    success, message = room_manager.join_room(room_code, current_user, request.sid)
    if not success:
        emit("error", {"message": message})
        return

    join_room(room_code)
    room_state = room_manager._rooms.get(room_code, {})
    leaderboard = room_manager.get_room_leaderboard(room_code)

    emit("joined_successfully", {
        "room_code": room_code,
        "is_host": (current_user.id == room_state.get("host_id")),
        "category_name": room_state.get("category_name", "All Categories"),
        "difficulty": room_state.get("difficulty", "medium"),
        "question_count": room_state.get("question_count", 10),
        "status": room_state.get("status", "lobby"),
        "leaderboard": leaderboard,
    })

    # Broadcast updated participant roster to other room members
    emit("roster_updated", {"leaderboard": leaderboard}, room=room_code)


@socketio.on("toggle_ready")
def handle_toggle_ready(data):
    """Player toggles ready state."""
    room_code = data.get("room_code", "").strip().upper()
    if not current_user.is_authenticated:
        return

    toggled = room_manager.toggle_ready(room_code, current_user.id)
    if toggled:
        leaderboard = room_manager.get_room_leaderboard(room_code)
        emit("roster_updated", {"leaderboard": leaderboard}, room=room_code)


@socketio.on("start_battle")
def handle_start_battle(data):
    """Host launches multiplayer battle."""
    room_code = data.get("room_code", "").strip().upper()
    if not current_user.is_authenticated:
        return

    can_start, message = room_manager.can_start_match(room_code, current_user.id)
    if not can_start:
        emit("error", {"message": message})
        return

    loaded = room_manager.initialize_match_questions(room_code)
    if not loaded:
        emit("error", {"message": "Failed to load questions for match."})
        return

    # Broadcast match starting
    emit("battle_started", {"room_code": room_code}, room=room_code)

    # Broadcast first question
    q_data = room_manager.get_current_question_broadcast(room_code)
    if q_data:
        emit("new_question", q_data, room=room_code)


@socketio.on("submit_answer")
def handle_submit_answer(data):
    """Authoritative answer submission from player."""
    room_code = data.get("room_code", "").strip().upper()
    question_id = data.get("question_id")
    selected_option_id = data.get("selected_option_id")

    if not current_user.is_authenticated:
        return

    success, result = room_manager.submit_answer(
        room_code=room_code,
        user_id=current_user.id,
        question_id=question_id,
        selected_option_id=selected_option_id,
    )

    if not success:
        return

    # Send private feedback to answering player
    emit("answer_feedback", result)

    # Broadcast live score update to entire room
    leaderboard = room_manager.get_room_leaderboard(room_code)
    emit("score_update", {"leaderboard": leaderboard}, room=room_code)

    # If all participants answered, announce question conclusion
    if result.get("all_answered"):
        emit("all_players_answered", {
            "correct_option_id": result.get("correct_option_id"),
            "explanation": result.get("explanation"),
        }, room=room_code)


@socketio.on("advance_question")
def handle_advance_question(data):
    """Host or server advances to next question."""
    room_code = data.get("room_code", "").strip().upper()
    if not current_user.is_authenticated:
        return

    room = room_manager._rooms.get(room_code)
    if not room or room.get("host_id") != current_user.id:
        return

    success, is_over = room_manager.advance_question(room_code)
    if not success:
        return

    if is_over:
        final_leaderboard = room_manager.get_room_leaderboard(room_code)
        emit("battle_ended", {"podium": final_leaderboard}, room=room_code)
    else:
        q_data = room_manager.get_current_question_broadcast(room_code)
        if q_data:
            emit("new_question", q_data, room=room_code)
