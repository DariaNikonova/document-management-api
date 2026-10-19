from fastapi import FastAPI

from routers.documents import documents_router
from routers.auth import auth_router


app = FastAPI()

app.include_router(documents_router)
app.include_router(auth_router)