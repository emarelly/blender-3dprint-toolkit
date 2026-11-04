"""
RC Remote Control Case -- M4 screws, fully ROUNDED shells (no sharp edges).

Same case as rc_case_build_m4.py, but each shell is shaped like a soft-edged product:

  * the four vertical corners are rounded            (CORNER_R, plan view)
  * the edges around the closed face are rounded     (EDGE_R: Lower bottom, Upper top)
  * the edges around the open/seam face get a small round (SEAM_R) -- the flat rim that the two
    halves meet on is kept, so they still close properly
  * the inside of the cavity is rounded too          (INNER_R corners, INNER_EDGE_R floor/ceiling),
    which is also stronger and prints cleaner

Everything else (M4 screw holes, posts, rails, supports, collars, wire hole, placement) is the
same as the M4 build. Edit the numbers below to make it rounder or sharper.
Keep utils_3d.py in the same folder. Run in Blender (Open > Run Script) or
    python run_blender.py rc_case_build_m4_rounded.py
"""

import os
import sys

import bpy

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

# ---------------- Settings ----------------
SCREW = 'M4'              # 'M2' | 'M2.5' | 'M3' | 'M4' | 'M5'
LOWER_KIND = 'pilot'      # 'pilot' (self-tapping) or 'insert' (heat-set insert)
FLIP_UPPER = True         # same as the original build; False = spec's un-flipped layout
HEAD_MARGIN = 0.5         # extra diameter on the ceiling access hole around the screw head
HIDE_OTHER_COLLECTIONS = True

# Rounding (mm). Rules of thumb: CORNER_R <= 1/4 of the narrow side; EDGE_R <= CORNER_R;
# INNER_R = CORNER_R - WALL keeps the wall an even thickness around the corners.
WALL = 2.5
CORNER_R = 5.0            # vertical corners, seen from above
EDGE_R = 2.0              # edges around the closed face (Lower bottom / Upper top)
SEAM_R = 0.6              # edges around the open face (keep small: the mating rim stays flat)
INNER_R = max(CORNER_R - WALL, 0.5)   # inside vertical corners of the cavity
INNER_EDGE_R = 1.0        # inside floor (Lower) / ceiling (Upper) edges
CORNER_SEG = 8            # smoothness of the corners
EDGE_SEG = 4              # smoothness of the edge rounds

COLL_NAME = "RC_Remote_Case_Modifier_M4_Rounded"
S = u.screw_spec(SCREW)
ACCESS_R = (S['head_d'] + HEAD_MARGIN) / 2
LOWER_BOSS_R = max(3.0, (S['insert'] if LOWER_KIND == 'insert' else S['pilot']) / 2 + 1.6)
UPPER_BOSS_R = max(4.5, S['clear'] / 2 + 1.6)
SCREW_Y = (69.0, -69.0)

u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)


def rounded_shell(name, x0, x1, y0, y1, z0, z1, open_face):
    """Hollow shell with every edge rounded. open_face: '+Z' (Lower) or '-Z' (Upper)."""
    closed, opened = ('BOTTOM', 'TOP') if open_face == '+Z' else ('TOP', 'BOTTOM')
    shell = u.make_box(name, x0, x1, y0, y1, z0, z1)
    u.round_edges(shell, CORNER_R, 'VERTICAL', CORNER_SEG)     # plan-view corners
    u.round_edges(shell, EDGE_R, closed, EDGE_SEG)             # closed-face perimeter
    u.round_edges(shell, SEAM_R, opened, EDGE_SEG)             # seam rim, small round
    if open_face == '+Z':
        cav = u.make_box(name + "_cavity", x0 + WALL, x1 - WALL, y0 + WALL, y1 - WALL, z0 + WALL, z1 + 5.0)
    else:
        cav = u.make_box(name + "_cavity", x0 + WALL, x1 - WALL, y0 + WALL, y1 - WALL, z0 - 2.0, z1 - WALL)
    u.round_edges(cav, INNER_R, 'VERTICAL', CORNER_SEG)        # inside corners (even wall)
    u.round_edges(cav, INNER_EDGE_R, closed, EDGE_SEG)         # inside floor/ceiling edges
    u.boolean_diff_apply(shell, cav)
    return shell


