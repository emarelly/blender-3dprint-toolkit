"""
verify_model.py -- check that a build script reproduces its description.

Run through run_blender.py (which lives in the library root next to utils_3d.py):

    python <root>/run_blender.py <skill>/reference/verify_model.py -- <build.py> <description.md>

It builds the model headless, then checks that
  1. the objects the build created (anything not already in the scene before it ran, so the
     startup Cube/Light/Camera are ignored) are exactly the backticked names in the spec's
     "## Final object list" section (none missing, none extra),
  2. every mesh is watertight (0 open edges, 0 non-manifold edges) with 0 modifiers.
Exit status is non-zero on any failure.
"""

import os
import re
import runpy
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 2:
    print("usage: ... verify_model.py -- <build.py> <description.md>")
    sys.exit(2)
build, md = (os.path.abspath(a) for a in args)

sys.path.insert(0, os.path.dirname(build))
preexisting = {o.name for o in bpy.data.objects}      # e.g. the startup Cube/Light/Camera
runpy.run_path(build, run_name="__main__")

import utils_3d as u      # same module the build used (found via the build's folder)

text = open(md, encoding="utf-8").read()
m = re.search(r"##\s+Final object list[^\n]*\n(.*?)(?:\n##\s|\Z)", text, re.S)   # skip the heading line itself
if not m:
    print("[FAIL] spec has no '## Final object list' section")
    sys.exit(1)
expected = set(re.findall(r"`([^`]+)`", m.group(1)))

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name not in preexisting]
actual = {o.name for o in meshes}
problems = []
for name in sorted(expected - actual):
    problems.append(f"missing object (in spec, not in scene): {name}")
for name in sorted(actual - expected):
    problems.append(f"extra object (in scene, not in spec): {name}")

for o in meshes:
    r = u.check_manifold(o)
    if not r["watertight"]:
        problems.append(f"{o.name}: not watertight (open={r['boundary_edges']}, nonmanifold={r['nonmanifold_edges']})")
    if r["modifiers"]:
        problems.append(f"{o.name}: {r['modifiers']} modifier(s) left unapplied")

print(f"VERIFY: spec lists {len(expected)} objects, scene has {len(actual)}")
if problems:
    for p in problems:
        print("[FAIL]", p)
    sys.exit(1)
print("VERIFY: OK")
