# Vacuum Bag Adapter — Test Rings (v1.2)

Two short test prints that check both fits of [`vacuum_bag_adapter_description.md`](vacuum_bag_adapter_description.md) before the full part is printed (they use about a third of its material). Build script: `vacuum_bag_adapter_test_build.py`. v1.2 follows the main spec's v1.2 (spigot 39.5 × 17.3 with 8 mm end arcs, thread copied from the bag's cover at pitch 1.5).

## General rules
- Units, material (PETG, 0.45 line, 0.16 layers) and every dimension come from the main spec. The script **loads** `vacuum_bag_adapter_build.py` (from its `SETTINGS (match the spec)` line up to its `PART` line: settings, derived values, the `oval_ring` / `circ` / `spigot_rings` / `socket_thread_rings` / `make_valve_dummy` helpers) at run time, so the rings always match the adapter. Keep both scripts in one folder.
- Both rings are `u.make_ring_tube` meshes (no Boolean), printed as they sit in the adapter, side by side on the bed.
- **Collection:** `VacuumBagAdapter_Test`.

## Decisions
| Parameter | Value | Source |
|---|---|---|
| Test parts | the oval side and the thread side, separately | stated |
| Oval test height | 10 mm | stated |
| Thread test | full 7 mm thread + mouth chamfer on a 3.2 mm base ring (bore Ø21) whose top is the flat seal shoulder; total 10.2 (shoulder at 20 layers of 0.16, the closest whole layer to the 10 mm the user named) | stated ("the thread side too") / derived |
| Thread test bottom edge | 0.4 × 45° bed chamfer (elephant's foot) | derived from the material set |
| Layout | oval ring at X = 0, thread ring at X = 19.75 + 8 + 15.1 = 42.85, both on Z = 0 | derived |

## Parts
- `VBA_Test_Oval`: `spigot_rings(10)`: the adapter's Z 0 … 10. Outside 39.5 × 17.3 (end arcs 8 deep) with the 1.0 lead-in chamfer at Z 0, inside 35.9 × 13.7. Bounding box 39.5 × 17.3 × 10.0, volume 1627.9 mm³.
- `VBA_Test_Thread`: outside Ø30.2 (0.4 chamfer at Z 0), bore Ø21 for Z 0 … 3.2, flat shoulder at Z 3.2, then `socket_thread_rings(3.2, 10.2)`: internal round thread root Ø26.6 / crest Ø24.4, P 1.5, right-hand, 0.8 mouth chamfer. Bounding box 30.2 × 30.2 × 10.2, volume 2530.8 mm³.

## How to use the results
- **Oval ring:** it should push into the vacuum by hand and hold by friction. Too tight: raise `SPIGOT_ADJ` (e.g. 0.2 makes it 0.1 smaller per side). Too loose: lower it (e.g. −0.2).
- **Thread ring:** it should screw onto the valve by hand, and the valve rim should stop flat on the shoulder. Binds: raise `THREAD_ADJ` (e.g. 0.1). Wobbles: lower it (e.g. −0.1).
- Change the value in `vacuum_bag_adapter_build.py` (and the main spec), rerun this script, and reprint only the ring that changed.

## Final object list (2 objects, collection `VacuumBagAdapter_Test`)
<!-- verify_model.py parses this section: one backticked exact object name per bullet -->
- `VBA_Test_Oval`
- `VBA_Test_Thread`

## Verification
1. Both objects exist, nothing else in the collection; watertight, 0 modifiers.
2. Fit check (same dummy valve as the main build): thread ring vs the male inlet's thread seated on the shoulder 0.0 mm³. (The oval is copied from an adapter that fits, so it has no dummy.)
3. Exported STLs pass `check_stl.py`.
