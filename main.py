from app.core.config import settings
from app.routers import academy, auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FastAPI CRUD with JWT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

app.include_router(auth.router)
app.include_router(academy.router)


@app.get("/")
def read_root():
    return {"message": "Academy of Digital Literacy"}
