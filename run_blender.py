"""
run_blender.py -- run a Blender Python script headless (no UI) from a normal terminal.

Plain Python (does NOT need bpy). Usage:

    python run_blender.py rc_case_build_final_utils.py
    python run_blender.py my_design.py --blender "C:\\path\\to\\blender.exe" -- arg1 arg2

Blender is located via, in order: --blender, the BLENDER_EXE environment variable,
`blender` on PATH, then the newest install under the usual Program Files / /Applications
/ /usr/bin locations. Anything after `--` is passed to your script (read it in Blender
with: sys.argv[sys.argv.index("--") + 1:]).

From Python:
    from run_blender import run_blender
    run_blender("my_design.py", args=["--size", "40"])
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys


def find_blender(explicit=None):
    """Return the path to the Blender executable or raise FileNotFoundError."""
    cands = [explicit, os.environ.get("BLENDER_EXE"), shutil.which("blender")]
    for pattern in (r"C:\Program Files\Blender Foundation\Blender*\blender.exe",
                    r"C:\Program Files (x86)\Blender Foundation\Blender*\blender.exe",
                    "/Applications/Blender.app/Contents/MacOS/Blender",
                    "/usr/bin/blender", "/snap/bin/blender"):
        cands += sorted(glob.glob(pattern), reverse=True)     # newest version first
    for c in cands:
        if c and os.path.isfile(c):
            return c
    raise FileNotFoundError("Blender not found: pass --blender, or set BLENDER_EXE")


def run_blender(script, args=(), blender=None, blend_file=None, factory_startup=True, check=True):
    """Run `script` inside headless Blender. Optionally open `blend_file` first.
    Returns the CompletedProcess (stdout/stderr go straight to your terminal)."""
    cmd = [find_blender(blender), "--background"]
    if factory_startup:
        cmd.append("--factory-startup")          # ignore user add-ons/prefs: reproducible
    if blend_file:
        cmd.append(blend_file)
    cmd += ["--python", os.path.abspath(script)]
    if args:
        cmd += ["--", *args]
    return subprocess.run(cmd, check=check)


if __name__ == "__main__":
    argv = sys.argv[1:]
    extra = []
    if "--" in argv:
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1:]
    p = argparse.ArgumentParser(description="Run a Blender script headless.")
    p.add_argument("script")
    p.add_argument("--blender", help="path to blender executable")
    p.add_argument("--blend", help=".blend file to open first")
    p.add_argument("--keep-prefs", action="store_true", help="do not use --factory-startup")
    a = p.parse_args(argv)
    try:
        run_blender(a.script, extra, a.blender, a.blend, not a.keep_prefs)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(str(e))
