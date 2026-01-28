from pydantic import BaseModel, Field
from typing import List
import json
import gzip
import base64

# An OpenSCAD source file
class SourceFile(BaseModel):
    path: str
    content: str

class PlaygroundPreferences(BaseModel):
    sources: List[SourceFile] = Field(..., description="List of all source files.")
    active_path: str = "/main.scad"
    features: List[str] = Field(default_factory=lambda: ["lazy-union"])
    exportFormat2D: str = "svg"
    exportFormat3D: str = "stl"
    color: str = "#f9d72c"
    show_axes: bool = True
    layout_mode: str = "multi"
    editor: bool = False
    viewer: bool = True
    customizer: bool = False
    logs: bool = False

    def to_payload(self):
        # Returns the dict format OpenSCAD Playground expects.
        return {
            "params": {
                "activePath": self.active_path,
                "sources": [f.dict() for f in self.sources],
                "features": self.features,
                "exportFormat2D": self.exportFormat2D,
                "exportFormat3D": self.exportFormat3D,
            },
            "view": {
                "layout": {
                    "mode": self.layout_mode,
                    "editor": self.editor,
                    "viewer": self.viewer,
                    "customizer": self.customizer,
                },
                "color": self.color,
                "showAxes": self.show_axes,
                "logs": self.logs
            },
        }

    def encode_playground(self) -> str:
        # Returns the base64-encoded, gzipped string for the playground
        payload_dict = self.to_payload()
        json_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
        compressed = gzip.compress(json_bytes)
        b64 = base64.b64encode(compressed)
        return b64.decode('ascii')

    def playground_url(self) -> str:
        # Returns the ready-to-use URL for ochafik playground
        encoded = self.encode_playground()
        return f"https://ochafik.com/openscad2/#{encoded}"

class RawChatResponse(BaseModel):
    sources: List[SourceFile] = Field(..., description="List of all source files.")
    active_path: str = Field("/main.scad", description="The primary file to view or render.")
    reply_text: str = Field(
        "Here is your object!",
        description="A summary or friendly description for the user."
    )

class EnrichedChatResponse(BaseModel):
    chat_response: RawChatResponse
    encoded_url: str

class ChatRequest(BaseModel):
    request_text: str

class PlaygroundEncodeResponse(BaseModel):
    base64string: str
    playground_url: str

if __name__ == "__main__":
    # Minimal cube test
    cube_files = [
        SourceFile(path="/main.scad", content="cube([10,10,10]);")
    ]
    cube_prefs = PlaygroundPreferences(sources=cube_files, active_path="/main.scad")
    print("Cube playground URL:")
    print(cube_prefs.playground_url())
    print("-----")

    # *** Robust: all "modules" at top level, includes with no folders ***
    fork_files = [
        SourceFile(
            path="/main.scad",
            content=(
                "include <fork_prong.scad>;\n"
                "include <fork_handle.scad>;\n"
                "\n"
                "// Assembles the fork from prongs and handle\n"
                "module fork() {\n"
                "    prongs(4);\n"
                "    translate([0, -10, 0]) fork_handle();\n"
                "}\n"
                "\n"
                "// Direct call for Playground render\n"
                "fork();\n"
            )
        ),
        SourceFile(
            path="/fork_prong.scad",
            content=(
                "// Generates n prongs for a fork\n"
                "module prongs(n) {\n"
                "    prong_width = 3;\n"
                "    prong_length = 40;\n"
                "    gap = 1.4;\n"
                "    thickness = 2.3;\n"
                "    for (i = [0:n-1]) {\n"
                "        translate([i * (prong_width + gap), 0, 0])\n"
                "            prong(prong_width, prong_length, thickness);\n"
                "    }\n"
                "}\n"
                "\n"
                "// Single prong helper\n"
                "module prong(width, length, thickness) {\n"
                "    // prong body\n"
                "    cube([width, length, thickness], center=false);\n"
                "    // tapered tip\n"
                "    translate([0, length, 0])\n"
                "        linear_extrude(height=thickness)\n"
                "            polygon(points = [ [0,0], [width,0], [width/2,7] ]);\n"
                "}\n"
            )
        ),
        SourceFile(
            path="/fork_handle.scad",
            content=(
                "// Creates a simple ergonomic fork handle\n"
                "module fork_handle() {\n"
                "    // handle base attaches at origin\n"
                "    handle_length = 80;\n"
                "    handle_width = 17;\n"
                "    handle_thickness = 7;\n"
                "    hull() {\n"
                "        translate([0,0,0]) cylinder(h=handle_thickness, r=handle_width/2, $fn=32);\n"
                "        translate([0,handle_length,0]) cylinder(h=handle_thickness, r=handle_width/2, $fn=32);\n"
                "    }\n"
                "}\n"
            )
        ),
    ]
    fork_prefs = PlaygroundPreferences(sources=fork_files, active_path="/main.scad")
    print("Fork playground URL:")
    print(fork_prefs.playground_url())
    print("-----")
