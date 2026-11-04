# Samsung Galaxy S24+ Storage & Charging Box — Build Specification (v1.2)

**v1.2 changes:** the phone is now measured **with its protector** (82.4 × 166 × 13.4 mm) and the clearance is **2.0 mm per side in X and Y** (1.0 mm above and below) so the phone lifts out easily. Ribs and two new end stops keep the phone within 0.5 mm of its nominal position, so it cannot drift into the snap hooks; with the wider gap the +Y and −X hooks no longer need wall niches. All hinge and hook positions follow automatically from the new size.
**v1.1 changes:** integrated snap-in stub-pin hinge (no separate pin); four more snap hooks on the +Y end and the free −X side (latched on three sides).

## Purpose
A printable box that holds the whole Samsung Galaxy S24+ in its protector when it is not in use. A door opens on an integrated snap-in hinge like a book cover, and a slot lets a USB-C cable enter from outside and plug into the phone while the door is closed, so the phone can charge inside. The door has a honeycomb vent for heat.

User's words: "a case for Samsung S24 plus that holds the entire phone and has a cover (opened like a door). This case is to be used to save the phone when not in use; the box should have a place to insert a charging cable."

## General rules
- **Units:** millimetres. Scene unit system METRIC, scale 0.001, length unit MILLIMETERS (`setup_units_mm()`).
- **Coordinate system:** origin at the box centre on the print bed. **X** = box width, **Y** = box length, **Z** = up, Z = 0 is the bed. **Hinge on the +X long side. Cable end at −Y.** Both parts are modelled in the **closed pose** (door sitting on the box); the door is then flipped and moved to its print position (see Placement).
- **Library:** all geometry is built with `utils_3d.py` (found by the script via `UTILS_DIR` / `UTILS_3D_DIR` / parent folders); every Bevel/Boolean is applied, no modifiers remain. One local helper (`make_prism_yz`, a YZ-profile extrusion) is defined in the script because `utils_3d` only has the XZ version.
- **Files:** `projects/s24plus_phone_box/s24plus_phone_box_description.md` (this spec) and `projects/s24plus_phone_box/s24plus_phone_box_build.py`. The hinge test coupon (`s24plus_hinge_test_*`) reads its hinge values from the build script.
- **Collection:** `S24P_Phone_Box`.
- **Printer / material:** 250 × 210 mm bed (Prusa MK4 class, build height taken as 220 mm), PETG.

## Decisions
Source: **stated** (user said it), **chosen** (user picked from options), **delegated** (user told Claude to decide, reason given), **derived** (computed from other values or forced by geometry).

