from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import quest

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
                quest.Quest(
                    "It's dangerous to go alone!",
                    objectives=["Take this."],
                    reward=quest.Reward(
                        items=["The Master Sword"],
                    ),
                ),
            ],
        },
    )
