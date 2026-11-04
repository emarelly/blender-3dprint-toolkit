# RC Remote Control Case — Blender build scripts

A parametric, 3D-printable two-part remote-control case (Lower + Upper half), generated entirely by Python
scripts for **Blender** (tested on Blender 5.1). All dimensions are in **millimetres**.

The design is specified in `rc_case_modifier_mesh_prompt_v1_3.md`; the scripts are the executable form of that spec.

## What is in this folder

| File | What it is | When to use it |
|---|---|---|
| `rc_case_modifier_mesh_prompt_v1_3.md` | The **specification** (as-built v1.3): every dimension, position, bore convention, and the list of ambiguities that were resolved. | When you want to know *what* the model should be, change a dimension, or re-generate the scripts with an AI. Edit the spec first, then update the scripts. |
| `rc_case_build_final.py` | **One-shot build.** Builds the complete model (24 objects) in a single run. | **Normal use.** Open in Blender → Run. This is the file to use unless you are debugging. |
| `step1_lower_shell.py` … `step8_flip_upper.py` | The same build **split into 8 stages**, each runnable on its own, each printing a status dict. | Learning how the model is built, debugging one stage, or rebuilding only part of it. Must be run **in order** (see below). |
| `rc_case_build_final_utils.py` | **Same model as `rc_case_build_final.py`, refactored** to use `utils_3d` (122 vs 304 lines; verified identical output). Has a `FLIP_UPPER` switch. | Preferred starting point if you want to modify the design. Needs `utils_3d.py` (see "Where the shared files live"). |
| `rc_case_build_m4.py` | The same case with the screw positions sized for **M4** (or M2/M2.5/M3/M5 via `SCREW`); optional heat-set inserts via `LOWER_KIND`. Objects end in `_M4`, a raised "M4" label is added inside Lower, other collections are hidden. | When you build the case for M4 screws. |
| `rc_case_build_m4_rounded.py` | M4 build with **rounded shells** (corner, edge, seam and inside-cavity radii set in the settings block). Objects end in `_M4R`. | The soft-edged version for printing. |
| `../../utils_3d.py` | **Reusable helper library** (lives two folders up in the library root, shared by all projects): the common functions from the scripts plus generic helpers, print-quality checks, screw/insert tables, snap fits, text, and STL / 3MF / .blend export. | Starting any *new* design. Not run directly — you `import` it. |
| `../../run_blender.py` | Plain-Python launcher that runs any Blender script headless (finds `blender.exe` itself). | Building/exporting from a terminal without opening Blender: `python ../../run_blender.py rc_case_build_m4.py` |

### Where the shared files live
This folder holds only the RC case project. The shared `utils_3d.py` and `run_blender.py` sit in the library root, two folders up (this project is in `projects/`). The `rc_case_build_final_utils.py`, `rc_case_build_m4.py` and `rc_case_build_m4_rounded.py` scripts find `utils_3d.py` themselves, searching in this order: the `UTILS_DIR` setting at the top of the script, the `UTILS_3D_DIR` environment variable, then the script's folder and every parent folder (so it is found two levels up). If you move a project somewhere that is not under the folder containing `utils_3d.py`, set `UTILS_DIR` or the environment variable. The original `rc_case_build_final.py` and `step1…step8` files are standalone and need nothing.
| `README.md` | This file. | — |

### The 8 step files

Run in numeric order, in the same Blender session. Step 1 wipes and recreates the `RC_Remote_Case_Modifier` collection; the others raise an error if their prerequisites are missing.

