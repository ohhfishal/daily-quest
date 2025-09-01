from fastapi import Depends, Request, Response, HTTPException
from sqlmodel import create_engine, Session, SQLModel, select
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker


from app.database.session import UserSession
from app.database.quest import Quest, quests

import uuid

# TODO: Remove singletons
engine = None
SessionLocal = None


def open():
    if engine is None:
        raise Exception("attempted to get database before calling init")

    with Session(engine) as session:
        yield session


def get_all_quests(session: UserSession, db=Depends(open)):
    return db.exec(select(Quest)).all()


def get_session_or_create(request: Request, response: Response, db=Depends(open)):
    session = _get_session(request, db, can_create=True)
    request.state.session = session
    return session


def get_session_or_error(request: Request, response: Response, db=Depends(open)):
    session = _get_session(request, db, can_create=False)
    request.state.session = session
    return session


def _get_session(request: Request, db=Depends(open), can_create=True) -> UserSession:
    session_id = request.cookies.get("session_id")
    if session_id:
        session = db.get(UserSession, uuid.UUID(session_id))
        if session:
            # TODO: Mark session as used??
            return session
        elif not can_create:
            raise HTTPException(
                status_code=401,
                detail="Unknown session",
            )
    if not can_create:
        raise HTTPException(
            status_code=400,
            detail="Missing session id",
        )
    else:
        user_session = UserSession()
        db.add(user_session)
        db.commit()
        db.refresh(user_session)
        return user_session
    raise Exception("BUG FOUND")


def init(file=":memory:"):
    connect_args = {"check_same_thread": False}
    global engine
    if file == ":memory:":
        engine = create_engine(
            "sqlite:///:memory:",
            # echo=True,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            f"sqlite:///{file}", echo=True, connect_args=connect_args
        )

    SQLModel.metadata.create_all(engine)

    global SessionLocal
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    with Session(engine) as session:
        for quest in quests:
            session.add(quest)
        session.commit()
