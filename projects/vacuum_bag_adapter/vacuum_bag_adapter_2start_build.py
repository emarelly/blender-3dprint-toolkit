"""
Vacuum bag adapter, TWO-START thread -- Blender build script
(generated from vacuum_bag_adapter_2start_description.md).

The same adapter as vacuum_bag_adapter_build.py, but its socket thread matches the bag valve's real
thread: two interlaced threads starting 180 deg apart, 1.0 mm between neighbouring ridges (each thread
advances 2.0 mm per turn), same diameters (root 26.6 / crest 24.4), round, right-hand.

This script RUNS vacuum_bag_adapter_build.py with the OVERRIDES below, so every other dimension, the fit
check against the dummy valve (also two-start here) and the report come from the main script. Keep both
scripts in one folder. Run in Blender (Scripting > Open > Run Script; Text > Reload if you edited
either file), or
    python run_blender.py projects/vacuum_bag_adapter/vacuum_bag_adapter_2start_build.py
"""

import os

MAIN_SCRIPT = "vacuum_bag_adapter_build.py"

OVERRIDES = dict(
    COLL_NAME="VacuumBagAdapter_2Start",
    OBJ_NAME="VBA2S_Adapter",
    THREAD_PITCH=1.0,          # axial distance between neighbouring ridges
    THREAD_STARTS=2,           # two threads, 180 deg apart -> lead 2.0 per turn
    # EXPORT=True,             # uncomment to write VBA2S_Adapter.stl into exports/
)


def _main_path():
    """The main script's path: next to this file, or (Blender text editor, where __file__ is only the
    text's name) next to any open text / the .blend / the current directory."""
    import bpy
    try:
        me = __file__
    except NameError:
        me = ""
    dirs = [os.path.dirname(os.path.abspath(me))] if me and os.path.isfile(os.path.abspath(me)) else []
    dirs += [os.path.dirname(bpy.path.abspath(t.filepath)) for t in bpy.data.texts if t.filepath]
    if bpy.data.filepath:
        dirs.append(os.path.dirname(bpy.data.filepath))
    dirs.append(os.getcwd())
    for d in dirs:
        p = os.path.join(d, MAIN_SCRIPT)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(f"{MAIN_SCRIPT} must be in the same folder as this script")


_path = _main_path()
_ns = {"__name__": "__main__", "__file__": _path, "OVERRIDES": OVERRIDES}
exec(compile(open(_path, encoding="utf-8").read(), _path, "exec"), _ns)
