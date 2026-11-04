"""
STEP 4 of 7 -- Upper shell.
Run this after step3. Builds RC_Case_Upper: beveled box, cavity cut, 6
button holes, and 2 screw-access holes. It sits at the same XY location
as Lower for now -- the sideways shift happens in step7. After running,
you'll see Upper's rounded, hollowed, hole-punched shell overlapping
Lower.
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

def apply_bevel(obj, width=0.6, segments=4):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.limit_method = 'ANGLE'
    mod.width = width
    mod.segments = segments
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)

def boolean_diff_apply(obj, cutter, delete_cutter=True):
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if delete_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)

# ---------- STEP 3: Upper shell ----------
upper = make_box("RC_Case_Upper", -28.75, 28.75, -87.5, 87.5, 0.0, 14.0)
apply_bevel(upper, width=0.6, segments=4)

upper_cavity_cutter = make_box("_cutter_upper_cavity", -26.25, 26.25, -85.0, 85.0, -2.0, 11.5, apply_scale=False)
boolean_diff_apply(upper, upper_cavity_cutter)

button_positions = [
    (0.0, 9.75),
    (-16.1, 5.55),
    (16.1, 13.95),
    (0.0, 35.75),
    (-16.1, 31.55),
    (16.1, 39.95),
]
for i, (x, y) in enumerate(button_positions, start=1):
    cutter = make_cylinder(f"_cutter_button_{i}", radius=7.0, z_min=11.3, z_max=14.2, x=x, y=y)
    boolean_diff_apply(upper, cutter)

screw_access_positions = [(0.0, 69.0), (0.0, -69.0)]
for i, (x, y) in enumerate(screw_access_positions, start=1):
    cutter = make_cylinder(f"_cutter_screwaccess_{i}", radius=3.2, z_min=11.3, z_max=14.2, x=x, y=y)
    boolean_diff_apply(upper, cutter)

print({"status": "ok", "step": 4, "created": [upper.name], "collection_count": len(coll.objects)})
