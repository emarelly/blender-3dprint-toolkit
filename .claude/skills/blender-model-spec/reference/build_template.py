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
    try:
        me = __file__
    except NameError:
        me = ""
    starts = []
    if me and os.path.isfile(os.path.abspath(me)):
        starts.append(os.path.dirname(os.path.abspath(me)))
    # Blender's text editor: __file__ is only the text's name, so the text with that name comes first,
    # then any other open text (so an unrelated script's folder cannot win)
    texts = [t for t in bpy.data.texts if t.filepath]
    texts.sort(key=lambda t: os.path.basename(t.filepath) != os.path.basename(me))
    starts += [os.path.dirname(bpy.path.abspath(t.filepath)) for t in texts]
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
if _here in sys.path:
    sys.path.remove(_here)
sys.path.insert(0, _here)                  # before any other folder that has a utils_3d.py
# a utils_3d imported earlier in this Blender session from ANOTHER folder would otherwise be reused
_cached = sys.modules.get("utils_3d")
if _cached is not None and os.path.normcase(os.path.dirname(os.path.abspath(getattr(_cached, "__file__", "") or "")))         != os.path.normcase(os.path.abspath(_here)):
    del sys.modules["utils_3d"]

import importlib
import utils_3d as u
importlib.reload(u)

# ---------------------------------------------------------------- SETTINGS (match the spec)
COLL_NAME = "Demo_Box"
LAYOUT = "print"               # "print"     = ready for print: every part on the bed, side by side, in its
                               #               print orientation
                               # "assembled" = parts in their assembled positions (to check how they fit)
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

# (assembly / fit checks go here: they need the assembled pose)


# ---------------------------------------------------------------- KEEP: layout (assembled -> ready for print)
def place_for_print():
    """Move every printed part from its assembled pose to its print pose: turn each part's objects
    over AS ONE GROUP into the print orientation, put the groups side by side and drop them on the bed.
    Example for a lid modelled on top of a base:
        lid_group = [lid, *lid_features]
        u.flip_objects(lid_group, axis='Y', pivot=(0.0, 0.0, LID_MID_Z))
        u.translate_objects(lid_group, (-(BASE_WIDTH + GAP), 0.0, 0.0))
        u.drop_to_bed(lid_group)
    This demo is one printed part that is already modelled in its print orientation: nothing moves."""
    u.drop_to_bed([case, boss])


if LAYOUT == "print":
    place_for_print()
elif LAYOUT != "assembled":
    raise ValueError(f"LAYOUT must be 'print' or 'assembled', not {LAYOUT!r}")

# ---------------------------------------------------------------- KEEP: visibility + report
coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "layout": LAYOUT, "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report(min_wall=MIN_WALL, bed=BED, overhang_deg=45)

if EXPORT:
    u.export_all(basename="demo_box", threemf=True)
