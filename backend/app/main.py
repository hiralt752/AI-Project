from app.api.v1.routes.auth import router as auth_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router)