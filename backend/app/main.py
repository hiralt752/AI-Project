from app.api.v1.routes.auth import router as auth_router
from fastapi import FastAPI
from app.api.v1.routes.admin import router as admin_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)