# blender-3dprint-toolkit

**3D printing as code.** Design 3D-printable parts as Python scripts for Blender, starting from a written spec, and check every build automatically before it goes to the slicer.

I wrote about the idea and how this repo came about on LinkedIn: **[3D printing as code](https://lnkd.in/p/dm92iRCH)**.

---

## The idea: 3D printing as code

Most 3D-printable parts are drawn by hand in a CAD tool. That works until you need a version with a 2 mm wider cavity, an M4 screw instead of M3, or a lid for a slightly different phone. Then you are editing geometry by hand again, and nothing tells you whether you broke something.

This repo treats a printable part the way software treats a program:

| Software | 3D printing as code |
|---|---|
| Requirements | **A spec** (`<name>_description.md`): every dimension, position, tolerance and design decision, written down, with no "approximately" |
| Source code | **A build script** (`<name>_build.py`): Blender Python that builds the model from the spec. All numbers sit in a SETTINGS block at the top |
| Library | **`utils_3d.py`**: reusable building blocks (hollow boxes, screw bosses, snap hooks, vents, text, print and fit checks, export…) |
| Build | `run_blender.py` runs the script in Blender with no UI, from a normal terminal |
| Tests | Checks for watertight meshes, wall thickness, overhangs, bed fit, STL integrity, and fit and motion checks (does the lid close, does the hinge swing, does the phone fit) |
| Version control | Git. A design change is a reviewable diff of a few numbers, not a new binary file |

What you get from this:
- **Parametric by default.** Change `WALL = 2.4` to `2.0`, run the script again, and you have the new model.
- **Reproducible.** The script *is* the model. `.blend` and `.stl` files are outputs you can regenerate at any time.
- **Verified before printing.** Every build reports open edges, non-manifold edges, thin walls and overlaps, so problems show up before you waste filament.
- **Works well with AI.** A spec plus a script is something an AI assistant can read, write and check. This repo includes a [Claude Code](https://claude.com/claude-code) skill that turns a rough description into a full spec and a verified build script (see below).

## What's in the repo

```
blender-3dprint-toolkit/
├── utils_3d.py            # the shared helper library (import it from any build script)
├── run_blender.py         # runs a script in Blender headless, from a normal terminal
├── CLAUDE.md              # project notes for Claude Code (conventions, verification steps, gotchas)
├── .claude/skills/blender-model-spec/   # Claude Code skill: description -> spec -> build script -> verification
│   └── reference/         # build template, spec template, checklist, verify_model.py, check_stl.py
└── projects/              # one folder per design
    ├── rc_remote_case/    # two-part RC remote enclosure (several generations of build scripts)
    ├── s24plus_phone_box/ # Samsung S24+ storage/charging box with a snap-in hinge and snap hooks
    └── g9_dome_adapter/   # lamp adapter: M10x1 pipe to a G9 glass globe, with a sealed dome cover
```

### Example projects

| Project | What it shows |
|---|---|
| [`projects/s24plus_phone_box`](projects/s24plus_phone_box) | Made end to end with the skill. A box and a door with a snap-in stub-pin hinge (no separate pin), six snap hooks, phone ribs, a cable slot, honeycomb vents and an engraved label. The build checks that the door closes, the hinge swings, the latch holds and the phone fits at every extreme position. Also contains a **hinge test coupon** that loads its settings from the main script, and a **separate-parts build** (every feature its own mesh, for editing by hand in Blender, with an export mode that fuses them back into printable parts). |
| [`projects/rc_remote_case`](projects/rc_remote_case) | A two-part RC remote case, built several ways: the original standalone scripts, a version refactored onto `utils_3d`, M4 screw variants and fully rounded shells. Its [README](projects/rc_remote_case/README.md) documents every file and lists the `utils_3d` functions. |
| [`projects/g9_dome_adapter`](projects/g9_dome_adapter) | Made with the skill. A one-piece outdoor-lamp adapter: a spigot that screws into a glass globe's G9 thread and carries a printed M10×1 pipe thread inside, plus a Ø60 dome that covers the globe's cut top and seals it with an O-ring. Two printed threads and a lathed dome, built **without a single Boolean cut** (`make_threaded_tube`, `make_revolved_ring`), an export mode that fuses the features into one STL, and a [section sketch](projects/g9_dome_adapter/g9_dome_adapter_sketch.html) drawn from the same values. It went through a real test print: the first print revealed the flat and the O-ring had to shrink, and that change was two numbers in the SETTINGS block. |

## Requirements

- **Blender** (tested with Blender 5.1). The scripts use Blender's own Python (`bpy`), so they run *inside* Blender, not in a regular Python.
- **Python 3** on your system, only to run `run_blender.py` (the headless launcher).
- Optional: **[Claude Code](https://claude.com/claude-code)** for the AI-assisted workflow.

## Quick start

### Run an existing design headless

From the repo root:

```bash
python run_blender.py projects/s24plus_phone_box/s24plus_phone_box_build.py
```

`run_blender.py` finds `blender.exe` by itself (Program Files on Windows, `/Applications` on macOS, `/usr/bin` on Linux). If it can't find it, pass `--blender <path>` or set `BLENDER_EXE`. Anything after `--` is passed on to the script.

The output ends with a report like this:

```
[OK ] S24P_Box    dims=(97.1, 199.8, 20.0) vol=65304.4 mm3 open_edges=0 nonmanifold=0 mods=0 ...
```

To write STL files, set `EXPORT = True` in the script's SETTINGS block. The STLs go into an `exports/` folder next to the script.

### Run it inside Blender (to see the model)

1. Open Blender, go to the **Scripting** workspace.
2. **Text → Open**, choose the build script, then **Run Script**.
3. The model appears in its own collection; other collections are hidden so builds don't overlap.

After you edit a script on disk, use **Text → Reload** before running it again. Blender keeps its own copy of the text, so otherwise you run the old version.

### Change a design

Open the build script, edit a value in the `SETTINGS` block (for example `WALL`, `CORNER_R`, `CLEAR_XY`), and run it again. If the design has a spec, update the spec as well so the two stay in sync.

## Writing your own design with `utils_3d`

```python
import sys
sys.path.insert(0, r"C:\path\to\blender-3dprint-toolkit")   # folder that contains utils_3d.py
import utils_3d as u

u.setup_units_mm()                                   # 1 Blender unit = 1 mm
u.use_collection("Demo_Box", clear=True)             # every new object goes here

# 60 x 40 x 25 mm tray, 2 mm walls, open top, rounded corners
box = u.make_hollow_box("Demo_Box_Body", -30, 30, -20, 20, 0, 25, wall=2.0, open_face="+Z",
                        bevel=[(5, 'VERTICAL', 8), (1.5, 'BOTTOM', 4)],
                        inner_radius=[(3, 'VERTICAL', 8)])
u.cut_hex_vents(box, 5, 3, 4.0, -1, 3, center=(0, 0))          # honeycomb vents in the floor
u.engrave_text(box, "v1", 0, -14, 2.0, size=4, depth=0.6)      # label on the inside floor
lid = u.make_lid_lip("Demo_Box_Lip", -27.75, 27.75, -17.75, 17.75, 25, 28, lip_t=1.2, corner_r=2.75)

u.print_report()                                     # watertight? modifiers left? size, volume
# u.export_stl_per_object("exports")                 # one STL per object
```

Round parts and printed threads are built directly from rings, with no Boolean cuts:

```python
# washer with a groove underneath: draw the groove into the profile instead of cutting it
washer = u.make_revolved_ring("Washer", [(5, 0), (8, 0), (8, 1), (9, 1), (9, 0), (12, 0), (12, 3), (5, 3)])

# 15 mm tube: G9 lamp-shade thread outside (fading in at the tip), M10x1 nut thread inside up to z = 0,
# then a plain dia 12.4 bore
spigot = u.make_threaded_tube("Spigot", -15, 1.05,
    outer=dict(u.thread_spec("G9_shade", clearance=0.1), leadin=2.0),
    inner=[dict(u.thread_spec("M10x1", internal=True), z1=0.0), dict(r=6.2)])
```

Conventions the library follows:
- **Millimetres everywhere**; Z = 0 is the print bed.
- **Primitives are built with `bmesh`**, origin at the geometric centre.
- **Every Boolean and bevel is applied immediately.** Each object ends with zero modifiers, so what you see is what gets exported.
- **Typical values, not verified data.** Screw/insert sizes (`SCREWS`), thread sizes (`thread_spec`, `THREADS`) and fit tolerances (`TOL_PRESS`, `TOL_SNUG`, `TOL_SLIDE`, `TOL_LOOSE`) are common starting points. Print a test piece and adjust them for your printer.

The library covers primitives (including revolved rings), edge rounding, Booleans, enclosure features (hollow boxes, bosses, lid lips, finger notches), screws/inserts/nut traps/magnets, printed threads (ISO metric and lamp-shade), snap hooks, vents, text, layout helpers, transforms, print-quality checks (manifold, min wall, overhang, bed fit, overlaps, pose sweeps for hinges and lids) and export (STL clean-up, STL, 3MF, `.blend`). The full function list is in the [RC case README](projects/rc_remote_case/README.md#utils_3dpy--reusable-helper-library), and every function has a docstring.

Build scripts in a project folder find `utils_3d.py` on their own: they check `UTILS_DIR` at the top of the script, then the `UTILS_3D_DIR` environment variable, then the script's folder and every parent folder. A project inside `projects/` needs no setup.

## The AI-assisted workflow (Claude Code skill)

The skill [`blender-model-spec`](.claude/skills/blender-model-spec/SKILL.md) turns a rough description into a finished, verified design. Open this repo in Claude Code and type:

```
/blender-model-spec a wall-mounted holder for two AA battery packs with a snap-on lid
```

What happens:

1. **Interview.** Claude asks questions until every dimension and decision is settled: size, parts, fastening, openings, tolerances, rounding, printer and bed. It never fills in a value silently. You can also say "you decide" for any item, and that is recorded in the spec. It always asks two structural questions:
   - **One mesh per printed part, or every feature as its own mesh** (so you can still adjust ribs, hooks or bosses by hand in Blender afterwards).
   - **Ready for print or assembled** as the starting layout. Both layouts are always in the script, one `LAYOUT` setting apart.
2. **Final summary.** A table of every parameter and where it came from. Nothing is generated until you confirm.
3. **Spec + script.** It writes `projects/<name>/<name>_description.md` and `projects/<name>/<name>_build.py` from the templates.
4. **Verification.** It builds headless, checks that the object list matches the spec, checks that every mesh is watertight, exports the STLs and checks them, runs any fit and motion checks, and fixes the spec and the script together until everything passes.

## How designs are verified

Run these after any geometry change, and always before printing:

1. **Build + topology.** Run the build and read the report: every object must show `open_edges=0 nonmanifold=0 mods=0`. For projects made with the skill:
   ```bash
   python run_blender.py .claude/skills/blender-model-spec/reference/verify_model.py -- <build.py> <description.md>
   ```
2. **STL integrity.** Export the parts and run
   ```bash
   python .claude/skills/blender-model-spec/reference/check_stl.py <files>.stl
   ```
   Every file must show `mismatched_edges=0` and the same volume as in Blender. Blender can report a mesh as watertight while the exported STL still has unpaired edges, so this check is the one that counts.
3. **Fit and motion.** Designs with moving or mating parts check them in the build itself, by measuring overlap at several poses (`overlap_at_offsets`, `overlap_at_rotations`): lid closed, hinge swing, latch lift, contents at their extreme positions.
4. **Visual.** Look at the model in Blender, or render it headless, and compare it against the spec.

## Tips and gotchas

- **Text → Reload** in Blender after editing a script on disk, or you run the old copy.
- **Only one `utils_3d.py`.** If you keep an older copy somewhere else, the scripts still load the one next to them, but delete old copies anyway to avoid confusion.
- **Exact Booleans fail on touching geometry.** Two shapes that only touch along a line, or share a face or vertex exactly, can leave open edges. Overlap them properly or offset them by 0.2–0.3 mm.
- **Don't cut round parts.** A Boolean cut on a lathed mesh lands on the lathe's own edges and leaves open edges. Draw bores, grooves and recesses into a `make_revolved_ring` profile, and build threads with `make_threaded_tube`.
- **Watertight in Blender is not a clean STL.** A union can leave vertices a hair apart that become one point in the STL. `fuse_copies` cleans them by default (`clean_for_stl`); call `clean_for_stl` yourself before exporting any other Boolean result, and always run `check_stl.py`.
- **Tapering tips read as thin walls.** The min-wall check is an estimate; the sharp tip of a snap hook reads as ~0.2 mm by nature. The specs note such expected readings.
- **`.stl`, `.3mf` and `exports/` are git-ignored.** They are build outputs; regenerate them from the scripts.

## Author

Created by [emarelly](https://github.com/emarelly). Read more about the approach in the [LinkedIn post](https://lnkd.in/p/dm92iRCH).
