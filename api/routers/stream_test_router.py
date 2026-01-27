import cv2
import numpy as np
import threading
import json
import time
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

# --- CONFIG ---
WIDTH = 320
HEIGHT = 240
BOX_SIZE = 20
MOVE_SPEED = 5
FPS = 30

# --- GLOBAL STATE ---
game = None
game_lock = threading.Lock()

# --- THE "GAME" ENGINE ---
class SimpleGame:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        
        self.keys = {
            "ArrowUp": False, "ArrowDown": False, 
            "ArrowLeft": False, "ArrowRight": False
        }
        self.lock = threading.Lock()
        self.current_frame = None
        self.running = True

        print(" [SimpleGame] Engine Started")
        threading.Thread(target=self._loop, daemon=True).start()

    def update_key(self, key, is_pressed):
        with self.lock:
            if key in self.keys:
                self.keys[key] = is_pressed

    def _loop(self):
        while self.running:
            start_time = time.time()

            with self.lock:
                # 1. Update Position
                if self.keys["ArrowUp"]: self.y -= MOVE_SPEED
                if self.keys["ArrowDown"]: self.y += MOVE_SPEED
                if self.keys["ArrowLeft"]: self.x -= MOVE_SPEED
                if self.keys["ArrowRight"]: self.x += MOVE_SPEED

                self.x = max(0, min(WIDTH - BOX_SIZE, self.x))
                self.y = max(0, min(HEIGHT - BOX_SIZE, self.y))

                # 2. Render
                canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                cv2.rectangle(canvas, (self.x, self.y), (self.x + BOX_SIZE, self.y + BOX_SIZE), (0, 255, 0), -1)
                cv2.putText(canvas, "TEST MODE (GREEN BOX)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                ret, buffer = cv2.imencode('.jpg', canvas)
                self.current_frame = buffer.tobytes()

            elapsed = time.time() - start_time
            sleep_time = (1.0 / FPS) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

# --- HELPER: LAZY START ---
def ensure_game_running():
    global game
    with game_lock:
        if game is None:
            game = SimpleGame()

# --- ROUTER ---
router = APIRouter(prefix="/stream", tags=["StreamTest"])

def frame_generator():
    ensure_game_running() # Auto-start on video request
    while True:
        if game and game.current_frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + game.current_frame + b'\r\n')
        time.sleep(1.0 / FPS)

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # 1. Auto-start on WebSocket connection
    ensure_game_running()
    
    # 2. Wait for game to be ready (Instant, but safe)
    while game is None:
        await asyncio.sleep(0.1)

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            
            # Simple "Green Box" Logic
            is_pressed = True if event['type'] == 'down' else False
            game.update_key(event['key'], is_pressed)
            
    except WebSocketDisconnect:
        # Don't print error on disconnect, it's normal during hot reload
        pass
    except Exception as e:
        print(f" [SimpleGame] Error: {e}")
