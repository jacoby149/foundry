import numpy as np
import cv2
import threading
import json
import time
import sys
from enum import Enum
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

# --- CONFIGURATION ENUM ---
class SimMode(Enum):
    SIMPLE = "simple"   # Ultra-light: 128p, Sphere, Frame Skipping
    REGULAR = "regular" # Standard: 320p, Box, High Fidelity

# *** SET THIS TO CHANGE MODE ***
CURRENT_MODE = SimMode.SIMPLE 

# --- Global Simulation Placeholder ---
sim = None 
sim_loading = False

class SimulationManager:
    def __init__(self):
        # LAZY IMPORT
        global gs
        import genesis as gs
        
        print(f" [Genesis] Initializing Mode: {CURRENT_MODE.value.upper()}")

        # 1. CONFIGURE SETTINGS BASED ON MODE
        if CURRENT_MODE == SimMode.SIMPLE:
            self.width = 128
            self.height = 96
            self.jpeg_quality = 30
            self.steps_per_frame = 4  # Physics runs 4x faster than video
            self.dt = 0.01
        else:
            self.width = 320
            self.height = 240
            self.jpeg_quality = 60
            self.steps_per_frame = 1  # 1:1 Physics to Video
            self.dt = 0.01

        # Force CPU backend for Docker/M3 stability
        if not gs.is_initialized():
            gs.init(backend=gs.cpu, logging_level='error') 
        
        # 2. SETUP SCENE
        self.scene = gs.Scene(
            viewer_options=gs.options.ViewerOptions(
                res=(self.width, self.height),
                camera_pos=(3.0, 3.0, 2.5),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=45,
            ),
            sim_options=gs.options.SimOptions(dt=self.dt),
            show_viewer=False, 
        )

        self.plane = self.scene.add_entity(gs.morphs.Plane())
        
        # 3. ADD ENTITY BASED ON MODE
        if CURRENT_MODE == SimMode.SIMPLE:
            # SPHERE (Cheapest math)
            print(" [Genesis] Spawning Sphere...")
            self.robot = self.scene.add_entity(
                gs.morphs.Sphere(radius=0.4, pos=(0, 0, 0.5)),
                surface=gs.surfaces.Rough(color=(0.8, 0.2, 0.2)) # Red
            )
        else:
            # BOX (More expensive collision math)
            print(" [Genesis] Spawning Box...")
            self.robot = self.scene.add_entity(
                gs.morphs.Box(size=(0.5, 0.5, 1.0), pos=(0, 0, 1.0)),
            )

        self.cam = self.scene.add_camera(
            res=(self.width, self.height),
            pos=(3.5, 0.0, 1.5),
            lookat=(0, 0, 0.5),
            fov=45,
            gui_mode=False,
        )

        self.scene.build()
        print(" [Genesis] Scene built successfully!")
        
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
        force = np.array([0.0, 0.0, 0.0])
        strength = 15.0 
        if self.keys["ArrowUp"]: force[0] = -strength
        if self.keys["ArrowDown"]: force[0] = strength
        if self.keys["ArrowLeft"]: force[1] = -strength
        if self.keys["ArrowRight"]: force[1] = strength

        if np.linalg.norm(force) > 0:
            try:
                # Works for both Box and Sphere (XYZ forces)
                dof_force = np.concatenate([force, [0,0,0]])
                # Safety check for DOFs (Sphere=6, Box=6 usually)
                if self.robot.n_dofs >= 3:
                    # Just apply to first 3 DOFs if possible, or all if matching
                    pad = np.zeros(self.robot.n_dofs - 3)
                    final_force = np.concatenate([force, pad])
                    self.robot.set_dofs_force(final_force)
            except Exception:
                pass

    def start_loop(self):
        self._loop()

    def _loop(self):
        while True:
            # --- PHYSICS STEP ---
            # In SIMPLE mode, this runs 4 times.
            # In REGULAR mode, this runs 1 time.
            for _ in range(self.steps_per_frame):
                self.apply_controls()
                self.scene.step()
            
            # --- RENDER STEP ---
            self.cam.render()
            rgb = self.cam.get_color_texture().numpy()
            
            if rgb.dtype != np.uint8:
                rgb = (rgb * 255).astype(np.uint8)
            
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            ret, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])

            with self.lock:
                self.current_frame = buffer.tobytes()
            
            # Simple manual sleep to prevent 100% CPU usage
            time.sleep(0.01)

# --- Background Loader ---
def init_simulation_background():
    global sim
    # Wait for Uvicorn startup
    time.sleep(3) 
    try:
        sim = SimulationManager()
        sim.start_loop()
    except Exception as e:
        print(f" [Genesis] Critical Error: {e}")
        import traceback
        traceback.print_exc()

# --- Router ---
PREFIX = "/genesis_stream"
router = APIRouter(prefix=PREFIX, tags=["Genesis"])

# --- Startup Event ---
@router.on_event("startup")
async def start_sim_thread():
    global sim_loading
    if not sim_loading:
        sim_loading = True
        t = threading.Thread(target=init_simulation_background, daemon=True)
        t.start()

# --- Endpoints ---
def frame_generator():
    while True:
        if sim is None:
            time.sleep(0.2)
            continue

        with sim.lock:
            frame = sim.current_frame
        
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Limit the sending rate to ~20FPS so we don't flood the network
        time.sleep(0.05) 

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Wait for sim
    retries = 0
    while sim is None and retries < 15:
        await websocket.send_text(json.dumps({"status": "loading"}))
        time.sleep(1)
        retries += 1
    
    if sim is None:
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            is_pressed = True if event['type'] == 'down' else False
            sim.update_key(event['key'], is_pressed)
    except WebSocketDisconnect:
        pass
