# Vacuum Bag Adapter — Build Specification (v1.3)

Sketch (confirmed by the user, drawn from the same values): [`vacuum_bag_adapter_sketch.html`](vacuum_bag_adapter_sketch.html)

**v1.3:** this is the adapter as printed, and its geometry is unchanged: single-start P 1.5. The bag valve's real thread turned out to be **two-start** (two threads 180° apart, 1.0 between neighbouring ridges, lead 2.0). Two parts were added, each with its own spec:
- [`vacuum_bag_adapter_2start_description.md`](vacuum_bag_adapter_2start_description.md): this adapter with the two-start thread.
- [`vacuum_bag_coupler_description.md`](vacuum_bag_coupler_description.md): a coupler that lets this adapter screw onto the valve.

The build has a new setting `THREAD_STARTS` (1 here), and an `OVERRIDES` hook that the two-start build uses. `socket_thread_rings` takes optional `pitch` / `starts` arguments.

**v1.2 (user's changes in the build script):** the oval's end arcs are 8 mm deep (were 6), and the thread pitch is 1.5 (was 1.0). Everything else is as in v1.1.

**v1.1 (after the first test print):** the thread pitch is 1.0 (not 2.0). The spigot and the thread are now copied from parts that fit: the spigot outside is 39.5 × 17.3 with 6 mm end arcs (measured on another vacuum adapter), and the printed internal thread is root Ø26.6 / crest Ø24.4 (measured on the bag's own female cover). The male inlet was re-measured at Ø23.5–25.1. The material-based push-fit allowance (`TOL_SNUG`) and thread clearance (`THREAD_CLR`) are replaced by `SPIGOT_ADJ` / `THREAD_ADJ` = 0.0 tuning knobs. The dummy vacuum-opening check is gone, because there is no measured opening any more.

## Purpose
"An adapter for a portable vacuum to fit to a storage vacuum bag standard connector. The vacuum side is an oval shape 17.5 × 39.5 mm with the oval part starting 8 mm from the edge of each side of the long part. The vacuum bag inlet is 25.5 mm with standard thread (23.6 mm – 25.5 mm)." (v1.0 description; corrected values in v1.1 above.) One printed part: an oval spigot that plugs into the vacuum, a transition to a round socket, and an internal thread that screws onto the bag valve, sealing on a flat shoulder.

## General rules
- **Units:** millimetres. Scene unit system METRIC, scale 0.001, length unit MILLIMETERS (`setup_units_mm()`).
- **Coordinate system:** the part's axis is Z; Z = 0 is the print bed (oval end); the oval's long axis is X, its short axis Y; the axis passes through X = Y = 0. The part is modelled in its print orientation.
- **Library:** all geometry is built with `utils_3d.py` (found by the script via `UTILS_DIR` / `UTILS_3D_DIR` / parent folders). No Boolean and no modifier is used: the part is one `u.make_ring_tube` (stacks of rings, one radius per angle).
- **Files:** `projects/vacuum_bag_adapter/vacuum_bag_adapter_description.md` (this spec), `vacuum_bag_adapter_build.py`, `vacuum_bag_adapter_sketch.html` (dimensioned sketch), the test rings `vacuum_bag_adapter_test_description.md` / `vacuum_bag_adapter_test_build.py`, and (v1.3) `vacuum_bag_adapter_2start_*` and `vacuum_bag_coupler_*` (both load this build: keep its `SETTINGS (match the spec)` / `PART` marker lines and the `OVERRIDES` line).
- **Collection:** `VacuumBagAdapter`.
- **Printer / material:** PETG, 0.4 nozzle (line width 0.45), 0.16 mm layers; report checks a 220 × 220 × 250 bed.

## Decisions
Source: **stated** (user said it), **chosen** (user picked from options), **suggested from material, confirmed** (derived from `materials.md`, accepted by the user), **derived** (follows from the others).

| Parameter | Value | Source |
|---|---|---|
| Mesh structure | one mesh (`VBA_Adapter`) | chosen |
| Scene layout | one part modelled in its print orientation; `LAYOUT = "print"` drops it on the bed, `"assembled"` is the same pose | chosen (orientation) |
| Print orientation | oval end on the bed, thread end up (seal shoulder faces up and prints flat) | chosen (after the shoulder-overhang conflict) |
| Material / nozzle / layers | PETG / 0.4 (line 0.45) / 0.16 | chosen |
| Use conditions | indoor, room temperature (PETG max 65 °C: OK) | chosen |
| `MIN_WALL` / `WALL` | 0.9 (2 lines) / 1.8 (4 lines) | suggested from material, confirmed |
| Overhang limit | 45° | suggested from material, confirmed |
| Fit tuning | `SPIGOT_ADJ` = 0.0 (on size, + = smaller spigot), `THREAD_ADJ` = 0.0 (per side, + = looser thread) | derived (v1.1: values copied from parts that fit) |
| Spigot outside | 39.5 (X) × 17.3 (Y), measured on another vacuum adapter; straight sides, end arcs 8.0 deep → end radius 8.676 (just over the 8.65 half-width: nearly a full half-circle), arc centres X = ±11.074, straight part 23.5 | stated (v1.1; arcs 8.0 in v1.2) |
| Fit direction | the spigot plugs **into** the vacuum's opening | chosen |
| Spigot inside / length | 35.9 × 13.7 (outline shrunk 1.8 per side), Z 0 … 30 | derived / chosen (30) |
| Spigot tip lead-in | 1.0 × 45° (outline shrunk a further 1.0 at Z 0); also serves as the elephant's-foot chamfer | chosen |
| Transition | ruled loft, Z 30 … 50: each angle's outer radius goes linearly from the spigot outline to R 15.1, inner from the spigot inside outline to R 10.5 | chosen (20) |
| Neck | Z 50 … 52, bore Ø21.0, outside Ø30.2 | chosen (2) |
| Seal shoulder | flat ring at Z 52 (325 layers), facing up, from Ø21.0 to the thread crest Ø24.4 | chosen |
| Printed internal thread | copied from the bag's female cover: root Ø26.6, crest Ø24.4, pitch 1.5, rounded profile, right-hand; `u.thread_radii(..., 'round')`, Z 52 … 59 (7 mm, 4.7 turns) | stated (v1.1; pitch 1.5 in v1.2) |
| Bag valve (male inlet) | Ø23.5 (root) – 25.1 (crest), pitch 1.5, used for the fit check only | stated (v1.1, re-measured; pitch v1.2) |
| Socket outside | Ø30.2 (root 26.6 + 2 × 1.8) | derived |
| Mouth chamfer | 0.8 × 45° from the thread root: Ø28.2 at Z 59, leaves a 1.0 mm rim | chosen |
| Total length | 59 | derived |
| Project / output | `projects/vacuum_bag_adapter/`, STL (`EXPORT = True` → `exports/VBA_Adapter.stl`) | chosen |

## Part — VBA_Adapter
- **Construction:** `u.make_ring_tube("VBA_Adapter", outer, inner)` with `SEGMENTS = 192` radii per ring (angle 0 on +X). The oval outline is converted to a radius per angle by a local helper `oval_radius(theta, d)` (utils_3d has no oval/loft primitive): straight side `y = ±(8.65 − d)` up to `x_c = 11.074 + √((8.676 − d)² − (8.65 − d)²)`, then the end arc of radius `8.676 − d` about `(±11.074, 0)`. Shared helpers `spigot_rings`, `socket_thread_rings` and `make_valve_dummy` sit above the `PART` marker (the test script loads them).
- **Outer rings (bottom → top):** Z 0 oval d = 1.0 → Z 1.0 oval d = 0 → Z 30 oval d = 0 → 20 linear rings to Z 50 circle R 15.1 → Z 59 circle R 15.1.
- **Inner rings (bottom → top):** Z 0 oval d = 1.8 → Z 30 oval d = 1.8 → 20 linear rings to Z 50 circle R 10.5 → Z 52 circle R 10.5 → (flat step) thread rings Z 52 … 59, 16 per pitch: `r = max(12.2 + 1.1 · form(z/1.5 − θ/2π), 14.1 − (59 − z))` (round form, right-hand; the second term is the mouth chamfer).
- **Geometry:** bounding box X ±19.75, Y ±15.1, Z 0 … 59 → 39.5 × 30.2 × 59.0; volume 12425.5 mm³.
- **Object name:** `VBA_Adapter`

## Placement
- One part, modelled in its print orientation; both `LAYOUT` values leave it in place (`"print"` drops it on Z = 0).

## Assembly check (`ASSEMBLY_CHECK = True`, dummy deleted afterwards)
- Dummy valve (`make_valve_dummy`): `u.make_threaded_tube` with the male inlet's thread (Ø23.5–25.1, P 1.5, round, same phase), Z 52.05 … 64, bore R 10.0 → overlap with the adapter **0.0 mm³** (radial gap 0.45 at the socket's crest, 0.75 at its root). Positive control: the same valve pushed 1 mm into the shoulder overlaps by 117.6 mm³.

## Print notes
- Oval end on the bed, thread end up, no supports, 0.16 mm layers. The loft leans at most about 18° from vertical (limit 45°). The seal shoulder faces up and prints flat.
- **Thread:** at pitch 1.5 and 1.1 mm depth each thread ridge is about 0.75 mm wide at half height, its lower flank up to about 66° from vertical over 0.55 mm. It prints without support (small overhangs inside a ring). `print_report` reads `min_wall` 1.33 (no flag) and about 374 mm² of overhang, almost all of it thread flanks plus the 45° chamfers. If the ridges print rough, try 0.12 mm layers for the top 8 mm.
- Print the two test rings first ([`vacuum_bag_adapter_test_description.md`](vacuum_bag_adapter_test_description.md), `vacuum_bag_adapter_test_build.py`): adjust `THREAD_ADJ` if the thread binds or wobbles, `SPIGOT_ADJ` if the spigot is loose or tight in the vacuum. The test script loads this build's SETTINGS and helpers (from the `SETTINGS (match the spec)` line to the `PART` line): keep those marker lines.
- Use: screw onto the valve by hand until the rim stops on the shoulder (up to about 4½ turns); push the spigot into the vacuum.

## Final object list (1 object, collection `VacuumBagAdapter`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `VBA_Adapter`

## Verification
1. Every object in the list exists and nothing else is in the collection.
2. The mesh is watertight (0 open edges, 0 non-manifold edges) and has 0 modifiers.
3. `VBA_Adapter` bounding box 39.5 × 30.2 × 59.0, lowest point Z = 0, volume 12425.5 mm³.
4. Assembly check: valve overlap 0.0 mm³.
5. Exported STL passes `check_stl.py` (0 mismatched edges, volume equal to Blender's).
6. `print_report` shows `[OK ]` (`min_wall` ≈ 1.33).
