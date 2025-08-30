from fastapi import Depends, Request
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

from typing import Annotated

from app.database.session import UserSession

from functools import wraps

import uuid
import contextlib

engine = None


def init(file=":memory:"):
    connect_args = {"check_same_thread": False}
    global engine
    if file == ":memory:":
        engine = create_engine(
            "sqlite:///:memory:",
            echo=True,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        engine = create_engine("sqlite:///{file}", echo=True, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)


def open():
    if engine is None:
        raise Exception("attempted to get database before calling init")

    with Session(engine) as session:
        yield session


Service = Annotated[Session, Depends(open)]


def get_or_create_session(open_func):
    def function(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with contextlib.contextmanager(open)() as database:
                request = kwargs["request"]
                session = get_session(request, database)
                request.state.session = session

                result = await func(*args, **kwargs)

                result.set_cookie(
                    key="session_id",
                    value=session.id,
                    httponly=True,
                    secure=False,  # TODO: set to true when using HTTPS
                    samesite="lax",
                )
                return result

        return wrapper

    return function


def get_session(request: Request, db: Service) -> UserSession:
    session_id = request.cookies.get("session_id")
    if session_id:
        session = db.get(UserSession, uuid.UUID(session_id))
        if session:
            # TODO: Mark session as used??
            return session

    user_session = UserSession()
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session
