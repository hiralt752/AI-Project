from app.api.v1.routes.auth import router as auth_router
from fastapi import FastAPI
from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.files import router as file

app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(file)