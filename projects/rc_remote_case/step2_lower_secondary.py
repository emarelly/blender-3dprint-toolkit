"""
STEP 2 of 7 -- Lower secondary parts.
Run this after step1. Adds the screw bosses, mounting posts, and guide
rails inside Lower's cavity. After running, you should see 6 small parts
sitting inside the Lower shell.
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

def make_box(name, x_min, x_max, y_min, y_max, z_min, z_max, apply_scale=True):
    cx, cy, cz = (x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = unique_name(name)
    obj.dimensions = (x_max - x_min, y_max - y_min, z_max - z_min)
    if apply_scale:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    return obj

def make_cylinder(name, radius, z_min, z_max, x, y, verts=32, rotation=(0, 0, 0)):
    depth = z_max - z_min
    cz = (z_min + z_max) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                         location=(x, y, cz), rotation=rotation)
    obj = bpy.context.active_object
    obj.name = unique_name(name)
    if rotation != (0, 0, 0):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    link_only(obj)
    return obj

def boolean_diff_apply(obj, cutter, delete_cutter=True):
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if delete_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)

def make_bore_cutter(name, radius, z_bottom, z_top_target, top_overshoot=0.5, bottom_overshoot=0.0, x=0, y=0):
    z0 = z_bottom - bottom_overshoot
    z1 = z_top_target + top_overshoot
    return make_cylinder(name + "_bore_cutter", radius, z0, z1, x, y)

# ---------- STEP 2: Lower secondary parts ----------
created = []

for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    name = f"RC_Boss_Lower_{tag}"
    boss = make_cylinder(name, radius=3.0, z_min=2.5, z_max=13.0, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=1.6, z_bottom=2.5, z_top_target=13.0, top_overshoot=0.5, bottom_overshoot=0.0, x=0.0, y=y)
    boolean_diff_apply(boss, bore)
    created.append(boss.name)

for tag, y in (("PosY", 22.75), ("NegY", -32.75)):
    name = f"RC_Post_Lower_{tag}"
    post = make_cylinder(name, radius=4.15, z_min=2.5, z_max=12.5, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=2.15, z_bottom=2.5, z_top_target=12.5, top_overshoot=0.5, bottom_overshoot=0.0, x=0.0, y=y)
    boolean_diff_apply(post, bore)
    created.append(post.name)

for tag, x in (("PosX", 18.0), ("NegX", -18.0)):
    name = f"RC_Rail_Lower_{tag}"
    rail = make_box(name, x - 0.5, x + 0.5, -85.0, 85.0, 2.5, 6.4)
    created.append(rail.name)

print({"status": "ok", "step": 2, "created": created, "collection_count": len(coll.objects)})
