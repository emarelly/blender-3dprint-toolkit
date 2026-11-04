# RC Remote Control Case — Modifier-Based Build Prompt (v1.3 / As-Built)

## Why this version exists

This is the as-built update to **v1.2** (`rc_case_modifier_mesh_prompt_v1_2.md`), folding in every clarification and correction made while actually building the model in Blender. v1.2 left several things ambiguous or internally contradictory (see "Resolved ambiguities" below); this version removes that ambiguity so the model can be rebuilt from this document alone, with no clarifying questions needed.

Everything from v1.2's own "Why this version exists" section still applies: the main shell of each half is a single mesh object built from one box primitive, with Bevel and Boolean modifiers doing the rounding and cutting, then applied/baked. Secondary parts (bosses, posts, rails, supports, collars, and now the joint posts) remain separate, non-unioned objects.

## General rules

- **Units:** millimetres throughout. Scene unit system METRIC, unit scale 0.001, length unit MILLIMETERS.
- **Main shell construction, per half (Lower and Upper):**
  1. Start from a single stock box primitive sized to the shell's full outer footprint and height.
  2. Add a **Bevel modifier** (Limit Method: Angle, width 0.6&nbsp;mm, 4 segments) and apply it — rounds all twelve edges of the solid box before anything is cut into it.
  3. Add a **Boolean modifier (Difference)** against a plain box cutter to hollow out the interior cavity, and apply it.
  4. For Upper only, add further **Boolean modifiers (Difference)** against cylinder cutters for the six button holes and the two screw-access holes through the ceiling, applying each in turn.
  5. Add the wire-entry-hole cut (see "Wire-entry hole" below) to both Lower and Upper, applying each.
  6. The result is one mesh object per half — `RC_Case_Lower` and `RC_Case_Upper` — with zero modifiers remaining in the stack.
- **Secondary parts stay separate:** screw bosses, mounting posts, guide rails, PCB supports, button collars, and the 4 corner joint posts are each their own object (bosses/posts/supports/collars/joint-posts use their own small Boolean-modifier cut where a bore is called for — none of these objects are unioned into the main shell).
- **Coordinate system, no rotation needed:** both halves are modeled in their natural resting orientation — Lower with its floor at the bottom (Z=0) and open top, Upper with its ceiling on top and open skirt at the bottom. Upper is placed beside Lower purely by translating every Upper-group object by ΔX = −80&nbsp;mm; no flips or rotations anywhere.
- **Joint — corner posts, not a sleeve fit:** the two halves are now the **same outer footprint** (see Step 3) and join via 4 solid square posts built onto Lower, at its 4 corners, rather than a telescoping sleeve. See "Step 2b" below for the finalized geometry — this replaces v1.2's underspecified "4 2×2mm rectangle pipe" description.
- **Collection:** all objects live in a Blender collection named `RC_Remote_Case_Modifier`.

## Step 1 — Lower shell

- Outer footprint: X half-extent 28.75&nbsp;mm (full width 57.5&nbsp;mm), Y half-extent 87.5&nbsp;mm (full depth 175&nbsp;mm). Height Z 0 to 15&nbsp;mm.
- Build as a plain box, then apply the Bevel modifier described above.
- Cavity cutter (Boolean Difference, applied): box X ±26.25, Y ±85, Z 2.5 to 20 (Z=20 overshoots for a clean open-top cut). Leaves a 2.5&nbsp;mm floor and 2.5&nbsp;mm walls on all sides.
- Object name: `RC_Case_Lower`.

## Step 2 — Lower secondary parts

- **Screw bosses** `RC_Boss_Lower_PosY` / `RC_Boss_Lower_NegY`: cylinder outer radius 3.0&nbsp;mm, Z 2.5 to 13.0, at (X=0, Y=±69). Central pilot bore radius 1.6&nbsp;mm, **blind at the base (no overshoot below Z=2.5), open through the top with a 0.5&nbsp;mm overshoot** (cutter Z 2.5 to 13.5) — a self-tapping pilot hole, not a through-hole.
- **Mounting posts** `RC_Post_Lower_PosY` / `RC_Post_Lower_NegY`: cylinder outer radius 4.15&nbsp;mm, Z 2.5 to 12.5, at (X=0, Y=22.75) and (X=0, Y=−32.75). Bore radius 2.15&nbsp;mm, same blind-base / open-top-with-0.5mm-overshoot convention as the bosses (cutter Z 2.5 to 13.0).
- **Guide rails** `RC_Rail_Lower_PosX` / `RC_Rail_Lower_NegX`: plain boxes (no cut), 1&nbsp;mm wide, at X=±18 (half-width 0.5&nbsp;mm either side), Y ±85, Z 2.5 to 6.4.

