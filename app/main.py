from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="EvalOps", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "evalops"}
    