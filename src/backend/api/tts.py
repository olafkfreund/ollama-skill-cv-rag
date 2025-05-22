from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Any, Dict
import asyncio
import tempfile
from TTS.api import TTS
import os
import logging

router = APIRouter()

# Set up logger
logger = logging.getLogger("tts_api")

tts_model = None

def get_tts_model() -> TTS:
    """
    Lazily load and return the Coqui TTS model.
    Returns:
        TTS: Coqui TTS model instance
    """
    global tts_model
    if tts_model is None:
        tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=os.environ.get("TTS_USE_GPU", "false").lower() == "true")
    return tts_model

def create_response(status: str, data: Any, message: str) -> Dict[str, Any]:
    """
    Create a standardized API response.
    Args:
        status: Response status
        data: Response data
        message: Response message
    Returns:
        Formatted response dictionary
    """
    return {"status": status, "data": data, "message": message}

class TTSRequest(BaseModel):
    text: str

class TTSResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str

@router.post("/tts", response_class=Response, tags=["TTS"], summary="Convert text to speech (Coqui TTS)")
async def text_to_speech(request: TTSRequest) -> Response:
    """
    Convert text to speech using Coqui TTS and return audio as WAV.
    Args:
        request: TTSRequest with text to convert
    Returns:
        WAV audio bytes in a standardized API response
    """
    if not request.text or not request.text.strip():
        error = create_response("error", {}, "Text is required for TTS.")
        return Response(content=str(error), media_type="application/json", status_code=400)
    try:
        tts = get_tts_model()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tts.tts_to_file(text=request.text, file_path=tmp.name)
            tmp.seek(0)
            audio_bytes = tmp.read()
        headers = {"Content-Disposition": "inline; filename=output.wav"}
        headers["X-API-Status"] = "success"
        headers["X-API-Message"] = "Audio generated successfully."
        return Response(content=audio_bytes, media_type="audio/wav", headers=headers)
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        error = create_response("error", {}, f"TTS generation failed: {str(e)}")
        return Response(content=str(error), media_type="application/json", status_code=500)
