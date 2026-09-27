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


def _include_routers():
    from app.api.evaluate import router as evaluate_router
    from app.api.runs import router as runs_router
    app.include_router(evaluate_router)
    app.include_router(runs_router)


_include_routers()
    