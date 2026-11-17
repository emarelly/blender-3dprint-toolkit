# Vacuum Bag Coupler — Build Specification (v1.0)

A short threaded ring that lets the already printed adapter ([`vacuum_bag_adapter_description.md`](vacuum_bag_adapter_description.md): single-start P 1.5 socket) screw onto the bag valve, whose real thread is two-start P 1.0. Stack: vacuum → old adapter → **coupler** → bag valve. Build script: `vacuum_bag_coupler_build.py`. It loads the main build's SETTINGS-to-PART section (diameters, wall, material, `circ` / `socket_thread_rings` / `make_valve_dummy`) at run time. Keep the scripts in one folder.

## General rules
- **Units:** mm. **Axis** Z, Z = 0 on the print bed (male end), bore on X = Y = 0. Modelled in its print orientation.
- **Library:** one `u.make_ring_tube` (rings, radius per angle), no Boolean, no modifier.
- **Material:** as the main spec (PETG, line 0.45, layers 0.16, `WALL` 1.8, `MIN_WALL` 0.9, overhang limit 45°).
- **Collection:** `VacuumBagCoupler`.

## Decisions
| Parameter | Value | Source |
|---|---|---|
| Layout | male end on the bed, female socket on top, bore Ø21 all the way through, 45° chamfer between them | chosen (first suggested option) |
| Male thread | the old adapter's thread: single-start, P 1.5, rounded, right-hand; Ø23.5 root / Ø25.1 crest (copies the bag valve's inlet, which the old socket was sized for: 0.45 radial gap at its crest) | chosen |
| Male length | Z 0 … 7.5 full thread (the old socket's thread is 7 mm, so the end face reaches its shoulder) | derived |
| Male lead-in | 0.4 × 45° from the root at Z 0 (Ø22.7 at the bed, also the elephant's-foot chamfer); the end face (Ø21 … 22.7) seals on the old adapter's Ø21 shoulder | derived |
| Outer chamfer | 45° cone from the male crest R 12.55 at Z 7.5 to the socket's outside R 15.1 at Z 10.05 (faces down at exactly 45°: no support) | derived |
| Seal shoulder | flat, facing up, Ø21 → crest Ø24.4 at Z 10.08 (63 layers of 0.16) | derived |
| Female thread | the bag valve's real thread: root Ø26.6, crest Ø24.4, rounded, right-hand, **2 starts 180° apart, 1.0 between neighbouring ridges (lead 2.0)**, Z 10.08 … 17.08 (7 mm), 0.8 mouth chamfer (Ø28.2 at the top) | stated (P 1.0, two-start); diameters as the main spec |
| Socket outside | Ø30.2 | main spec |
| Total height | 17.08 | derived |
| Output | `EXPORT = True` → `exports/VBC_Coupler.stl` | chosen |

## Part — VBC_Coupler
- **Outer rings** (Z 0 … 10.05, 16 per 1.5 mm): `r = min(15.1, 11.35 + z, max(11.75 + 0.8 · form(z/1.5 − θ/2π), 12.55 + (z − 7.5)))`, then Z 17.08 circle R 15.1.
- **Inner rings:** Z 0 and Z 10.08 circle R 10.5, then (flat step) `socket_thread_rings(10.08, 17.08, 1.0, 2)`: `r = max(12.2 + 1.1 · form(z/1.0 − 2·θ/2π), 14.1 − (17.08 − z))`.
- **Geometry:** 30.2 × 30.2 × 17.08, volume 2882.3 mm³.
- **Object name:** `VBC_Coupler`

## Assembly check (`ASSEMBLY_CHECK = True`, dummies deleted afterwards)
- Dummy old-adapter socket (single-start P 1.5, root 26.6 / crest 24.4, its mouth chamfer) with its shoulder 0.05 below the coupler's end face, same thread phase: overlap **0.0 mm³**.
- Dummy bag valve (`make_valve_dummy`, two-start P 1.0) seated 0.05 above the coupler's shoulder: overlap **0.0 mm³**.
- Positive control: the old socket moved 1 mm up into the coupler collides (98.5 mm³).

## Print notes
- Male end on the bed, female end up, no supports, 0.16 layers. The outer chamfer is at the 45° limit.
- **Thin ridges:** the female thread's ridges at 1.0 spacing are about 0.5 mm wide, close to one 0.45 line. `print_report` flags `min_wall` ≈ 0.28 `[BAD]`, and that is the ridge tips. The flag is expected and accepted. The coupler is also the test print for the two-start adapter's thread. If the thread binds on the valve, raise `THREAD_ADJ` in the main script (e.g. 0.1). If the ridges print rough, try 0.12 mm layers.
- Use: screw the coupler into the old adapter until its end face stops on the shoulder (about 4½ turns). Then screw that pair onto the valve until the valve rim stops on the coupler's shoulder (up to about 3½ turns).

## Final object list (1 object, collection `VacuumBagCoupler`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `VBC_Coupler`

## Verification
1. Only `VBC_Coupler` in the collection; watertight (0 open edges, 0 non-manifold edges), 0 modifiers.
2. Bounding box 30.2 × 30.2 × 17.08, lowest point Z = 0, volume 2882.3 mm³.
3. Assembly check: old socket 0.0 mm³, valve 0.0 mm³, control > 0.
4. Exported STL passes `check_stl.py` (0 mismatched edges, volume equal to Blender's).
5. `print_report` flags only `min_wall` ≈ 0.28 (thread ridges, see Print notes).
