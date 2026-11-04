"""
Samsung Galaxy S24+ storage / charging box -- Blender build script
(generated from s24plus_phone_box_description.md; every number below is in the SETTINGS block
and matches the spec's Decisions table).

Two parts: S24P_Box (deep tray with hinge knuckles that carry round sockets, snap grooves and niches on
three sides, phone ribs and stop, cable slot, finger notch) and S24P_Door (flat lid with locating lip, snap hooks, hinge
knuckles with snap-in stub pins, honeycomb vents, engraved label). The hinge needs no separate pin:
the door is pressed down onto the box and the stubs click into the sockets. Both are modelled in the CLOSED pose; the door is then flipped and moved
beside the box in its print orientation (outer face down).

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python <library root>/run_blender.py s24plus_phone_box_build.py
utils_3d.py is found by searching parent folders (or UTILS_DIR / UTILS_3D_DIR below).
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

# ================================================================ SETTINGS (match the spec)
COLL_NAME = "S24P_Phone_Box"
BOX_NAME = "S24P_Box"
DOOR_NAME = "S24P_Door"
HIDE_OTHER_COLLECTIONS = True
ASSEMBLY_CHECK = True            # closed-pose overlap, dummy-phone clearance and hinge swing test
EXPORT = False                   # True: one STL per part into EXPORT_DIR
EXPORT_DIR = ""                  # "" = an "exports" folder next to this script

# Phone (with its cover) and fit
PHONE_L, PHONE_W, PHONE_T = 166.0, 82.4, 13.4   # phone WITH its protector (v1.2)
CLEAR_XY = 2.0                   # free space per side in X and Y (easy to lift the phone out)
CLEAR_Z = 1.0                    # free space above and below the phone
RIB_PLAY = 0.5                   # ribs / end stops leave the phone this much play per side, so it
                                 # cannot drift into the snap hooks that sit in the 2 mm gap
PLUG_POCKET = 25.0               # extra cavity length at the -Y (cable) end

# Shell
WALL = 2.4
FLOOR = 2.4
DOOR_T = 2.4
CORNER_R = 10.0                  # vertical corners
BOX_BOTTOM_EDGE_R = 3.0          # box closed-face (bottom) edge
BOX_SEAM_R = 0.6                 # box rim edge
DOOR_TOP_EDGE_R = 2.0            # door outer edge (plate is only 2.4 thick)
DOOR_SEAM_R = 0.2                # door underside edge (2.0 + 0.2 < 2.4 plate thickness)
INNER_CORNER_R = CORNER_R - WALL # even wall thickness round the corners
INNER_FLOOR_R = 1.0              # inside floor edge
CORNER_SEG = 8
EDGE_SEG = 4

# Derived geometry (closed pose; origin = box centre on the bed)
CAV_HW = (PHONE_W + 2 * CLEAR_XY) / 2                 # cavity half width  (X)  43.2
CAV_HL = (PHONE_L + 2 * CLEAR_XY + PLUG_POCKET) / 2   # cavity half length (Y)  97.5
CAV_DEPTH = PHONE_T + 2 * CLEAR_Z                     # 15.4
OUT_HW = CAV_HW + WALL                                # 45.6
OUT_HL = CAV_HL + WALL                                # 99.9
BOX_H = FLOOR + CAV_DEPTH                             # 17.8 (rim / seam plane)
DOOR_Z1 = BOX_H + DOOR_T                              # 20.2
POCKET_END_Y = -CAV_HL + PLUG_POCKET                  # -72.5 (start of phone region)
PHONE_Y0 = POCKET_END_Y + CLEAR_XY                    # -70.5 (phone nominal start, 2 mm from the stop)
PHONE_Z0 = FLOOR + CLEAR_Z                            # 3.4
PHONE_Y1 = PHONE_Y0 + PHONE_L                         # 95.5 (phone nominal end toward +Y)
PHONE_LIM_X = PHONE_W / 2 + RIB_PLAY                  # 41.7 furthest the phone edge can reach sideways
PHONE_LIM_Y1 = PHONE_Y1 + RIB_PLAY                    # 96.0 furthest the phone end can reach toward +Y

# Locating lip (on the door, hangs into the cavity above the phone)
LIP_T = 1.2
LIP_H = 0.8
LIP_GAP = 0.3
FUSE = 0.2                       # overlap used to fuse added parts into their shell

# Snap latch: two hooks on the door at the -Y end, grooves in the box end wall
HOOK_XS = (24.0, -24.0)
HOOK_W = 8.0
HOOK_TIP = 0.8
HOOK_LEN = 7.0                   # from the door underside down to the hook's lowest point
HOOK_HEIGHT = 1.4
GROOVE_EXTRA_W = 1.0
GROOVE_DEPTH = 1.0
GROOVE_BELOW = 0.5
GROOVE_ABOVE = 0.4

# Extra snap hooks on the +Y end and the free -X long side. The phone leaves only 1.0 mm beside the
# walls, so these hooks are smaller and each one sinks into a niche cut into the wall, with the catch
# groove behind the niche. Same hook length/height and groove heights as the cable-end hooks.
HOOK2_ARM_T = 1.0                # arm thickness (flex direction)
HOOK2_TIP = 0.7                  # tip protrusion (0.45 of it reaches past the wall face into the groove)
HOOK2_PHONE_GAP = 0.25           # arm stays this far from the furthest phone position (rib / end-stop limit)
HOOK2_WALL_GAP = 0.25            # arm outer face to the wall; a niche is cut only if the arm would come closer
HOOK2_GROOVE_CLEAR = 0.3         # catch groove floor this far behind the hook tip
HOOK2_XS_END = (24.0, -24.0)     # hooks on the +Y end wall (X positions)
HOOK2_YS_SIDE = (35.0, -35.0)    # hooks on the -X long wall (Y positions, clear of the phone ribs)
GROOVE2_LIFT = 0.2               # groove bottom sits this far above the niche bottom (no coplanar floors)

# Snap-in stub-pin hinge on the +X side (axis parallel to Y), no separate pin
HINGE_N = 5
KNUCKLE_L = 16.0
KNUCKLE_GAP = 0.4
BARREL_R = 2.8                   # wall around the 3.0 mm socket = 1.3
HINGE_X = OUT_HW + BARREL_R + 0.3
BARREL_SINK = 0.2                # barrel top sits this far below the door outer face (avoids a
                                 # tangent-line contact that breaks the Boolean solver)
HINGE_Z = DOOR_Z1 - BARREL_R - BARREL_SINK
BOX_BLOCK_X0 = OUT_HW - 1.35       # block reaches 1.35 into the wall
BOX_BLOCK_Z0 = HINGE_Z - 5.5       # block hangs 5.5 below the hinge axis
BLOCK_TOP_BELOW_AXIS = 0.3     # block top is not exactly at the axis height (avoids degenerate slivers)
BLOCK_END_BEFORE_AXIS = 0.3    # block ends 0.3 short of the axis so the barrel's lowest vertex does not touch its end face
DOOR_ARM_X0 = OUT_HW - 0.5
# stubs on the door knuckle end faces (tapered, with a slit so the two halves can squeeze together)
STUB_R_ROOT = 1.3
STUB_R_TIP = 0.8
STUB_L = 2.2                     # protrudes this far from the knuckle end face
STUB_FUSE = 0.2                  # embedded in the knuckle so the union is solid
STUB_SLIT_W = 0.6                # slit along the stub axis, splits it into two flexing halves
STUB_SLIT_INTO_KNUCKLE = 2.0     # slit continues this far into the knuckle (longer flex length = lower strain)
# sockets in the box knuckle faces: round hole + a channel up through the barrel top (drop-in entry)
SOCKET_R = 1.5
SOCKET_D = 2.4                   # depth into the box knuckle (stub engages 1.8 of it)
CHANNEL_W = 2.2                  # the click: first contact is at stub radius ~1.21 (after the 0.4 gap), so
                                 # 2.2 = ~0.1 per side of interference; 2.4 = none (no click at all)
LEADIN = 0.8                     # funnel at the top of the channel
CHANNEL_END_TRIM = 0.2           # channel + funnel stop this far short of the socket bottom (no coplanar back walls)
DROPIN_HEIGHTS = (1.0, 2.0, 3.0, 4.0, 5.0)   # door lifted this far above closed, for the test

# Cable slot (stadium, through the -Y end wall)
SLOT_W, SLOT_H = 14.0, 8.0
SLOT_Z = FLOOR + CLEAR_Z + PHONE_T / 2                # 10.1
SLOT_ARC_SEG = 16

# Phone retention
RIB_YS = (-20.0, 60.0)
RIB_L = 6.0
RIB_PROUD = CLEAR_XY - RIB_PLAY   # 1.5
RIB_H = 6.0
STOP_T = 2.0
STOP_H = 6.0
STOP_GAP = 16.0                  # centre gap for the plug
END_STOP_XS = (10.0, -10.0)      # bumps on the +Y end wall (clear of the +Y snap hooks at X = +-24)
END_STOP_W = 6.0
END_STOP_H = 6.0
END_STOP_PROUD = CLEAR_XY - RIB_PLAY   # 1.5

# Finger notch (half-round scoop in the -X wall rim at Y=0)
NOTCH_W = 14.0
NOTCH_D = 3.5

# Door label and vents
LABEL_TEXT = "S24+"
LABEL_SIZE = 10.0
LABEL_DEPTH = 0.6
LABEL_ROT_DEG = 90.0             # reads along the long (Y) side
VENT_COLS, VENT_ROWS = 6, 3
VENT_AF = 5.0
VENT_WEB = 1.2
VENT_CENTER = (0.0, 30.0)

# Print layout and checks
DOOR_GAP = 10.0                  # door is placed this far to the -X side of the box
MIN_WALL = 0.9                   # thinnest designed section is the ~1.0 mm lip beside each hinge socket
BED = (250, 210, 220)
PHONE_CORNER_R_CHECK = 5.0       # corner radius of the dummy phone used only by the clearance check
OVERHANG_DEG = 45


# ================================================================ local helpers (snap-in stub-pin hinge;
# s24plus_hinge_test_build.py loads this section, keep it between the SETTINGS and scene-setup markers)
def knuckle_ranges():
    span = HINGE_N * KNUCKLE_L + (HINGE_N - 1) * KNUCKLE_GAP
    y = -span / 2
    out = []
    for i in range(HINGE_N):
        out.append((y, y + KNUCKLE_L))
        y += KNUCKLE_L + KNUCKLE_GAP
    return out                                                 # even index -> box, odd -> door


def make_stub(face_y, sign):
    """Tapered stub on a door knuckle end face at y = face_y, pointing toward sign (+1 / -1) along Y."""
    y_in = face_y - sign * STUB_FUSE
    y_tip = face_y + sign * STUB_L
    return u.make_frustum_between("_stub", STUB_R_ROOT, STUB_R_TIP, (HINGE_X, y_in, HINGE_Z),
                                  (HINGE_X, y_tip, HINGE_Z), verts=24)


def cut_stub_slit(door_obj, face_y, sign):
    """Slit along the stub axis (plane YZ), running from the tip into the knuckle, so the two stub
    halves can squeeze together while the stub clicks through the socket channel."""
    ya = face_y + sign * (STUB_L + 0.1)
    yb = face_y - sign * STUB_SLIT_INTO_KNUCKLE
    slit = u.make_box("_stub_slit", HINGE_X - STUB_SLIT_W / 2, HINGE_X + STUB_SLIT_W / 2,
                      ya, yb, HINGE_Z - STUB_R_ROOT - 0.1, HINGE_Z + STUB_R_ROOT + 0.1)
    u.boolean_diff_apply(door_obj, slit)


def cut_socket(obj, face_y, sign):
    """Socket in a box knuckle face at y = face_y; sign = direction INTO the knuckle (+1 / -1)."""
    ya, yb = face_y - sign * 0.1, face_y + sign * SOCKET_D
    y0, y1 = min(ya, yb), max(ya, yb)
    hole = u.make_cylinder_between("_socket", SOCKET_R, (HINGE_X, y0, HINGE_Z), (HINGE_X, y1, HINGE_Z), verts=32)
    u.boolean_diff_apply(obj, hole)
    z_top = HINGE_Z + BARREL_R
    yc0, yc1 = (y0, y1 - CHANNEL_END_TRIM) if sign > 0 else (y0 + CHANNEL_END_TRIM, y1)   # trim the inner end only
    chan = u.make_box("_channel", HINGE_X - CHANNEL_W / 2, HINGE_X + CHANNEL_W / 2, yc0, yc1,
                      HINGE_Z, z_top + 1.0)
    u.boolean_diff_apply(obj, chan)
    funnel = u.make_prism_xz("_leadin", [(HINGE_X - CHANNEL_W / 2 - LEADIN, z_top + 0.5),
                                         (HINGE_X + CHANNEL_W / 2 + LEADIN, z_top + 0.5),
                                         (HINGE_X + CHANNEL_W / 2, z_top - LEADIN),
                                         (HINGE_X - CHANNEL_W / 2, z_top - LEADIN)], yc0, yc1)
    u.boolean_diff_apply(obj, funnel)


# ================================================================ KEEP: scene setup
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)

# ================================================================ BOX (closed pose)
box = u.make_hollow_box(BOX_NAME, -OUT_HW, OUT_HW, -OUT_HL, OUT_HL, 0.0, BOX_H, wall=WALL,
                        open_face='+Z', floor=FLOOR, overshoot=5.0,
                        bevel=[(CORNER_R, 'VERTICAL', CORNER_SEG), (BOX_BOTTOM_EDGE_R, 'BOTTOM', EDGE_SEG),
                               (BOX_SEAM_R, 'TOP', EDGE_SEG)],
                        inner_radius=[(INNER_CORNER_R, 'VERTICAL', CORNER_SEG),
                                      (INNER_FLOOR_R, 'BOTTOM', EDGE_SEG)])

# phone centring ribs (both long walls)
for sx in (1, -1):
    for ry in RIB_YS:
        rib = u.make_box("_rib", sx * (CAV_HW - RIB_PROUD), sx * (CAV_HW + 0.1),
                         ry - RIB_L / 2, ry + RIB_L / 2, FLOOR - 0.1, FLOOR + RIB_H)
        u.boolean_union_apply(box, rib)

# phone stop at the plug-pocket boundary, centre gap for the plug
for sx in (1, -1):
    stop = u.make_box("_stop", sx * (STOP_GAP / 2), sx * (CAV_HW + 0.1), POCKET_END_Y - STOP_T, POCKET_END_Y,
                      FLOOR - 0.1, FLOOR + STOP_H)
    u.boolean_union_apply(box, stop)

# end stops on the +Y wall: keep the phone end within RIB_PLAY of its nominal position
for ex in END_STOP_XS:
    es = u.make_box("_end_stop", ex - END_STOP_W / 2, ex + END_STOP_W / 2, CAV_HL - END_STOP_PROUD, CAV_HL + 0.1,
                    FLOOR - 0.1, FLOOR + END_STOP_H)
    u.boolean_union_apply(box, es)

# hinge knuckles on the box (even indices)
for i, (y0, y1) in enumerate(knuckle_ranges()):
    if i % 2 == 0:
        barrel = u.make_cylinder_between("_barrel", BARREL_R, (HINGE_X, y0, HINGE_Z), (HINGE_X, y1, HINGE_Z), verts=32)
        block = u.make_box("_block", BOX_BLOCK_X0, HINGE_X - BLOCK_END_BEFORE_AXIS, y0, y1, BOX_BLOCK_Z0, HINGE_Z - BLOCK_TOP_BELOW_AXIS)
        u.boolean_union_apply(box, barrel)
        u.boolean_union_apply(box, block)
# sockets on the faces that look toward a door knuckle
for i, (y0, y1) in enumerate(knuckle_ranges()):
    if i % 2 == 0:
        if i > 0:
            cut_socket(box, y0, +1)       # face at y0 looks toward -Y neighbour; hole goes +Y into the knuckle
        if i < HINGE_N - 1:
            cut_socket(box, y1, -1)       # face at y1 looks toward +Y neighbour; hole goes -Y into the knuckle

# cable slot through the -Y end wall
slot_half = (SLOT_W - SLOT_H) / 2                     # arc centres sit this far either side of X = 0
slot = u.make_prism("_slot", u.stadium_profile((-slot_half, SLOT_Z), (slot_half, SLOT_Z), SLOT_H, SLOT_ARC_SEG),
                    'Y', -OUT_HL - 2.0, -CAV_HL + 0.5)
u.boolean_diff_apply(box, slot)

# snap grooves in the -Y end wall (inner face) for the door hooks
hook_bottom_z = BOX_H - HOOK_LEN
for hx in HOOK_XS:
    g = u.make_box("_groove", hx - (HOOK_W + GROOVE_EXTRA_W) / 2, hx + (HOOK_W + GROOVE_EXTRA_W) / 2,
                   -CAV_HL - GROOVE_DEPTH, -CAV_HL + 0.2,
                   hook_bottom_z - GROOVE_BELOW, hook_bottom_z + HOOK_HEIGHT + GROOVE_ABOVE)
    u.boolean_diff_apply(box, g)

# catch grooves (and niches only if the arm needs one) for the extra hooks:
# +Y end wall (hook tips point +Y), -X long wall (tips point -X)
hk_w2 = HOOK_W + GROOVE_EXTRA_W
z_n0 = hook_bottom_z - GROOVE_BELOW
z_g1 = hook_bottom_z + HOOK_HEIGHT + GROOVE_ABOVE
y_arm_in = PHONE_LIM_Y1 + HOOK2_PHONE_GAP              # +Y end hooks: arm inner / outer face, tip, wall-or-niche face, groove floor
y_arm_out = y_arm_in + HOOK2_ARM_T
y_arm_tip = y_arm_out + HOOK2_TIP
y_niche = max(CAV_HL, y_arm_out + HOOK2_WALL_GAP)
y_groove = y_arm_tip + HOOK2_GROOVE_CLEAR
y_has_niche = y_niche > CAV_HL + 0.05
for hx in HOOK2_XS_END:
    if y_has_niche:
        u.boolean_diff_apply(box, u.make_box("_niche", hx - hk_w2 / 2, hx + hk_w2 / 2, CAV_HL - 0.1, y_niche, z_n0, BOX_H + 0.5))
    u.boolean_diff_apply(box, u.make_box("_groove2", hx - hk_w2 / 2, hx + hk_w2 / 2, y_niche - 0.1, y_groove,
                                         z_n0 + (GROOVE2_LIFT if y_has_niche else 0.0), z_g1))
x_arm_in = -(PHONE_LIM_X + HOOK2_PHONE_GAP)            # -X side hooks (mirror: values are negative X)
x_arm_out = x_arm_in - HOOK2_ARM_T
x_arm_tip = x_arm_out - HOOK2_TIP
x_niche = min(-CAV_HW, x_arm_out - HOOK2_WALL_GAP)
x_groove = x_arm_tip - HOOK2_GROOVE_CLEAR
x_has_niche = x_niche < -CAV_HW - 0.05
for hy in HOOK2_YS_SIDE:
    if x_has_niche:
        u.boolean_diff_apply(box, u.make_box("_niche", x_niche, -CAV_HW + 0.1, hy - hk_w2 / 2, hy + hk_w2 / 2, z_n0, BOX_H + 0.5))
    u.boolean_diff_apply(box, u.make_box("_groove2", x_groove, x_niche + 0.1, hy - hk_w2 / 2, hy + hk_w2 / 2,
                                         z_n0 + (GROOVE2_LIFT if x_has_niche else 0.0), z_g1))

# finger notch in the -X wall rim (box only)
u.cut_finger_notch(box, (-OUT_HW - 1.0, 0.0), (-CAV_HW + 0.4, 0.0), NOTCH_W, NOTCH_D, BOX_H, verts=48)

# ================================================================ DOOR (closed pose)
door = u.make_box(DOOR_NAME, -OUT_HW, OUT_HW, -OUT_HL, OUT_HL, BOX_H, DOOR_Z1)
u.round_edges(door, CORNER_R, 'VERTICAL', CORNER_SEG)
u.round_edges(door, DOOR_TOP_EDGE_R, 'TOP', EDGE_SEG)
u.round_edges(door, DOOR_SEAM_R, 'BOTTOM', EDGE_SEG)

# locating lip: rounded rectangular frame under the plate, 0.3 mm inside the cavity wall
lip_hw, lip_hl = CAV_HW - LIP_GAP, CAV_HL - LIP_GAP
lip_r = INNER_CORNER_R - LIP_GAP
lip = u.make_lid_lip("_lip", -lip_hw, lip_hw, -lip_hl, lip_hl, BOX_H - LIP_H, BOX_H + FUSE, lip_t=LIP_T,
                     corner_r=lip_r, segments=CORNER_SEG)
u.boolean_union_apply(door, lip)

# hinge knuckles on the door (odd indices): barrel + arm out from the plate edge
for i, (y0, y1) in enumerate(knuckle_ranges()):
    if i % 2 == 1:
        barrel = u.make_cylinder_between("_barrel", BARREL_R, (HINGE_X, y0, HINGE_Z), (HINGE_X, y1, HINGE_Z), verts=32)
        arm = u.make_box("_arm", DOOR_ARM_X0, HINGE_X, y0, y1, BOX_H, DOOR_Z1)
        u.boolean_union_apply(door, barrel)
        u.boolean_union_apply(door, arm)
        # stubs on both end faces of the knuckle
        u.boolean_union_apply(door, make_stub(y0, -1))
        u.boolean_union_apply(door, make_stub(y1, +1))
        cut_stub_slit(door, y0, -1)
        cut_stub_slit(door, y1, +1)

# honeycomb heat vents through the plate
u.cut_hex_vents(door, VENT_COLS, VENT_ROWS, VENT_AF, BOX_H - 0.5, DOOR_Z1 + 1.0,
                web=VENT_WEB, center=VENT_CENTER)

# engraved label on the outer face
u.engrave_text(door, LABEL_TEXT, 0.0, 0.0, DOOR_Z1, size=LABEL_SIZE, depth=LABEL_DEPTH, rot_deg=LABEL_ROT_DEG)


def lift_overlaps(fixed, moving, heights):
    """{height: mm3} for `moving` lifted straight up by each height."""
    res = u.overlap_at_offsets(fixed, moving, [(0.0, 0.0, h) for h in heights])
    return {off[2]: v for off, v in res.items()}


# ================================================================ hinge swing check (door without hooks)
# The snap hooks are meant to catch in their grooves, so the swing test runs before they exist.
check_results = {}
if ASSEMBLY_CHECK:
    check_results["swing_overlap_mm3"] = u.overlap_at_rotations(box, door, 'Y', (15, 45, 90, 135, 180),
                                                                pivot=(HINGE_X, 0.0, HINGE_Z))
    # drop-in test: lift the closed door straight up; the stubs pass through the socket channels,
    # so a small overlap = the snap interference (0 at the closed position = free stub in socket)
    check_results["dropin_overlap_mm3"] = lift_overlaps(box, door, (0.0,) + tuple(DROPIN_HEIGHTS))

# snap hooks hang from the door (root FUSE above the seam, fused into the plate / lip) with a flat catch
# on top of the tip and a ramp from the arm's free end up to the tip (pointed=True)
z_top = BOX_H + FUSE
hook_l = HOOK_LEN + FUSE                               # root down to the hook's lowest point (BOX_H - HOOK_LEN)
# -Y end: the arm continues the lip downward, tip points toward -Y
for hx in HOOK_XS:
    u.boolean_union_apply(door, u.make_snap_hook("_hook", hx, -(lip_hl - LIP_T), z_top, width=HOOK_W,
                                                 length=hook_l, thickness=LIP_T, hook_depth=HOOK_TIP,
                                                 hook_height=HOOK_HEIGHT, direction='-Y', hanging=True,
                                                 pointed=True))
# extra hooks (smaller, in wall niches): +Y end (tip toward +Y) and -X long side (tip toward -X)
hook2 = dict(width=HOOK_W, length=hook_l, thickness=HOOK2_ARM_T, hook_depth=HOOK2_TIP, hook_height=HOOK_HEIGHT,
             hanging=True, pointed=True)
for hx in HOOK2_XS_END:
    u.boolean_union_apply(door, u.make_snap_hook("_hook2", hx, y_arm_in, z_top, direction='+Y', **hook2))
for hy in HOOK2_YS_SIDE:
    u.boolean_union_apply(door, u.make_snap_hook("_hook2", x_arm_in, hy, z_top, direction='-X', **hook2))

# ================================================================ assembly checks (closed pose, with hooks)
if ASSEMBLY_CHECK:
    check_results["closed_overlap_mm3"] = round(u.overlap_volume(box, door), 3)
    # latch test: lift the closed door; every hook bites into its groove ceiling once the lift exceeds the
    # 0.4 mm groove clearance, so the overlap grows with the lift (retention); a few hundredths = hinge stubs only
    check_results["latch_lift_overlap_mm3"] = lift_overlaps(box, door, (0.2, 0.6, 1.0))
    # dummy phone at its nominal place and pushed to every extreme it can reach (ribs / end stops allow
    # RIB_PLAY sideways and toward +Y; toward -Y it can slide CLEAR_XY until the phone stop). Shifts stop
    # 0.01 short of the contact so touching faces do not count as overlap.
    e = 0.01
    shifts = [(0, 0, 0), (RIB_PLAY - e, RIB_PLAY - e, 0), (-(RIB_PLAY - e), RIB_PLAY - e, 0),
              (RIB_PLAY - e, -(CLEAR_XY - e), 0), (-(RIB_PLAY - e), -(CLEAR_XY - e), 0)]
    phone = u.make_rounded_box("_phone", -PHONE_W / 2, PHONE_W / 2, PHONE_Y0, PHONE_Y0 + PHONE_L,
                               PHONE_Z0, PHONE_Z0 + PHONE_T, PHONE_CORNER_R_CHECK, 'VERTICAL', CORNER_SEG)
    for key, part in (("phone_vs_box_mm3", box), ("phone_vs_door_mm3", door)):
        res = u.overlap_at_offsets(part, phone, shifts)
        check_results[key] = {f"{dx:+.2f},{dy:+.2f}": v for (dx, dy, _), v in res.items()}
    u.delete_object(phone)
    print("ASSEMBLY CHECK:", check_results)

# ================================================================ print layout: door flipped, beside box
u.flip_objects([door], axis='Y', pivot=(0.0, 0.0, (BOX_H + DOOR_Z1) / 2))
u.translate_objects([door], (-(2 * OUT_HW + DOOR_GAP), 0.0, 0.0))
u.drop_to_bed([door])

# ================================================================ KEEP: visibility + report
coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report([box, door], min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)
print("NOTE: S24P_Door min_wall (~0.19 mm) is the tapering tip of the snap hooks, by design. The "
      "designed sections are: hook arm and lip 1.2, vent webs 1.2, hinge socket lip ~1.0, walls 2.4.")

if EXPORT:
    out = EXPORT_DIR or os.path.join(u.script_dir("s24plus_phone_box_build.py"), "exports")
    print("exported:", u.export_stl_per_object(out, [box, door]))
