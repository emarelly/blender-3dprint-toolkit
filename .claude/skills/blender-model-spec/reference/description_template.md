# <Object name> — Build Specification (v1.0)

## Purpose
<One or two sentences: what the object is and what it must hold/do. Quote the user's own description.>

## General rules
- **Units:** millimetres. Scene unit system METRIC, scale 0.001, length unit MILLIMETERS (`setup_units_mm()`).
- **Coordinate system:** <origin; X = ..., Y = ..., Z = up, Z=0 is the print bed>.
- **Library:** all geometry is built with `utils_3d.py` (found by the script via `UTILS_DIR` / `UTILS_3D_DIR` / parent folders); every Bevel/Boolean is applied, no modifiers remain.
- **Files:** `<project folder>/<name>_description.md` (this spec) and `<project folder>/<name>_build.py`.
- **Collection:** `<CollectionName>`.
- **Printer / material:** <bed x×y×z, nozzle, layer height, material>.

## Decisions
Every value below is final. Source: **stated** (user said it), **chosen** (user picked from options), **delegated** (user told Claude to decide; reason given).

| Parameter | Value | Source |
|---|---|---|
| Mesh structure | one mesh per printed part / every feature its own mesh (which ones) | chosen |
| Scene layout at start | ready for print / assembled (`LAYOUT = "print"` / `"assembled"`; the other is one setting away) | chosen |
| Wall thickness | 2.5 mm | chosen |
| ... | ... | ... |

## Part 1 — <PartName>
- **Construction:** `u.make_hollow_box(...)` / ... with the exact arguments.
- **Geometry:** outer X <min>…<max>, Y <min>…<max>, Z <min>…<max>; wall/floor; rounding radii.
- **Features:** table of holes/openings — | Feature | Shape | Size | Centre (X, Y) | Z range | Cut into |
- **Object name:** `<ExactName>`

## Part 2 — <PartName>
...

## Secondary parts
Table: | Object name | Type | Position (X, Y) | Z range | Outer size | Bore (size, blind/through) |

## Placement (two layouts, setting `LAYOUT`)
- **Assembled** (`LAYOUT = "assembled"`): the pose every part is modelled in — <how the parts sit together>.
- **Ready for print** (`LAYOUT = "print"`): <rotation/flip and offset applied to each part group, in order, so every part lies on Z = 0 in its print orientation, side by side with <gap> mm between parts>.
- Default when the script runs: <print / assembled> (chosen).
- <If every feature is its own mesh: the parts of one printed part move as a group; `MODE = "export"` fuses copies of the current parts into one mesh per printed part (`u.fuse_copies`), lays them out for print if needed and writes the STLs.>

## Print notes
- Orientation per part, supports (yes/no and where), fit tolerances used (`TOL_*`), known risks.

## Final object list (N objects, collection `<CollectionName>`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `<ExactName1>`
- `<ExactName2>`

## Verification
1. Every object in the list exists and nothing else is in the scene.
2. Every mesh is watertight (0 open edges, 0 non-manifold edges) and has 0 modifiers.
3. <Dimension checks: e.g. `<Part>` bounding box = X × Y × Z.>
4. <Wall/bed/overhang checks the user cares about, with the thresholds.>
