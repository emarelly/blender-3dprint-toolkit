"""
G9 dome adapter -- Blender build script (generated from g9_dome_adapter_description.md).

One printed PETG part that hangs a closed glass globe (dia 120, top cut flat to dia 36, internal
G9-shade thread) from an M10x1 lamp pipe and covers the cut top against rain and dust:
  * G9A_Dome   -- dia 60 dome, flat top with an R8 edge, underside following the globe; dia 13 bore,
                  washer recess on top, O-ring groove (32 x 2 face seal) underneath
  * G9A_Spigot -- 15 mm spigot below the dome: M20.8 x 2 glass thread outside, printed M10x1 pipe
                  thread inside
The two features are kept as SEPARATE meshes so they can be edited by hand in Blender (cuts are
already applied to every mesh they pass through). Every number is in the SETTINGS block and matches
the spec's Decisions table. utils_3d.py is found in any parent folder (or set UTILS_DIR /
the UTILS_3D_DIR environment variable).

MODE (below, or as an argument: run_blender.py g9_dome_adapter_build.py -- export):
  "build"  -- (re)build the parts. WARNING: replaces the collection, so hand edits are lost.
  "export" -- does NOT rebuild: fuses copies of the CURRENT parts (including hand edits) into one
              printable mesh, turns it into the print orientation if the parts are still assembled,
              checks it and writes G9A_Adapter.stl into EXPORT_DIR.
LAYOUT (build mode):
  "assembled" -- as installed: dome on top, spigot pointing down, Z = 0 at the glass's cut top
  "print"     -- upside down, flat dome top on the bed (Z = 0), spigot pointing up; no supports

Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited the file), or
    python run_blender.py projects/g9_dome_adapter/g9_dome_adapter_build.py
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
MODE = "build"                 # "build" | "export" (see the docstring); a "-- export" argument overrides
LAYOUT = "assembled"           # "assembled" = as installed on the glass (dome on top, spigot down)
                               # "print"     = upside down, dome top on the bed, ready to print
COLL_NAME = "G9_Dome_Adapter"
PART_COLL = "G9A_Adapter_Parts"   # child collection: the feature meshes of the one printed part
PRINT_NAME = "G9A_Adapter"     # export mode: fused copy / STL name
HIDE_OTHER_COLLECTIONS = True
EXPORT_DIR = ""                # "" = an "exports" folder next to this script
KEEP_PRINT_COPY = False        # export mode: keep the fused, laid-out copy in the scene

# Glass globe (not printed, used for the shapes that sit on it)
GLOBE_R = 60.0                 # dia 120 globe
CUT_D = 36.0                   # flat cut top of the globe, Z = 0 (was 40; reduced to 36 after the test print)

# Dome (Z 0 .. DOME_TOP_Z)
DOME_D = 60.0
DOME_TOP_Z = 15.0
DOME_EDGE_R = 8.0              # round of the top outer edge
UNDERSIDE_GAP = 0.5            # flat underside over the cut, as modelled: 0.5 above the glass = the O-ring
                               # just touches; tightening moves the dome down 0.5 until this flat rests on
                               # the glass (hard stop, O-ring at its design squeeze)
CURVE_GAP = 1.0                # curved underside outside the cut, as modelled (0.5 left once tightened),
                               # so only the flat ring touches the glass
HUB_BORE_D = 13.0              # plain bore through the dome, Z 0 .. DOME_TOP_Z
WASHER_RECESS_D = 15.0         # recess on top for an M10 rubber washer (pressed by a metal M10x1 nut)
WASHER_RECESS_DEPTH = 1.5
ORING_GROOVE_ID_D = 29.8       # face seal on the flat cut top of the glass, O-ring 32 x 2 mm (ID x cord, 36 OD);
ORING_GROOVE_OD_D = 35.2       # groove OD 0.8 mm under the O-ring's 36 OD, so it sits slightly squeezed
                               # against the outer wall, centred on about dia 33 (1.5 mm from the glass edge)
ORING_GROOVE_DEPTH = 1.5       # from the flat underside: 25 % squeeze of the 2.0 cord at the hard stop

# Spigot (Z -SPIGOT_LEN .. 0, screws into the glass)
SPIGOT_LEN = 15.0
SPIGOT_OVERLAP = 0.55          # spigot reaches this far into the dome (that is how the two fuse); not 0.5,
                               # which put a ring of thread vertices exactly in the dome's underside plane
SPIGOT_TOP_BORE_D = 12.4       # bore of the spigot's top end (Z 0 .. its top, inside the dome): 0.3 mm/side
                               # narrower than the dome's dia 13, so the dome's bore edge is buried in the
                               # spigot (equal walls, or a 0.1 mm ledge, broke the fused STL); the pipe is dia 10
GLASS_THREAD_PITCH = 2.0       # common G9 shade thread M20.8 x 2 (rounded profile; glass is not precise)
GLASS_THREAD_MAJOR_D = 20.6    # 20.8 - 2 x 0.1 clearance (set by the user)
GLASS_THREAD_MINOR_D = 19.0
GLASS_THREAD_LEADIN = 2.0      # thread fades in over the first 2 mm at the spigot tip

# Printed internal M10x1 pipe thread (Z -SPIGOT_LEN .. 0)
PIPE_THREAD_PITCH = 1.0
PIPE_THREAD_MAJOR_D = 10.4     # M10 + 2 x 0.2 clearance
PIPE_THREAD_MINOR_D = 9.32     # ISO internal minor 8.917 + 2 x 0.2 clearance

SEGMENTS = 128                 # around the axis (dome, bores)
THREAD_SEGMENTS = 96           # around the axis (threads)
THREAD_Z_STEPS = 16            # rings per pitch (threads)

if "--" in sys.argv:
    _args = sys.argv[sys.argv.index("--") + 1:]
    if _args and _args[0] in ("build", "export"):
        MODE = _args[0]

_this_dir = u.script_dir("g9_dome_adapter_build.py")


# ---------------------------------------------------------------- local helper
def globe_z(r):
    """Z of the globe's outer surface at radius r (Z = 0 at the cut top)."""
    return math.sqrt(GLOBE_R ** 2 - r ** 2) - math.sqrt(GLOBE_R ** 2 - (CUT_D / 2) ** 2)


