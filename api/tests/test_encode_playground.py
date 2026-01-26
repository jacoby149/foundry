import json
import gzip
import base64

def encode_for_playground(payload_dict):
    json_bytes = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64 = base64.b64encode(compressed)
    return b64.decode('ascii')

def get_fork_sources():
    return [
        {
            "path": "/main.scad",
            "content": """
// Main fork assembly
use <handle.scad>;
use <neck.scad>;
use <tines.scad>;
module fork() { handle(); translate([0,0,100]) neck(); translate([0,0,115]) tines(); }
fork();
            """.strip()
        },
        {
            "path": "/handle.scad",
            "content": "include <round_cylinder.scad>;\nmodule handle() { round_cylinder(h=100, r=10); }"
        },
        {
            "path": "/round_cylinder.scad",
            "content": "module round_cylinder(h, r) { cylinder(h=h, r=r); }"
        },
        {
            "path": "/neck.scad",
            "content": "module neck() { cylinder(h=15, r=6.5); }"
        },
        {
            "path": "/tines.scad",
            "content": "module tines() { for (i = [0:3]) { translate([i*5,0,0]) cube([3,1,35]); } }"
        },
    ]

def print_variant(mode, editor, viewer, title):
    payload = {
        "params": {
            "activePath": "/main.scad",
            "sources": get_fork_sources(),
            "features": ["lazy-union"],
            "exportFormat2D": "svg",
            "exportFormat3D": "stl",
        },
        "view": {
            "layout": {
                "mode": mode,
                "editor": editor,
                "viewer": viewer,
                "customizer": False
            },
            "color": "#e2a9fc",
            "showAxes": True,
            "logs": False
        }
    }
    result = encode_for_playground(payload)
    print(f"{title}\nMode: {mode!r}, Editor: {editor}, Viewer: {viewer}\n"
          f"https://ochafik.com/openscad2/#{result}\n")

def main():
    print_variant("multi", True,  True,  "[1] mode='multi', editor ON, viewer ON (both panels, editable)")
    print_variant("multi", False, True,  "[2] mode='multi', editor OFF, viewer ON (both panels, not editable)")
    print_variant("single", True,  True, "[3] mode='single', editor ON, viewer ON (single panel with editor, editable)")
    print_variant("single", False, True, "[4] mode='single', editor OFF, viewer ON (single panel viewer only)")

if __name__ == "__main__":
    main()
