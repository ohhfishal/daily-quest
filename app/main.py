from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.database.quest import Quest, Reward, Item
from app.database import database


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    database.init()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, response: Response, db: database.Service):
    session = database.get_or_create_session(request, db)

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
