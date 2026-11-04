"""
STEP 5 of 7 -- Upper secondary parts.
Run this after step4. Adds Upper's screw bosses, PCB supports, and
button collars inside Upper's cavity.
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

button_positions = [
    (0.0, 9.75),
    (-16.1, 5.55),
    (16.1, 13.95),
    (0.0, 35.75),
    (-16.1, 31.55),
    (16.1, 39.95),
]

# ---------- STEP 4: Upper secondary parts ----------
created = []

for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    name = f"RC_Boss_Upper_{tag}"
    boss = make_cylinder(name, radius=4.5, z_min=3.5, z_max=11.5, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=1.8, z_bottom=3.5, z_top_target=11.5, top_overshoot=0.5, bottom_overshoot=0.5, x=0.0, y=y)
    boolean_diff_apply(boss, bore)
    created.append(boss.name)

support_positions = {
    "L1": (-16.1, 18.55),
    "R1": (16.1, 26.95),
    "L2": (-16.1, -35.45),
    "R2": (16.1, -27.05),
}
for tag, (x, y) in support_positions.items():
    name = f"RC_Support_Upper_{tag}"
    sup = make_cylinder(name, radius=2.5, z_min=1.5, z_max=11.5, x=x, y=y)
    bore = make_bore_cutter(name, radius=1.0, z_bottom=1.5, z_top_target=11.5, top_overshoot=0.5, bottom_overshoot=0.0, x=x, y=y)
    boolean_diff_apply(sup, bore)
    created.append(sup.name)

for i, (x, y) in enumerate(button_positions, start=1):
    name = f"RC_Collar_Hole{i}"
    collar = make_cylinder(name, radius=8.5, z_min=8.0, z_max=11.5, x=x, y=y)
    bore = make_bore_cutter(name, radius=7.0, z_bottom=8.0, z_top_target=11.5, top_overshoot=0.5, bottom_overshoot=0.5, x=x, y=y)
    boolean_diff_apply(collar, bore)
    created.append(collar.name)

print({"status": "ok", "step": 5, "created": created, "collection_count": len(coll.objects)})