| Parameter | Value | Source |
|---|---|---|
| Object | storage box for a Samsung Galaxy S24+ in its protector, door opens like a door, cable inserted for charging | stated |
| Phone with protector (L × W × T) | 166.0 (Y) × 82.4 (X) × 13.4 (Z) mm, thickest point including the camera bump | stated (v1.2; Z "13/4" confirmed as 13.4) |
| Clearance | 2.0 mm per side in X and Y; 1.0 mm above and below | chosen (v1.2) |
| Removal aid | none (the extra clearance only) | chosen (v1.2) |
| Phone play limit | ribs and end stops leave the phone 0.5 mm play per side (furthest edge X = ±41.7, furthest end Y = 96.0), so it cannot reach the snap hooks | delegated (v1.2, fixes code-review finding 1) |
| Plug pocket | +25.0 mm cavity length at the −Y end (whole USB-C plug sits inside) | chosen |
| Cavity | 86.4 (X) × 195.0 (Y: 170 for the phone + 25 pocket) × 15.4 (Z) mm | derived |
| Wall, floor, door plate thickness | 2.4 mm | chosen |
| Box outer | 91.2 × 199.8 × 17.8 mm; closed case 20.2 mm tall; with hinge 97.1 mm wide | derived |
| Layout | phone flat, door hinged on a long side | chosen |
| Hinge type | snap-in stub-pin hinge, no separate pin: the door knuckles carry tapered stubs that click into round sockets in the box knuckles; door is pressed down onto the box to assemble | chosen (v1.1) |
| Hinge dimensions | 5 knuckles × 16.0 mm, 0.4 mm gaps (81.6 mm span, centred on Y = 0), barrel R2.8; box owns knuckles 1, 3, 5, door owns 2, 4; axis at X = 48.7, Z = 17.2 (barrel top 0.2 below the door's outer face) | delegated |
| Stub pins (door) | tapered, root R1.3 → tip R0.8, protrude 2.2 mm from both end faces of each door knuckle (embedded 0.2); slit 0.6 wide along the stub axis, continuing 2.0 mm into the knuckle (estimated strain about 2.6 %) | delegated (tuned with the hinge test coupon) |
| Sockets (box) | round hole R1.5 × 2.4 deep in each knuckle face that looks toward a door knuckle (stub engages 1.8); channel 2.2 wide from the hole up through the barrel top (about 0.1 mm interference per side where the stub first touches, R1.21 after the 0.4 mm knuckle gap), stopping 0.2 short of the socket bottom; 0.8 lead-in funnel | delegated (tuned with the hinge test coupon) |
| Cable function | charge inside the closed box | chosen |
| Cable slot | 14 × 8 mm stadium through the −Y end wall, centred X = 0, Z = 6.1…14.1 | chosen |
| USB-C port position | bottom short edge, centred across the width (slot centre X = 0, Z = 10.1 = phone mid-thickness) | chosen |
| Latch | printed snap-fit, 6 hooks, each 8 mm wide: 2 at the −Y (cable) end (X = ±24), 2 at the +Y end (X = ±24), 2 on the free −X long side (Y = ±35) | chosen (+Y end and −X side added at the user's request in v1.1); sizes delegated |
| Latch geometry, cable-end hooks | arm 1.2 thick (continues the lip), hangs 7.0 below the door underside, tip protrudes 0.8 toward −Y, hook height 1.4; grooves in the end-wall inner face 9.0 wide × 1.0 deep, 0.5 below / 0.4 above the hook | delegated |
| Latch geometry, +Y end and −X side hooks | arm 1.0 thick, same 7.0 length and 1.4 hook height, tip 0.7; the arm sits in the 1.5 mm gap between the furthest phone position and the wall (0.25 to each); 0.45 of the tip reaches into a catch groove (floor 0.3 behind the tip, 1.65 mm of wall left) | delegated |
| Door style | flat plate with locating lip | chosen |
| Locating lip | 1.2 thick × 0.8 tall, 0.3 mm inside the cavity wall, rounded rectangle; its inner face is at the furthest phone position (X ±41.7) and it sits 0.2 mm above the phone top (17.0 vs 16.8) | chosen (shallow-lip option); size delegated |
| Rounding | vertical corners R10; box bottom edge R3; box rim edge R0.6; door outer edge R2.0 | chosen |
| Door underside (seam) edge | R0.2 (2.0 + 0.6 would exceed the 2.4 plate) | derived |
| Inside radii | cavity corners R7.6 (= 10 − 2.4, even wall); cavity floor edge R1.0 | delegated |
| Phone retention | 4 ribs (6 long × 1.5 proud × 6 tall) at Y = −20 and Y = 60 on both long walls; 2.0 mm stop across the cavity at Y = −74.5…−72.5, 6 tall, 16 mm centre gap for the plug; 2 end stops (6 wide × 1.5 proud × 6 tall) on the +Y wall at X = ±10 | chosen type; sizes delegated (v1.2: proud = clearance − 0.5 play) |
| Finger notch | half-round scoop, 14 mm wide × 3.5 mm deep, in the −X wall rim at Y = 0 (box only) | chosen; size delegated |
| Door label | "S24+", engraved 0.6 deep, 10 mm tall, centred on the outer face, reading along Y | chosen; orientation delegated |
| Heat vents | honeycomb through the door plate: 6 × 3 hex holes, 5.0 mm across flats, 1.2 mm webs, centre X = 0, Y = +30 | chosen; layout delegated |
| Fit tolerances | lip gap 0.3; hinge gaps 0.4 (knuckles), 0.3 (barrel to wall); socket R1.5 vs stub root R1.3; hook arm 0.25 to phone limit and wall | delegated (PETG values) |
| Scene layout | print layout: door flipped (outer face down) and placed 10 mm to the −X side of the box | chosen |
| Printer | 250 × 210 mm bed, PETG | chosen |
| Exports | one STL per part (`EXPORT = True` in the script) | chosen |
| Project / object names | `s24plus_phone_box`; `S24P_Box`, `S24P_Door` | chosen / delegated |

## Part 1 — `S24P_Box`
- **Construction:** `make_box` X ±45.6, Y ±99.9, Z 0…17.8 → `round_edges` vertical R10 → bottom edges R3 → rim edges R0.6; cavity cutter X ±43.2, Y ±97.5, Z 2.4…22.8 with vertical corners R7.6 and floor edge R1.0, applied with `boolean_diff_apply`.
- **Added (unioned into the one mesh):**
  - Ribs: X = ±(41.7…43.3), Y = −23…−17 and 57…63, Z 2.3…8.4.
  - Phone stop: |X| = 8…43.3, Y −74.5…−72.5, Z 2.3…8.4.
  - End stops: X = 7…13 and −13…−7, Y 96.0…97.6, Z 2.3…8.4.
  - Hinge knuckles 1, 3, 5 (Y = −40.8…−24.8, −8.0…8.0, 24.8…40.8): barrel R2.8 on the axis (X 48.7, Z 17.2) plus a block X 44.25…48.4, Z 11.7…16.9 (stops 0.3 short of the axis in X and Z).
- **Cut:**
  - Hinge sockets on the axis: R1.5 × 2.4 deep in the faces at Y = −24.8, −8.0, 8.0 and 24.8; each with a 2.2 wide channel (2.2 deep) up through the barrel top and a 0.8 funnel.
  - Cable slot: stadium 14 × 8 centred X = 0, Z = 10.1, through the −Y end wall.
  - Cable-end snap grooves: X = ±24 ± 4.5, Y −98.5…−97.3, Z 10.3…12.6.
  - +Y end catch grooves: X = ±24 ± 4.5, Y 97.4…98.25, Z 10.3…12.6.
  - −X side catch grooves: Y = ±35 ± 4.5, X −43.95…−43.1, Z 10.3…12.6.
  - Finger notch: cylinder axis along X, R = 8.75 centred Z = 23.05 (3.5 deep, 14 wide at the rim), Y = 0, X −46.6…−42.8, box only.
- **Object name:** `S24P_Box`.

## Part 2 — `S24P_Door` (closed pose, before the print flip)
- **Construction:** `make_box` X ±45.6, Y ±99.9, Z 17.8…20.2 → vertical corners R10 → top edges R2.0 → bottom edges R0.2.
- **Added (unioned):**
  - Lip: rounded-rectangle frame, outer X ±42.9 / Y ±97.2 (R7.3), 1.2 wide, Z 17.0…18.0.
  - Cable-end snap hooks at X = ±24 (8 wide): profile in YZ (arm Y −97.2…−96.0, from Z 18.0 down to 10.8, tip to Y −98.0 at Z 12.2, ramp down to Z 10.8).
  - +Y end hooks at X = ±24 (8 wide): arm Y 96.25…97.25, tip to Y 97.95; −X side hooks at Y = ±35 (8 wide): arm X −42.95…−41.95, tip to X −43.65; both from Z 18.0 down to 10.8 with the hook top at Z 12.2.
  - Hinge knuckles 2 and 4 (Y −24.4…−8.4 and 8.4…24.4): barrel R2.8 on the axis plus an arm X 45.1…48.7, Z 17.8…20.2, each with a tapered stub (root R1.3 → tip R0.8, 2.2 long) on both end faces, pointing into the neighbouring box knuckles.
- **Cut:** a 0.6 wide slit along each stub axis (X = 48.7 ± 0.3, from the tip 2.0 mm into the knuckle); honeycomb vents (6 × 3, 5.0 across flats, 1.2 webs, centre X 0, Y 30) through the plate; label "S24+" engraved 0.6 deep, size 10, rotated 90° so it reads along Y, centred on the outer face.
- **Object name:** `S24P_Door`.

## Placement
1. Both parts are built in the closed pose (door plate Z 17.8…20.2 above the box).
2. The door is flipped 180° about the Y axis through (X 0, Z 19.0), moved 101.2 mm toward −X (= box width 91.2 + 10 mm gap), then dropped so its lowest point is on Z = 0. Result: outer face on the bed, lip, hooks and knuckles pointing up, hinge knuckles on the door's −X side.
3. The box stays where it is built (its floor on the bed, open side up).
4. No separate hinge pin is needed: assemble by pressing the door down onto the box (see Print notes).

## Print notes
- PETG, 0.4 mm nozzle, 0.2 mm layers, 5–6 perimeters. Box printed open side up; door printed with the outer face down. No supports expected; a few millimetres of bridging at the slot top, the hook undersides and under the hinge barrels.
- Both parts fit the 250 × 210 mm bed (box 97.1 × 199.8, door 97.1 × 199.8; print each along the bed's 210 mm direction).
- **Assembly:** with the door open about 90° or lifted flat above the box, line the four stubs up with the sockets and press the door straight down until the stubs click in; then swing it shut and press around the edge until the hooks click. To remove it, lift the door straight up.
- **Snap values still need a test print.** The hinge click is gentle: about 0.1 mm interference per side; estimated peak strain in the stub halves about 2.6 % (PETG tolerates roughly 3–4 %). Print the hinge test coupon first (`s24plus_hinge_test_build.py`: four box strips with channel widths 2.0 / 2.1 / 2.2 / 2.3 and two door strips), pick the narrowest channel that clicks without white stress marks, and set `CHANNEL_W` here to it.
- **Hook strain:** the +Y and −X hooks deflect about 0.45 mm (estimated strain about 2.2 %); the cable-end hooks about 0.5 mm (about 2.9 %). Both are inside PETG's elastic range; the cable-end hooks have less margin.
- **Fit assumption:** the cavity's inside corner radius is 7.6 mm; with the phone at its furthest position a protector with corners tighter than about R2.5 would touch the corners. The build's clearance check uses a dummy phone with R5 corners.
- The thinnest sections are by design: snap-hook arm and lip 1.2 (extra hooks 1.0), vent webs 1.2, the lip beside each hinge socket about 1.0, hinge stub halves about 1.0 thick at the root, walls 2.4 (1.65 behind the extra catch grooves). The wall checker reads about 0.19 mm at the tapering tip of the snap hooks, which is expected.

## Final object list (2 objects, collection `S24P_Phone_Box`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `S24P_Box`
- `S24P_Door`

## Verification
1. Both objects exist and nothing else is in the scene.
2. Both meshes are watertight (0 open edges, 0 non-manifold edges) with 0 modifiers; exported STLs pair every edge.
3. Bounding boxes: `S24P_Box` 97.1 × 199.8 × 20.0 mm (X × Y × Z, includes the hinge); `S24P_Door` (print pose) 97.1 × 199.8 × 9.4 mm.
4. Assembly checks in the build script (`ASSEMBLY_CHECK = True`):
   - closed door vs box: 0 mm³;
   - dummy phone (166 × 82.4 × 13.4, corners R5) at its nominal place and pushed to each reachable extreme (±0.5 sideways, +0.5 toward +Y, −2.0 toward the stop): 0 mm³ against the box and against the door in every position;
   - hinge swing without hooks at 15°, 45°, 90°, 135°, 180°: 0 mm³ each;
   - latch test, closed door lifted 0.2 / 0.6 / 1.0 mm: 0 / 3.2 / 4.1 mm³ (all six hooks bite once the 0.4 mm groove clearance is used up);
   - drop-in path (door lifted straight up 0…5 mm): 0 mm³ closed, about 0.02 mm³ of snap interference at 1–2 mm, 0 mm³ from 3 mm up.
5. Both parts fit the 250 × 210 mm bed; down-facing area needing support is small (box ≈ 1600 mm², door ≈ 1000 mm²).
