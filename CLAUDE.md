# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Blender (`bpy`) Python tooling for 3D-printable models, in millimetres. Layout:

- **Library root (this folder):** `utils_3d.py` (shared helper library), `run_blender.py` (headless launcher), `CLAUDE.md`, and `.claude/skills/blender-model-spec/` (skill: interview → `<name>_description.md` spec + `<name>_build.py` + headless verification via `reference/verify_model.py`).
- **`projects/`** holds one folder per project, each containing only that project's files:
  - `projects/rc_remote_case/`: a two-part RC remote case (Lower + Upper half). `rc_case_modifier_mesh_prompt_v1_3.md` is the **spec** (every dimension, bore convention, resolved ambiguities), the scripts are its executable form, and its `README.md` documents each file for the user.
  - `projects/s24plus_phone_box/`: Samsung S24+ storage/charging box (made with the skill). `s24plus_phone_box_description.md` (spec, v1.2) + `s24plus_phone_box_build.py` (box + door with snap-in stub-pin hinge, six snap hooks, built-in assembly checks); `s24plus_hinge_test_*` is a hinge test coupon that **loads the main script's SETTINGS + helpers sections at run time** (do not duplicate hinge values into it; keep the `# === SETTINGS` / `# === KEEP: scene setup` markers in the main script intact). `s24plus_phone_box_parts_build.py` loads the same sections and builds the box as separate part meshes (closed pose, cuts applied per part) for manual editing; its `export` mode fuses the current parts with `fuse_copies` and writes the STLs.
  - `projects/g9_dome_adapter/`: one-piece outdoor-lamp adapter (made with the skill): M10×1 pipe → G9 glass-shade thread spigot + Ø60 dome cover with an O-ring face seal. `g9_dome_adapter_description.md` (spec) + `g9_dome_adapter_build.py` (two feature meshes, `MODE` build/export, `LAYOUT`); built entirely without Booleans (`make_revolved_ring` + `make_threaded_tube`). `g9_dome_adapter_sketch.html` is an older concept sketch, not kept in sync.

`utils_3d.py` is deliberately **not** copied into projects. No git repo, no test suite, no linter, no build step.

## Running / verifying

Scripts need Blender's `bpy`, so plain `python x.py` fails except for `run_blender.py`. Blender 5.1 is installed at `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`.

```
python run_blender.py projects/rc_remote_case/rc_case_build_m4_rounded.py   # headless run from the library root (finds blender.exe itself; --blender / BLENDER_EXE override)
python run_blender.py my_test.py -- extra args              # anything after -- goes to the script
python -m py_compile utils_3d.py                            # quick syntax check without Blender
```

Verification, after any geometry change and always before telling the user a model is ready to print:

