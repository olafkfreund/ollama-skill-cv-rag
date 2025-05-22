from fastapi import FastAPI
from src.backend.api import tts

app = FastAPI()

app.include_router(tts.router)