from fastapi import Depends, Request, Response, HTTPException
from sqlmodel import create_engine, Session, SQLModel, select
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_


from app.database.user import UserSession, UserState
from app.database.quest import Quest, load_quests

import uuid
import logging
from datetime import date

logger = logging.getLogger("uvicorn")


# TODO: Remove singletons
engine = None
SessionLocal = None

# TODO: Don't have hard coded
_JSON_PATH = "app/database/quests.json"
TUTORIAL_ID = "tutorial"


def open_session():
    if engine is None:
        raise Exception("attempted to get database before calling init")

    with Session(engine) as session:
        yield session


def get_daily_quests(session: UserSession, db=Depends(open_session)):
    # TODO: This is an assummption that won't be true in the future
    show_tutorial = session.created_at == session.updated_at
    query = (
        select(Quest, UserState)
        .where(
            or_(
                func.date(Quest.release_date) == date.today(),
                (show_tutorial and Quest.id == TUTORIAL_ID),
            )
        )
        .outerjoin(
            UserState,
            Quest.id == UserState.quest,
        )
    )
    return db.exec(query).all()


def mark_quest_as_done(session: UserSession, quest_id: str, db=Depends(open_session)):
    quest = db.exec(select(Quest).where(Quest.id == quest_id)).one_or_none()
    if quest is None or (
        quest.id != TUTORIAL_ID and quest.release_date != date.today()
    ):
        raise ValueError("Quest does not exist")

    state = UserState(
        user=session.id,
        quest=quest_id,
    )
    db.add(state)
    db.commit()
    db.refresh(state)
    return quest, state


def get_session_or_create(
    request: Request, response: Response, db=Depends(open_session)
):
    session = _get_session(request, db, can_create=True)
    request.state.session = session
    return session


def get_session_or_error(
    request: Request, response: Response, db=Depends(open_session)
):
    session = _get_session(request, db, can_create=False)
    request.state.session = session
    return session


def _get_session(
    request: Request, db=Depends(open_session), can_create=True
) -> UserSession:
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
        logger.info(f"creating new session: {user_session.id}")
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

    try:
        quests = load_quests(_JSON_PATH)
    except ValueError as e:
        logger.error(f"Loading JSON quests: {e}")
        quests = []

    with Session(engine) as session:
        for quest in quests:
            session.add(quest)
        session.commit()
    logger.info(f"Loaded {len(quests)} quests")
