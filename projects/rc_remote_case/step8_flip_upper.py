"""
STEP 8 of 8 -- Flip Upper open-face-up.
Run this after step7. Rotates Upper's whole group 180 degrees about a
horizontal axis (X) so the open skirt faces up and the ceiling faces
down -- matching Lower's own "bowl up" orientation. Good for a side by
side visual comparison, or for a print orientation where Upper's bosses
and collars don't hang off an overhead ceiling.

Note: this also mirrors Upper's Y-axis feature layout (button holes,
bosses, etc.). That's the correct physical result of flipping a real
part over, not a bug -- the part's own local geometry is unchanged,
only its orientation in world space changes.
"""
import bpy, math, mathutils

COLL_NAME = "RC_Remote_Case_Modifier"
if COLL_NAME not in bpy.data.collections:
    raise RuntimeError("Run the earlier steps first -- collection not found.")
coll = bpy.data.collections[COLL_NAME]

upper_group_names = [
    "RC_Case_Upper",
    "RC_Boss_Upper_PosY", "RC_Boss_Upper_NegY",
    "RC_Support_Upper_L1", "RC_Support_Upper_R1", "RC_Support_Upper_L2", "RC_Support_Upper_R2",
    "RC_Collar_Hole1", "RC_Collar_Hole2", "RC_Collar_Hole3",
    "RC_Collar_Hole4", "RC_Collar_Hole5", "RC_Collar_Hole6",
]

missing = [n for n in upper_group_names if n not in bpy.data.objects]
if missing:
    raise RuntimeError(f"Run step4/step5/step7 first -- missing objects: {missing}")

# Pivot: Upper's own X position (wherever it currently sits, e.g. after
# the -80mm shift in step7), Y=0, and Z=7 (the vertical midpoint of
# Upper's own 0-14mm height) -- rotating about this line flips the
# shell in place without it jumping off to the side or below the floor.
flip_cx = bpy.data.objects["RC_Case_Upper"].location.x
flip_pivot = mathutils.Vector((flip_cx, 0.0, 7.0))
flip_matrix = mathutils.Matrix.Rotation(math.radians(180), 4, 'X')

for name in upper_group_names:
    obj = bpy.data.objects[name]
    obj.matrix_world = (
        mathutils.Matrix.Translation(flip_pivot) @ flip_matrix @
        mathutils.Matrix.Translation(-flip_pivot) @ obj.matrix_world
    )

bpy.context.view_layer.update()

print({"status": "ok", "step": 8, "flipped": upper_group_names, "collection_count": len(coll.objects)})
