from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import trimesh
import numpy as np
import io
import zipfile
import os
import tempfile
import subprocess
from models.models import PlaygroundPreferences

router = APIRouter(prefix="/openscad_render", tags=["OpenSCAD Render"])

def get_cube_view_dirs():
    dirs = [
        [1,0,0], [-1,0,0], [0,1,0], [0,-1,0], [0,0,1], [0,0,-1],
        [1,1,1], [1,1,-1], [1,-1,1], [1,-1,-1],
        [-1,1,1], [-1,1,-1], [-1,-1,1], [-1,-1,-1]
    ]
    return [np.array(v)/np.linalg.norm(v) for v in dirs]

@router.post("/rendershots_zip/")
async def rendershots_zip(prefs: PlaygroundPreferences):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Write all source files to tempdir
        for f in prefs.sources:
            full_path = os.path.join(tmpdirname, os.path.normpath(f.path).lstrip("/"))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as ff:
                ff.write(f.content)
        main_path = os.path.join(tmpdirname, os.path.normpath(prefs.active_path).lstrip("/"))
        stl_path = os.path.join(tmpdirname, "out.stl")
        # OpenSCAD CLI to STL
        result = subprocess.run(
            ["openscad", "-o", stl_path, main_path],
            capture_output=True,
            cwd=tmpdirname,
            timeout=30
        )
        if result.returncode != 0:
            return {"error": "OpenSCAD failed", "stderr": result.stderr.decode()}
        # Load STL into trimesh
        with open(stl_path, "rb") as sf:
            stl_data = sf.read()
        mesh = trimesh.load_mesh(file_obj=io.BytesIO(stl_data), file_type='stl')
        mesh.apply_translation(-mesh.centroid)
        # Render 14 views into a zip in-memory
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, direction in enumerate(get_cube_view_dirs()):
                camera_distance = mesh.extents.max() * 1.5 + 0.01
                camera_pose = trimesh.scene.cameras.look_at(
                    points=[np.zeros(3)],
                    eye=[direction * camera_distance],
                    up=[0,0,1],
                )
                scene = mesh.scene()
                png_bytes = scene.save_image(
                    resolution=[512,512],
                    visible=True,
                    camera_transform=camera_pose
                )
                zipf.writestr(f"view_{idx:02d}.png", png_bytes)
            zipf.writestr("model.stl", stl_data)
        mem_zip.seek(0)
        return StreamingResponse(
            mem_zip,
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="rendershots.zip"'}
        )
