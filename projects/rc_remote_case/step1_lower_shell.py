"""
STEP 1 of 7 -- Lower shell.
Run this first. Creates the RC_Remote_Case_Modifier collection (clearing
it if it already exists) and builds RC_Case_Lower: a beveled box with its
interior cavity cut out. After running, rotate the viewport -- you should
see one rounded, hollow box.
"""
import bpy

# ---------- Units ----------
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

# ---------- Collection (fresh start) ----------
COLL_NAME = "RC_Remote_Case_Modifier"
if COLL_NAME in bpy.data.collections:
    coll = bpy.data.collections[COLL_NAME]
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    coll = bpy.data.collections.new(COLL_NAME)
    scene.collection.children.link(coll)

# ---------- Helpers (reused by every step file) ----------
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

def make_bore_cutter(name, radius, z_bottom, z_top_target, top_overshoot=0.5, bottom_overshoot=0.0, x=0, y=0):
    z0 = z_bottom - bottom_overshoot
    z1 = z_top_target + top_overshoot
    return make_cylinder(name + "_bore_cutter", radius, z0, z1, x, y)

# ---------- STEP 1: Lower shell ----------
lower = make_box("RC_Case_Lower", -28.75, 28.75, -87.5, 87.5, 0.0, 15.0)
apply_bevel(lower, width=0.6, segments=4)

lower_cavity_cutter = make_box("_cutter_lower_cavity", -26.25, 26.25, -85.0, 85.0, 2.5, 20.0, apply_scale=False)
boolean_diff_apply(lower, lower_cavity_cutter)

print({"status": "ok", "step": 1, "created": [lower.name], "collection_count": len(coll.objects)})
