import time
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timezone
from app.extensions import db
from app.models.multiplayer import MultiplayerRoom, RoomParticipant, generate_room_code
from app.models.category import Category
from app.models.question import Question
from app.repositories import QuestionRepository, StatsRepository, CategoryRepository
from app.games.scoring import ScoringEngine

question_repo = QuestionRepository()
stats_repo = StatsRepository()
category_repo = CategoryRepository()


class RoomManager:
    """Authoritative in-memory state manager for real-time multiplayer rooms."""

    def __init__(self):
        # Maps room_code -> room_state dict
        self._rooms: Dict[str, dict] = {}
        # Maps sid -> (room_code, user_id)
        self._sid_map: Dict[str, Tuple[str, int]] = {}

    def create_room(
        self,
        host_user,
        category_slug: str = "all",
        difficulty: str = "medium",
        question_count: int = 10,
        max_players: int = 8,
    ) -> str:
        """Initialize in-memory and database records for a multiplayer match room."""
        category = None
        category_id = None
        if category_slug and category_slug != "all":
            category = category_repo.get_by_slug(category_slug)
            if category:
                category_id = category.id

        code = generate_room_code()
        # Ensure code uniqueness
        while code in self._rooms or MultiplayerRoom.query.filter_by(room_code=code).first():
            code = generate_room_code()

        # Database record
        db_room = MultiplayerRoom(
            room_code=code,
            host_user_id=host_user.id,
            category_id=category_id,
            difficulty=difficulty,
            question_count=question_count,
            max_players=max_players,
            status="waiting",
        )
        db.session.add(db_room)
        db.session.commit()

        # In-memory authoritative state
        self._rooms[code] = {
            "id": db_room.id,
            "room_code": code,
            "host_id": host_user.id,
            "category_slug": category_slug,
            "category_id": category_id,
            "category_name": category.name if category else "All Categories",
            "difficulty": difficulty,
            "question_count": question_count,
            "max_players": max_players,
            "status": "lobby",  # lobby, in_progress, finished
            "participants": {},
            "questions": [],
            "current_index": 0,
            "question_started_at": 0.0,
            "answers_received": {},
        }

        return code

    def join_room(self, room_code: str, user, sid: str) -> Tuple[bool, str]:
        """Add user to room if room exists, is in lobby, and has capacity."""
        room = self._rooms.get(room_code)
        if not room:
            # Check if exists in DB to restore state
            db_room = MultiplayerRoom.query.filter_by(room_code=room_code).first()
            if not db_room or db_room.status in ("finished", "closed"):
                return False, "Room not found or match already ended."
            # Restore to memory
            cat_name = db_room.category.name if db_room.category else "All Categories"
            room = {
                "id": db_room.id,
                "room_code": room_code,
                "host_id": db_room.host_user_id,
                "category_slug": db_room.category.slug if db_room.category else "all",
                "category_id": db_room.category_id,
                "category_name": cat_name,
                "difficulty": db_room.difficulty,
                "question_count": db_room.question_count,
                "max_players": db_room.max_players,
                "status": "lobby" if db_room.status == "waiting" else db_room.status,
                "participants": {},
                "questions": [],
                "current_index": 0,
                "question_started_at": 0.0,
                "answers_received": {},
            }
            self._rooms[room_code] = room

        if room["status"] != "lobby":
            # Reconnection check
            if user.id in room["participants"]:
                room["participants"][user.id]["sid"] = sid
                room["participants"][user.id]["connected"] = True
                self._sid_map[sid] = (room_code, user.id)
                return True, "Reconnected to active match."
            return False, "Battle already in progress."

        if len(room["participants"]) >= room["max_players"] and user.id not in room["participants"]:
            return False, "Room is full."

        # Add or update participant
        room["participants"][user.id] = {
            "user_id": user.id,
            "username": user.username,
            "display_name": user.effective_display_name,
            "avatar_seed": user.avatar_seed,
            "sid": sid,
            "ready": (user.id == room["host_id"]),  # Host is ready by default
            "score": 0,
            "streak": 0,
            "connected": True,
        }
        self._sid_map[sid] = (room_code, user.id)

        # Sync DB participant
        existing_part = RoomParticipant.query.filter_by(room_id=room["id"], user_id=user.id).first()
        if not existing_part:
            db.session.add(RoomParticipant(room_id=room["id"], user_id=user.id, is_ready=(user.id == room["host_id"])))
            db.session.commit()

        return True, "Joined room successfully."

    def leave_room(self, sid: str) -> Optional[str]:
        """Handle player leaving room."""
        mapping = self._sid_map.pop(sid, None)
        if not mapping:
            return None

        room_code, user_id = mapping
        room = self._rooms.get(room_code)
        if not room:
            return None

        if user_id in room["participants"]:
            room["participants"][user_id]["connected"] = False
            # If in lobby, remove participant entirely
            if room["status"] == "lobby":
                del room["participants"][user_id]
                # If host leaves lobby, close room or transfer host
                if user_id == room["host_id"]:
                    if room["participants"]:
                        new_host_id = next(iter(room["participants"]))
                        room["host_id"] = new_host_id
                    else:
                        del self._rooms[room_code]

        return room_code

    def toggle_ready(self, room_code: str, user_id: int) -> bool:
        """Toggle player ready status."""
        room = self._rooms.get(room_code)
        if not room or room["status"] != "lobby":
            return False

        if user_id in room["participants"]:
            curr = room["participants"][user_id]["ready"]
            room["participants"][user_id]["ready"] = not curr
            return True
        return False

    def can_start_match(self, room_code: str, host_user_id: int) -> Tuple[bool, str]:
        """Validate if all players are ready and host is authorized to launch."""
        room = self._rooms.get(room_code)
        if not room:
            return False, "Room not found."
        if room["host_id"] != host_user_id:
            return False, "Only the host can start the battle."
        if len(room["participants"]) < 1:
            return False, "At least 1 player required."
        not_ready = [p["display_name"] for p in room["participants"].values() if not p["ready"]]
        if not_ready:
            return False, f"Waiting for players to be ready: {', '.join(not_ready)}"
        return True, "Ready to start."

    def initialize_match_questions(self, room_code: str) -> bool:
        """Load randomized questions for the multiplayer battle."""
        room = self._rooms.get(room_code)
        if not room:
            return False

        pool = question_repo.get_random_questions(
            category_id=room["category_id"],
            difficulty=room["difficulty"],
            count=room["question_count"],
        )
        if not pool:
            return False

        room["questions"] = pool
        room["status"] = "in_progress"
        room["current_index"] = 0
        room["answers_received"] = {}

        # Update DB room status
        db_room = db.session.get(MultiplayerRoom, room["id"])
        if db_room:
            db_room.status = "in_progress"
            db.session.commit()

        return True

    def get_current_question_broadcast(self, room_code: str) -> Optional[dict]:
        """Prepare synchronized question broadcast payload for room clients."""
        room = self._rooms.get(room_code)
        if not room or room["status"] != "in_progress":
            return None

        if room["current_index"] >= len(room["questions"]):
            return None

        q = room["questions"][room["current_index"]]
        room["question_started_at"] = time.time()
        room["answers_received"] = {}

        return {
            "question_index": room["current_index"] + 1,
            "total_questions": len(room["questions"]),
            "question_id": q.id,
            "question_text": q.question_text,
            "category_name": q.category.name if q.category else "General",
            "difficulty": q.difficulty,
            "time_limit_sec": q.time_limit_sec,
            "options": [opt.to_client_dict() for opt in q.options],
            "timestamp": room["question_started_at"],
        }

    def submit_answer(
        self,
        room_code: str,
        user_id: int,
        question_id: int,
        selected_option_id: Optional[int],
    ) -> Tuple[bool, dict]:
        """Record player answer authoritatively in real-time."""
        room = self._rooms.get(room_code)
        if not room or room["status"] != "in_progress":
            return False, {}

        # Guard against duplicate submissions for this question
        if user_id in room["answers_received"]:
            return False, {}

        q = room["questions"][room["current_index"]]
        if q.id != question_id:
            return False, {}

        elapsed_ms = int((time.time() - room["question_started_at"]) * 1000)
        is_correct = False
        correct_opt_id = q.correct_option.id if q.correct_option else None

        if selected_option_id and correct_opt_id and selected_option_id == correct_opt_id:
            is_correct = True

        participant = room["participants"].get(user_id)
        current_streak = participant["streak"] if participant else 0

        points, streak_pts, speed_pts, new_streak = ScoringEngine.calculate_submission_score(
            difficulty=q.difficulty,
            is_correct=is_correct,
            response_time_ms=elapsed_ms,
            time_limit_sec=q.time_limit_sec,
            current_streak=current_streak,
        )

        if participant:
            participant["score"] += points
            participant["streak"] = new_streak

        room["answers_received"][user_id] = {
            "selected_option_id": selected_option_id,
            "is_correct": is_correct,
            "points": points,
            "time_ms": elapsed_ms,
        }

        # Check if all connected participants have answered
        all_answered = len(room["answers_received"]) >= len([p for p in room["participants"].values() if p["connected"]])

        return True, {
            "user_id": user_id,
            "is_correct": is_correct,
            "points_awarded": points,
            "correct_option_id": correct_opt_id,
            "explanation": q.explanation,
            "current_score": participant["score"] if participant else 0,
            "all_answered": all_answered,
        }

    def advance_question(self, room_code: str) -> Tuple[bool, bool]:
        """Advance question index. Returns (success, is_match_over)."""
        room = self._rooms.get(room_code)
        if not room:
            return False, False

        room["current_index"] += 1
        is_over = room["current_index"] >= len(room["questions"])
        if is_over:
            room["status"] = "finished"
            # Update DB room
            db_room = db.session.get(MultiplayerRoom, room["id"])
            if db_room:
                db_room.status = "finished"
                db_room.finished_at = datetime.now(timezone.utc)
                db.session.commit()

        return True, is_over

    def get_room_leaderboard(self, room_code: str) -> List[dict]:
        """Return participants sorted by score descending."""
        room = self._rooms.get(room_code)
        if not room:
            return []
        sorted_parts = sorted(room["participants"].values(), key=lambda p: p["score"], reverse=True)
        return [
            {
                "user_id": p["user_id"],
                "username": p["username"],
                "display_name": p["display_name"],
                "avatar_seed": p["avatar_seed"],
                "score": p["score"],
                "streak": p["streak"],
                "connected": p["connected"],
            }
            for p in sorted_parts
        ]


# Global singleton room manager
room_manager = RoomManager()
