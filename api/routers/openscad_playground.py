from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from models.models import PlaygroundPreferences,PlaygroundEncodeResponse
import json
import gzip
import base64


router = APIRouter(prefix="/openscad_playground")

def encode_for_playground(payload_dict):
    json_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64 = base64.b64encode(compressed)
    return b64.decode('ascii')

@router.post("/encode-playground")
async def encode_playground(prefs: PlaygroundPreferences):
    payload = prefs.to_payload()
    result = encode_for_playground(payload)
    return {
        "base64string": result,
        "playground_url": f"https://ochafik.com/openscad2/#{result}"
    }

@router.get("/test-fork-project")
async def test_fork_project():
    sources = [
        SourceFile(
            path="/main.scad",
            content="""
// Main fork assembly
use <handle.scad>;
use <neck.scad>;
use <tines.scad>;

module fork() {
    handle();
    translate([0,0,100]) neck();
    translate([0,0,115]) tines();
}

fork();
            """.strip()
        ),
        SourceFile(
            path="/handle.scad",
            content="""
// Handle uses the parametric round_cylinder below
include <round_cylinder.scad>;

module handle() {
    round_cylinder(h=100, r=10);
}
            """.strip()
        ),
        SourceFile(
            path="/round_cylinder.scad",
            content="""
// Lowest-level dependency, provides round_cylinder()
module round_cylinder(h, r) {
    cylinder(h=h, r=r);
}
            """.strip()
        ),
        SourceFile(
            path="/neck.scad",
            content="""
module neck() {
    cylinder(h=15, r=6.5);
}
            """.strip()
        ),
        SourceFile(
            path="/tines.scad",
            content="""
// Tines module
module tines() {
    for (i = [0:3]) {
        translate([i*5,0,0]) cube([3,1,35]);
    }
}
            """.strip()
        ),
    ]
    prefs = PlaygroundPreferences(
        sources=sources,
        active_path="/main.scad",
        color="#e2a9fc",
        features=["lazy-union"],
        editor=True, viewer=True, customizer=False, logs=False, show_axes=True,
        layout_mode="multi", exportFormat2D="svg", exportFormat3D="stl"
    )
    payload = prefs.to_payload()
    result = encode_for_playground(payload)
    return {
        "base64string": result,
        "playground_url": f"https://ochafik.com/openscad2/#{result}",
        "main_scad": sources[0].content
    }