| Step file | Builds | Spec section |
|---|---|---|
| `step1_lower_shell.py` | `RC_Case_Lower`: bevelled 57.5 × 175 × 15 box, cavity cut (2.5 mm walls/floor) | Step 1 |
| `step2_lower_secondary.py` | 2 screw bosses, 2 mounting posts, 2 guide rails (separate objects) | Step 2 |
| `step3_corner_posts.py` | 4 solid 2×2 mm corner joint posts, Z 0–19 | Step 2b |
| `step4_upper_shell.py` | `RC_Case_Upper`: same footprint, 6 button holes, 2 screw-access holes | Step 3 |
| `step5_upper_secondary.py` | 2 screw bosses, 4 PCB supports, 6 button collars | Step 4 |
| `step6_wire_hole.py` | ⌀9.7 mm cable hole split across the seam (a half-round notch in each shell) | Wire-entry hole |
| `step7_final_placement.py` | Shifts the Upper group by ΔX = −80 mm so the halves sit side by side | Step 5 |
| `step8_flip_upper.py` | Turns the Upper group 180° about X so it lies open-side-up like Lower | *not in the spec* |

## How to run

**Option A – inside Blender (easiest):** open Blender → *Scripting* workspace → *Open* → pick `rc_case_build_final.py` → *Run Script* (▶). The model appears in a collection named `RC_Remote_Case_Modifier`.

**Option B – command line, no UI:**
```
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python rc_case_build_final.py
```

**Option C – step by step:** run `step1…` through `step8…` in order, each via *Run Script*, and rotate the viewport between steps to see what each one added.

### How the model is built (the technique)
1. Each shell is **one mesh** made from a single box: **Bevel** modifier (0.6 mm, 4 segments) → **Boolean Difference** cuts for the cavity, button holes, screw holes and wire notch. Every modifier is **applied**, so each shell has zero modifiers left.
2. Bosses, posts, rails, supports, collars and corner posts stay **separate objects** (not fused to the shell).
3. Bores follow one convention: Lower bosses/posts and Upper PCB supports are **blind at the base, open at the top**; Upper bosses and button collars are **through-holes** (this was an engineering assumption — see spec, item 5).

## Things to know (issues I noticed while reviewing)

1. **The one-shot script and the spec disagree about the flip.** Spec v1.3 says "no flips or rotations anywhere", but `rc_case_build_final.py` (and `step8`) *does* flip Upper. The finished model therefore matches the spec **plus** step 8. If you want the spec's un-flipped result, delete the "STEP 6 — Flip" block at the end of `rc_case_build_final.py` (or skip `step8`).
2. **The flip is about the X axis, which mirrors Y.** After it, Upper's wire-hole notch is at the **+Y** end while Lower's is at **−Y**, and the button layout is mirrored end-for-end. When you physically close a case you turn Upper over about its *long (Y)* axis, which would keep Y and mirror X instead. If the flipped Upper is meant to show how the halves meet, you probably want `flip_objects(..., axis='Y')` (in `utils_3d.py`) rather than X. Worth confirming which you intended.
3. **Numbering is inconsistent.** Step file docstrings say "STEP n of 7", but there are 8 files, and the file numbers don't match the spec's section numbers (table above maps them). The `rc_case_build_final.py` header still says "v1.2 build".
4. **Step files 6–8 look objects up by exact name** (`RC_Case_Lower`, …). If a name had to be suffixed `_M` (the `unique_name` collision handling), those steps fail or hit the wrong object.
5. **Button collar bore (7.0 mm) equals the button hole radius (7.0 mm)**, but the spec says it "clears the 6 mm hole with margin" — the comment is stale; the geometry itself is consistent.
6. **All step files copy-paste the same helper functions** (~60 lines each). That duplication is what `utils_3d.py` removes.

Verification I ran: `rc_case_build_final.py` in Blender 5.1 produces **24 objects, every one watertight (0 open edges, 0 non-manifold edges) with 0 leftover modifiers**; Lower is 57.5 × 175 × 15 mm, Upper 57.5 × 175 × 14 mm.

---

## `utils_3d.py` — reusable helper library

