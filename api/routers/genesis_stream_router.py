import genesis as gs
import numpy as np
import cv2
import threading
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse

# --- CONFIGURATION: Docker / M3 Mac Optimization ---
# We use low resolution and CPU backend to ensure this runs 
# inside a Docker container without GPU passthrough.
RENDER_WIDTH = 320
RENDER_HEIGHT = 240
FPS_LIMIT = 20
BACKEND = gs.cpu  # <--- Critical for M3 Docker compatibility

# --- 1. Simulation Manager ---
class SimulationManager:
    def __init__(self):
        # Prevent re-initialization issues if imported multiple times
        if not gs.is_initialized():
            # Force CPU backend for Docker compatibility
            gs.init(backend=BACKEND, logging_level='warning')
        
        self.scene = gs.Scene(
            viewer_options=gs.options.ViewerOptions(
                res=(RENDER_WIDTH, RENDER_HEIGHT),
                camera_pos=(3.0, 3.0, 2.5),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=40,
            ),
            sim_options=gs.options.SimOptions(dt=0.01),
            show_viewer=False, # Essential for headless Docker
        )

        self.plane = self.scene.add_entity(gs.morphs.Plane())
        
        # Replace this with your humanoid XML if you have one
        self.robot = self.scene.add_entity(
            gs.morphs.Box(size=(0.5, 0.5, 1.0), pos=(0, 0, 1.0)),
        )

        self.cam = self.scene.add_camera(
            res=(RENDER_WIDTH, RENDER_HEIGHT),
            pos=(4.0, 0.0, 2.0),
            lookat=(0, 0, 0.5),
            fov=45,
            gui_mode=False,
        )

        self.scene.build()
        
        self.current_frame = None
        self.lock = threading.Lock()
        
        self.keys = {
            "ArrowUp": False, "ArrowDown": False, 
            "ArrowLeft": False, "ArrowRight": False
        }

    def update_key(self, key, is_pressed):
        if key in self.keys:
            self.keys[key] = is_pressed

    def apply_controls(self):
        # Basic logic to push the object based on keys
        force = np.array([0.0, 0.0, 0.0])
        strength = 20.0 

        if self.keys["ArrowUp"]: force[0] = -strength
        if self.keys["ArrowDown"]: force[0] = strength
        if self.keys["ArrowLeft"]: force[1] = -strength
        if self.keys["ArrowRight"]: force[1] = strength

        # Apply force if any key is pressed
        if np.linalg.norm(force) > 0:
            try:
                # Assuming a 6-DOF free joint for the box/humanoid root
                dof_force = np.concatenate([force, [0,0,0]])
                if self.robot.n_dofs == len(dof_force):
                    self.robot.set_dofs_force(dof_force)
            except Exception:
                pass

    def start_loop(self):
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while True:
            self.apply_controls()
            self.scene.step()
            
            # Render
            self.cam.render()
            
            # Since we are on CPU backend, .cpu() isn't strictly necessary but safe
            rgb = self.cam.get_color_texture().numpy()
            
            # Ensure format is correct for OpenCV
            if rgb.dtype != np.uint8:
                rgb = (rgb * 255).astype(np.uint8)
            
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            
            # Encode with lower quality (60%) for faster network streaming/lower CPU usage
            ret, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 60])

            with self.lock:
                self.current_frame = buffer.tobytes()

# Instantiate global simulation
sim = SimulationManager()
sim.start_loop()

# --- 2. API Router ---
PREFIX = "/genesis_stream"
router = APIRouter(prefix=PREFIX, tags=["Genesis"])

# HTML Client (Optional fallback if not using React)
html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Genesis Stream</title>
        <style>
            body {{ display: flex; flex-direction: column; align-items: center; background: #222; color: white; font-family: sans-serif; }}
            img {{ border: 2px solid #555; margin-top: 20px; image-rendering: pixelated; }}
            .status {{ margin-top: 10px; color: #0f0; }}
        </style>
    </head>
    <body>
        <h1>Genesis Remote Control (Docker Mode)</h1>
        <img src="{PREFIX}/video_feed" width="{RENDER_WIDTH * 2}" height="{RENDER_HEIGHT * 2}">
        <div class="status">Controls: Arrow Keys</div>
        <script>
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + "//" + location.host + "{PREFIX}/ws";
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => console.log("Connected");

            window.addEventListener("keydown", function(e) {{
                if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].indexOf(e.code) > -1) {{
                    e.preventDefault();
                    if(ws.readyState === 1) ws.send(JSON.stringify({{key: e.code, type: "down"}}));
                }}
            }}, false);

            window.addEventListener("keyup", function(e) {{
                if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].indexOf(e.code) > -1) {{
                    if(ws.readyState === 1) ws.send(JSON.stringify({{key: e.code, type: "up"}}));
                }}
            }}, false);
        </script>
    </body>
</html>
"""

@router.get("/")
async def get_interface():
    return HTMLResponse(html)

def frame_generator():
    """Reads the latest frame"""
    while True:
        with sim.lock:
            frame = sim.current_frame
        
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Limit FPS to save CPU cycles in Docker
        time.sleep(1.0 / FPS_LIMIT)

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            is_pressed = True if event['type'] == 'down' else False
            sim.update_key(event['key'], is_pressed)
            
    except WebSocketDisconnect:
        for key in sim.keys:
            sim.keys[key] = False
        print("Client disconnected")
