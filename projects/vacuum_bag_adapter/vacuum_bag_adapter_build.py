"""
Vacuum bag adapter -- Blender build script (generated from vacuum_bag_adapter_description.md, v1.3).
This is the adapter as printed (single-start P1.5 thread). The bag's valve turned out to be two-start
P1.0: vacuum_bag_adapter_2start_build.py builds this adapter with that thread, and
vacuum_bag_coupler_build.py a short coupler that lets this adapter screw onto the valve.

One printed PETG part that connects a portable vacuum to a storage vacuum bag's valve:
  * oval spigot 39.5 x 17.3 (copied from another vacuum adapter that fits), 30 mm, plugs into the vacuum
  * 20 mm ruled loft from the oval to a round neck (bore dia 21)
  * flat seal shoulder (ID dia 21) the valve's rim tightens against
  * round socket (OD dia 30.2) with a printed internal thread copied from the bag's own female cover
    (root dia 26.6 / crest 24.4, pitch 1.5, round), 7 mm long, 0.8 mm mouth lead-in chamfer; it screws
    onto the valve's male dia 23.5-25.1 thread
Modelled in its print orientation: oval end on the bed (Z = 0), thread end up, axis = Z, the oval's
long axis = X. The whole part is ONE ring tube (u.make_ring_tube): every surface is a stack of rings
(radius per angle), so there is no Boolean anywhere. Every number is in the SETTINGS block and
matches the spec's Decisions table. utils_3d.py is found in any parent folder (or set UTILS_DIR /
the UTILS_3D_DIR environment variable).

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python run_blender.py projects/vacuum_bag_adapter/vacuum_bag_adapter_build.py
"""

import math
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

# ---------------------------------------------------------------- SETTINGS (match the spec)
COLL_NAME = "VacuumBagAdapter"
OBJ_NAME = "VBA_Adapter"
LAYOUT = "print"               # "print"     = ready for print: oval end on the bed (Z = 0), thread end up
                               # "assembled" = the same pose: one part, modelled in its print orientation
HIDE_OTHER_COLLECTIONS = True
ASSEMBLY_CHECK = True          # fit check against a dummy bag valve (deleted after)
EXPORT = False                 # True: write VBA_Adapter.stl into EXPORT_DIR
EXPORT_DIR = ""                # "" = an "exports" folder next to this script
BED = (220, 220, 250)          # printer build volume x, y, z (report check only)

# Material / process (suggested from reference/materials.md, confirmed by the user). Dimensions that
# depend on the material are computed from these names, so switching material = editing this group.
MATERIAL = "PETG"
LINE_W = 0.45                  # 0.4 nozzle
LAYER_H = 0.16
MIN_WALL = 2 * LINE_W          # thinnest wall allowed (used by the report): 0.9
WALL = 4 * LINE_W              # structural wall, whole line widths: 1.8
OVERHANG_DEG = 45              # report: faces flatter than this from vertical are flagged
# Fit tuning (v1.1): spigot and thread are copied from parts that fit (see below), so both start at 0.0.
# Change these after a test print instead of editing the measured values.
SPIGOT_ADJ = 0.0               # on size: + makes the oval spigot smaller (looser in the vacuum)
THREAD_ADJ = 0.0               # per side: + makes the printed thread bigger (looser on the valve)

# Vacuum side: the oval SPIGOT's outside, measured on another vacuum adapter that fits (v1.1; v1.0 used
# the opening 39.5 x 17.5 minus 0.20, which printed too wide)
OVAL_L = 39.5                  # along X
OVAL_W = 17.3                  # along Y
OVAL_END = 8.0                 # each end is a circular arc that starts 8 mm from the tip (arc depth)
SPIGOT_LEN = 30.0              # Z 0 .. 30, insertion depth
LEADIN = 1.0                   # 45 deg lead-in chamfer at the spigot tip (also the elephant's-foot chamfer)

# Transition and neck
TRANS_LEN = 20.0               # ruled loft, oval -> round, Z 30 .. 50
NECK_LEN = 2.0                 # round neck, bore = SHOULDER_ID, Z 50 .. 52
SHOULDER_ID = 21.0             # flat seal shoulder at Z 52 (faces up); the valve rim tightens against it

