import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # ✅ added this
from hume.legacy import HumeVoiceClient, MicrophoneInterface
from typing import Dict
import json
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")
active_connections: Dict[WebSocket, bool] = {}

# ✅ Mount /static to serve gifs, css, js, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")  # ✅ added this

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HUME_API_KEY = "aq0kRkUm3KkJAmDRmVAPzXvPA1POBFAaErGJZtepGSejgTbH"
CONFIG_ID = "bbf3717d-67f3-49f0-91d5-ae37dcb3b4d7"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections[websocket] = True
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "start_voice":
                active_connections[websocket] = True
            elif message.get("type") == "stop_voice":
                active_connections[websocket] = False
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.pop(websocket, None)

@app.get("/start-voice")
async def start_voice():
    client = HumeVoiceClient(HUME_API_KEY)
    async with client.connect(config_id=CONFIG_ID) as socket:
        mic = MicrophoneInterface()
        await mic.start(socket)
        while True:
            try:
                text = await mic.get_transcription()
                if text:
                    logger.info(f"[HUME] User said: {text}")
                    for conn, active in active_connections.items():
                        if active:
                            await conn.send_json({"type": "user", "message": text})
                            await conn.send_json({"type": "ai", "message": f"I heard: {text}"})
            except Exception as e:
                logger.error(f"Mic error: {e}")
                break
    return {"status": "Voice session ended"}
