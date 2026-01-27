import cv2
import numpy as np
import threading
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

# --- CONFIG ---
WIDTH = 320
HEIGHT = 240
BOX_SIZE = 20
MOVE_SPEED = 5
FPS = 30

# --- THE "GAME" ENGINE ---
# No physics, just X/Y coordinates
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

        # Start the "Game Loop" immediately
        threading.Thread(target=self._loop, daemon=True).start()

    def update_key(self, key, is_pressed):
        with self.lock:
            if key in self.keys:
                self.keys[key] = is_pressed

    def _loop(self):
        while self.running:
            start_time = time.time()

            # 1. UPDATE STATE (Move the box)
            with self.lock:
                if self.keys["ArrowUp"]: self.y -= MOVE_SPEED
                if self.keys["ArrowDown"]: self.y += MOVE_SPEED
                if self.keys["ArrowLeft"]: self.x -= MOVE_SPEED
                if self.keys["ArrowRight"]: self.x += MOVE_SPEED

                # Keep in bounds
                self.x = max(0, min(WIDTH - BOX_SIZE, self.x))
                self.y = max(0, min(HEIGHT - BOX_SIZE, self.y))

                # 2. RENDER (Draw box on black background)
                # Create black canvas (Height, Width, 3 Color Channels)
                canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                
                # Draw Green Rectangle
                # cv2.rectangle(img, start_point, end_point, color, thickness)
                cv2.rectangle(canvas, (self.x, self.y), (self.x + BOX_SIZE, self.y + BOX_SIZE), (0, 255, 0), -1)

                # Add some text
                cv2.putText(canvas, "TEST MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Encode to JPEG
                ret, buffer = cv2.imencode('.jpg', canvas)
                self.current_frame = buffer.tobytes()

            # 3. SLEEP (Maintain FPS)
            elapsed = time.time() - start_time
            sleep_time = (1.0 / FPS) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

# Initialize immediately (No heavy loading needed)
game = SimpleGame()

# --- ROUTER ---
router = APIRouter(prefix="/stream", tags=["StreamTest"])

def frame_generator():
    while True:
        if game.current_frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + game.current_frame + b'\r\n')
        time.sleep(1.0 / FPS)

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive JSON from frontend
            data = await websocket.receive_text()
            event = json.loads(data)
            
            # Parse logic matches your frontend
            # Expects: { "type": "down"|"up", "key": "ArrowUp" }
            is_pressed = True if event['type'] == 'down' else False
            game.update_key(event['key'], is_pressed)
            
    except WebSocketDisconnect:
        print("Client disconnected")