### Setup (any new Blender script)
```python
import sys, importlib
sys.path.append(r"<PATH_TO_FOLDER_CONTAINING_utils_3d.py>")   # e.g. r"C:\my_projects\blender_scripts"
import utils_3d as u
importlib.reload(u)            # only needed while you are editing utils_3d.py

u.setup_units_mm()                            # 1 Blender unit = 1 mm
u.use_collection("My_Design", clear=True)     # new objects land here; clear=True resets it

body = u.make_hollow_box("Body", -20, 20, -30, 30, 0, 15, wall=2, open_face="+Z", bevel=0.6)
boss = u.make_boss("Boss", 0, 0, 2, 12, outer_r=3, bore_r=1.6)          # blind pilot hole
u.cut_cylinders(body, [(0, 10), (0, -10)], radius=4, z_min=10, z_max=16)
u.print_report()                               # watertight / size / volume check
u.export_all(basename="my_design")             # .blend copy + combined STL + one STL per part
```
Primitives are built with `bmesh` (no selection or viewport needed), so they also work with `--background`.

### Functions carried over from the RC scripts
`setup_units_mm`, `unique_name`, `link_only`, `make_box`, `make_cylinder`, `apply_bevel`, `boolean_diff_apply`, `make_bore_cutter`, `make_wire_cutter`, and the translate/flip logic (`translate_objects`, `flip_objects`). Same names and argument order where possible; improvements: boxes/cylinders no longer need `transform_apply`, cutters free their mesh data, and `make_wire_cutter` takes its radius/position as arguments.

### New generic functions

