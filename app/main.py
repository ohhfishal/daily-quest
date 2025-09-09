from fastapi import FastAPI, Request, Depends, Response, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated

from app.database import database
from app.discord import submit_feedback

import functools
import os
from datetime import datetime

import logging

logger = logging.getLogger("uvicorn")


app = FastAPI()


@app.on_event("startup")
def on_startup():
    database.init()
    now = datetime.now()
    logger.debug(f"Stared: {now.date()} {now.time()}")


def get_logger():
    return logging.getLogger("uvicorn")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/components/inventory", response_class=HTMLResponse)
async def components_inventory(
    request: Request,
    user_session=Depends(database.get_session_or_error),
    db=Depends(database.open_session),
):
    return templates.TemplateResponse(
        request=request,
        name="components/inventory.html",
        context={
            "session": user_session,
        },
    )


@app.get("/components/notification", response_class=HTMLResponse)
async def components_notification(
    request: Request,
    user_session=Depends(database.get_session_or_error),
    db=Depends(database.open_session),
):
    quests = database.get_daily_quests(user_session, db)
    if len(quests) == 0:
        logger.error(f"Got 0 quests session={user_session.id}")

    return templates.TemplateResponse(
        request=request,
        name="components/notification.html",
        context={
            "done": functools.reduce(lambda x, y: x and y[1] is not None, quests),
        },
    )


@app.post("/quest/{id}", response_class=HTMLResponse)
async def update_quest(
    request: Request,
    id: str,
    user_session=Depends(database.get_session_or_error),
    db=Depends(database.open_session),
    logger=Depends(get_logger),
):
    # TODO: Have this refresh the page or emit an event
    try:
        quest, state = database.mark_quest_as_done(user_session, id, db)
        response = templates.TemplateResponse(
            request=request,
            name="components/quest.html",
            context={
                "quest": quest,
                "state": state,
            },
        )
        response.headers["HX-Trigger"] = "quest_completed"
        return response
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Quest does not exist",
        )
    except AssertionError as e:
        logger.error(f"Assert tripped: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unknown error occurred",
        )
    except Exception as e:
        logger.error(f"Unknown Exception: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unknown error occurred",
        )
    assert False, "Unreachable code reached"


@app.get("/contact")
async def contact(request: Request, response: Response):
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "contact": {
                "discord": os.getenv("CONTACT_DISCORD", None),
            },
        },
    )


@app.get("/tutorial")
async def tutorial(
    request: Request,
    response: Response,
    # user_session=Depends(database.get_session_or_create),
    db=Depends(database.open_session),
):
    # TODO: Make sure there is no session?
    return templates.TemplateResponse(
        request=request,
        name="tutorial.html",
        context={
            "quest": database.get_tutorial(db),
        },
    )


@app.get("/")
async def root(
    request: Request,
    user_session=Depends(database.get_session_or_none),
    db=Depends(database.open_session),
):
    if user_session is None:
        return RedirectResponse("/tutorial")

    quests = database.get_daily_quests(user_session, db)
    if len(quests) == 0:
        logger.warn(f"Got 0 quests session={user_session.id}")

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "session": user_session,
            "quests": quests,
            # Check if all quests are done
            "done": functools.reduce(lambda x, y: x and y[1] is not None, quests),
        },
    )
    response.set_cookie(
        key="session_id",
        value=user_session.id,
        httponly=True,
        secure=False,  # TODO: set to true when using HTTPS
        samesite="lax",
    )
    return response


@app.post("/register")
async def register(
    request: Request,
    user_session=Depends(database.get_session_or_none),
    db=Depends(database.open_session),
):
    if user_session is not None:
        return PlainTextResponse("Already in a valid session", status_code=400)
    user_session = database.create_new_session(db=db)

    _, _ = database.mark_quest_as_done(user_session, database.TUTORIAL_ID, db)

    response = PlainTextResponse("OK")
    response.headers["HX-Redirect"] = "/"
    response.set_cookie(
        key="session_id",
        value=user_session.id,
        httponly=True,
        secure=False,  # TODO: set to true when using HTTPS
        samesite="lax",
    )
    return response


@app.post("/feedback")
async def handle_feedback(
    feedback: Annotated[str, Form()],
    request: Request,
    user_session=Depends(database.get_session_or_none),
):
    try:
        await submit_feedback(feedback, user_session=user_session)
    except Exception as e:
        logger.error(f"submitting feedback: {e}")
        raise HTTPException(detail="Unknown error occurred", status_code=500)


@app.get("/health")
async def health():
    return "OK"
