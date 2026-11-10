# G9 Dome Adapter — Build Specification (v1.0)

## Purpose
A printed adapter for a custom outdoor light fixture: it hangs a closed glass globe from a threaded 10 mm lamp pipe and covers the globe's cut top against water and dust. In the user's words: *"adapter from 10M to G9 thread and also a dome shape cover for the 40 mm open side to protect from water and dust"*, *"the adapter connects from the M10 (pipe) to the glass neck (replacing the G9 holder), adapter and cover as one piece"*.

How it is used: the adapter's spigot screws into the glass's internal thread and carries the glass. The dome sits on the globe over the Ø36 cut top and seals it with an O-ring pressed onto the flat cut top of the glass. The pipe (wires inside) passes the Ø13 bore, screws through the M10×1 thread in the spigot and comes out inside the globe, where a G9 holder with an M10×1 back thread screws onto the pipe end and holds the bulb (not the glass).

Section sketch: `g9_dome_adapter_sketch.html` (this folder).

## General rules
- **Units:** millimetres. Scene unit system METRIC, scale 0.001, length unit MILLIMETERS (`setup_units_mm()`).
- **Coordinate system:** the part's axis is Z. In the **assembled** layout Z = 0 is the flat cut top of the glass, the dome is above (Z 0…15) and the spigot below (Z −15…0); +Z points up (towards the ceiling). In the **print** layout the part is turned over about X, and the flat dome top lies on the print bed at Z = 0.
- **Library:** geometry is built with `utils_3d.py` (found by the script via `UTILS_DIR` / `UTILS_3D_DIR` / parent folders) (`make_revolved_ring`, `make_threaded_tube`, `fuse_copies` with `clean_for_stl`; these started as local helpers of this script and moved into `utils_3d`) plus one local helper, `globe_z`. Both meshes are built directly, without any Boolean; the only Boolean is the fusing union in export mode. No modifiers remain.
- **Files:** `projects/g9_dome_adapter/g9_dome_adapter_description.md` (this spec), `projects/g9_dome_adapter/g9_dome_adapter_build.py`, `projects/g9_dome_adapter/g9_dome_adapter_sketch.html`.
- **Collection:** `G9_Dome_Adapter`, with the child collection `G9A_Adapter_Parts` holding the feature meshes.
- **Printer / material:** PETG, 0.4 mm nozzle, 0.12 mm layers. Outdoor, under cover, LED G9 bulb.

## Decisions
Every value below is final. Source: **stated** (user said it), **chosen** (user picked from options), **delegated** (user told Claude to decide; reason given).

