from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import database

import logging

logger = logging.getLogger("uvicorn")


app = FastAPI()


@app.on_event("startup")
def on_startup():
    database.init()


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.post("/quest/{id}", response_class=HTMLResponse)
async def update_quest(request: Request, db=Depends(database.open_session)):
    # TODO: Implement
    return PlainTextResponse("OK")
    # return templates.TemplateResponse(
    #     request=request,
    #     name="components/quest.html",
    #     context={
    #     },
    # )


@app.get("/")
async def root(
    request: Request,
    response: Response,
    user_session=Depends(database.get_session_or_create),
    db=Depends(database.open_session),
):
    quests = database.get_all_quests(user_session, db)
    logger.info(quests)
    response = templates.TemplateResponse(
        request=request,
        name="pages/index.html",
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
