from fastapi import FastAPI

from app.routers import auth


app = FastAPI()
app.include_router(auth.router)


@app.get("/")
async def home():
    return {"message" : "Olá Mundo"}