| Parameter | Value | Source |
|---|---|---|
| Mesh structure | every feature its own mesh: `G9A_Dome`, `G9A_Spigot` (one printed part); `MODE = "export"` fuses them into `G9A_Adapter` | chosen |
| Scene layout at start | assembled (`LAYOUT = "assembled"`; `"print"` is one setting away) | chosen |
| Glass | closed Ø120 globe, top cut flat to Ø36 (first version Ø40; reduced by the user after the test print) | stated |
| Pipe | M10×1, wires inside, 20 mm of thread at its end | stated |
| Adapter length | 30 mm: 15 mm dome hub (Z 0…15) + 15 mm spigot (Z −15…0) | stated |
| Bore in the dome hub | Ø13 plain, Z 0.5…13.5 (the dome's underside is at Z 0.5), Ø13 below the washer recess | stated |
| Spigot top bore | Ø12.4 from Z 0 to the spigot's top (Z 1.05, inside the dome): 0.3 mm/side narrower than Ø13 so the fused part has no coincident or 0.1 mm walls; the Ø10 pipe passes freely | Claude, geometry fix found in verification (see "Why no Booleans"); reported to the user for confirmation |
| Pipe thread | printed internal M10×1, Z −15…0 (after the Ø13 bore, so the pipe's short threaded end reaches it) | stated |
| Pipe-thread clearance | 0.2 mm per side: cut major Ø10.40, minor Ø9.32, ISO 60° form | chosen (printed thread) |
| Glass thread on the spigot | common G9 shade thread M20.8 × 2 ([Starled listing](https://www.starled.fr/en/g9-lamp-holder-mounted-on-m20-8-ring-at-2mm-pitch-with-coaxial-cable)), rounded profile, printed major Ø20.6 / minor Ø19.0 (values set by the user in the script), right hand, 2 mm lead-in at the tip | stated ("use common G9 thread") |
| Dome | Ø60, flat top, R8 outer top edge, solid (slicer walls/infill) | chosen |
| Underside | modelled at first O-ring contact: flat over the Ø36 cut 0.5 mm above the glass; curved part (Ø36…Ø60) following the Ø120 globe 1.0 mm above it. Tightening moves the dome down 0.5 until the flat rests on the glass (hard stop); the curved part then keeps 0.5 clearance | chosen / derived from the face seal |
| O-ring | 32 × 2 mm (ID × cord, 36 OD), face seal on the flat, smooth cut top of the glass. Groove in the flat underside Ø29.8…Ø35.2 (2.7 wide, 1.5 deep); the O-ring sits slightly squeezed against the outer wall, centred on about Ø33 (1.5 mm from the glass edge); 25 % squeeze at the hard stop | stated (reduced with the flat, from 36 × 2; flat smooth glass) / chosen |
| Top seal | Ø15 × 1.5 mm recess on top for an M10 rubber washer, pressed by a metal M10×1 lamp nut on the pipe (first version Ø21; set to Ø15 by the user in the script) | stated |
| Print | dome top on the bed, spigot up, no supports | chosen |
| Project folder | `projects/g9_dome_adapter/` | stated |

## Part — Adapter (one printed part, two feature meshes)

### Feature 1 — `G9A_Dome`
- **Construction:** `u.make_revolved_ring` of one closed (r, z) profile, `SEGMENTS = 128` around the axis. The Ø13 bore, the washer recess and the O-ring groove are all part of the profile (no Boolean).
- **Profile** (r, z), assembled pose (first O-ring contact), going outward along the underside and back over the top:
  - flat underside over the glass's cut top at Z 0.5: (6.5, 0.5) → (14.9, 0.5); O-ring groove (14.9, 0.5) → (14.9, 2.0) → (17.6, 2.0) → (17.6, 0.5); then (17.6, 0.5) → (18, 0.5)
  - step up at the cut edge to the curved part: (18, 1.0), then for r = 18…30 the curve z = √(60² − r²) − √(60² − 18²) + 1.0 (globe surface + 1.0), 24 steps, ending at (30, −4.275)
  - outer side: (30, −4.275) → (30, 7), then an R8 quarter round (16 segments) to (22, 15)
  - top: (22, 15) → (7.5, 15); washer recess (7.5, 15) → (7.5, 13.5) → (6.5, 13.5)
  - bore: (6.5, 13.5) → (6.5, 0.5), Ø13
- **Size:** Ø60 × 19.275 (Z −4.275…15), volume 39921.0 mm³.

### Feature 2 — `G9A_Spigot`
- **Construction:** `u.make_threaded_tube` (outer: glass-thread section with a 2 mm lead-in; inner: M10×1 section up to Z 0, then a plain section): one watertight tube built from rings of 96 radii (no Boolean). Each thread surface is r(angle, z) = r_min + (r_max − r_min) · form(z / pitch − angle / 2π), right hand, 16 rings per pitch.
  - Outside, Z −15…1.05: glass thread, r 9.5…10.3, pitch 2.0, rounded form 0.5 − 0.5·cos(2πt); the thread height grows from 0 at Z = −15 to full at Z = −13 (lead-in).
  - Inside, Z −15…0: M10×1 pipe thread, r 4.66…5.20, pitch 1.0, ISO 60° trapezoid form (crest P/8, root P/4).
  - Inside, Z 0…1.05: Ø12.4 plain (a flat step at Z 0 joins it to the thread).
  - Flat ring faces close the bottom (Z −15) and the top (Z 1.05).
- **Z range:** −15…1.05; it reaches 0.55 mm into the dome (underside at Z 0.5), which is how the two fuse. 0.55 rather than 0.5 keeps the thread's vertex rings out of the dome's underside plane.
- **Size:** Ø20.6 × 16.05, volume 3659.9 mm³.

### Why no Booleans
The first version cut the groove, the bores and the pipe thread with exact Booleans. Each cut left near-zero-area triangles (and one cut that only overlapped the dome's bounding box left 63 open edges), and the fusing union in export mode then failed. Building both meshes directly gives clean topology. In the fused part the dome's Ø13 bore edge is buried inside the spigot's Ø12.4 top, so no surfaces coincide.

## Placement (two layouts, setting `LAYOUT`)
- **Assembled** (`LAYOUT = "assembled"`, default): the pose the parts are modelled in, as installed on the glass (Z = 0 = glass cut top, dome up).
- **Ready for print** (`LAYOUT = "print"`): both meshes are flipped together 180° about X through (0, 0, 0), then dropped so the flat dome top is on Z = 0; the spigot points up and its tip is at Z = 30.
- `MODE = "export"` does not rebuild: it fuses copies of the current objects of `G9A_Adapter_Parts` with `u.fuse_copies` into `G9A_Adapter`, which also cleans it for STL (`u.clean_for_stl`: merge vertices closer than 0.0001 mm, dissolve degenerate faces, triangulate; without it the STL had ~220 doubled edges although Blender reported the mesh watertight), flips it for print if the collection's stored layout is `"assembled"`, drops it to the bed, reports, and writes `G9A_Adapter.stl` to `EXPORT_DIR` (default `exports/` next to the script). `MODE = "build"` replaces the collection, so hand edits are lost.

## Print notes
- Orientation: flat dome top on the bed, spigot up. No supports.
- Both threads print with a vertical axis (best quality). Use 0.12 mm layers for the 1 mm-pitch pipe thread.
- The first ~2.3 mm of the R8 edge rise from the bed at more than 45° overhang (the round starts horizontal at the bed). It is short and usually prints cleanly; if it curls, reduce `DOME_EDGE_R` or print with a brim.
- The step from the Ø12.4 bore to the M10×1 thread is a 0.5 mm ledge facing the bed in print orientation: a small circular overhang that bridges fine.
- Fit: the glass thread is a common size, not measured on this glass (the user measured Ø20 across the inside of the glass thread, while M20.8×2 is about Ø18.6 there). Print the spigot alone first (delete `G9A_Dome` in Blender, export) and adjust `GLASS_THREAD_*`.
- Glass hangs on PETG threads: tighten by hand until the dome's flat underside rests on the glass (you feel it stop), no further.
- The pipe has 20 mm of thread; 15 mm are inside the spigot, so about 5 mm remain for the G9 holder below.

## Final object list (2 objects, collection `G9_Dome_Adapter`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `G9A_Dome`
- `G9A_Spigot`

## Verification
1. Every object in the list exists and nothing else is in the scene.
2. Every mesh is watertight (0 open edges, 0 non-manifold edges) and has 0 modifiers.
3. Assembled: `G9A_Dome` bbox 60 × 60 × 19.275 (Z −4.275…15), 39921.0 mm³; `G9A_Spigot` bbox 20.6 × 20.6 × 16.05 (Z −15…1.05), 3659.9 mm³.
4. Print layout: lowest point Z = 0 (dome top on the bed), part height 30.0 (from the dome top down to the spigot tip).
5. Export mode: the fused `G9A_Adapter` is watertight, 60 × 60 × 30, 43484.5 mm³, and `check_stl.py` reports `mismatched_edges=0` with the same volume.
