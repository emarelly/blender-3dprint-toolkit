"""
Vacuum bag coupler -- Blender build script (generated from vacuum_bag_coupler_description.md).

A short threaded ring that lets the already printed adapter (vacuum_bag_adapter_build.py, single-start
P1.5 socket) screw onto the bag valve (two-start P1.0):
  * bottom (on the bed): MALE single-start P1.5 thread, dia 23.5 / 25.1 (copies the valve's male inlet, the
    size the old adapter's socket was made for), 7.5 mm long, 0.4 mm lead-in chamfer; its end face seals
    on the old adapter's dia 21 shoulder
  * 45 deg outward chamfer from the male crest dia 25.1 to the socket's outside dia 30.2 (no overhang)
  * top: the new FEMALE two-start socket, the same as vacuum_bag_adapter_2start_build.py: flat dia 21
    shoulder (faces up), root 26.6 / crest 24.4, 1.0 between ridges, 2 starts (lead 2.0), round,
    right-hand, 7 mm, 0.8 mm mouth chamfer
  * bore dia 21 all the way through
One ring tube (u.make_ring_tube), no Booleans. The diameters, wall, material and helpers are LOADED FROM
vacuum_bag_adapter_build.py (from its "SETTINGS (match the spec)" line to its "PART" line); keep both
scripts in one folder.

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python run_blender.py projects/vacuum_bag_adapter/vacuum_bag_coupler_build.py
"""

import math                                 # used by the helpers loaded from the main script
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
if _cached is not None and os.path.normcase(os.path.dirname(os.path.abspath(getattr(_cached, "__file__", "") or ""))) \
        != os.path.normcase(os.path.abspath(_here)):
    del sys.modules["utils_3d"]

import importlib
import utils_3d as u
importlib.reload(u)

# ---------------------------------------------------------------- load the adapter's definition
MAIN_SCRIPT = "vacuum_bag_adapter_build.py"

_my_dir = u.script_dir("vacuum_bag_coupler_build.py")
_main_path = os.path.join(_my_dir, MAIN_SCRIPT)
if not os.path.isfile(_main_path):
    raise FileNotFoundError(f"{MAIN_SCRIPT} must be in the same folder as this script ({_my_dir})")
_src = open(_main_path, encoding="utf-8").read()
_a = _src.index("# ---------------------------------------------------------------- SETTINGS (match the spec)")
_b = _src.index("# ---------------------------------------------------------------- PART")
# defines the settings (SOCKET_THREAD_*, VALVE_THREAD_*, THREAD_LEN, MOUTH_CH, SHOULDER_ID, WALL, material,
# SEGMENTS ...), the derived values (R_CREST, R_ROOT, SOCKET_R, SHOULDER_R) and the helpers circ /
# socket_thread_rings / make_valve_dummy in THIS script's namespace
exec(compile(_src[_a:_b], _main_path, "exec"), globals())

# ================================================================ COUPLER SETTINGS (match the spec)
COLL_NAME = "VacuumBagCoupler"
OBJ_NAME = "VBC_Coupler"
HIDE_OTHER_COLLECTIONS = True
ASSEMBLY_CHECK = True            # dummy old-adapter socket + dummy bag valve (deleted after)
EXPORT = False                   # True: write VBC_Coupler.stl into EXPORT_DIR
EXPORT_DIR = ""                  # "" = an "exports" folder next to this script

# Male end: the old (printed) adapter's thread
OLD_PITCH = 1.5                  # single-start, as printed (vacuum_bag_adapter_build.py THREAD_PITCH)
OLD_STARTS = 1
MALE_MINOR_D = VALVE_THREAD_MINOR   # 23.5  copies the valve's male inlet (what the old socket was sized for)
MALE_MAJOR_D = VALVE_THREAD_MAJOR   # 25.1
MALE_LEN = 7.5                   # Z 0 .. 7.5: full thread; longer than the old socket's 7 mm thread
MALE_CH = 0.4                    # 45 deg lead-in chamfer at Z 0, from the root dia (also elephant's foot)