## Step 2b — Corner joint posts (final geometry)

Four solid square posts, one at each of Lower's four inner corners, replacing v1.2's ambiguous "4 2×2mm rectangle pipe" wording:

- **Cross-section:** 2&nbsp;mm × 2&nbsp;mm square, solid (not hollow — "pipe" in v1.2 was a loose figure of speech, confirmed during the build).
- **XY placement — flush against Lower's inner cavity wall from the inside**, not centered in the wall material: each post's two outer faces sit exactly flush with the cavity's inner wall faces (X=±26.25, Y=±85) at that corner, extending 2&nbsp;mm inward into the cavity. Concretely, per corner (all four are the same shape, mirrored):

  | Post | X range | Y range |
  |---|---|---|
  | `RC_JointPost_Lower_PosXPosY` | 24.25 to 26.25 | 83.0 to 85.0 |
  | `RC_JointPost_Lower_PosXNegY` | 24.25 to 26.25 | −85.0 to −83.0 |
  | `RC_JointPost_Lower_NegXPosY` | −26.25 to −24.25 | 83.0 to 85.0 |
  | `RC_JointPost_Lower_NegXNegY` | −26.25 to −24.25 | −85.0 to −83.0 |

- **Z range: 0 to 19&nbsp;mm** — the post runs the *full height of Lower's cavity*, connected to the floor at Z=0, and rises 4&nbsp;mm above Lower's top rim (Z=15) to Z=19. (v1.2 only said "4mm rise above the lower pipe edge"; it did not say the post also needed to reach down to the floor — this was added during the build so the post is structurally connected to Lower rather than floating inside the cavity.)
- **No matching cut on Upper.** The posts are not hollow and Upper gets no socket/hole for them — they simply project up into Upper's open cavity for alignment when assembled. (This was one of three options considered — solid+socket, hollow+socket, or posts-only — and posts-only-no-cut was the one chosen.)
- These 4 objects are part of the Lower group and are **not** translated by the Step 5 ΔX shift.

## Step 3 — Upper shell

