---
name: blender-model-spec
description: Turn a rough description of a 3D-printable object into a fully specified model. Interviews the user until every dimension and design choice is explicitly decided (no silent assumptions), then writes an object-description .md (the spec) and a Blender Python build script that uses utils_3d.py, and verifies the build headless. Use when the user wants to design a new object/case/enclosure/part for 3D printing in Blender, or says "create a model/script for ...".
argument-hint: "<object description>"
---

# Blender model spec + build script

Goal: from a short description, produce **two files** that agree with each other exactly, plus proof they build:

1. `<name>_description.md` — the spec (every number, position, name, decision)
2. `<name>_build.py` — a Blender script built on `utils_3d.py` that reproduces the spec

The user's description (if given with the command) is: `$ARGUMENTS`

**The rule that matters most: no internal assumptions.** Every value in the spec must be either stated by the user, chosen by the user from options you offered, or explicitly delegated ("you decide") and recorded as such. Never silently pick a default. Offering a default as a *recommended option in a question* is fine; applying one without asking is not.

## Phase 0 — Orient (silent, before the first question)

1. Locate `utils_3d.py` (Glob `**/utils_3d.py`) and `run_blender.py`. Their folder is the **library root** (`<root>`); it is normally *not* a project folder. If `utils_3d.py` is missing, tell the user and stop — do not re-implement helpers.
2. List its API: Grep `^def |^[A-Z_]+ = ` in `utils_3d.py`. Build only from functions that exist there (hollow boxes, bosses, screw tables, snap fits, vents, text, rounding, split/orient, export…). Read the docstring of any function you plan to use.
3. Read `reference/checklist.md` (this skill folder) — the list of decision areas to cover.
4. If a spec from an earlier object exists in the project (e.g. `rc_case_modifier_mesh_prompt_v1_3.md`), skim it for the house style only.

## Phase 1 — Interview until nothing is assumed

Keep an **assumption ledger** (in your head, and shown to the user at the gate): every decision area from the checklist, each marked `stated` / `decided` / `open`. Do not leave Phase 1 while anything is `open`.

- Start from what the user already said; mark those items `stated` (quote them).
- Ask with **AskUserQuestion**, 1–4 questions per call, 2–4 options each, the best-practice choice first and labelled "(Recommended)". Put the *numbers* in the options ("Wall 2.0 mm (Recommended)", "Wall 2.5 mm"), and use "Other" for free-form values.
- Ask the **highest-impact questions first** (overall size and parts split → fastening → openings and positions → fit/tolerances → rounding and finish → printing → naming/output) so later questions can build on earlier answers. Do not re-ask what is already answered; do not ask what can be derived (derive it, show it at the gate).
- **Two questions are always asked**, right after the parts split is known (checklist area 2), in one AskUserQuestion call:
  1. *Mesh structure* — "Should each printed part be one mesh, or should every feature be its own mesh so you can edit it by hand in Blender?" Options: **One mesh per printed part (Recommended)** (features fused in, ready to slice) / **Every feature its own mesh** (ribs, bosses, hooks, hinge knuckles… separate; cuts applied to every part they pass through; the script gets an export mode that fuses copies into one mesh per printed part for the STL) / **Only the major features separate** (follow up: which ones; the rest are fused into their part).
  2. *Scene layout* — "The script will contain both layouts, assembled and ready for print (one setting, `LAYOUT`). Which should it start with?" Options: **Ready for print (Recommended)** (parts side by side on the bed, each in its print orientation) / **Assembled** (parts in their assembled positions, to check how they fit). Tell the user that the other layout is always available by changing `LAYOUT`.
  Even for a single-part object ask question 1 (fused vs separate features); skip question 2 only when there is one part that is modelled in its print orientation, and say so in the summary.
- Positions need coordinates. Agree the coordinate system first (origin, which axis is length/width/height, Z=0 on the print bed) and ask for every hole/opening position and size explicitly. If the user cannot give a number, offer 2–3 concrete layouts as options and let them pick.
- If the user says "you decide" for an item, decide it, then record it in the spec as **Decided by Claude (user delegated)** with the reason. That is a decision, not an assumption.
- Flag conflicts you notice (e.g. boss radius leaves < 1.2 mm wall, hole too close to an edge, part larger than the bed, overhang with no support plan) and ask how to resolve them.
- Hardware sizes (screws, inserts, nuts, magnets) come from the `SCREWS` table / `TOL_*` constants in `utils_3d.py`; state the values you will use and confirm them — they are typical, not verified.

## Phase 2 — Finalize gate

