# Material profiles: suggested design parameters

The skill reads this table to **suggest** the material-driven parameters (Phase 1, "Material and process").
The user confirms or changes them; the confirmed values go into the spec's Decisions table (source
`suggested from material, confirmed`) and into the build's SETTINGS block as named values.

All values are **typical starting points for a tuned FDM printer (0.4 mm nozzle) or a standard resin
printer**, not measured data. If the user has calibrated values (a tolerance test print, their own
clearances), those win. Say so when you present them.

## 1. Inputs to ask for (one AskUserQuestion call)

| Input | Options to offer |
|---|---|
| Material | PLA / PETG / ABS-ASA / Nylon (PA) / TPU / Resin (standard or tough) |
| Nozzle → line width | 0.4 → 0.45 (Recommended) / 0.6 → 0.65 / 0.25 → 0.3 (resin: n/a) |
| Layer height | 0.2 / 0.16 / 0.12 (fine threads, small text) / resin 0.05 |
| Use conditions | indoor room temperature / near heat (lamp, car, electronics: give °C) / outdoor (sun, rain) / carries load for a long time (hanging, clamped) / flexes (snaps, clips) — multi-select |

## 2. Values derived from nozzle and layer height (all materials)

| Parameter (SETTINGS name) | Rule | 0.4 nozzle, 0.2 layer |
|---|---|---|
| `LINE_W` | nozzle + ~0.05 | 0.45 |
| `MIN_WALL` (thinnest wall allowed) | 2 × `LINE_W` | 0.9 |
| `WALL` (structural wall, suggestion) | material table: n × `LINE_W` | e.g. 4 × 0.45 = 1.8 |
| Wall rounding | every wall a whole number of line widths (avoid 1.0 with 0.45 lines: slicer leaves a gap or a thin fill) | 0.9 / 1.35 / 1.8 / 2.25 |
| `LAYER_H` | as chosen | 0.2 |
| Vertical sizes | floors, ceilings, steps, text depth as multiples of `LAYER_H` | floor 1.2 = 6 layers |
| Min. feature (pin, rib, text stroke) | ≥ 2 × `LINE_W` wide, ≥ 3 × `LAYER_H` high | 0.9 wide, 0.6 high |
| Min. printed thread pitch | ≥ 5 × `LAYER_H` | 1.0 at 0.2 layers; 0.75 at 0.12–0.16 |
| Floor / ceiling | ≥ 4 solid layers (6 for watertight) | 0.8 (1.2) |

## 3. Material table (FDM unless noted)

| Parameter | PLA | PETG | ABS / ASA | Nylon (PA) | TPU (95A) | Resin (standard / tough) |
|---|---|---|---|---|---|---|
| Structural wall (`WALL`) | 4 lines | 4 lines | 4 lines | 4 lines | 3–4 lines (1.2+) | 1.5 (0.8 min) |
| `TOL_PRESS` (per fit, on diameter) | 0.10 | 0.15 | 0.15 | 0.20 | interference −0.2 | 0.05 |
| `TOL_SNUG` | 0.15 | 0.20 | 0.20 | 0.25 | 0.0 | 0.10 |
| `TOL_SLIDE` | 0.25 | 0.30 | 0.30 | 0.35 | 0.30 | 0.15 |
| `TOL_LOOSE` | 0.40 | 0.45 | 0.45 | 0.50 | 0.50 | 0.25 |
| Hole compensation (`HOLE_COMP`, add to modelled hole Ø) | +0.15 | +0.2 | +0.3 (shrinks) | +0.3 | +0.3 | +0.05 |
| Printed thread clearance (per side) | 0.15 | 0.2 | 0.25 | 0.25 | not for threads | 0.1 |
| Max. use temperature (keep 10 °C margin) | 50 °C | 65 °C | 85 °C (ASA 90) | 80 °C | 60 °C | 50 / 60 °C |
| Outdoor / UV | no (creeps, softens in sun) | yes, moderate | ASA yes, ABS no (yellows, brittle) | yes if dried; absorbs water | ok | no (keeps curing, gets brittle) |
| Creep under constant load | high | moderate | low | moderate | high | moderate |
| Max. overhang (`OVERHANG_DEG` from vertical) | 50 | 45 | 45 | 45 | 40 | needs supports per slicer |
| Max. bridge | 20 mm | 15 mm | 15 mm | 10 mm | 5 mm | n/a |
| Snap fit: allowable strain | 2 % (brittle: long thin arms) | 4 % | 3.5 % | 7 % (best for snaps) | the part flexes itself: no hooks | 1 % / 3 % (standard: avoid snaps) |
| Bed-edge chamfer (`BED_CHAMFER`, elephant's foot) | 0.4 | 0.4 | 0.5 | 0.5 | 0.3 | 0 (raft) |
| Large flat parts | ok | ok | warps: corner radius ≥ 3, brim, avoid long sharp corners | warps: brim, enclosure | ok | hollow + drain holes |
| Living hinge | no | short life | ok-ish (ABS) | yes | yes | no |

## 4. How the use conditions change the suggestion

- **Heat** above the material's max. use temperature → do not just warn: suggest a material that fits (PETG up to ~65 °C, ASA up to ~90 °C) and more distance or an air gap to the heat source.
- **Outdoor** with PLA or standard resin → suggest PETG or ASA. Water: 6 solid layers top/bottom, walls ≥ 3 lines, a drain path or a seal (O-ring groove) where water collects.
- **Long-term load** (hanging, clamped by screws, threads carrying weight) → `WALL` +1 line around the loaded features, ribs, coarser/larger threads or heat-set inserts instead of printed threads for repeated assembly; with PLA or TPU say that it creeps.
- **Flexing** (snaps, clips) → arm length from the strain limit: for a cantilever hook, deflection y, arm thickness t, length L, strain ≈ 1.5 · t · y / L² ≤ allowable strain → L ≥ √(1.5 · t · y / strain). Suggest nylon or PETG over PLA when the arm would not fit.
- **Load direction vs layers** → layers split easily; orient hooks, pins and threads so the load does not pull layers apart. If that conflicts with the print orientation, ask.

## 5. Conflict checks (run before the gate)

- Every wall is ≥ `MIN_WALL` and a whole number of line widths (within 0.05).
- Floors, ceilings, steps and text depth are multiples of `LAYER_H` (within 0.02).
- Printed thread pitch ≥ 5 × `LAYER_H`.
- Use temperature ≤ the material's max. use temperature.
- Snap arms within the allowable strain (formula above).
- Bridges and overhangs within the material's limits, or a support/orientation plan.
- Outdoor + UV-sensitive material, or long-term load + high-creep material: flagged and answered.
