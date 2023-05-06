from fastapi import FastAPI

from app.card.card_router import card_router
from app.train.train_router import train_router

title = "NYC Subway System API"
description = """
The NYC subway system API has a few different features you can use to emulate life in NYC

## Important notes
- There is a race condition between Entering and exiting. someone who exits will see the current balance of the 
card. its assumed they aren't swiping that card before exiting
- No permissions exist
"""

app = FastAPI(
    title=title,
    description=description,
    version="0.0.1",
)

app.include_router(train_router)
app.include_router(card_router)


@app.on_event("startup")
async def startup_event():
    print("startup...")


@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown...")