# ---------------------------------------------------------------- BUILD
# Both meshes are built directly (lathe profile / ring tube), with NO Boolean: every Boolean cut here
# (O-ring groove, bores, pipe-thread cutter) left near-zero-area triangles that broke the later fusing
# union in export mode.
def build_parts():
    u.use_collection(PART_COLL, clear=True, parent=COLL_NAME)
    ro, rc = DOME_D / 2, CUT_D / 2
    rb, rw = HUB_BORE_D / 2, WASHER_RECESS_D / 2
    g0, g1 = ORING_GROOVE_ID_D / 2, ORING_GROOVE_OD_D / 2
    zf, zg = UNDERSIDE_GAP, UNDERSIDE_GAP + ORING_GROOVE_DEPTH

    # Dome: one lathe profile with the dia 13 bore, the washer recess and the O-ring groove in it;
    # underside flat over the cut (groove in it), a small step up at the cut edge, then following the globe
    prof = [(rb, zf), (g0, zf), (g0, zg), (g1, zg), (g1, zf), (rc, zf)]
    n_sph = 24
    for k in range(0, n_sph + 1):
        r = rc + (ro - rc) * k / n_sph
        prof.append((r, globe_z(r) + CURVE_GAP))
    prof.append((ro, DOME_TOP_Z - DOME_EDGE_R))
    n_arc = 16
    for k in range(1, n_arc + 1):                      # R8 round: (ro, top-R) -> (ro-R, top)
        a = math.pi / 2 * k / n_arc
        prof.append((ro - DOME_EDGE_R + DOME_EDGE_R * math.cos(a), DOME_TOP_Z - DOME_EDGE_R + DOME_EDGE_R * math.sin(a)))
    prof += [(rw, DOME_TOP_Z), (rw, DOME_TOP_Z - WASHER_RECESS_DEPTH), (rb, DOME_TOP_Z - WASHER_RECESS_DEPTH)]
    dome = u.make_revolved_ring("G9A_Dome", list(reversed(prof)), verts=SEGMENTS)

    # Spigot: glass thread outside (fading in at the tip), M10x1 pipe thread inside up to Z 0, then a
    # dia SPIGOT_TOP_BORE_D bore up to its top, which sits SPIGOT_OVERLAP inside the dome
    z0, z1 = -SPIGOT_LEN, UNDERSIDE_GAP + SPIGOT_OVERLAP
    glass = dict(r_min=GLASS_THREAD_MINOR_D / 2, r_max=GLASS_THREAD_MAJOR_D / 2, pitch=GLASS_THREAD_PITCH,
                 form='round', leadin=GLASS_THREAD_LEADIN)
    pipe = dict(r_min=PIPE_THREAD_MINOR_D / 2, r_max=PIPE_THREAD_MAJOR_D / 2, pitch=PIPE_THREAD_PITCH,
                form='iso', z1=0.0)
    spigot = u.make_threaded_tube("G9A_Spigot", z0, z1, outer=glass,
                                  inner=[pipe, dict(r=SPIGOT_TOP_BORE_D / 2)],
                                  segments=THREAD_SEGMENTS, steps_per_pitch=THREAD_Z_STEPS)
    return [dome, spigot]


