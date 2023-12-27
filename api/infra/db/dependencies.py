from typing import Generator

from sqlalchemy.orm import Session
from starlette.requests import Request


async def get_db_session(request: Request) -> Generator[Session, None, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: Session = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        session.commit()
        session.close()
