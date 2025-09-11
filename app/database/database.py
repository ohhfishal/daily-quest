from fastapi import Depends, Request, Response, HTTPException
from sqlmodel import create_engine, Session, SQLModel, select
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_


from app.database.user import UserSession, UserState
from app.database.quest import Quest, load_quests
from app.config import Settings

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
TUTORIAL_ITEM = "The Master Sword"


def open_session():
    if engine is None:
        raise Exception("attempted to get database before calling init")

    with Session(engine) as session:
        yield session


def get_tutorial(db=Depends(open_session)):
    return db.exec(select(Quest).where(Quest.id == TUTORIAL_ID)).one_or_none()


def get_daily_quests(session: UserSession, db=Depends(open_session)):
    show_tutorial = (TUTORIAL_ITEM not in session.items) or (
        session.updated_at.date() == session.created_at.date()
    )
    return db.exec(
        (
            select(Quest, UserState)
            .where(
                or_(
                    func.date(Quest.release_date) == date.today(),
                    (show_tutorial and Quest.id == TUTORIAL_ID),
                )
            )
            .order_by(Quest.release_date)
            .outerjoin(
                UserState,
                Quest.id == UserState.quest,
            )
        )
    ).all()


def mark_quest_as_done(session: UserSession, quest_id: str, db=Depends(open_session)):
    quest = db.get(Quest, quest_id)
    if not quest or (quest.id != TUTORIAL_ID and quest.release_date != date.today()):
        raise ValueError("Quest does not exist")

    state = UserState(user=session.id, quest=quest_id)
    db.add(state)

    session.xp += quest.rewards_xp
    session.items = session.items + quest.rewards_items
    db.add(session)
    db.commit()

    db.refresh(session)
    db.refresh(state)

    assert session.xp >= quest.rewards_xp, (
        f"Expected at least {quest.rewards_xp} in session"
    )
    assert len(session.items) >= len(quest.rewards_items), (
        f"Expected at least {len(quest.rewards_items)} in items"
    )
    return quest, state


def get_session_or_error(
    request: Request, response: Response, db=Depends(open_session)
):
    session = _get_session(request, db, can_create=False)
    request.state.session = session
    return session


def get_session_or_none(request: Request, response: Response, db=Depends(open_session)):
    try:
        session = _get_session(request, db, can_create=False)
        request.state.session = session
        return session
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Unknown Exception (get_session_or_none): {e}")
        return None


def create_new_session(db=Depends(open_session)) -> UserSession:
    user_session = UserSession()
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    logger.info(f"creating new session: {user_session.id}")
    return user_session


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
        return create_new_session(db=db)
    raise Exception("BUG FOUND")


def init(config: Settings):
    connection = config.database_connection
    connect_args = {"check_same_thread": False}
    global engine
    if connection == "sqlite:///:memory:":
        engine = create_engine(
            connection,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
        logger.warn("Using in memory database")
    else:
        engine = create_engine(connection, connect_args=connect_args)

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
        ids = {quest.id: quest for quest in session.exec(select(Quest)).all()}
        updating = 0
        inserting = 0
        for quest in quests:
            if existing_quest := ids.get(quest.id, None):
                existing_quest.release_date = quest.release_date
                existing_quest.title = quest.title
                existing_quest.rewards_xp = quest.rewards_xp
                existing_quest.rewards_items = quest.rewards_items
                existing_quest.objectives = quest.objectives
                updating += 1
            else:
                inserting += 1
                session.add(quest)
        session.commit()
    logger.info(f"Updated {updating} quests and Created {inserting} quests")
