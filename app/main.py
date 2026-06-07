from fastapi import FastAPI

from app.routers import accounts, auth, customers, transactions


app = FastAPI()
app.include_router(accounts.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(transactions.router)


@app.get("/")
async def home():
    return {"message" : "Olá Mundo"}
