import pytest
from app.extensions import db
from app.multiplayer.manager import RoomManager
from app.models.multiplayer import MultiplayerRoom
from app.models.user import User


class TestMultiplayerRoomManager:
    """Integration test suite for authoritative real-time multiplayer state manager."""

    @pytest.fixture
    def manager(self):
        """Isolated instance of RoomManager."""
        return RoomManager()

    def test_create_room(self, app, test_user, sample_category, sample_questions, manager):
        with app.app_context():
            u = db.session.get(User, test_user.id)
            code = manager.create_room(
                host_user=u,
                category_slug=sample_category.slug,
                difficulty="medium",
                question_count=5,
                max_players=4,
            )
            assert code is not None
            assert len(code) == 6

            db_room = MultiplayerRoom.query.filter_by(room_code=code).first()
            assert db_room is not None
            assert db_room.host_user_id == test_user.id
            assert db_room.status == "waiting"

    def test_join_room_and_ready_state(self, app, test_user, test_admin, sample_category, sample_questions, manager):
        with app.app_context():
            u_host = db.session.get(User, test_user.id)
            u_joiner = db.session.get(User, test_admin.id)

            code = manager.create_room(host_user=u_host, category_slug=sample_category.slug, question_count=5)

            # Host joins room
            h_success, h_msg = manager.join_room(code, u_host, sid="sid_host_1")
            assert h_success is True

            # Joiner joins room
            j_success, j_msg = manager.join_room(code, u_joiner, sid="sid_joiner_1")
            assert j_success is True

            # Ready states
            manager.toggle_ready(code, u_joiner.id)

            # Ready to start match check
            can_start, _ = manager.can_start_match(code, u_host.id)
            assert can_start is True

    def test_start_match_and_answer_submission(self, app, test_user, sample_category, sample_questions, manager):
        with app.app_context():
            u_host = db.session.get(User, test_user.id)
            code = manager.create_room(host_user=u_host, category_slug=sample_category.slug, question_count=5)
            manager.join_room(code, u_host, sid="sid_host_1")

            # Initialize match
            init_ok = manager.initialize_match_questions(code)
            assert init_ok is True

            # Get question broadcast
            q_broadcast = manager.get_current_question_broadcast(code)
            assert q_broadcast is not None
            assert "question_id" in q_broadcast
            assert "options" in q_broadcast

            q_id = q_broadcast["question_id"]
            from app.models.question import Question
            q = db.session.get(Question, q_id)
            correct_opt = [o for o in q.options if o.is_correct][0]

            # Submit answer
            ok, res = manager.submit_answer(
                room_code=code,
                user_id=u_host.id,
                question_id=q_id,
                selected_option_id=correct_opt.id,
            )
            assert ok is True
            assert res["is_correct"] is True
            assert res["points_awarded"] > 0
            assert res["all_answered"] is True


            # Check leaderboard
            leaderboard = manager.get_room_leaderboard(code)
            assert len(leaderboard) == 1
            assert leaderboard[0]["score"] > 0

    def test_advance_question_and_completion(self, app, test_user, sample_category, sample_questions, manager):
        with app.app_context():
            u_host = db.session.get(User, test_user.id)
            code = manager.create_room(host_user=u_host, category_slug=sample_category.slug, question_count=2)
            manager.join_room(code, u_host, sid="sid_host_1")
            manager.initialize_match_questions(code)

            # Advance Q1 -> Q2
            ok1, over1 = manager.advance_question(code)
            assert ok1 is True
            assert over1 is False

            # Advance Q2 -> Finish
            ok2, over2 = manager.advance_question(code)
            assert ok2 is True
            assert over2 is True

            db_room = MultiplayerRoom.query.filter_by(room_code=code).first()
            assert db_room.status == "finished"
