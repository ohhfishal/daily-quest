from fastapi import FastAPI, Request, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import database

import logging

logger = logging.getLogger("uvicorn")


app = FastAPI()


@app.on_event("startup")
def on_startup():
    database.init()


def get_logger():
    return logging.getLogger("uvicorn")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.post("/quest/{id}", response_class=HTMLResponse)
async def update_quest(
    request: Request,
    id: str,
    user_session=Depends(database.get_session_or_error),
    db=Depends(database.open_session),
    logger=Depends(get_logger),
):
    try:
        quest, state = database.mark_quest_as_done(user_session, id, db)
        return templates.TemplateResponse(
            request=request,
            name="components/quest.html",
            context={
                "quest": quest,
                "state": state,
            },
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Quest does not exist",
        )
    except Exception as e:
        logger.error(f"Unknown Exception: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unknown error occurred",
        )
    raise HTTPException(
        status_code=500,
        detail="Unknown error occurred",
    )


@app.get("/")
async def root(
    request: Request,
    response: Response,
    user_session=Depends(database.get_session_or_create),
    db=Depends(database.open_session),
):
    quests = database.get_daily_quests(user_session, db)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "session": user_session,
            "quests": quests,
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
