from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.quest import Quest, Reward, Item


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Main HTML Page
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "id": 1,
            "quests": [
                Quest(
                    "It's dangerous to go alone!",
                    objectives=["Take this."],
                    reward=Reward(
                        items=[
                            Item("The Master Sword", description="Unlocks the inventory!"),
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