1. **Build + topology:** run the build (headless) and read `utils_3d.print_report()` / `check_manifold()`; every object should have 0 open edges, 0 non-manifold edges, 0 modifiers. For skill-made projects, `python run_blender.py .claude/skills/blender-model-spec/reference/verify_model.py -- <build.py> <description.md>` does this plus checks the object list against the spec.
2. **STL integrity (required):** export the parts (`u.export_stl_per_object(<tmp dir>, objs)` from a throwaway script in the scratchpad, or the build's `EXPORT = True` into a temp copy) and run
   ```
   python .claude/skills/blender-model-spec/reference/check_stl.py <tmp dir>/*.stl
   ```
   Pass = `mismatched_edges=0` on every file and a volume equal to Blender's for that object. A handful of `zero_area_tris` is harmless. This is the ground truth: Blender's edge-based check can report a mesh as watertight while the exported STL still has unpaired edges (it happened twice in the phone box: hinge block touching the barrel's lowest vertex, coplanar niche/groove floors). Delete the test STLs afterwards unless the user asked for them.
3. **Fit / motion:** builds with moving or mating parts carry their own checks (`ASSEMBLY_CHECK` in the phone box: closed overlap, dummy phone at nominal and extreme positions, hinge swing, latch lift, drop-in) — all overlaps must read as designed.
4. **Visual:** headless Workbench renders (or the live Blender screenshot tool) to compare against the spec.

For quick regression checks, compare per-object volume + bounding box between two builds (the utils refactor was verified identical to the original this way). Throwaway scripts go in the scratchpad, not the repo.

## Architecture

Two generations of build scripts in `projects/rc_remote_case/` that share no code:

- **Standalone, helpers copy-pasted** (original): `rc_case_build_final.py` (one-shot, 24 objects) and `step1_…step8_*.py` (same build split into 8 stages that must run in order in one Blender session; each embeds its own ~60-line helper block). File numbering does **not** match the spec's step numbers (step3 file = spec "Step 2b", step4 = spec Step 3, etc.).
- **`utils_3d.py`-based** (current): `rc_case_build_final_utils.py` (identical output to the original, with `FLIP_UPPER`), `rc_case_build_m4.py` (screws driven by `SCREW`/`LOWER_KIND`, see below), `rc_case_build_m4_rounded.py` (M4 + fully rounded shells). New designs should import `utils_3d`, not copy helpers.

`utils_3d.py` is a reusable bmesh/bpy library (primitives, modifier wrappers, enclosure/screw/snap/text features, layout helpers, transforms, print checks, STL/3MF/.blend export). Key conventions to keep:
- Everything is mm; `setup_units_mm()` sets scene units so 1 BU = 1 mm.
- Primitives are built with `bmesh` (no `bpy.ops`, no selection), origin at the geometric centre. Modifier application (`apply_modifier`, `boolean_*`) does use `bpy.ops` and needs the object active.
- `use_collection(name, clear=True)` sets a module-global default collection that all `make_*` functions link to.
- Every Boolean/Bevel is applied immediately, so each object ends with zero modifiers; cutters are deleted after use.
- Bore convention (spec, item 5): `make_boss(bore='blind')` = closed at base, open top (0.5 mm overshoot); `'through'` = open both ends.
- `round_edges(obj, r, where)` fillets selected edges directly on the mesh with `bmesh.ops.bevel`; use it on a plain box *before* cutting. `apply_bevel` is the modifier version (all edges / chamfer). `round_edges_multi` / list-valued `bevel`/`inner_radius` in `make_hollow_box` apply several radii in order.
- Round parts: draw bores, grooves and recesses into a `make_revolved_ring` profile (closed (r, z) polygon off the axis) instead of cutting them; printed threads come from `make_threaded_tube` (sections: plain radius or thread dict, `thread_spec('M10x1', internal=True)` / `THREADS`), also Boolean-free. `fuse_copies` runs `clean_for_stl` on its result by default (merge near-duplicate vertices + triangulate), which is what makes fused Boolean results pass `check_stl.py`.
- Build scripts end with `u.show_only_collection(COLL_NAME)` + `u.frame_all()` (not a copied `_walk` loop), use `u.script_dir(<file name>)` for their own folder, and run motion/fit checks with `overlap_at_offsets` / `overlap_at_rotations`.

Model structure (RC case scripts): each shell is one mesh made from a box → bevel/round → Boolean cavity → Boolean hole cuts. In the RC case, bosses, posts, rails, PCB supports, button collars and the 4 corner joint posts are separate objects (never unioned) — that is the RC spec's convention, not a library rule. The phone box deliberately fuses its ribs, stops, hinge knuckles and hooks into the two shells (one printable mesh per part). Each project's spec decides. The Upper group is shifted ΔX = −80 mm, then optionally flipped 180° about X (the flip is **not** in the v1.3 spec, which says "no flips"; it also mirrors Y, so Upper's wire notch ends up at +Y while Lower's is at −Y). The wire hole is one full cylinder centred on each half's own open edge, so each shell keeps a half-notch.

M4 variants: only the screw features change (bosses sized from `SCREWS`, ceiling access holes sized to the screw head). Mounting posts, corner posts, supports, collars and the wire hole stay as in the spec.

## Gotchas

- Scripts import `utils_3d` via a `_find_utils_dir()` block that checks `UTILS_DIR` (setting at the top of the script), the `UTILS_3D_DIR` environment variable, then the script's folder **and every parent folder** (also Blender text-editor file paths, the .blend folder, cwd). Parent-walking is what lets a project subfolder find the library root; in Blender's text editor `__file__` is only the bare script name, hence the text-editor paths. A project placed outside the library root needs `UTILS_DIR` or `UTILS_3D_DIR`. The same block is in `reference/build_template.py` of the skill — change them together.
- Blender's text editor caches script text: after editing a file on disk the user must use Text → Reload before re-running, or they run a stale copy (this has caused "I don't see the change" reports).
- The M4 scripts rename every object with a suffix (`_M4`, `_M4R`) and hide all other collections, because builds overlap at the same coordinates. Re-running replaces the same-named collection; objects colliding with names in other collections get Blender's `_M` suffix from `unique_name`.
- `utils_3d` analysis helpers (`min_wall_thickness`, `overhang_report`, `orient_flat_face_down`, `export_3mf`) work from `_world_tris()` (Blender's own loop-triangle tessellation) and `_world_bmesh()` refreshes normals after the world transform. `bmesh.ops.triangulate` on world-space bmeshes with stale normals produced overlapping flipped triangles and bogus overhang/min-wall numbers — don't reintroduce it. These checks are estimates (a tapering tip reads as a thin wall); for ground truth export STLs and run `.claude/skills/blender-model-spec/reference/check_stl.py`.
- Exact-solver Booleans break (open/non-manifold edges, zero-area slivers) when operands touch tangentially or share a vertex/plane exactly; offset by 0.2–0.3 mm. See the skill's "Geometry pitfalls".
- Step files 6–8 look objects up by exact name (`RC_Case_Lower`, …) and will break if names were suffixed.
- `utils_3d` values in `SCREWS` / `TOL_*` are typical starting points, not verified hardware data.
- **Live Blender (MCP):** Blender Lab's MCP server is registered for Claude Code as `blender` (local scope for this folder) via `.claude/blender_mcp_launcher.py`, which runs the copy Claude Desktop installed (its own `blender-mcp.exe` fails outside the Desktop app container with "Failed to canonicalize script path"). Tools include `execute_blender_code` (assign a dict to `result` to return data), object/scene summaries and viewport screenshots. The Blender add-on accepts **one client at a time**: Claude Desktop's Blender connection must be closed, and the add-on started in Blender (N-panel). If the tools are not loaded in the current session, a session restart is needed; until then the server can be driven with a small stdio MCP client. Running a build script in the live scene replaces that script's collection and hides others — fine when the user asked for it, otherwise prefer read-only calls. If Claude Desktop updates the extension, the paths in the launcher may need adjusting.