# =====================================================================
# STEP 1 -- Lower shell (rounded)
# =====================================================================
lower = rounded_shell("RC_Case_Lower", -28.75, 28.75, -87.5, 87.5, 0.0, 15.0, '+Z')
# Raised size label on the inside floor of Lower
u.emboss_text(lower, SCREW, 0.0, 0.0, WALL, size=9.0, height=0.6)

# =====================================================================
# STEP 2 -- Lower secondary parts (screw bosses sized for the chosen screw)
# =====================================================================
lower_secondary = []
for tag, y in zip(("PosY", "NegY"), SCREW_Y):
    lower_secondary.append(u.make_screw_boss(f"RC_Boss_Lower_{tag}", 0.0, y, 2.5, 13.0,
                                             screw=SCREW, kind=LOWER_KIND, outer_r=LOWER_BOSS_R))
for tag, y in (("PosY", 22.75), ("NegY", -32.75)):
    lower_secondary.append(u.make_boss(f"RC_Post_Lower_{tag}", 0.0, y, 2.5, 12.5,
                                       outer_r=4.15, bore_r=2.15, bore='blind'))
for tag, x in (("PosX", 18.0), ("NegX", -18.0)):
    lower_secondary.append(u.make_box(f"RC_Rail_Lower_{tag}", x - 0.5, x + 0.5, -85.0, 85.0, 2.5, 6.4))

# =====================================================================
# STEP 2b -- Corner joint posts (unchanged; they overlap the rounded inside corner slightly)
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
# STEP 3 -- Upper shell (rounded) + button holes + screw-access holes
# =====================================================================
upper = rounded_shell("RC_Case_Upper", -28.75, 28.75, -87.5, 87.5, 0.0, 14.0, '-Z')

button_positions = [(0.0, 9.75), (-16.1, 5.55), (16.1, 13.95),
                    (0.0, 35.75), (-16.1, 31.55), (16.1, 39.95)]
u.cut_cylinders(upper, button_positions, radius=7.0, z_min=11.3, z_max=14.2)
u.cut_cylinders(upper, [(0.0, y) for y in SCREW_Y], radius=ACCESS_R, z_min=11.3, z_max=14.2)

# =====================================================================
# STEP 4 -- Upper secondary parts
# =====================================================================
upper_secondary = []
for tag, y in zip(("PosY", "NegY"), SCREW_Y):
    upper_secondary.append(u.make_screw_boss(f"RC_Boss_Upper_{tag}", 0.0, y, 3.5, 11.5,
                                             screw=SCREW, kind='clearance', outer_r=UPPER_BOSS_R))

support_positions = {"L1": (-16.1, 18.55), "R1": (16.1, 26.95),
                     "L2": (-16.1, -35.45), "R2": (16.1, -27.05)}
for tag, (x, y) in support_positions.items():
    upper_secondary.append(u.make_boss(f"RC_Support_Upper_{tag}", x, y, 1.5, 11.5,
                                       outer_r=2.5, bore_r=1.0, bore='blind'))

for i, (x, y) in enumerate(button_positions, start=1):
    upper_secondary.append(u.make_boss(f"RC_Collar_Hole{i}", x, y, 8.0, 11.5,
                                       outer_r=8.5, bore_r=7.0, bore='through'))

# =====================================================================
# WIRE-ENTRY HOLE (split across the seam)
# =====================================================================
WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX = 4.85, -90.0, -83.0
u.boolean_diff_apply(lower, u.make_wire_cutter("_cutter_wire_lower", WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX, 15.0))
u.boolean_diff_apply(upper, u.make_wire_cutter("_cutter_wire_upper", WIRE_RADIUS, WIRE_Y_MIN, WIRE_Y_MAX, 0.0))

# =====================================================================
# Placement and optional flip
# =====================================================================
upper_group = [upper] + upper_secondary
u.translate_objects(upper_group, (-80.0, 0.0, 0.0))
if FLIP_UPPER:
    u.flip_objects(upper_group, axis='X', pivot=(upper.location.x, 0.0, 7.0))

coll = bpy.data.collections[COLL_NAME]

# ---------------- Make this build easy to see ----------------
tag = "_" + SCREW.replace(".", "") + "R"            # e.g. RC_Case_Lower_M4R
for o in coll.objects:
    o.name = o.name + tag

if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "screw": SCREW, "collection": COLL_NAME, "object_count": len(coll.objects),
       "corner_r": CORNER_R, "edge_r": EDGE_R, "seam_r": SEAM_R})
u.print_report()
