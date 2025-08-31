from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.database.quest import Quest, Reward, Item
from app.database import database

import uuid

app = FastAPI()

@app.on_event("startup")
def on_startup():
    database.init()


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.post("/quest/{id}", response_class=HTMLResponse)
@database.get_session(database.open, can_create=False)
async def update_quest(request: Request):
    # TODO: Implement
    return PlainTextResponse("OK")
    # return templates.TemplateResponse(
    #     request=request,
    #     name="components/quest.html",
    #     context={
    #     },
    # )

@app.get("/", response_class=HTMLResponse)
@database.get_session(database.open, can_create=True)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        context={
            "session": request.state.session,
            "quests": [
                Quest(
                    uuid.uuid4(),
                    "It's dangerous to go alone!",
                    objectives=["Take this."],
                    reward=Reward(
                        items=[
                            Item("The Master Sword"),
                        ],
                    ),
                ),
                Quest(
                    uuid.uuid4(),
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
