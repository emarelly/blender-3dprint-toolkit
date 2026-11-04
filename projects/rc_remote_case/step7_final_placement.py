"""
STEP 7 of 7 -- Final placement.
Run this last. Shifts RC_Case_Upper and its secondary parts sideways by
-80mm in X, so Upper sits next to Lower instead of overlapping it. Once
this runs, the model is complete and matches the final build.
"""
import bpy

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
    raise RuntimeError(f"Run step4 and step5 first -- missing objects: {missing}")

for name in upper_group_names:
    obj = bpy.data.objects[name]
    obj.location.x += -80.0

bpy.context.view_layer.update()

print({"status": "ok", "step": 7, "shifted": upper_group_names, "collection_count": len(coll.objects)})