Before writing anything, show one compact **final summary**: a table of every parameter with its value and its source (`stated` / `decided` / `delegated`), the part list with names (for separate feature meshes: every feature object, grouped by the printed part it belongs to), the coordinate system, the mesh structure and the start layout (mentioning that both layouts are in the script). Then ask (AskUserQuestion): "Is everything final? Any remaining open point?" with options *"All final — generate files"* / *"Change something"*. Only an explicit "all final" ends the interview. If they change something, update the ledger, re-check for knock-on effects, and show the summary again.

## Phase 3 — Write the description (`<name>_description.md`)

Use `reference/description_template.md`. Requirements:
- Name `<name>` = short snake_case of the object. Create a **project folder** `<root>/projects/<name>/` (create `projects/` if it does not exist) (or wherever the user chose during the interview — area 9 of the checklist) and put the description, the build script and any later exports there. Never put them next to `utils_3d.py` / `run_blender.py` at the library root, and never inside `.claude/`. `utils_3d.py` stays where it is; do not copy it into the project.
- Self-contained: someone could rebuild the model from this file alone with no questions. Every dimension in mm, every position as coordinates, Z=0 on the print bed.
- Include: units/coordinate rules, construction method per part (the utils functions used), **every part with name + geometry**, final placement, **Final object list** (backticked exact object names, one per line — the verifier parses this section), **Decisions** (each with source), print notes (orientation, supports, fit tolerances), verification criteria.
- No "TBD", "approximately", "roughly" or unspecified values. If you cannot fill a field, you skipped Phase 1 — go back.

## Phase 4 — Write the build script (`<name>_build.py`)

