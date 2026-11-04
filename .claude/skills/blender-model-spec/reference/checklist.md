# Decision checklist (cover every row; none may stay "open")

For each area: ask, or confirm it is stated. Skip a row only if it genuinely does not apply *and* you say so in the final summary.

## 1. Purpose and constraints
- What is the object, what does it hold/do, who uses it? Indoor/outdoor, handled/mounted?
- Contents to fit inside (PCB, battery, buttons, display, cables): exact outer dimensions, mounting-hole positions, connector positions, clearance needed around them.
- Printer: bed size (x, y, z), nozzle, layer height, material (PLA/PETG/ABS/resin) — drives min wall, tolerances, overhang limits.

## 2. Overall form
- Overall outer size (L × W × H) and which axis is which. Coordinate system: origin location, Z=0 = print bed.
- One part or several? If several: how they split (lid/base, left/right), which is printed which way up, how they sit relative to each other in the model (side by side offset? assembled?).
- Wall thickness (sides), floor/ceiling thickness, rim/seam design (flat rim, lip, overlap).

## 3. Rounding and finish
- Vertical corner radius, closed-face edge radius, seam-edge radius, inside corner radius (or "sharp"). Chamfer vs round.
- Surface features: text/labels (what text, where, engraved/embossed, size), texture, logos.

## 4. Fastening and joining
- Method: screws (which size: M2/M2.5/M3/M4/M5), heat-set inserts, snap fits, press-fit pins, magnets, glue.
- Screw count and exact positions; pilot vs insert vs clearance; countersink/counterbore/plain; boss outer size and height.
- Alignment features (posts, lips, pins) between parts.

## 5. Openings and holes (each needs size + position + which face)
- Buttons, switches, display window, LEDs, USB/connector cut-outs, cable pass-through, vents (slots/hex), screw-access holes.
- For each: shape, dimensions, centre coordinates, through/blind, which part it is cut into, edge distance ≥ 2 wall thicknesses.

## 6. Internal features
- PCB/board standoffs (positions, height, bore), guide rails, ribs, battery holders, cable clips, nut traps, magnet pockets. Each: position, size, height, bore convention (blind / through).

## 7. Fit and tolerance
- Clearance for sliding / press / snug fits (default constants TOL_PRESS 0.10, TOL_SNUG 0.15, TOL_SLIDE 0.25, TOL_LOOSE 0.40 — confirm which applies where).

## 8. Printing plan
- Print orientation per part, supports allowed? max overhang angle, bed-fit check, splitting oversized parts, minimum wall to enforce in checks.

## 9. Naming and output
- Project folder name and location (default: a new `projects/<name>/` folder under the folder containing `utils_3d.py`); if outside that tree, how the script should find `utils_3d.py` (`UTILS_DIR` setting vs `UTILS_3D_DIR` environment variable).
- Object names (prefix convention), collection name, whether to hide other collections, flip/placement of parts in the scene.
- Outputs wanted: .blend, STL (combined / per part), 3MF; output folder.
- Blender version in use (affects nothing important, but confirm if unsure).

## Conflict checks to run before the gate
- Wall around every boss/hole ≥ 1.2 mm (or user minimum); features not closer than 2 mm to edges/rounds.
- Rounding radii consistent (edge ≤ corner; inner corner = corner − wall for even wall).
- Part fits the bed; overhangs flagged; screw head fits its access hole; bore sizes match the screw table.
- Stacked heights add up (boss tops vs rim vs mating part).
