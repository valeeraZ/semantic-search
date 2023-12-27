from typing import Any, Generic, Type, TypeVar

from fastapi_pagination import Page, Params, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.engine.result import Result
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from api.infra.db.model.base import Base

disable_installed_extensions_check()

T = TypeVar("T", bound=Base)
TEntity = TypeVar("TEntity", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def _query(self, *criterion: Any, order_by: Any = None, **kwargs: Any) -> Result:
        query = select(self.model).filter(*criterion)
        if order_by is not None:
            query = query.order_by(order_by)
        return self.session.execute(query)

    def get(self, *criterion: Any, order_by: Any = None, **kwargs: Any) -> T | None:
        result = self._query(*criterion, order_by=order_by, **kwargs)
        return result.scalars().first()

    def get_many(
        self,
        *criterion: Any,
        params: Params = Params(),
        order_by: Any = None,
        **kwargs: Any,
    ) -> Page[T]:
        result = self._query(*criterion, order_by=order_by, **kwargs)
        items = result.scalars().all()
        return paginate(items, params=params)

    def create(self, obj_in: dict[str, Any] | T) -> T:
        if isinstance(obj_in, dict):
            return self._create_from_dict(obj_in)
        if isinstance(obj_in, self.model):
            return self._create_from_model(obj_in)
        raise ValueError(f"Object {obj_in} is not a dict or {self.model}")

    def _create_from_dict(self, obj_in: dict[str, Any]) -> T:
        return add_and_commit(self.session, self.model(**obj_in))

    def _create_from_model(self, obj_in: T) -> T:
        return add_and_commit(self.session, obj_in)

    def get_by_id(self, id: int) -> T | None:
        return self.get(id=id)

    def update(self, obj_in: T) -> T:
        self.session.commit()
        return obj_in

    def update_with_dict(self, obj_in: T, updated_data: dict[str, Any]) -> T:
        for attr, value in updated_data.items():
            if obj_in.__table__.columns.keys().__contains__(attr):
                setattr(obj_in, attr, value)
        self.session.commit()
        return obj_in

    def delete(self, obj_in: T) -> None:
        self.session.delete(obj_in)  # type: ignore
        self.session.commit()

    def delete_many(self, objs_in: list[T]) -> None:
        for obj in objs_in:
            self.session.delete(obj)  # type: ignore
        self.session.commit()


class RepositoryError(Exception):
    pass


def add_and_commit(session: Session, obj: T) -> T:
    try:
        session.add(obj)  # type: ignore
        session.commit()
    except Exception as e:
        session.rollback()
        raise RepositoryError(
            f"Error while adding {obj} to session: {str(e)}",
        ) from e
    return obj
