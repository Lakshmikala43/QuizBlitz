import random
from typing import Optional, List, Dict
from sqlalchemy import func
from app.extensions import db
from app.models.category import Category
from app.models.question import Question, AnswerOption
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Data-access repository for categories."""

    def __init__(self):
        super().__init__(Category)

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return db.session.query(Category).filter_by(slug=slug).first()

    def get_active_categories(self) -> List[Category]:
        return (
            db.session.query(Category)
            .filter_by(is_active=True)
            .order_by(Category.sort_order.asc(), Category.name.asc())
            .all()
        )


class QuestionRepository(BaseRepository[Question]):
    """Data-access repository for questions and options."""

    def __init__(self):
        super().__init__(Question)

    def get_random_questions(
        self,
        category_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        count: int = 10,
    ) -> List[Question]:
        """
        Fetch a randomized pool of published questions matching category and difficulty.
        If not enough match the strict difficulty, falls back gracefully.
        """
        query = db.session.query(Question).filter(Question.is_published == True)

        if category_id:
            query = query.filter(Question.category_id == category_id)

        if difficulty and difficulty != "mixed":
            query = query.filter(Question.difficulty == difficulty)

        # Use SQL random ordering
        questions = query.order_by(func.random()).limit(count).all()

        # If pool size is smaller than requested, fallback to any difficulty in category
        if len(questions) < count and difficulty and difficulty != "mixed":
            existing_ids = [q.id for q in questions]
            fallback_query = db.session.query(Question).filter(
                Question.is_published == True,
                Question.id.notin_(existing_ids) if existing_ids else True,
            )
            if category_id:
                fallback_query = fallback_query.filter(Question.category_id == category_id)
            needed = count - len(questions)
            fallback_questions = fallback_query.order_by(func.random()).limit(needed).all()
            questions.extend(fallback_questions)

        return questions

    def search_questions(
        self,
        category_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        search_text: Optional[str] = None,
        is_published: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict:
        """Search and paginate questions for administrative management."""
        query = db.session.query(Question)

        if category_id:
            query = query.filter(Question.category_id == category_id)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if is_published is not None:
            query = query.filter(Question.is_published == is_published)
        if search_text:
            s = f"%{search_text.strip()}%"
            query = query.filter(Question.question_text.ilike(s))

        query = query.order_by(Question.created_at.desc())
        return self.paginate(query, page=page, per_page=per_page)

    def detect_duplicate_question(self, question_text: str) -> Optional[Question]:
        """Check if an identical question text already exists (case-insensitive strip)."""
        normalized = question_text.strip().lower()
        return (
            db.session.query(Question)
            .filter(func.lower(Question.question_text) == normalized)
            .first()
        )

    def create_question_with_options(
        self,
        question_data: dict,
        options_data: List[dict],
    ) -> Question:
        """
        Create a Question and its corresponding AnswerOptions in a single transaction.
        `options_data` format: [{'option_text': 'A', 'is_correct': True}, ...]
        """
        question = Question(**question_data)
        db.session.add(question)
        db.session.flush()

        for idx, opt in enumerate(options_data):
            option = AnswerOption(
                question_id=question.id,
                option_text=opt.get("option_text", ""),
                is_correct=opt.get("is_correct", False),
                order_index=opt.get("order_index", idx),
            )
            db.session.add(option)

        db.session.commit()
        return question

    def update_question_with_options(
        self,
        question_id: int,
        question_data: dict,
        options_data: Optional[List[dict]] = None,
    ) -> Optional[Question]:
        """Update question and optionally replace its options atomically."""
        question = self.get_by_id(question_id)
        if not question:
            return None

        for k, v in question_data.items():
            if hasattr(question, k):
                setattr(question, k, v)

        if options_data is not None:
            # Delete old options
            db.session.query(AnswerOption).filter_by(question_id=question.id).delete()
            db.session.flush()

            for idx, opt in enumerate(options_data):
                option = AnswerOption(
                    question_id=question.id,
                    option_text=opt.get("option_text", ""),
                    is_correct=opt.get("is_correct", False),
                    order_index=opt.get("order_index", idx),
                )
                db.session.add(option)

        db.session.commit()
        return question