Start from `reference/build_template.py` (a runnable skeleton: utils lookup block, settings block, collection, parts, report, optional export). Requirements:
- All numbers live in the **settings block** at the top, named to match the spec; the script body contains no magic numbers.
- Object names are **exactly** those in the spec's Final object list (no suffixes), one collection named in the spec.
- Use `utils_3d` for everything it covers; add small local helpers only for shapes it lacks, and say so in a comment.
- Keep the `_find_utils_dir()` / `UTILS_DIR` block unchanged. It finds `utils_3d.py` in `UTILS_DIR`, then the `UTILS_3D_DIR` environment variable, then the script's folder and **every parent folder** (also from Blender's text editor), so a project folder under the library root works with no setup. If the project folder is **not** under the folder containing `utils_3d.py`, ask the user which they prefer — set `UTILS_DIR` in the script's settings, or set the `UTILS_3D_DIR` environment variable — and record that in the spec's Decisions table. Never hard-code any other absolute path.
- End with `u.print_report(...)`; add `min_wall=`, `bed=` and `overhang_deg=` checks when the spec gives a wall minimum / printer bed. Include a commented-out `u.export_all(basename="<name>")` line, enabled via an `EXPORT` flag in settings.
- **Both layouts, always:** model every part in its **assembled** pose, then keep the template's `LAYOUT` setting (`"print"` | `"assembled"`, default = the user's choice) and fill in `place_for_print()`: rotate/flip each printed part's objects **as one group** into its print orientation (`u.flip_objects` / `u.rotate_objects` with an explicit pivot), move the groups side by side with a gap (`u.translate_objects` / `u.arrange_in_row`), and `u.drop_to_bed` each group. Run any assembly/fit checks *before* the layout step (they need the assembled pose). Comment the `LAYOUT` line so the user sees both options.
- **Every feature its own mesh** (if chosen): one child collection per printed part under the spec's collection (`u.use_collection(<part coll>, clear=True, parent=<COLL_NAME>)`); each feature is its own object named `<Part>_<Feature>_<n>`; parts overlap the body they join by 0.1–0.2 mm (that is how they fuse); every cut goes through `u.cut_objects(<that part's objects>, cutter)` so it is applied to every mesh it passes through; add cuts in the same order as a fused build would (a feature added after a cut must not be cut by it). Add a `MODE = "build" | "export"` setting: `"export"` does not rebuild — it fuses copies of the current objects of each part collection with `u.fuse_copies`, applies `place_for_print` only if the collection's stored layout (`coll["layout"]`, written by the build) is `"assembled"`, runs `print_report` and writes one STL per printed part. Warn in the docstring that `"build"` replaces the collections (hand edits are lost). Working example: `projects/s24plus_phone_box/s24plus_phone_box_parts_build.py`.
- **Only the major features separate:** the same structure, with the minor features fused into their part (or into the major feature they sit on) before the part's cuts.

## Phase 5 — Verify, then report

1. Run `python <root>/run_blender.py <skill>/reference/verify_model.py -- <project>/<name>_build.py <project>/<name>_description.md` (use real paths; `<skill>` is this skill's folder, `.claude/skills/blender-model-spec`). It builds headless, checks every object in the spec's Final object list exists (and nothing extra), and that each mesh is watertight with zero leftover modifiers. Exit status ≠ 0 means fix and re-run.
2. Export the parts once (set `EXPORT = True` in a temporary copy, or call `u.export_stl_per_object` from a throwaway script) and run `python <skill>/reference/check_stl.py <stl files>`: every file must show `mismatched_edges=0` and a volume matching the model. This looks at what the slicer receives; delete the test exports afterwards unless the user asked for them. If the model has moving parts (hinge, slider), the build script should also test clearance by rotating/offsetting a copy and measuring `u.overlap_volume` (0 mm³ = free), as the phone-box build does.
3. **Both layouts:** verify_model runs the default layout; build the other one too (a temporary copy with `LAYOUT` changed) and check it: in the print layout every printed part's lowest point is Z = 0, the parts do not overlap each other (`u.find_overlaps` on the printed parts, or their fused copies) and the group fits the bed; in the assembled layout the assembly checks give their designed values. For separate feature meshes, also run `MODE = "export"` once in the same session after a build (temporary copy, `EXPORT_DIR` in the scratchpad): each fused part must be watertight, its volume must equal a fused build of the same design, and `check_stl.py` must pass on the exported STLs.
4. If the object is visual or fit-critical, render a quick Workbench preview (see CLAUDE.md for the headless render approach) and look at it. Compare against the spec, not just "it ran".
5. Fix any mismatch **in both files** so the spec and the script never diverge. Re-run until clean.
6. Report to the user in a few lines: the project folder and the two file paths, object count, verification result, what to do in Blender (open script via Open → Run Script; Text → Reload if re-running), and any print-risk you noticed (thin walls, overhangs, bed fit). Do not paste the files. **Always tell the user about the two layouts**, e.g. "The script starts in the ready-for-print layout (parts side by side on the bed). Set `LAYOUT = "assembled"` at the top of the script and run it again to see the parts in their assembled positions (and back to `"print"` before exporting)." For separate feature meshes also explain the two modes: `MODE = "build"` recreates the parts (hand edits are lost), `MODE = "export"` fuses the current, hand-edited parts and writes the STLs.

## Geometry pitfalls (learned the hard way — check the spec against these before Phase 2)

- **Exact Boolean and tangent contacts:** never let two operands touch along a line or share a vertex/plane exactly (a cylinder whose top is tangent to a plate's face, a block top exactly at a barrel's axis height). Offset by 0.2–0.3 mm or overlap properly; otherwise the result gets open edges, non-manifold edges or zero-area slivers.
- **Rounding vs thickness:** an edge round must be smaller than the thickness it is cut into; two rounds on one thin plate must add up to less than the plate thickness. Ask the user when their chosen radius does not fit.
- **Corner radii vs what sits inside:** a cavity corner radius must be large enough for the contents' corners (and a lip/hook inside a tight clearance must be checked against the contents with a dummy part and `overlap_volume`).
- **Snap hooks need room:** hooks cannot live in a gap narrower than arm + tip; if the contents leave 1 mm beside the walls, put them where the contents are not (e.g. an extension pocket) and tell the user.
- **Flush faces on a bed:** a feature that should be flush with the printed bed face (a barrel top, a label) works better a few tenths of a mm inside the plane than exactly on it.
- **Separate feature meshes and fusing:** unioning parts one by one can re-process already-cut details (a socket-cut hinge knuckle) and leave open edges; `u.fuse_copies` does one union with self-intersection, which works — use it, and check its result (it warns when not watertight).
- **Lathed parts and threads:** a Boolean cut on a revolved mesh puts cutter vertices on the lathe's own edges and leaves open edges, and even a cutter that only overlaps a mesh's bounding box can break it. Draw bores, grooves and recesses into a `u.make_revolved_ring` profile and build threads with `u.make_threaded_tube` (no Booleans). Where two such meshes fuse, keep their surfaces from coinciding (bury one bore edge in the other part, keep vertex rings out of the other part's planes, e.g. a 0.55 rather than 0.5 overlap).
- **Watertight in Blender ≠ clean STL:** near-duplicate vertices from a union become identical in the STL's 32-bit floats and show up as mismatched edges in `check_stl.py`; `u.fuse_copies` cleans them (`clean=True`, default), otherwise call `u.clean_for_stl` before exporting a Boolean result.
- **Moving parts:** hinge/slider clearances are verified by measuring overlap at several poses, and snap hooks must be left out of that test (they are meant to catch).
- **Analysis helpers:** `utils_3d` checks are estimates. A tapering tip (hook, rounded plate edge) reads as a thin "wall" by nature; explain such expected readings in the spec instead of hiding them.

## Don'ts

- Don't generate files before the Phase 2 gate passes.
- Don't invent dimensions to "make it work"; if geometry conflicts, ask.
- Don't copy-paste helper functions into the build script; import `utils_3d`.
- Don't modify `utils_3d.py` or existing build scripts as part of this skill; if a missing helper is needed, put it locally in the new script and mention it so the user can decide to promote it.
