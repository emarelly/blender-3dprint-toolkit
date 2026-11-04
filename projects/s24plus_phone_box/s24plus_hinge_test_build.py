"""
Samsung Galaxy S24+ box -- HINGE TEST COUPON (Blender build script)
(generated from s24plus_hinge_test_description.md).

A small print to tune the snap-in stub-pin hinge before printing the full box:
  * four BOX strips (a short wall piece with two knuckles) that differ only in the socket channel
    width: 2.0 / 2.1 / 2.2 / 2.3 mm (the value is engraved on each strip's foot)
  * two identical DOOR strips (a short plate piece with one knuckle carrying the two snap stubs)
Press a door strip straight down onto each box strip and feel the click: pick the narrowest channel
that goes in without cracking or white stress marks and still holds the door when it is lifted
gently. Then set CHANNEL_W in s24plus_phone_box_build.py to that value.

All hinge numbers and the hinge helper functions are LOADED FROM s24plus_phone_box_build.py (its
SETTINGS and local-helpers sections) at run time, so the coupon always matches the real box.
Keep both scripts in the same folder.

Both parts are modelled in the CLOSED pose (same coordinates as the full box), checked, then laid out
for printing: box strips as built, door strips flipped (outer face down) beside them.

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python <library root>/run_blender.py s24plus_hinge_test_build.py
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

# ---------------------------------------------------------------- load the real box's hinge definition
MAIN_SCRIPT = "s24plus_phone_box_build.py"


_coupon_dir = u.script_dir("s24plus_hinge_test_build.py")
_main_path = os.path.join(_coupon_dir, MAIN_SCRIPT)
if not os.path.isfile(_main_path):
    raise FileNotFoundError(f"{MAIN_SCRIPT} must be in the same folder as this coupon script ({_coupon_dir})")
_src = open(_main_path, encoding="utf-8").read()
_a = _src.index("# ================================================================ SETTINGS")
_b = _src.index("# ================================================================ KEEP: scene setup")
# defines every setting (PHONE_*, CAV_HW, OUT_HW, BOX_H, HINGE_*, STUB_*, SOCKET_*, CHANNEL_W, ...) and the
# helpers knuckle_ranges / make_stub / cut_stub_slit / cut_socket in THIS script's namespace
exec(compile(_src[_a:_b], _main_path, "exec"), globals())

# ================================================================ COUPON SETTINGS (override / add)
COLL_NAME = "S24P_Hinge_Test"
HIDE_OTHER_COLLECTIONS = True
ASSEMBLY_CHECK = True
EXPORT = False                   # True: one STL per part into EXPORT_DIR
EXPORT_DIR = ""                  # "" = an "exports_hinge_test" folder next to this script

CHANNEL_W_VARIANTS = (2.0, 2.1, 2.2, 2.3)     # the value being tuned (CHANNEL_W in the main script)
DOOR_STRIPS = 2

# coupon-only geometry, derived from the real box (knuckles 0 (box), 1 (door), 2 (box) of the hinge)
STRIP_MARGIN = 1.2               # strip extends this far beyond the outer knuckle faces
BOX_STRIP_Z0 = BOX_BLOCK_Z0 - 2.0   # wall piece starts 2 mm below the knuckle block
FOOT_X0 = CAV_HW - 7.45          # foot plate inboard edge (adhesion, keeps the thin wall upright)
FOOT_T = 2.4
DOOR_STRIP_X0 = OUT_HW - 12.85   # door strip plate inboard edge
LABEL_SIZE = 5.0
LABEL_DEPTH = 0.5
BOX_STRIP_PITCH = 20.0           # X spacing between box strips in the print layout
LAYOUT_GAP = 8.0                 # gap between the box strips and the door strips
MIN_WALL = 0.9
BED = (250, 210, 220)
OVERHANG_DEG = 45
SWING_ANGLES = (45, 90, 180)
DROPIN_HEIGHTS = (0.0, 1.0, 2.0, 3.0, 5.0)

KN = knuckle_ranges()[:3]                                   # box, door, box
STRIP_Y0 = KN[0][0] - STRIP_MARGIN
STRIP_Y1 = KN[2][1] + STRIP_MARGIN


def tag(channel_w):
    return f"CW{round(channel_w * 10):02d}"


def make_box_strip(channel_w):
    global CHANNEL_W
    CHANNEL_W = channel_w                                   # cut_socket (from the main script) reads it
    z0 = BOX_STRIP_Z0
    # wall + foot as ONE L-shaped profile (XZ) extruded along Y: no coplanar union of two boxes
    wall = u.make_prism_xz(f"S24P_HingeTest_Box_{tag(channel_w)}",
                           [(FOOT_X0, z0), (OUT_HW, z0), (OUT_HW, BOX_H), (CAV_HW, BOX_H),
                            (CAV_HW, z0 + FOOT_T), (FOOT_X0, z0 + FOOT_T)],
                           STRIP_Y0, STRIP_Y1)
    for i in (0, 2):                                        # box knuckles
        y0, y1 = KN[i]
        barrel = u.make_cylinder_between("_barrel", BARREL_R, (HINGE_X, y0, HINGE_Z), (HINGE_X, y1, HINGE_Z), verts=32)
        block = u.make_box("_block", BOX_BLOCK_X0, HINGE_X - BLOCK_END_BEFORE_AXIS, y0, y1, BOX_BLOCK_Z0,
                           HINGE_Z - BLOCK_TOP_BELOW_AXIS)
        u.boolean_union_apply(wall, barrel)
        u.boolean_union_apply(wall, block)
    cut_socket(wall, KN[0][1], -1)                          # faces toward the door knuckle
    cut_socket(wall, KN[2][0], +1)
    u.engrave_text(wall, f"{channel_w:.1f}", (FOOT_X0 + CAV_HW) / 2, (STRIP_Y0 + STRIP_Y1) / 2, z0 + FOOT_T,
                   size=LABEL_SIZE, depth=LABEL_DEPTH, rot_deg=90.0)
    return wall


def make_door_strip(name):
    plate = u.make_box(name, DOOR_STRIP_X0, OUT_HW, STRIP_Y0, STRIP_Y1, BOX_H, DOOR_Z1)
    y0, y1 = KN[1]
    barrel = u.make_cylinder_between("_barrel", BARREL_R, (HINGE_X, y0, HINGE_Z), (HINGE_X, y1, HINGE_Z), verts=32)
    arm = u.make_box("_arm", DOOR_ARM_X0, HINGE_X, y0, y1, BOX_H, DOOR_Z1)
    u.boolean_union_apply(plate, barrel)
    u.boolean_union_apply(plate, arm)
    u.boolean_union_apply(plate, make_stub(y0, -1))
    u.boolean_union_apply(plate, make_stub(y1, +1))
    cut_stub_slit(plate, y0, -1)
    cut_stub_slit(plate, y1, +1)
    return plate


# ================================================================ KEEP: scene setup
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)

box_strips = [make_box_strip(cw) for cw in CHANNEL_W_VARIANTS]
door_a = make_door_strip("S24P_HingeTest_Door_A")

# ================================================================ checks (closed pose)
check_results = {}
if ASSEMBLY_CHECK:
    for cw, bx in zip(CHANNEL_W_VARIANTS, box_strips):
        r = {"closed_overlap_mm3": round(u.overlap_volume(bx, door_a), 3)}
        r["swing_overlap_mm3"] = u.overlap_at_rotations(bx, door_a, 'Y', SWING_ANGLES, pivot=(HINGE_X, 0.0, HINGE_Z))
        di = u.overlap_at_offsets(bx, door_a, [(0.0, 0.0, h) for h in DROPIN_HEIGHTS])
        r["dropin_overlap_mm3"] = {off[2]: v for off, v in di.items()}
        check_results[f"channel_{cw:.1f}"] = r
    print("COUPON CHECK:", check_results)

doors = [door_a] + [u.duplicate_object(door_a, f"S24P_HingeTest_Door_{chr(ord('A') + k)}")
                    for k in range(1, DOOR_STRIPS)]

# ================================================================ print layout
for k, bx in enumerate(box_strips):                                # box strips: side by side along X, on the bed
    u.translate_objects([bx], (k * BOX_STRIP_PITCH, 0.0, -BOX_STRIP_Z0))
box_max_x = max(u.group_bbox([bx])[1].x for bx in box_strips)
for k, d in enumerate(doors):                                      # door strips: flipped (outer face down)
    u.flip_objects([d], axis='Y', pivot=(0.0, 0.0, (BOX_H + DOOR_Z1) / 2))
    u.drop_to_bed([d])
    d_min_x = u.group_bbox([d])[0].x
    u.translate_objects([d], (box_max_x + LAYOUT_GAP - d_min_x + k * BOX_STRIP_PITCH, 0.0, 0.0))

# ================================================================ KEEP: visibility + report
coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report(box_strips + doors, min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)
print("NOTE: min_wall readings of ~0.4-0.5 mm are expected here: the thin walls between the engraved digits on "
      "the box strips and the tapering tips of the slit stubs on the door strips. The designed sections are the "
      "socket lip (~1.0) and the stub halves (~0.9).")

if EXPORT:
    out = EXPORT_DIR or os.path.join(_coupon_dir, "exports_hinge_test")
    print("exported:", u.export_stl_per_object(out, box_strips + doors))