# ---------------------------------------------------------------- KEEP: layout (assembled -> ready for print)
def place_for_print(objs):
    """Turn the part over as ONE group (dome top down) and put it on the bed."""
    u.flip_objects(objs, axis='X', pivot=(0.0, 0.0, 0.0))
    u.drop_to_bed(objs)


# ---------------------------------------------------------------- EXPORT (fuse the current parts)
def export_current():
    part_c = bpy.data.collections.get(PART_COLL)
    if part_c is None:
        raise RuntimeError(f"collection {PART_COLL} not found: run with MODE = 'build' first")
    u.use_collection(COLL_NAME)
    fused = u.fuse_copies(list(part_c.objects), PRINT_NAME)   # also cleans it for STL (u.clean_for_stl)
    if part_c.get("layout", "assembled") == "assembled":   # parts still as installed: turn the copy over
        place_for_print([fused])
    u.drop_to_bed([fused])
    u.print_report([fused], overhang_deg=45)
    out = EXPORT_DIR or os.path.join(_this_dir, "exports")
    print("exported:", u.export_stl_per_object(out, [fused]))
    if not KEEP_PRINT_COPY:
        u.delete_object(fused)


# ---------------------------------------------------------------- KEEP: scene setup + run
u.setup_units_mm()
if MODE == "build":
    u.use_collection(COLL_NAME, clear=True)
    parts = build_parts()
    if LAYOUT == "print":
        place_for_print(parts)
    elif LAYOUT != "assembled":
        raise ValueError(f"LAYOUT must be 'print' or 'assembled', not {LAYOUT!r}")
    bpy.data.collections[PART_COLL]["layout"] = LAYOUT      # export mode reads this
    if HIDE_OTHER_COLLECTIONS:
        u.show_only_collection(COLL_NAME)
    u.frame_all()                                           # no-op headless
    print({"status": "ok", "mode": MODE, "layout": LAYOUT, "collection": COLL_NAME,
           "objects": sorted(o.name for o in parts)})
    u.print_report(parts, overhang_deg=45)
elif MODE == "export":
    export_current()
else:
    raise ValueError(f"MODE must be 'build' or 'export', not {MODE!r}")
