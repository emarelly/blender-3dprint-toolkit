"""
<Object name> -- Blender build script (generated from <name>_description.md).

Builds the model described in the spec using utils_3d.py. Every number is in the SETTINGS
block below and matches the spec's Decisions table. utils_3d.py can live in any parent folder
(or set UTILS_DIR / the UTILS_3D_DIR environment variable).

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python run_blender.py <name>_build.py

NOTE: this template is a runnable demo (a rounded box with lid-side screw boss). Replace the
SETTINGS values and the PARTS section with the real object; keep everything marked KEEP.
"""

import os
import sys

import bpy

# ---------------------------------------------------------------- KEEP: find utils_3d.py
# Where is utils_3d.py? It does NOT have to sit next to this script. Searched in order:
#   1. UTILS_DIR below (set it to the folder that contains utils_3d.py)
#   2. the UTILS_3D_DIR environment variable
#   3. this script's folder and every PARENT folder (plus the folder of any script opened in
#      Blender's text editor, the saved .blend's folder, and the current directory)
UTILS_DIR = ""


def _find_utils_dir():
    cands = [UTILS_DIR, os.environ.get("UTILS_3D_DIR", "")]
    starts = []
    try:
        starts.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    starts += [os.path.dirname(bpy.path.abspath(t.filepath)) for t in bpy.data.texts if t.filepath]
    if bpy.data.filepath:
        starts.append(os.path.dirname(bpy.data.filepath))
    starts.append(os.getcwd())
    for s in starts:                       # the folder itself, then each parent up to the root
        d = os.path.abspath(s)
        while True:
            cands.append(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    for d in cands:
        if d and os.path.isfile(os.path.join(d, "utils_3d.py")):
            return d
    raise ImportError("utils_3d.py not found. Set UTILS_DIR at the top of this script, or set the "
                      "UTILS_3D_DIR environment variable, to the folder that contains it.")


_here = _find_utils_dir()
if _here not in sys.path:
    sys.path.append(_here)

import importlib
import utils_3d as u
importlib.reload(u)

# ---------------------------------------------------------------- SETTINGS (match the spec)
COLL_NAME = "Demo_Box"
HIDE_OTHER_COLLECTIONS = True
EXPORT = False                 # True: write .blend + STL + 3MF next to the script via export_all
MIN_WALL = 1.2                 # mm, used by the report
BED = (220, 220, 250)          # printer build volume x, y, z

X0, X1 = -20.0, 20.0           # outer extents
Y0, Y1 = -30.0, 30.0
Z0, Z1 = 0.0, 15.0
WALL = 2.0
CORNER_R = 4.0
EDGE_R = 1.5
SCREW = 'M3'                   # key in utils_3d.SCREWS
BOSS_Z = (WALL, Z1 - 2.0)
BOSS_XY = (0.0, 0.0)

# ---------------------------------------------------------------- KEEP: scene setup
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)

# ---------------------------------------------------------------- PARTS
# Object names must match the spec's "Final object list" exactly.
case = u.make_box("Demo_Case", X0, X1, Y0, Y1, Z0, Z1)
u.round_edges(case, CORNER_R, 'VERTICAL', 8)
u.round_edges(case, EDGE_R, 'BOTTOM', 4)
cavity = u.make_box("Demo_Case_cavity", X0 + WALL, X1 - WALL, Y0 + WALL, Y1 - WALL, Z0 + WALL, Z1 + 5.0)
u.round_edges(cavity, max(CORNER_R - WALL, 0.5), 'VERTICAL', 8)
u.boolean_diff_apply(case, cavity)

boss = u.make_screw_boss("Demo_Boss", BOSS_XY[0], BOSS_XY[1], BOSS_Z[0], BOSS_Z[1],
                         screw=SCREW, kind='pilot')

# ---------------------------------------------------------------- KEEP: visibility + report
coll = bpy.data.collections[COLL_NAME]


def _walk(layer_coll):
    for lc in layer_coll.children:
        yield lc
        yield from _walk(lc)


if HIDE_OTHER_COLLECTIONS:
    for lc in _walk(bpy.context.view_layer.layer_collection):
        lc.hide_viewport = lc.collection.name != COLL_NAME

for win in bpy.context.window_manager.windows:          # frame the model (no-op headless)
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if region:
                with bpy.context.temp_override(window=win, area=area, region=region):
                    bpy.ops.view3d.view_all()

print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report(min_wall=MIN_WALL, bed=BED, overhang_deg=45)

if EXPORT:
    u.export_all(basename="demo_box", threemf=True)
