"""
Samsung Galaxy S24+ storage / charging box -- SEPARATE-PARTS build (for manual editing in Blender).

Same box and door as s24plus_phone_box_build.py, but every added feature is its own mesh object, so it
can be moved, scaled or edited by hand:
  Box:  shell (tray with its cavity), 4 centring ribs, 2 phone stops, 2 end stops, 3 hinge knuckles
  Door: plate, locating lip, 2 hinge knuckles, 4 snap stubs, 6 snap hooks
Cuts (cable slot, snap grooves / niches, finger notch, hinge sockets, stub slits, vents, label) are
APPLIED to every part mesh they pass through. Parts overlap where they join (that is how they fuse).
They sit in the nested collections S24P_Phone_Box_Parts / S24P_Parts_Box and S24P_Parts_Door.
LAYOUT "print" (default): the door parts are turned over (outer face down) and placed beside the box,
ready to print, as in the main build; "closed": the door sits on the box as assembled.

All dimensions and the hinge helpers are LOADED FROM s24plus_phone_box_build.py (its SETTINGS and
local-helpers sections) at run time, so this file always matches the real box. Keep both in one folder.

MODE (below, or as an argument: run_blender.py s24plus_phone_box_parts_build.py -- export):
  "build"   (re)creates the parts. WARNING: replaces the parts collections, so hand edits are lost.
  "export"  does NOT rebuild: takes the parts as they are now in the scene (with your edits), fuses
            copies of them into one Box and one Door mesh, lays the door out for printing if the parts
            were built "closed" (flipped, outer face down, beside the box), checks them and writes one
            STL each into EXPORT_DIR.
            The fused copies are deleted afterwards unless KEEP_PRINT_COPIES = True.
For the assembly checks (hinge swing, latch, dummy phone) use s24plus_phone_box_build.py.

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python <library root>/run_blender.py s24plus_phone_box_parts_build.py
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

# ---------------------------------------------------------------- load the real box's settings + hinge helpers
MAIN_SCRIPT = "s24plus_phone_box_build.py"
_this_dir = u.script_dir("s24plus_phone_box_parts_build.py")
_main_path = os.path.join(_this_dir, MAIN_SCRIPT)
if not os.path.isfile(_main_path):
    raise FileNotFoundError(f"{MAIN_SCRIPT} must be in the same folder as this script ({_this_dir})")
_src = open(_main_path, encoding="utf-8").read()
_a = _src.index("# ================================================================ SETTINGS")
_b = _src.index("# ================================================================ KEEP: scene setup")
# defines every setting (OUT_HW, CAV_HL, BOX_H, HINGE_*, HOOK_*, ...) and knuckle_ranges / make_stub /
# cut_stub_slit / cut_socket in THIS script's namespace
exec(compile(_src[_a:_b], _main_path, "exec"), globals())

# ================================================================ SETTINGS (this file only)
MODE = "build"                   # "build" | "export" (see the docstring); a "-- export" argument overrides
LAYOUT = "print"                 # build mode: "print" = door parts flipped (outer face down) beside the box,
                                 # ready to print; "closed" = door on the box, as assembled
COLL_NAME = "S24P_Phone_Box_Parts"
BOX_COLL = "S24P_Parts_Box"
DOOR_COLL = "S24P_Parts_Door"
PRINT_COLL = "S24P_Parts_Print"  # fused print copies (export mode)
HIDE_OTHER_COLLECTIONS = True
EXPORT_DIR = ""                  # "" = an "exports_parts" folder next to this script
KEEP_PRINT_COPIES = False        # export mode: keep the fused, laid-out copies in PRINT_COLL

if "--" in sys.argv:
    _args = sys.argv[sys.argv.index("--") + 1:]
    if _args and _args[0] in ("build", "export"):
        MODE = _args[0]


def _side(v):
    return "P" if v > 0 else "N"


# ================================================================ BUILD
def build_box():
    u.use_collection(BOX_COLL, clear=True, parent=COLL_NAME)
    parts = []
    shell = u.make_hollow_box(f"{BOX_NAME}_Shell", -OUT_HW, OUT_HW, -OUT_HL, OUT_HL, 0.0, BOX_H, wall=WALL,
                              open_face='+Z', floor=FLOOR, overshoot=5.0,
                              bevel=[(CORNER_R, 'VERTICAL', CORNER_SEG), (BOX_BOTTOM_EDGE_R, 'BOTTOM', EDGE_SEG),
                                     (BOX_SEAM_R, 'TOP', EDGE_SEG)],
                              inner_radius=[(INNER_CORNER_R, 'VERTICAL', CORNER_SEG),
                                            (INNER_FLOOR_R, 'BOTTOM', EDGE_SEG)])
    parts.append(shell)

    # phone centring ribs (both long walls), 0.1 into the wall and floor
    for sx in (1, -1):
        for k, ry in enumerate(RIB_YS, start=1):
            parts.append(u.make_box(f"{BOX_NAME}_Rib_{_side(sx)}X_{k}", sx * (CAV_HW - RIB_PROUD), sx * (CAV_HW + 0.1),
                                    ry - RIB_L / 2, ry + RIB_L / 2, FLOOR - 0.1, FLOOR + RIB_H))
    # phone stops at the plug-pocket boundary (centre gap for the plug)
    for sx in (1, -1):
        parts.append(u.make_box(f"{BOX_NAME}_Stop_{_side(sx)}X", sx * (STOP_GAP / 2), sx * (CAV_HW + 0.1),
                                POCKET_END_Y - STOP_T, POCKET_END_Y, FLOOR - 0.1, FLOOR + STOP_H))
    # end stops on the +Y wall
    for k, ex in enumerate(END_STOP_XS, start=1):
        parts.append(u.make_box(f"{BOX_NAME}_EndStop_{k}", ex - END_STOP_W / 2, ex + END_STOP_W / 2,
                                CAV_HL - END_STOP_PROUD, CAV_HL + 0.1, FLOOR - 0.1, FLOOR + END_STOP_H))

    # hinge knuckles (even indices): barrel + block reaching into the wall, sockets toward the door knuckles
    for i, (y0, y1) in enumerate(knuckle_ranges()):
        if i % 2:
            continue
        kn = u.make_cylinder_between(f"{BOX_NAME}_Knuckle_{i + 1}", BARREL_R, (HINGE_X, y0, HINGE_Z),
                                     (HINGE_X, y1, HINGE_Z), verts=32)
        u.boolean_union_apply(kn, u.make_box("_block", BOX_BLOCK_X0, HINGE_X - BLOCK_END_BEFORE_AXIS, y0, y1,
                                             BOX_BLOCK_Z0, HINGE_Z - BLOCK_TOP_BELOW_AXIS))
        if i > 0:
            cut_socket(kn, y0, +1)
        if i < HINGE_N - 1:
            cut_socket(kn, y1, -1)
        parts.append(kn)

    # ---- cuts, applied to every box part they pass through
    slot_half = (SLOT_W - SLOT_H) / 2
    u.cut_objects(parts, u.make_prism("_slot", u.stadium_profile((-slot_half, SLOT_Z), (slot_half, SLOT_Z), SLOT_H,
                                                                 SLOT_ARC_SEG), 'Y', -OUT_HL - 2.0, -CAV_HL + 0.5))
    hook_bottom_z = BOX_H - HOOK_LEN
    for hx in HOOK_XS:                                     # grooves for the -Y end hooks
        u.cut_objects(parts, u.make_box("_groove", hx - (HOOK_W + GROOVE_EXTRA_W) / 2, hx + (HOOK_W + GROOVE_EXTRA_W) / 2,
                                        -CAV_HL - GROOVE_DEPTH, -CAV_HL + 0.2, hook_bottom_z - GROOVE_BELOW,
                                        hook_bottom_z + HOOK_HEIGHT + GROOVE_ABOVE))
    hk_w2 = HOOK_W + GROOVE_EXTRA_W                        # niches (only if needed) + catch grooves, extra hooks
    z_n0 = hook_bottom_z - GROOVE_BELOW
    z_g1 = hook_bottom_z + HOOK_HEIGHT + GROOVE_ABOVE
    for hx in HOOK2_XS_END:                                # +Y end wall
        if Y_HAS_NICHE:
            u.cut_objects(parts, u.make_box("_niche", hx - hk_w2 / 2, hx + hk_w2 / 2, CAV_HL - 0.1, Y_NICHE,
                                            z_n0, BOX_H + 0.5))
        u.cut_objects(parts, u.make_box("_groove2", hx - hk_w2 / 2, hx + hk_w2 / 2, Y_NICHE - 0.1, Y_GROOVE,
                                        z_n0 + (GROOVE2_LIFT if Y_HAS_NICHE else 0.0), z_g1))
    for hy in HOOK2_YS_SIDE:                               # -X long wall
        if X_HAS_NICHE:
            u.cut_objects(parts, u.make_box("_niche", X_NICHE, -CAV_HW + 0.1, hy - hk_w2 / 2, hy + hk_w2 / 2,
                                            z_n0, BOX_H + 0.5))
        u.cut_objects(parts, u.make_box("_groove2", X_GROOVE, X_NICHE + 0.1, hy - hk_w2 / 2, hy + hk_w2 / 2,
                                        z_n0 + (GROOVE2_LIFT if X_HAS_NICHE else 0.0), z_g1))
    notch_r = u.chord_radius(NOTCH_W, NOTCH_D)             # finger notch in the -X rim
    u.cut_objects(parts, u.make_cylinder_between("_notch", notch_r, (-OUT_HW - 1.0, 0.0, BOX_H - NOTCH_D + notch_r),
                                                 (-CAV_HW + 0.4, 0.0, BOX_H - NOTCH_D + notch_r), verts=48))
    return parts


def build_door():
    u.use_collection(DOOR_COLL, clear=True, parent=COLL_NAME)
    parts = []
    plate = u.make_box(f"{DOOR_NAME}_Plate", -OUT_HW, OUT_HW, -OUT_HL, OUT_HL, BOX_H, DOOR_Z1)
    u.round_edges_multi(plate, [(CORNER_R, 'VERTICAL', CORNER_SEG), (DOOR_TOP_EDGE_R, 'TOP', EDGE_SEG),
                                (DOOR_SEAM_R, 'BOTTOM', EDGE_SEG)])
    parts.append(plate)
    parts.append(u.make_lid_lip(f"{DOOR_NAME}_Lip", -LIP_HW, LIP_HW, -LIP_HL, LIP_HL, BOX_H - LIP_H, BOX_H + FUSE,
                                lip_t=LIP_T, corner_r=INNER_CORNER_R - LIP_GAP, segments=CORNER_SEG))

    # hinge knuckles (odd indices): barrel + arm out from the plate edge; a slit stub on each end face
    for i, (y0, y1) in enumerate(knuckle_ranges()):
        if i % 2 == 0:
            continue
        kn = u.make_cylinder_between(f"{DOOR_NAME}_Knuckle_{i + 1}", BARREL_R, (HINGE_X, y0, HINGE_Z),
                                     (HINGE_X, y1, HINGE_Z), verts=32)
        u.boolean_union_apply(kn, u.make_box("_arm", DOOR_ARM_X0, HINGE_X, y0, y1, BOX_H, DOOR_Z1))
        parts.append(kn)
        for face_y, sign, tag in ((y0, -1, "NY"), (y1, +1, "PY")):
            stub = make_stub(face_y, sign)
            stub.name = u.unique_name(f"{DOOR_NAME}_Stub_{i + 1}_{tag}")
            stub.data.name = stub.name
            cut_stub_slit(stub, face_y, sign)              # the slit runs through the stub ...
            cut_stub_slit(kn, face_y, sign)                # ... and on into the knuckle
            parts.append(stub)

    # vents and label (cut before the hooks exist, as in the main build)
    # (the vent field and the label lie inside the plate, clear of the lip and knuckles)
    u.cut_hex_vents(plate, VENT_COLS, VENT_ROWS, VENT_AF, BOX_H - 0.5, DOOR_Z1 + 1.0, web=VENT_WEB, center=VENT_CENTER)
    u.engrave_text(plate, LABEL_TEXT, 0.0, 0.0, DOOR_Z1, size=LABEL_SIZE, depth=LABEL_DEPTH, rot_deg=LABEL_ROT_DEG)

    # snap hooks hanging from the door (root FUSE inside the plate / lip), wedge-shaped free end
    z_top = BOX_H + FUSE
    hook_l = HOOK_LEN + FUSE
    for k, hx in enumerate(HOOK_XS, start=1):              # -Y end, continue the lip downward
        parts.append(u.make_snap_hook(f"{DOOR_NAME}_Hook_NY_{k}", hx, -(LIP_HL - LIP_T), z_top, width=HOOK_W,
                                      length=hook_l, thickness=LIP_T, hook_depth=HOOK_TIP, hook_height=HOOK_HEIGHT,
                                      direction='-Y', hanging=True, pointed=True))
    hook2 = dict(width=HOOK_W, length=hook_l, thickness=HOOK2_ARM_T, hook_depth=HOOK2_TIP, hook_height=HOOK_HEIGHT,
                 hanging=True, pointed=True)
    for k, hx in enumerate(HOOK2_XS_END, start=1):         # +Y end, in wall niches
        parts.append(u.make_snap_hook(f"{DOOR_NAME}_Hook_PY_{k}", hx, Y_ARM_IN, z_top, direction='+Y', **hook2))
    for k, hy in enumerate(HOOK2_YS_SIDE, start=1):        # -X long side, in wall niches
        parts.append(u.make_snap_hook(f"{DOOR_NAME}_Hook_NX_{k}", X_ARM_IN, hy, z_top, direction='-X', **hook2))
    return parts


# derived positions shared by the box grooves and the door hooks (same formulas as the main build)
LIP_HW, LIP_HL = CAV_HW - LIP_GAP, CAV_HL - LIP_GAP
Y_ARM_IN = PHONE_LIM_Y1 + HOOK2_PHONE_GAP                 # +Y end hooks: arm inner face
Y_NICHE = max(CAV_HL, Y_ARM_IN + HOOK2_ARM_T + HOOK2_WALL_GAP)
Y_GROOVE = Y_ARM_IN + HOOK2_ARM_T + HOOK2_TIP + HOOK2_GROOVE_CLEAR
Y_HAS_NICHE = Y_NICHE > CAV_HL + 0.05
X_ARM_IN = -(PHONE_LIM_X + HOOK2_PHONE_GAP)               # -X side hooks (negative X)
X_NICHE = min(-CAV_HW, X_ARM_IN - HOOK2_ARM_T - HOOK2_WALL_GAP)
X_GROOVE = X_ARM_IN - HOOK2_ARM_T - HOOK2_TIP - HOOK2_GROOVE_CLEAR
X_HAS_NICHE = X_NICHE < -CAV_HW - 0.05


# ================================================================ LAYOUT
def place_door_for_print(door_objs):
    """Turn the door group over (outer face down) and put it beside the box, as in the main build.
    All objects move together, so the parts keep their places relative to each other."""
    u.flip_objects(door_objs, axis='Y', pivot=(0.0, 0.0, (BOX_H + DOOR_Z1) / 2))
    u.translate_objects(door_objs, (-(2 * OUT_HW + DOOR_GAP), 0.0, 0.0))
    u.drop_to_bed(door_objs)


# ================================================================ EXPORT (fuse the current parts)
def export_current():
    box_c, door_c = bpy.data.collections.get(BOX_COLL), bpy.data.collections.get(DOOR_COLL)
    if box_c is None or door_c is None:
        raise RuntimeError(f"collections {BOX_COLL} / {DOOR_COLL} not found: run with MODE = 'build' first")
    u.use_collection(PRINT_COLL, clear=True, parent=COLL_NAME)
    box = u.fuse_copies(list(box_c.objects), f"{BOX_NAME}_Print")
    door = u.fuse_copies(list(door_c.objects), f"{DOOR_NAME}_Print")
    if door_c.get("layout", "closed") == "closed":       # parts still assembled: lay the door out now
        place_door_for_print([door])
    u.drop_to_bed([box])
    u.drop_to_bed([door])
    u.print_report([box, door], min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)
    print("NOTE: a door min_wall of ~0.19 mm is the tapering tip of the snap hooks, by design (the door then "
          "reads BAD only for that reason). Anything else BAD, or open_edges / nonmanifold > 0, needs a look.")
    out =EXPORT_DIR or os.path.join(_this_dir, "exports_parts")
    print("exported:", u.export_stl_per_object(out, [box, door]))
    if not KEEP_PRINT_COPIES:
        for o in (box, door):
            u.delete_object(o)


# ================================================================ KEEP: scene setup + run
u.setup_units_mm()
if MODE == "build":
    u.use_collection(COLL_NAME)                           # parent; the parts go into its two children
    box_parts = build_box()
    door_parts = build_door()
    if LAYOUT == "print":
        place_door_for_print(door_parts)
    elif LAYOUT != "closed":
        raise ValueError(f"LAYOUT must be 'print' or 'closed', not {LAYOUT!r}")
    bpy.data.collections[DOOR_COLL]["layout"] = LAYOUT      # export mode reads this
    if HIDE_OTHER_COLLECTIONS:
        u.show_only_collection(COLL_NAME)
    u.frame_all()                                         # no-op headless
    print({"status": "ok", "mode": MODE, "layout": LAYOUT, "collection": COLL_NAME, "box_parts": len(box_parts),
           "door_parts": len(door_parts)})
    u.print_report(box_parts + door_parts)
elif MODE == "export":
    export_current()
else:
    raise ValueError(f"MODE must be 'build' or 'export', not {MODE!r}")
