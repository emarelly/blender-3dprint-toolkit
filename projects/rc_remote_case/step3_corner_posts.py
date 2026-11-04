"""
STEP 3 of 7 -- Corner joint posts.
Run this after step2. Adds the 4 square posts at Lower's corners, flush
against the inner cavity wall, running from the floor up to 4mm above
the rim. After running, you should see 4 small square columns standing
up at Lower's 4 corners.
"""
import bpy

COLL_NAME = "RC_Remote_Case_Modifier"
if COLL_NAME not in bpy.data.collections:
    raise RuntimeError("Run step1_lower_shell.py first -- collection not found.")
coll = bpy.data.collections[COLL_NAME]

def unique_name(name):
    if name in bpy.data.objects:
        n = name + "_M"
        i = 2
        while n in bpy.data.objects:
            n = f"{name}_M{i}"
            i += 1
        return n
    return name

def link_only(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)

def make_box(name, x_min, x_max, y_min, y_max, z_min, z_max):
    cx, cy, cz = (x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = unique_name(name)
    obj.dimensions = (x_max - x_min, y_max - y_min, z_max - z_min)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    return obj

# ---------- STEP 2b: Corner joint posts ----------
# 2x2mm solid posts, flush against Lower's inner cavity wall (X=+-26.25, Y=+-85),
# extending 2mm inward. Full height Z 0-19 (floor to 4mm above the rim).
POST = 2.0
corner_defs = [
    ("PosXPosY",  26.25 - POST, 26.25,        85.0 - POST, 85.0),
    ("PosXNegY",  26.25 - POST, 26.25,       -85.0,        -85.0 + POST),
    ("NegXPosY", -26.25,       -26.25 + POST,  85.0 - POST, 85.0),
    ("NegXNegY", -26.25,       -26.25 + POST, -85.0,        -85.0 + POST),
]
created = []
for tag, x_min, x_max, y_min, y_max in corner_defs:
    name = f"RC_JointPost_Lower_{tag}"
    post = make_box(name, x_min, x_max, y_min, y_max, 0.0, 19.0)
    created.append(post.name)

print({"status": "ok", "step": 3, "created": created, "collection_count": len(coll.objects)})
