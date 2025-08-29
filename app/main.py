from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlmodel import Session

from app.database.quest import Quest, Reward, Item
from app.database import database
from app.database.session import UserSession

from typing import Annotated

import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

Database = Annotated[Session, Depends(database.open)]


def get_or_create_session(request: Request, database: Database) -> UserSession:
    session_id = request.cookies.get("session_id")
    if session_id:
        session = database.get(UserSession, uuid.UUID(session_id))
        if session:
            # TODO: Mark session as used??
            return session

    user_session = UserSession()
    database.add(user_session)
    database.commit()
    database.refresh(user_session)
    return user_session


@app.on_event("startup")
def on_startup():
    database.init()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, response: Response, database: Database):
    session = get_or_create_session(request, database)

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "session": session,
            "quests": [
                Quest(
                    "It's dangerous to go alone!",
                    objectives=["Take this."],
                    reward=Reward(
                        items=[
                            Item("The Master Sword"),
                        ],
                    ),
                ),
                Quest(
                    "Enter the dragon's lair",
                    objectives=["Do something new and uncomfortable"],
                    reward=Reward(
                        gold=10,
                        # items=["The Master Sword"],
                    ),
                ),
            ],
        },
    )

    # reset the cookie
    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=False,  # TODO: set to true when using HTTPS
        samesite="lax",
    )
    return response