# Bag side (v1.1, measured after the first test print): the printed internal thread copies the bag's own
# female cover; the valve's male inlet is used only for the fit check
SOCKET_THREAD_ROOT_D = 26.6    # female cover: thread root (groove) dia
SOCKET_THREAD_CREST_D = 24.4   # female cover: thread crest dia
VALVE_THREAD_MAJOR = 25.1      # male inlet: crest dia (fit check only)
VALVE_THREAD_MINOR = 23.5      # male inlet: root dia (fit check only)
THREAD_PITCH = 1.5             # axial distance between neighbouring ridges; right-hand, rounded profile (v1.0 had 2.0, v1.1 had 1.0)
THREAD_STARTS = 1              # 1 = this (printed) adapter. The bag's real valve is two-start P1.0 (lead 2.0):
                               # see vacuum_bag_adapter_2start_build.py and vacuum_bag_coupler_build.py
THREAD_LEN = 7.0               # Z 52 .. 59 (4.7 turns)
MOUTH_CH = 0.8                 # 45 deg lead-in chamfer at the socket mouth (from the thread root dia)

SEGMENTS = 192                 # radii per ring (around the axis)
THREAD_Z_STEPS = 16            # rings per pitch in the thread
TRANS_STEPS = 20               # rings in the loft (a ruled surface; more rings = finer triangles only)

# vacuum_bag_adapter_2start_build.py runs this whole script with OVERRIDES = {setting: value} (names,
# THREAD_PITCH, THREAD_STARTS); run directly, nothing is overridden.
globals().update(globals().get("OVERRIDES", {}))

# ---------------------------------------------------------------- derived (do not edit)
R_CREST = SOCKET_THREAD_CREST_D / 2 + THREAD_ADJ   # 12.2  the socket's thread crest (material)
R_ROOT = SOCKET_THREAD_ROOT_D / 2 + THREAD_ADJ     # 13.3  the socket's thread root (groove)
SOCKET_R = R_ROOT + WALL                       # 15.1
SHOULDER_R = SHOULDER_ID / 2                   # 10.5
Z_T0 = SPIGOT_LEN                              # 30  loft starts
Z_T1 = Z_T0 + TRANS_LEN                        # 50  loft ends, neck starts
Z_SH = Z_T1 + NECK_LEN                         # 52  seal shoulder
Z_TOP = Z_SH + THREAD_LEN                      # 59
D_OUT = SPIGOT_ADJ / 2                         # spigot outside = the OVAL_* outline shrunk by this per side
D_IN = D_OUT + WALL                            # spigot inside

_this_dir = u.script_dir("vacuum_bag_adapter_build.py")


# ---------------------------------------------------------------- local helpers (oval shape)
# utils_3d has no oval/loft primitive; the oval is given as one radius per angle so it can be fed to
# u.make_ring_tube together with the round and threaded rings.
def oval_radius(theta, d):
    """Distance from the axis to the oval outline (OVAL_*) shrunk by d (mm) along direction theta.
    The outline: straight sides y = +-OVAL_W/2 and circular end arcs OVAL_END deep (convex)."""
    hl, hw = OVAL_L / 2, OVAL_W / 2
    r_end = (hw ** 2 + OVAL_END ** 2) / (2 * OVAL_END)  # 8.676 (OVAL_END 8)
    cx = hl - r_end                                     # arc centres at x = +-cx
    r, w = r_end - d, hw - d
    xc = cx + math.sqrt(r * r - w * w)                  # where the straight side meets the arc
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    if s > 1e-12 and (w / s) * c <= xc:
        return w / s                                    # hits the straight side
    return cx * c + math.sqrt((cx * c) ** 2 - cx * cx + r * r)   # hits the end arc


def oval_ring(d):
    return [oval_radius(2 * math.pi * i / SEGMENTS, d) for i in range(SEGMENTS)]


def lerp_ring(a, b, t):
    return [x + (y - x) * t for x, y in zip(a, b)]


def circ(r):
    return [r] * SEGMENTS


def spigot_rings(z_top):
    """Outer and inner ring lists of the oval spigot from Z 0 (tip, lead-in chamfer) to z_top.
    Also used by vacuum_bag_adapter_test_build.py (oval test ring)."""
    oval_out, oval_in = oval_ring(D_OUT), oval_ring(D_IN)
    return ([(0.0, oval_ring(D_OUT + LEADIN)), (LEADIN, oval_out), (z_top, oval_out)],
            [(0.0, oval_in), (z_top, oval_in)])


