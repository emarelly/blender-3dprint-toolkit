# Vacuum Bag Adapter, Two-Start Thread — Build Specification (v1.0)

The adapter of [`vacuum_bag_adapter_description.md`](vacuum_bag_adapter_description.md) (v1.3) with the bag valve's real thread. After the prints the user found that the valve's thread is **two-start**: two threads interlaced, starting 180° apart, with 1.0 mm between neighbouring ridges. Build script: `vacuum_bag_adapter_2start_build.py`. It **runs** `vacuum_bag_adapter_build.py` with `OVERRIDES`, so every value not listed here comes from the main spec. Keep both scripts in one folder.

## Decisions
| Parameter | Value | Source |
|---|---|---|
| Socket thread | root Ø26.6, crest Ø24.4 (unchanged), rounded, right-hand, **2 starts 180° apart, 1.0 between neighbouring ridges, lead 2.0 per turn**; `u.thread_radii(..., starts=2)`, Z 52 … 59 (7 mm, 3.5 turns) | stated (two-start, P 1.0) |
| Pitch meaning | 1.0 = axial distance between neighbouring ridges (each thread advances 2.0 per turn) | derived (matches the first measurement of 2.0 = lead) |
| Bag valve (fit check) | Ø23.5–25.1, the same two-start P 1.0 thread | stated |
| Everything else | as the main spec: oval spigot 39.5 × 17.3 (8 mm end arcs), loft, Ø21 shoulder at Z 52, socket Ø30.2, mouth chamfer 0.8, PETG 0.45 / 0.16, oval end on the bed | main spec |
| Collection / object | `VacuumBagAdapter_2Start` / `VBA2S_Adapter` (they don't clash with the single-start adapter, so both can be in one scene) | chosen (two files, "so I have them both") |

## Part — VBA2S_Adapter
- **Construction:** the main build's `build_adapter()` with `THREAD_PITCH = 1.0`, `THREAD_STARTS = 2`. The thread rings are `r = max(12.2 + 1.1 · form(z/1.0 − 2·θ/2π), 14.1 − (59 − z))`.
- **Geometry:** bounding box 39.5 × 30.2 × 59.0, volume 12425.5 mm³. The volume equals the single-start adapter's, because the thread profile's average radius is the same.

## Assembly check
- Dummy valve (`make_valve_dummy`, two-start P 1.0, same phase) seated 0.05 above the shoulder: overlap **0.0 mm³**.

## Print notes
- As the main part: oval end on the bed, no supports, 0.16 layers.
- **Thin ridges:** at 1.0 mm between ridges and 1.1 mm depth, each ridge is about 0.5 mm wide at half height, close to one 0.45 line. `print_report` therefore flags `min_wall` ≈ 0.29 `[BAD]`. That is the ridge tips, which the estimate reads as a thin wall. The flag is expected and accepted. Print the coupler (`vacuum_bag_coupler_description.md`) first: its top is this exact thread. If the ridges print rough, use 0.12 mm layers for the top 8 mm. If the thread binds, raise `THREAD_ADJ` in the main script (e.g. 0.1).
- Use: screw onto the valve by hand until the rim stops on the shoulder (up to about 3½ turns).

## Final object list (1 object, collection `VacuumBagAdapter_2Start`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `VBA2S_Adapter`

## Verification
1. Only `VBA2S_Adapter` in the collection; watertight (0 open edges, 0 non-manifold edges), 0 modifiers.
2. Bounding box 39.5 × 30.2 × 59.0, volume 12425.5 mm³.
3. Valve overlap 0.0 mm³.
4. Exported STL passes `check_stl.py` (0 mismatched edges, 12425.5 mm³).
5. `print_report` flags only `min_wall` ≈ 0.29 (thread ridges, see Print notes).
