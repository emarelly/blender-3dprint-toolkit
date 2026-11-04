"""
RC Remote Control Case -- Modifier-Based Build (FINAL), refactored to use utils_3d.

Same model as rc_case_build_final.py (24 objects, Upper flipped open-face-up),
but all generic helpers now live in utils_3d.py. Keep both files in the same
folder. Set FLIP_UPPER = False to get the un-flipped result described in the
v1.3 spec.

Run in Blender (Scripting > Open > Run Script) or:
    blender --background --python rc_case_build_final_utils.py
"""

import os
import sys

# Make utils_3d importable (works when run from a file; in Blender's text editor
# __file__ may be missing, so fall back to the saved .blend's folder).
import bpy

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

FLIP_UPPER = True          # Step 6 in the original script (not in the v1.3 spec)

COLL_NAME = "RC_Remote_Case_Modifier"
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)

# =====================================================================
# STEP 1 -- Lower shell (57.5 x 175 x 15, 2.5 mm walls/floor, open top)
# =====================================================================
lower = u.make_hollow_box("RC_Case_Lower", -28.75, 28.75, -87.5, 87.5, 0.0, 15.0,
                          wall=2.5, open_face='+Z', bevel=0.6, bevel_segments=4, overshoot=5.0)

# =====================================================================
# STEP 2 -- Lower secondary parts
# =====================================================================
lower_secondary = []
for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    lower_secondary.append(u.make_boss(f"RC_Boss_Lower_{tag}", 0.0, y, 2.5, 13.0,
                                       outer_r=3.0, bore_r=1.6, bore='blind'))
for tag, y in (("PosY", 22.75), ("NegY", -32.75)):
    lower_secondary.append(u.make_boss(f"RC_Post_Lower_{tag}", 0.0, y, 2.5, 12.5,
                                       outer_r=4.15, bore_r=2.15, bore='blind'))
for tag, x in (("PosX", 18.0), ("NegX", -18.0)):
    lower_secondary.append(u.make_box(f"RC_Rail_Lower_{tag}", x - 0.5, x + 0.5, -85.0, 85.0, 2.5, 6.4))

# =====================================================================
# STEP 2b -- Corner joint posts: 2x2 mm, flush to the inner cavity wall,
# Z 0..19 (floor to 4 mm above the rim). No matching cut on Upper.
# =====================================================================
POST = 2.0
corner_defs = [
    ("PosXPosY",  26.25 - POST, 26.25,        85.0 - POST, 85.0),
    ("PosXNegY",  26.25 - POST, 26.25,       -85.0,        -85.0 + POST),
    ("NegXPosY", -26.25,       -26.25 + POST,  85.0 - POST, 85.0),
    ("NegXNegY", -26.25,       -26.25 + POST, -85.0,        -85.0 + POST),
]
corner_posts = [u.make_box(f"RC_JointPost_Lower_{tag}", x0, x1, y0, y1, 0.0, 19.0)
                for tag, x0, x1, y0, y1 in corner_defs]

# =====================================================================
# STEP 3 -- Upper shell (same footprint as Lower, 14 mm high, open bottom)
# =====================================================================
upper = u.make_hollow_box("RC_Case_Upper", -28.75, 28.75, -87.5, 87.5, 0.0, 14.0,
                          wall=2.5, open_face='-Z', bevel=0.6, bevel_segments=4, overshoot=2.0)

button_positions = [(0.0, 9.75), (-16.1, 5.55), (16.1, 13.95),
                    (0.0, 35.75), (-16.1, 31.55), (16.1, 39.95)]
u.cut_cylinders(upper, button_positions, radius=7.0, z_min=11.3, z_max=14.2)
u.cut_cylinders(upper, [(0.0, 69.0), (0.0, -69.0)], radius=3.2, z_min=11.3, z_max=14.2)

# =====================================================================
# STEP 4 -- Upper secondary parts
# =====================================================================
upper_secondary = []
for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    upper_secondary.append(u.make_boss(f"RC_Boss_Upper_{tag}", 0.0, y, 3.5, 11.5,
                                       outer_r=4.5, bore_r=1.8, bore='through'))

support_positions = {"L1": (-16.1, 18.55), "R1": (16.1, 26.95),
                     "L2": (-16.1, -35.45), "R2": (16.1, -27.05)}
for tag, (x, y) in support_positions.items():
    upper_secondary.append(u.make_boss(f"RC_Support_Upper_{tag}", x, y, 1.5, 11.5,
                                       outer_r=2.5, bore_r=1.0, bore='blind'))

for i, (x, y) in enumerate(button_positions, start=1):
    upper_secondary.append(u.make_boss(f"RC_Collar_Hole{i}", x, y, 8.0, 11.5,
                                       outer_r=8.5, bore_r=7.0, bore='through'))

# =====================================================================
# WIRE-ENTRY HOLE -- full cylinder centred on each half's own open edge
# (Lower rim Z=15, Upper rim Z=0 in local coords) -> half-round notch each.
# =====================================================================
WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX = 4.85, -90.0, -83.0
u.boolean_diff_apply(lower, u.make_wire_cutter("_cutter_wire_lower", WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX, 15.0))
u.boolean_diff_apply(upper, u.make_wire_cutter("_cutter_wire_upper", WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX, 0.0))

# =====================================================================
# STEP 5 -- Final placement: Upper group shifted dX = -80 mm
# =====================================================================
upper_group = [upper] + upper_secondary
u.translate_objects(upper_group, (-80.0, 0.0, 0.0))

# =====================================================================
# STEP 6 -- Flip Upper open-face-up (180 deg about X through its own centre).
# NOTE: this mirrors Y; flip about 'Y' instead if you want book-style closing.
# =====================================================================
if FLIP_UPPER:
    u.flip_objects(upper_group, axis='X', pivot=(upper.location.x, 0.0, 7.0))

coll = bpy.data.collections[COLL_NAME]
print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report()
