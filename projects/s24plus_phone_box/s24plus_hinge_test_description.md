# Samsung Galaxy S24+ Box — Hinge Test Coupon Specification (v1.1)

**v1.1 change:** the coupon no longer keeps its own copy of the hinge numbers and hinge helpers; it loads them from `s24plus_phone_box_build.py` at run time, so it always matches the box (follows the box's v1.2 size).

## Purpose
A small test print for tuning the snap-in stub-pin hinge of `s24plus_phone_box` before printing the full box. The click depends on printer, filament and tolerances, so this coupon prints the hinge in four channel widths so you can pick one.

## General rules
- **Units:** millimetres (`setup_units_mm()`); Z = 0 is the print bed.
- **Library:** built with `utils_3d.py` (found via `UTILS_DIR` / `UTILS_3D_DIR` / parent folders); every Boolean is applied, no modifiers remain.
- **Hinge definition:** the script executes the SETTINGS and local-helpers sections of `s24plus_phone_box_build.py` (same folder) and uses its values and its `knuckle_ranges`, `make_stub`, `cut_stub_slit`, `cut_socket` functions. Only the channel width is varied.
- **Collection:** `S24P_Hinge_Test`.
- **Files:** `s24plus_hinge_test_description.md` (this spec) and `s24plus_hinge_test_build.py`, next to the main box files.
- **Printer / material:** same as the box: 250 × 210 mm bed, PETG.

## Decisions
| Parameter | Value | Source |
|---|---|---|
| What is tuned | the socket channel width (`CHANNEL_W`) | derived (the only snap value still open) |
| Channel width variants | 2.0, 2.1, 2.2, 2.3 mm (one box strip each; 2.4 and above give no interference, i.e. no click) | derived |
| Door strips | 2 identical (a spare in case one deforms) | delegated |
| Knuckles on the coupon | box / door / box (indices 0, 1, 2 of the real hinge: Y −40.8…−24.8, −24.4…−8.4, −8.0…8.0), so both stubs of the door knuckle are tested | delegated |
| Box strip | one L-shaped profile extruded along Y −42.0…9.2: wall X 43.2…45.6 from Z 9.7 to the rim at 17.8, plus a 2.4 thick foot X 35.75…45.6 (derived from the box: wall starts 2 mm below the knuckle block, foot reaches 7.45 inboard); box knuckles and sockets exactly as in the box; channel width engraved (0.5 deep, 5 mm tall) on the foot, reading along Y | delegated |
| Door strip | plate X 32.75…45.6, Y −42.0…9.2, Z 17.8…20.2 with one door knuckle (barrel, arm, two slit stubs) exactly as in the box | delegated |
| Print layout | box strips side by side, 20 mm pitch, lowered onto the bed (−9.7); door strips flipped (outer face down) 8 mm beyond the last box strip | delegated |
| Wall check threshold | 0.9 mm (same as the box) | delegated |

## Parts
- **Box strips** `S24P_HingeTest_Box_CW20`, `…_CW21`, `…_CW22`, `…_CW23` (channel 2.0 / 2.1 / 2.2 / 2.3).
- **Door strips** `S24P_HingeTest_Door_A`, `S24P_HingeTest_Door_B`.

## Placement
1. Box strips and the first door strip are built in the closed pose (same coordinates as the full box) and tested.
2. The second door strip is a copy of the first.
3. Box strips are lowered onto the bed and spaced 20 mm apart along X.
4. Door strips are flipped 180° about Y through Z = 19.0, dropped to the bed and placed 8 mm beyond the last box strip, 20 mm apart.

## How to use the printed coupon
1. Press a door strip straight down onto each box strip until the stubs click into the sockets.
2. Swing the door strip through its range, then lift it gently. Note which channel widths go in without force, click, hold the door when lifted, and show no white stress marks or cracks after several cycles.
3. Choose the narrowest channel that passes, set `CHANNEL_W` in `s24plus_phone_box_build.py` to it (and update its spec), and rebuild.

## Print notes
- PETG, 0.4 mm nozzle, 0.2 mm layers, 5–6 perimeters, no supports needed.
- The strips print in a few minutes each; the finest tuning is the 0.1 mm steps in channel width.

## Final object list (6 objects, collection `S24P_Hinge_Test`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `S24P_HingeTest_Box_CW20`
- `S24P_HingeTest_Box_CW21`
- `S24P_HingeTest_Box_CW22`
- `S24P_HingeTest_Box_CW23`
- `S24P_HingeTest_Door_A`
- `S24P_HingeTest_Door_B`

## Verification
1. All six objects exist and nothing else is in the scene.
2. Every mesh is watertight (0 open edges, 0 non-manifold edges) with 0 modifiers; exported STLs pair every edge.
3. Coupon check (`ASSEMBLY_CHECK = True`), per channel width: closed overlap 0 mm³; swing at 45°, 90° and 180° 0 mm³; drop-in path (door strip lifted 0…5 mm): 0 mm³ closed and a small interference while the stubs pass the channel (2.0: about 0.11 mm³, 2.1: 0.045, 2.2: 0.011, 2.3: 0.001).
4. The hinge values are read from `s24plus_phone_box_build.py`, so they cannot differ from the box.
5. The wall check reads about 0.4–0.5 mm on the strips: the thin walls between the engraved digits (box strips) and the tapering tips of the slit stubs (door strips). These are expected; the designed sections are the socket lip (about 1.0 mm) and the stub halves (about 0.9 mm).
