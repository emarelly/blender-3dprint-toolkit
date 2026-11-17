"""
Vacuum bag adapter -- TEST RINGS (Blender build script)
(generated from vacuum_bag_adapter_test_description.md).

Two small prints to check both fits before printing the whole adapter (about 1/4 of its material):
  * VBA_Test_Oval   -- the oval spigot, 10 mm long, with the same 1.0 mm lead-in chamfer at the tip.
                       Push it into the vacuum's opening: it should go in by hand and hold by friction.
  * VBA_Test_Thread -- the threaded socket: a 3.2 mm base ring (bore dia 21) with the flat seal shoulder
                       on top, then the 7 mm thread with the mouth chamfer. Screw it onto the bag valve:
                       it should turn by hand and the valve rim should stop flat on the shoulder.
If a fit is wrong, change the value in vacuum_bag_adapter_build.py (SPIGOT_ADJ for the oval, THREAD_ADJ for
the thread), run this script again and reprint the test ring.

All dimensions and the ring helpers are LOADED FROM vacuum_bag_adapter_build.py (its SETTINGS, derived
values and local helpers) at run time, so the test rings always match the real adapter. Keep both
scripts in the same folder.

Both rings print as they sit in the adapter (oval tip down / shoulder face up), side by side on the bed.

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python run_blender.py projects/vacuum_bag_adapter/vacuum_bag_adapter_test_build.py
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

# ---------------------------------------------------------------- load the real adapter's definition
MAIN_SCRIPT = "vacuum_bag_adapter_build.py"

_test_dir = u.script_dir("vacuum_bag_adapter_test_build.py")
_main_path = os.path.join(_test_dir, MAIN_SCRIPT)
if not os.path.isfile(_main_path):
    raise FileNotFoundError(f"{MAIN_SCRIPT} must be in the same folder as this test script ({_test_dir})")
_src = open(_main_path, encoding="utf-8").read()
_a = _src.index("# ---------------------------------------------------------------- SETTINGS (match the spec)")
_b = _src.index("# ---------------------------------------------------------------- PART")
# defines every setting (OVAL_*, SPIGOT_ADJ, THREAD_*, SOCKET_THREAD_*, VALVE_THREAD_*, MOUTH_CH, SEGMENTS,
# ...), the derived values (R_CREST, R_ROOT, SOCKET_R, SHOULDER_R, D_OUT, D_IN) and the helpers oval_ring /
# circ / spigot_rings / socket_thread_rings / make_valve_dummy in THIS script's namespace
exec(compile(_src[_a:_b], _main_path, "exec"), globals())

# ================================================================ TEST SETTINGS (override / add)
COLL_NAME = "VacuumBagAdapter_Test"
HIDE_OTHER_COLLECTIONS = True
ASSEMBLY_CHECK = True            # dummy opening / dummy valve, as in the main build (deleted after)
EXPORT = False                   # True: one STL per test ring into EXPORT_DIR
EXPORT_DIR = ""                  # "" = an "exports_test" folder next to this script

OVAL_TEST_LEN = 10.0             # oval test ring height (Z 0 .. 10)
THREAD_BASE_H = 3.2              # thread test: base ring under the shoulder, 20 layers of 0.16 (shoulder on a
                                 # whole layer); total height 3.2 + THREAD_LEN = 10.2
BED_CHAMFER = 0.4                # thread test: 45 deg chamfer on the outer bottom edge (elephant's foot)
LAYOUT_GAP = 8.0                 # gap between the two rings on the bed


# ================================================================ test rings
def make_oval_test():
    outer, inner = spigot_rings(OVAL_TEST_LEN)
    return u.make_ring_tube("VBA_Test_Oval", outer, inner)


def make_thread_test():
    z_sh, z_top = THREAD_BASE_H, THREAD_BASE_H + THREAD_LEN
    outer = [(0.0, circ(SOCKET_R - BED_CHAMFER)), (BED_CHAMFER, circ(SOCKET_R)), (z_top, circ(SOCKET_R))]
    inner = [(0.0, circ(SHOULDER_R)), (z_sh, circ(SHOULDER_R))] + socket_thread_rings(z_sh, z_top)
    return u.make_ring_tube("VBA_Test_Thread", outer, inner)


def check_fits(thread):
    """Same dummy valve as the main build (measured male inlet, same phase) seated 0.05 above the test
    shoulder: must be 0.0 mm3. The oval is copied from an adapter that fits, so it has no dummy."""
    valve = make_valve_dummy(THREAD_BASE_H, THREAD_LEN + 5.0)
    res = {"thread_vs_valve_mm3": round(u.overlap_volume(thread, valve), 3)}
    u.delete_object(valve)
    print({"test_check": res, "expected": 0.0})
    return res


# ================================================================ KEEP: scene setup
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)
oval = make_oval_test()
thread = make_thread_test()
if ASSEMBLY_CHECK:
    check_fits(thread)

# print layout: oval ring at the origin, thread ring beside it along +X, both on the bed
x_off = OVAL_L / 2 + LAYOUT_GAP + SOCKET_R
u.translate_objects([thread], (x_off, 0.0, 0.0))
u.drop_to_bed([oval])
u.drop_to_bed([thread])

# ================================================================ KEEP: visibility + report
coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report([oval, thread], min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)

if EXPORT:
    out = EXPORT_DIR or os.path.join(_test_dir, "exports_test")
    print("exported:", u.export_stl_per_object(out, [oval, thread]))
