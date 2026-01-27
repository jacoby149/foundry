import os
import sys
import threading
import json
import time
import asyncio
import cv2
import numpy as np
from enum import Enum
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

# --- CONFIG ---
if sys.platform == "darwin":
    os.environ["MUJOCO_GL"] = "cgl"
else:
    os.environ["MUJOCO_GL"] = "osmesa" 

class SimMode(Enum):
    SIMPLE = "simple"
    REGULAR = "regular"

CURRENT_MODE = SimMode.REGULAR

sim = None 
sim_lock = threading.Lock()

# --- 1. CONNECTION MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def close_all(self):
        print(" [Manager] Force closing all WebSockets for reload...")
        # Iterate over a copy so we don't break the list while modifying it
        for websocket in list(self.active_connections):
            try:
                await websocket.close()
            except Exception:
                pass
        self.active_connections.clear()

# Create a global instance to export to main.py
sim_ws_manager = ConnectionManager()

# --- SIMULATION ENGINE ---
class SimulationManager:
    def __init__(self):
        import mujoco
        print(f" [MuJoCo] Initializing Physics...")
        self.width, self.height = 640, 480
        self.dt = 0.01 
        self.xml = f"""
        <mujoco>
            <option timestep="{self.dt}" gravity="0 0 -9.81" />
            <visual>
                <global offwidth="{self.width}" offheight="{self.height}"/>
                <quality shadowsize="2048"/>
            </visual>
            <asset>
                <texture name="grid" type="2d" builtin="checker" rgb1=".25 .3 .4" rgb2=".1 .15 .2" width="512" height="512" mark="edge" markrgb=".8 .8 .8"/>
                <material name="grid_mat" texture="grid" texrepeat="2 2" texuniform="true" reflectance=".0"/>
                <texture name="wall_tex" type="2d" builtin="flat" rgb1=".6 .6 .6" width="100" height="100"/>
                <material name="wall_mat" texture="wall_tex"/>
            </asset>
            <worldbody>
                <light pos="0 0 5" dir="0 0 -1" castshadow="true" diffuse=".8 .8 .8"/>
                <camera name="main_cam" pos="0 -6 5" mode="targetbody" target="player"/>
                <geom name="floor" type="plane" size="5 5 0.1" material="grid_mat" friction="2.0 0.5 0.5"/>
                <geom name="wall_back" type="box" size="5 0.2 2" pos="0 5 2" material="wall_mat" rgba="0.5 0.5 0.5 1"/>
                <geom name="wall_front" type="box" size="5 0.2 2" pos="0 -5 2" material="wall_mat" rgba="0.5 0.5 0.5 0.3"/> 
                <geom name="wall_left" type="box" size="0.2 5 2" pos="-5 0 2" material="wall_mat" rgba="0.5 0.5 0.5 1"/>
                <geom name="wall_right" type="box" size="0.2 5 2" pos="5 0 2" material="wall_mat" rgba="0.5 0.5 0.5 1"/>
                <body name="player" pos="0 0 0.25">
                    <joint name="slide_x" type="slide" axis="1 0 0" frictionloss="1000" damping="0" armature="1" limited="true" range="-4.5 4.5"/>
                    <joint name="slide_y" type="slide" axis="0 1 0" frictionloss="1000" damping="0" armature="1" limited="true" range="-4.5 4.5"/>
                    <joint name="hinge_z" type="hinge" axis="0 0 1" damping="1.0" />
                    <geom type="box" size="0.25 0.25 0.25" rgba="0.9 0.5 0.2 1" mass="10"/>
                </body>
            </worldbody>
            <actuator>
                <motor joint="slide_x" gear="1200" />
                <motor joint="slide_y" gear="1200" />
            </actuator>
        </mujoco>
        """
        self.model = mujoco.MjModel.from_xml_string(self.xml)
        self.data = mujoco.MjData(self.model)
        self.renderer = mujoco.Renderer(self.model, height=self.height, width=self.width)
        self.cam_id = 0 
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.running = True
        self.keys = {"ArrowUp": False, "ArrowDown": False, "ArrowLeft": False, "ArrowRight": False}

    def update_key(self, key, is_pressed):
        if key in self.keys: self.keys[key] = is_pressed

    def _loop(self):
        import mujoco
        while self.running:
            self.data.ctrl[:] = 0.0 
            if self.keys["ArrowRight"]: self.data.ctrl[0] = 1.0
            if self.keys["ArrowLeft"]:  self.data.ctrl[0] = -1.0
            if self.keys["ArrowUp"]:    self.data.ctrl[1] = 1.0
            if self.keys["ArrowDown"]:  self.data.ctrl[1] = -1.0
            
            mujoco.mj_step(self.model, self.data)
            self.renderer.update_scene(self.data, camera=self.cam_id)
            pixels = self.renderer.render()
            bgr = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
            ret, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            with self.frame_lock: self.current_frame = buffer.tobytes()
            time.sleep(self.dt)

    def stop(self):
        self.running = False

def ensure_sim_running():
    global sim
    with sim_lock:
        if sim is None:
            try:
                sim_instance = SimulationManager()
                t = threading.Thread(target=sim_instance._loop, daemon=True)
                t.start()
                sim = sim_instance
            except Exception as e:
                print(f" [System] Failed to start engine: {e}")

router = APIRouter(prefix="/sim_stream", tags=["Simulation"])

# --- GENERATOR (Clean) ---
async def frame_generator():
    ensure_sim_running()
    try:
        while True:
            if sim and sim.current_frame:
                with sim.frame_lock: frame_data = sim.current_frame
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            await asyncio.sleep(0.04)
    except (asyncio.CancelledError, GeneratorExit):
        return

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- WEBSOCKET (Clean) ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 2. Register with Manager
    await sim_ws_manager.connect(websocket)
    
    ensure_sim_running()
    try:
        while sim is None: await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        sim_ws_manager.disconnect(websocket)
        return

    try:
        while True:
            # 3. Standard Blocking Call
            # This is fine now, because manager.close_all() in main.py 
            # will force this to raise an exception and break the loop.
            data = await websocket.receive_text()
            
            event = json.loads(data)
            if 'key' in event:
                sim.update_key(event['key'], event['type'] == 'down')
                
    except (WebSocketDisconnect, asyncio.CancelledError, Exception):
        pass
    finally:
        sim_ws_manager.disconnect(websocket)