def socket_thread_rings(z0, z1, pitch=None, starts=None):
    """Inner rings of the printed valve thread from z0 (shoulder) to z1 (mouth, 45 deg chamfer).
    pitch / starts default to THREAD_PITCH / THREAD_STARTS. Also used by vacuum_bag_adapter_test_build.py
    (thread test ring) and vacuum_bag_coupler_build.py."""
    pitch = THREAD_PITCH if pitch is None else pitch
    starts = THREAD_STARTS if starts is None else starts
    rings = []
    for z in u.thread_z_steps(z0, z1, pitch, THREAD_Z_STEPS):
        thread = u.thread_radii(z, R_CREST, R_ROOT, pitch, 'round', segments=SEGMENTS, starts=starts)
        cone = R_ROOT + MOUTH_CH - (z1 - z)             # 45 deg mouth chamfer
        rings.append((z, [max(r, cone) for r in thread]))
    return rings


def make_valve_dummy(z_shoulder, length):
    """The bag's male inlet (measured thread, same phase as the socket) seated 0.05 above the shoulder,
    for overlap checks. Also used by vacuum_bag_adapter_test_build.py."""
    return u.make_threaded_tube(
        "_chk_valve", z_shoulder + 0.05, z_shoulder + length,
        outer=dict(r_min=VALVE_THREAD_MINOR / 2, r_max=VALVE_THREAD_MAJOR / 2, pitch=THREAD_PITCH, form='round',
                   starts=THREAD_STARTS),
        inner=SHOULDER_R - 0.5, segments=SEGMENTS, steps_per_pitch=THREAD_Z_STEPS)


# ---------------------------------------------------------------- PART
# (vacuum_bag_adapter_test_build.py loads this script from the "SETTINGS (match the spec)" line up to the
#  "PART" line above: keep both marker lines.)
def build_adapter():
    # outer surface: chamfered tip, oval spigot, loft to the round socket, socket
    outer, inner = spigot_rings(Z_T0)
    oval_out, oval_in = outer[-1][1], inner[-1][1]
    for k in range(1, TRANS_STEPS + 1):
        t = k / TRANS_STEPS
        outer.append((Z_T0 + TRANS_LEN * t, lerp_ring(oval_out, circ(SOCKET_R), t)))
    outer.append((Z_TOP, circ(SOCKET_R)))

    # inner surface: oval bore, loft to the dia 21 neck, flat shoulder step, thread with mouth chamfer
    for k in range(1, TRANS_STEPS + 1):
        t = k / TRANS_STEPS
        inner.append((Z_T0 + TRANS_LEN * t, lerp_ring(oval_in, circ(SHOULDER_R), t)))
    inner.append((Z_SH, circ(SHOULDER_R)))
    inner += socket_thread_rings(Z_SH, Z_TOP)
    return u.make_ring_tube(OBJ_NAME, outer, inner)


# ---------------------------------------------------------------- fit check (dummy, deleted after)
def assembly_check(part):
    """The dummy valve must not overlap the adapter. (The spigot is copied from an adapter that fits, so
    there is no measured vacuum opening to check against since v1.1.)"""
    valve = make_valve_dummy(Z_SH, THREAD_LEN + 5.0)
    res = {"valve_overlap_mm3": round(u.overlap_volume(part, valve), 3)}
    u.delete_object(valve)
    print({"assembly_check": res, "expected": 0.0})
    return res


# ---------------------------------------------------------------- KEEP: layout
def place_for_print(objs):
    """One part, already modelled in its print orientation (oval end down): only drop it on the bed."""
    u.drop_to_bed(objs)


# ---------------------------------------------------------------- KEEP: scene setup + run
u.setup_units_mm()
u.use_collection(COLL_NAME, clear=True)
adapter = build_adapter()
if ASSEMBLY_CHECK:
    assembly_check(adapter)
if LAYOUT == "print":
    place_for_print([adapter])
elif LAYOUT != "assembled":
    raise ValueError(f"LAYOUT must be 'print' or 'assembled', not {LAYOUT!r}")

coll = bpy.data.collections[COLL_NAME]
if HIDE_OTHER_COLLECTIONS:
    u.show_only_collection(COLL_NAME)
u.frame_all()                                           # no-op headless

print({"status": "ok", "layout": LAYOUT, "collection": COLL_NAME, "object_count": len(coll.objects),
       "objects": sorted(o.name for o in coll.objects)})
u.print_report([adapter], min_wall=MIN_WALL, bed=BED, overhang_deg=OVERHANG_DEG)

if EXPORT:
    out = EXPORT_DIR or os.path.join(_this_dir, "exports")
    print("exported:", u.export_stl_per_object(out, [adapter]))
