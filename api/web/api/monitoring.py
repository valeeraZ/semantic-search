from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from api.infra.db.dependencies import get_db_session

router = APIRouter()


def is_database_online(session: Session) -> bool:
    """
    Check if database is online.

    :return: True if database is online, False otherwise.
    """
    try:
        session.execute(text("SELECT 1"))
        return True
    except DatabaseError:
        return False


@router.get("/health")
def health_check(session: Session = Depends(get_db_session)):
    """
    Health check endpoint.

    :return: 200 if database is online, 500 otherwise.
    """
    if is_database_online(session):
        return Response(status_code=200)
    return Response(status_code=500)
