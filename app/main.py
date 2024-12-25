from contextlib import asynccontextmanager

from fastapi import FastAPI


from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.auth.base_config import router as auth_router
from app.auth.database import create_db_and_tables

from app.api import router


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_db_and_tables()

    yield

app = FastAPI(
    title="Car scan market",
    version="0.1",
    summary="Webpage to control coming cars to market.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello, This is root path!"}

app.include_router(auth_router)
app.include_router(router)
app.mount("/storage", StaticFiles(directory="app/storage"), name="storage")
