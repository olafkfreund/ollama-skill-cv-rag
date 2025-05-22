import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from src.backend.api.tts import router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.mark.asyncio
async def test_tts_success(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tts", json={"text": "Hello, world!"})
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/wav")
        assert response.headers["x-api-status"] == "success"
        assert response.headers["x-api-message"] == "Audio generated successfully."
        assert response.content  # Should contain audio bytes

@pytest.mark.asyncio
async def test_tts_empty_text(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tts", json={"text": "   "})
        assert response.status_code == 400
        assert response.headers["content-type"] == "application/json"
        assert b'Text is required for TTS.' in response.content

@pytest.mark.asyncio
async def test_tts_missing_text(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tts", json={})
        assert response.status_code == 422  # FastAPI validation error