- **Outer footprint is now identical to Lower's**: X half-extent 28.75&nbsp;mm, Y half-extent 87.5&nbsp;mm (full 57.5 × 175&nbsp;mm, same as Step 1). Height Z 0 to 14&nbsp;mm (unchanged from v1.2 — only the footprint changed, not the height).

  *(v1.2 still listed Upper's old sleeve-fit footprint — X half-extent 31.55, Y half-extent 90.3 — left over from v1.1, while its own Joint section said "the 2 part[s] should be identical in size." Those two statements contradicted each other. Confirmed during the build: the parts are identical in outer footprint; the old sleeve-fit numbers and the 0.3mm clearance concept are dropped entirely, replaced by the corner-post joint above.)*
- Build as a plain box, then apply the same Bevel modifier settings (width 0.6&nbsp;mm, 4 segments, angle limit).
- Cavity cutter (Boolean Difference, applied): box X ±26.25, Y ±85, Z −2 to 11.5 (Z=−2 overshoots for a clean open-bottom cut). Leaves a 2.5&nbsp;mm ceiling and 2.5&nbsp;mm walls — same wall thickness as Lower, now that the footprints match.
- **Button holes** (×6, Boolean Difference, applied one at a time): cylinder radius 7.0&nbsp;mm, Z 11.3 to 14.2 (overshoots both faces of the 2.5&nbsp;mm ceiling), at:

  | Hole | X | Y |
  |---|---|---|
  | 1 | 0 | 9.75 |
  | 2 | −16.1 | 5.55 |
  | 3 | 16.1 | 13.95 |
  | 4 | 0 | 35.75 |
  | 5 | −16.1 | 31.55 |
  | 6 | 16.1 | 39.95 |

- **Screw-access holes** (×2, Boolean Difference, applied): cylinder radius 3.2&nbsp;mm, Z 11.3 to 14.2, at (X=0, Y=±69).
- Object name: `RC_Case_Upper`.

## Step 4 — Upper secondary parts

- **Screw bosses** `RC_Boss_Upper_PosY` / `RC_Boss_Upper_NegY`: cylinder outer radius 4.5&nbsp;mm, Z 3.5 to 11.5, at (X=0, Y=±69), aligned under the screw-access holes. Bore radius 1.8&nbsp;mm, **through-hole — open at both ends with a 0.5&nbsp;mm overshoot each** (cutter Z 3.0 to 12.0), so a screw passes fully through the boss and continues down into the Lower boss's pilot hole.
- **PCB supports** `RC_Support_Upper_L1/R1/L2/R2`: cylinder outer radius 2.5&nbsp;mm, bore radius 1.0&nbsp;mm, Z 1.5 to 11.5, **blind at the base, open through the top with a 0.5&nbsp;mm overshoot** (cutter Z 1.5 to 12.0) — same convention as the Lower bosses/posts. At:

  | Support | X | Y |
  |---|---|---|
  | L1 | −16.1 | 18.55 |
  | R1 | 16.1 | 26.95 |
  | L2 | −16.1 | −35.45 |
  | R2 | 16.1 | −27.05 |

- **Button collars** `RC_Collar_Hole1..6`: cylinder outer radius 8.5&nbsp;mm, bore radius 7.0&nbsp;mm (clears the 6&nbsp;mm hole with margin), Z 8.0 to 11.5, **through-hole — open at both ends with a 0.5&nbsp;mm overshoot each** (cutter Z 7.5 to 12.0), since a collar's whole purpose is a straight pass-through for the button shaft. Centred on each of the six button hole positions above.

## Wire-entry hole (split across the seam)

A ⌀9.7&nbsp;mm hole (4.85&nbsp;mm radius) for a cable, centered X=0, at the far end wall Y=−87.5 (the end opposite the 6 button holes), bored straight through the 2.5&nbsp;mm end wall (axis along Y):

- **Implementation used:** a single full cylinder cutter, radius 4.85&nbsp;mm, 48 vertices, axis rotated to run along world Y (rotate 90° about X), spanning Y −90 to −83 (overshoots both the outer and inner wall faces by several mm for a clean cut).
- For **Lower**, the cutter is centered at Z=15 — Lower's own top rim. Since Lower's solid material only exists at Z ≤ 15, the Boolean difference automatically leaves only the **lower half** of the circle cut into the wall (Z 10.15 to 15), with nothing to remove above the rim.
- For **Upper**, the cutter is centered at Z=0 (in Upper's own local, pre-shift coordinates) — Upper's own bottom/skirt rim. Since Upper's solid material only exists at Z ≥ 0, the cut automatically leaves only the **upper half** of the circle (Z 0 to 4.85).
- No separate half-cylinder or wedge cutter is needed — using a full cylinder centered exactly on each half's own open edge is sufficient, because Boolean difference can't remove material that isn't there. This is simpler than modelling two half-circle profiles by hand and was the method actually used.
- Together, when the halves are assembled (Upper's bottom rim against Lower's top rim), the two notches form one complete round ⌀9.7&nbsp;mm hole across the seam.

## Step 5 — Final placement

- Lower and everything in Step 2 / Step 2b (including the 4 corner joint posts) stays at its built coordinates.
- Upper (`RC_Case_Upper`) and everything in Step 4 (`RC_Boss_Upper_*`, `RC_Support_Upper_*`, `RC_Collar_Hole*`) is translated by ΔX = −80&nbsp;mm, ΔY = 0, ΔZ = 0 — a pure sideways shift, no rotation.

## Final object list (24 objects, collection `RC_Remote_Case_Modifier`)

`RC_Case_Lower`, `RC_Boss_Lower_PosY`, `RC_Boss_Lower_NegY`, `RC_Post_Lower_PosY`, `RC_Post_Lower_NegY`, `RC_Rail_Lower_PosX`, `RC_Rail_Lower_NegX`, `RC_JointPost_Lower_PosXPosY`, `RC_JointPost_Lower_PosXNegY`, `RC_JointPost_Lower_NegXPosY`, `RC_JointPost_Lower_NegXNegY`, `RC_Case_Upper`, `RC_Boss_Upper_PosY`, `RC_Boss_Upper_NegY`, `RC_Support_Upper_L1`, `RC_Support_Upper_R1`, `RC_Support_Upper_L2`, `RC_Support_Upper_R2`, `RC_Collar_Hole1`, `RC_Collar_Hole2`, `RC_Collar_Hole3`, `RC_Collar_Hole4`, `RC_Collar_Hole5`, `RC_Collar_Hole6`.

(v1.2's list only had 20 objects and predates the 4 corner joint posts, which were added during the build. Object names in the actual `.blend` file may carry a `_M` suffix on any part where it would otherwise collide with an identically-named object already in the file.)

## Resolved ambiguities and clarifications from the build

These points were underspecified or contradictory in v1.1/v1.2 and were resolved during the actual build. They're recorded here so a future rebuild from this document alone reproduces the same result without needing to ask again:

1. **Sleeve fit vs. identical footprint (user-confirmed).** v1.1 gave Upper a larger outer footprint than Lower (a telescoping sleeve joint, 0.3mm clearance). v1.2's Joint section said the two halves "should be identical in the size" but left Step 3's old sleeve-fit numbers in place uncorrected. Confirmed: Lower and Upper now share the exact same outer footprint (57.5 × 175mm); the sleeve/clearance concept is fully retired.
2. **Corner joint post mechanism (user-confirmed).** v1.2 called for "4 2×2mm rectangle pipe" posts "to fit to the upper part as a holder" without saying whether they're hollow, whether Upper gets a matching socket, or exactly where within the corner they sit. Confirmed: solid (not hollow) posts, no matching cut/socket in Upper.
3. **Corner post XY placement (user-corrected).** First built centered within the 2.5mm corner wall's own cross-section. Corrected: posts sit flush against Lower's inner cavity wall faces, extending inward from the inside, not embedded in the wall material.
4. **Corner post Z extent (user-corrected).** First built spanning only Z 15–19 (i.e. floating above the cavity, only touching the top rim). Corrected: extended down to Z=0 so the post is structurally connected to Lower's floor, still rising to Z=19 (4mm above the rim).
5. **Bore conventions for bosses/posts/supports/collars (engineering assumption, not explicitly specified in either version of the prompt, carried forward without objection).** Neither v1.1 nor v1.2 states whether each secondary part's central bore is a blind pilot hole or a full through-hole beyond noting a 0.5mm top overshoot. The convention used throughout the build: Lower's screw bosses and mounting posts, and Upper's PCB supports, are **blind at the base, open through the top** (self-tapping pilot holes) with a 0.5mm overshoot above the top face only; Upper's screw bosses and the button collars are **full through-holes**, open at both ends with a 0.5mm overshoot at each face. If this isn't the intent, flag it — it's the one part of the geometry that was inferred rather than stated or confirmed.

## Verification

1. **Zero leftover modifiers.** Every object in the collection has `len(obj.modifiers) == 0` after the build.
2. **Manifold check.** `RC_Case_Lower` and `RC_Case_Upper` each have 0 boundary edges and 0 non-manifold (3+ face) edges after triangulation.
3. **Single mesh per shell.** Each half is exactly one object (`RC_Case_Lower`, `RC_Case_Upper`) regardless of how many Boolean cuts were applied.
4. **Identical footprint.** Lower's and Upper's outer half-extents both equal (28.75, 87.5) — exactly matching, not offset by a clearance.
5. **Corner posts.** All 4 `RC_JointPost_Lower_*` objects span Z 0 to 19, with their outer two faces flush against Lower's inner cavity wall (X=±26.25 or Y=±85, whichever applies) and extending 2mm inward.
6. **Object count.** 24 objects total in the `RC_Remote_Case_Modifier` collection.