| Group | Functions | Typical 3D-printing use |
|---|---|---|
| **Primitives** | `make_box_centered`, `make_cone`, `make_cylinder_between` / `make_frustum_between` (any direction), `make_slot` (round-ended slot), `stadium_profile` (slot outline as 2D points), `make_prism` (extrude any 2D profile along X, Y or Z; `make_prism_xz` = along Y), `make_revolved` (lathe any profile). `make_box` accepts each min/max pair in either order | Cutters in any orientation, slots (also through side walls), custom turned shapes |
| **Modifiers** | `boolean_apply`, `boolean_union_apply`, `boolean_intersect_apply`, `apply_array`, `apply_solidify`, `apply_all_modifiers` | Fuse parts into one solid, repeat features, thicken a surface |
| **Edge rounding** | `round_edges(obj, r, where)` — `where` = `'ALL'`, `'VERTICAL'`, `'HORIZONTAL'`, `'TOP'`, `'BOTTOM'`, `'X'`/`'Y'`/`'Z'`, or your own `f(v0, v1)`; `round_edges_multi(obj, [(r, where, segments), ...])` (a different radius per edge set); `make_rounded_box` (radius or list); `apply_bevel` (all edges / chamfer) | Rounded corners only in plan view, softened top rim, chamfers (`segments=1`) |
| **Enclosure features** | `make_hollow_box` (open face, wall/floor thickness, outer rounding `bevel`/`bevel_edges`, inner cavity fillet `inner_radius`; both also take a `round_edges_multi` list), `make_boss` (blind / through / solid), `add_pcb_supports`, `make_lid_lip` (optional rounded corners `corner_r`), `cut_finger_notch` / `chord_radius` | Boxes, lids, screw posts, board standoffs, finger scoops |
| **Cuts** | `cut_cylinders`, `cut_boxes`, `cut_slots`, `make_countersink_cutter`, `make_counterbore_cutter`, `cut_vent_slots`, `cut_hex_vents` (honeycomb) | Buttons, USB/switch openings, display windows, ventilation, flat- and socket-head screws |
| **Screws, inserts, nuts, magnets** | `SCREWS` table (M2–M5), `screw_spec`, `make_screw_boss(screw='M3', kind='pilot'/'insert'/'clearance')`, `make_screw_hole_cutter(style='clearance'/'countersink'/'counterbore')`, `make_nut_trap_cutter` (optional slide-in slot), `make_magnet_pocket_cutter` | Sizes come from one table instead of magic numbers. Values are typical — verify against your hardware |
| **Tolerances** | `TOL_PRESS` 0.10, `TOL_SNUG` 0.15, `TOL_SLIDE` 0.25, `TOL_LOOSE` 0.40, `clearance(d, tol)` | Fit allowances for mating parts; print a test piece and tune |
| **Snap fits** | `make_snap_hook` (cantilever with ramp; `direction='+X'/'-X'/'+Y'/'-Y'`, `hanging=True` for a lid hook, `pointed=True` for a full-length ramp), `make_snap_catch_cutter` | Screw-free lid closure |
| **Text** | `make_text`, `engrave_text`, `emboss_text` (all take `rot_deg`) | Labels, version numbers on lids |
| **Parameters** | `Params` (dict with attribute access and `.report()`) | One block of dimensions at the top of a script |
| **Layout** | `grid_positions`, `linear_positions`, `polar_positions`, `mirror_positions` | Vent grids, button matrices, bolt circles, symmetric hole patterns |
| **Scene / viewport** | `setup_units_mm`, `use_collection`, `show_only_collection` (hide the other builds), `frame_all` | Keep overlapping builds apart in the viewport |
| **Transforms** | `translate_objects`, `rotate_objects`, `flip_objects`, `drop_to_bed`, `arrange_in_row`, `join_objects`, `duplicate_object`, `group_bbox` | Orient for printing, lay parts out on the plate |
| **Inspection / print checks** | `check_manifold`, `min_wall_thickness`, `overhang_report`, `check_bed_fit` (`BEDS` presets), `find_overlaps` / `overlap_volume`, `overlap_at_offsets` / `overlap_at_rotations` (lift, drop-in, hinge swing, dummy part at its extremes), `print_report(min_wall=, bed=, overhang_deg=)` | Catch open edges, thin walls, unsupported overhangs, too-big parts and colliding parts before slicing |
| **Print preparation** | `orient_flat_face_down` (largest flat face to the bed, reports overhang), `split_object` (cut a part in two, optional alignment pins + holes), `drop_to_bed`, `arrange_in_row` | Orientation and splitting oversized parts |
| **Export / save** | `export_stl`, `export_stl_per_object`, `export_3mf`, `save_blend`, `export_all(threemf=True)`, `default_output_dir`, `script_dir` (folder of the running script, also from Blender's text editor) | See below |

### Exporting STL and saving the Blender result
- `u.export_stl(r"C:\prints\case.stl", objs)` — one STL of the given objects (default: the active collection), in **mm**. Uses the new exporter on Blender 4.2+ and falls back to the old one automatically.
- `u.export_stl_per_object(r"C:\prints\parts", objs)` — one STL per object (usually what you slice).
- `u.save_blend()` re-saves the open file; `u.save_blend(r"C:\prints\case.blend", copy=True)` writes a copy.
- `u.export_3mf(r"C:\prints\case.3mf", objs)` — one multi-object 3MF in mm (parts stay separate in the slicer). Self-contained writer, no add-on needed.
- `u.export_all(out_dir, "case", threemf=True)` — does it all: `case.blend`, `case_all.stl`, `parts/*.stl` and (optionally) `case.3mf`. With no `out_dir` it writes to an `exports/` folder next to the saved `.blend` (or the current working folder if unsaved).

### Pre-print checklist
```python
u.print_report(min_wall=1.2, bed='prusa_mk4', overhang_deg=45)   # [BAD] = fix before slicing
u.find_overlaps(parts, ignore=lambda a, b: False)                # parts that collide
info = u.orient_flat_face_down(parts)                            # lay the biggest flat face on the bed
u.export_all(basename="my_design", threemf=True)
```
`min_wall_thickness` samples at face centres and `overhang_report` is geometric, so treat both as good estimates, not guarantees; the screw/insert and tolerance numbers are typical starting points to tune for your printer.

### Not done
- `step1…step8` still carry their own copies of the helpers and work standalone (only the one-shot build has a utils-based version).
- Not implemented: living-hinge strips.

### Running without opening Blender
```
python ../../run_blender.py rc_case_build_final_utils.py
```
(`--blender <path>` or the `BLENDER_EXE` environment variable if Blender is installed somewhere unusual.)