# Female end: the bag valve's real thread (same as vacuum_bag_adapter_2start_build.py)
NEW_PITCH = 1.0                  # axial distance between neighbouring ridges
NEW_STARTS = 2                   # two threads 180 deg apart -> lead 2.0 per turn
SHOULDER_Z = 10.08               # flat shoulder (63 layers of 0.16), above the 45 deg outer chamfer

# ---------------------------------------------------------------- derived (do not edit)
R_MALE_MIN = MALE_MINOR_D / 2                  # 11.75
R_MALE_MAX = MALE_MAJOR_D / 2                  # 12.55
Z_CH_TOP = MALE_LEN + (SOCKET_R - R_MALE_MAX)  # 10.05  outer chamfer reaches the socket's outside
Z_TOP_C = SHOULDER_Z + THREAD_LEN              # 17.08
THREAD_PITCH, THREAD_STARTS = NEW_PITCH, NEW_STARTS   # the loaded helpers (dummy valve) use these


# ================================================================ part
def build_coupler():
    # outer: male thread with a lead-in chamfer at the bed, then a 45 deg cone out to the socket's outside
    outer = []
    for z in u.thread_z_steps(0.0, Z_CH_TOP, OLD_PITCH, THREAD_Z_STEPS):
        thread = u.thread_radii(z, R_MALE_MIN, R_MALE_MAX, OLD_PITCH, 'round', segments=SEGMENTS,
                                starts=OLD_STARTS)
        low = R_MALE_MIN - MALE_CH + z              # bottom lead-in cone (caps the thread)
        high = R_MALE_MAX + (z - MALE_LEN)          # 45 deg cone to the socket (covers the thread)
        outer.append((z, [min(SOCKET_R, low, max(r, high)) for r in thread]))
    outer.append((Z_TOP_C, circ(SOCKET_R)))
    # inner: dia 21 bore, flat shoulder, two-start female thread with mouth chamfer
    inner = [(0.0, circ(SHOULDER_R)), (SHOULDER_Z, circ(SHOULDER_R))]
    inner += socket_thread_rings(SHOULDER_Z, Z_TOP_C, NEW_PITCH, NEW_STARTS)
    return u.make_ring_tube(OBJ_NAME, outer, inner)


# ================================================================ fit checks (dummies, deleted after)
def make_old_socket_dummy():
    """The old adapter's socket (single-start P1.5, its mouth chamfer) with its shoulder 0.05 below the
    coupler's end face, same thread phase as the coupler's male thread."""
    z_sh, z_top = -0.05, -0.05 + THREAD_LEN
    outer = [(-3.0, circ(SOCKET_R)), (z_top, circ(SOCKET_R))]
    inner = [(-3.0, circ(SHOULDER_R)), (z_sh, circ(SHOULDER_R))]
    inner += socket_thread_rings(z_sh, z_top, OLD_PITCH, OLD_STARTS)
    return u.make_ring_tube("_chk_old_socket", outer, inner)


def assembly_check(part):
    old = make_old_socket_dummy()
    valve = make_valve_dummy(SHOULDER_Z, THREAD_LEN + 5.0)     # two-start (THREAD_PITCH/STARTS above)
    res = {"old_adapter_overlap_mm3": round(u.overlap_volume(part, old), 3),
           "valve_overlap_mm3": round(u.overlap_volume(part, valve), 3)}
    # positive control: the coupler pushed 1 mm down into the old adapter's shoulder must collide
    u.translate_objects([old], (0.0, 0.0, 1.0))
    res["control_old_up_1mm_mm3"] = round(u.overlap_volume(part, old), 3)
    u.delete_object(old)
    u.delete_object(valve)
    print({"assembly_check": res, "expected": "0.0, 0.0, control > 0"})
    return res


# ================================================================ KEEP: scene setup + report
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)
coupler = build_coupler()
if ASSEMBLY_CHECK:
    assembly_check(coupler)
u.drop_to_bed([coupler])                    # modelled in its print orientation (male end down)

coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report([coupler], min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)

if EXPORT:
    out = EXPORT_DIR or os.path.join(_my_dir, "exports")
    print("exported:", u.export_stl_per_object(out, [coupler]))
