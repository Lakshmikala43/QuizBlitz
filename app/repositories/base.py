from typing import TypeVar, Generic, Type, Optional, List, Any
from app.extensions import db

T = TypeVar("T", bound=db.Model)


class BaseRepository(Generic[T]):
    """
    Abstract generic base repository encapsulating SQLAlchemy persistence.
    Provides decoupled queries, transaction management, and safe pagination.
    """

    def __init__(self, model_class: Type[T]):
        self.model = model_class

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Fetch an entity by primary key."""
        return db.session.get(self.model, entity_id)

    def get_all(self) -> List[T]:
        """Fetch all records of the entity."""
        return db.session.query(self.model).all()

    def create(self, **kwargs) -> T:
        """Instantiate and persist a new entity within an automatic transaction."""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        """Update fields on an existing entity."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        """Remove an entity from the database."""
        db.session.delete(instance)
        db.session.commit()

    def paginate(self, query=None, page: int = 1, per_page: int = 20):
        """
        Execute paginated query.
        Returns a dictionary containing items, total, page, pages, has_prev, has_next.
        """
        if query is None:
            query = db.session.query(self.model)

        total = query.count()
        offset = max(0, (page - 1) * per_page)
        items = query.limit(per_page).offset(offset).all()
        pages = max(1, (total + per_page - 1) // per_page)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
        }
