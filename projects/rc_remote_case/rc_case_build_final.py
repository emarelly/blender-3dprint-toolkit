"""
RC Remote Control Case -- Modifier-Based Build (FINAL, consolidated)

Single script that reproduces the current, final state of the model in one
pass -- this is the v1.2 build with the corner joint posts built directly
at their final, corrected geometry (flush against Lower's inner cavity
wall, running the full height from the floor to 4mm above the rim).

It intentionally skips:
  - the abandoned v1.1 sleeve-fit build (Upper used to be a larger
    telescoping shell; Lower and Upper are now the same outer footprint)
  - the two intermediate corner-post revisions (first centered in the
    wall material at Z 15-19, then moved flush to the inner wall at
    Z 15-19, before finally being extended down to Z 0)

Running this against a Blender instance (via execute_blender_code, or
directly with `blender --background --python this_file.py`) produces the
same 24-object RC_Remote_Case_Modifier collection as the current build,
with Upper flipped open-face-up (Step 6) to match Lower's orientation.
"""

import bpy, math

# ---------- Units ----------
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

# ---------- Collection ----------
COLL_NAME = "RC_Remote_Case_Modifier"
if COLL_NAME in bpy.data.collections:
    coll = bpy.data.collections[COLL_NAME]
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    coll = bpy.data.collections.new(COLL_NAME)
    scene.collection.children.link(coll)

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

created = []

# =====================================================================
# STEP 1 -- Lower shell
# =====================================================================
lower = make_box("RC_Case_Lower", -28.75, 28.75, -87.5, 87.5, 0.0, 15.0)
apply_bevel(lower, width=0.6, segments=4)

lower_cavity_cutter = make_box("_cutter_lower_cavity", -26.25, 26.25, -85.0, 85.0, 2.5, 20.0, apply_scale=False)
boolean_diff_apply(lower, lower_cavity_cutter)
created.append(lower.name)

# =====================================================================
# STEP 2 -- Lower secondary parts
# =====================================================================
lower_secondary = []

for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    name = f"RC_Boss_Lower_{tag}"
    boss = make_cylinder(name, radius=3.0, z_min=2.5, z_max=13.0, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=1.6, z_bottom=2.5, z_top_target=13.0, top_overshoot=0.5, bottom_overshoot=0.0, x=0.0, y=y)
    boolean_diff_apply(boss, bore)
    lower_secondary.append(boss.name)

for tag, y in (("PosY", 22.75), ("NegY", -32.75)):
    name = f"RC_Post_Lower_{tag}"
    post = make_cylinder(name, radius=4.15, z_min=2.5, z_max=12.5, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=2.15, z_bottom=2.5, z_top_target=12.5, top_overshoot=0.5, bottom_overshoot=0.0, x=0.0, y=y)
    boolean_diff_apply(post, bore)
    lower_secondary.append(post.name)

for tag, x in (("PosX", 18.0), ("NegX", -18.0)):
    name = f"RC_Rail_Lower_{tag}"
    rail = make_box(name, x - 0.5, x + 0.5, -85.0, 85.0, 2.5, 6.4)
    lower_secondary.append(rail.name)

created.extend(lower_secondary)

# =====================================================================
# STEP 2b -- Corner joint posts (FINAL geometry, built directly)
# 2x2mm solid square posts, flush against Lower's inner cavity wall
# faces (X=+-26.25, Y=+-85), extending 2mm inward. Full height from the
# floor (Z=0) up to 4mm above the top rim (Z=19), so each post is
# structurally connected to Lower's floor. No matching cut on Upper.
# =====================================================================
corner_posts = []
POST = 2.0
corner_defs = [
    ("PosXPosY",  26.25 - POST, 26.25,        85.0 - POST, 85.0),
    ("PosXNegY",  26.25 - POST, 26.25,       -85.0,        -85.0 + POST),
    ("NegXPosY", -26.25,       -26.25 + POST,  85.0 - POST, 85.0),
    ("NegXNegY", -26.25,       -26.25 + POST, -85.0,        -85.0 + POST),
]
for tag, x_min, x_max, y_min, y_max in corner_defs:
    name = f"RC_JointPost_Lower_{tag}"
    post = make_box(name, x_min, x_max, y_min, y_max, 0.0, 19.0)
    corner_posts.append(post.name)

created.extend(corner_posts)

# =====================================================================
# STEP 3 -- Upper shell (identical outer footprint to Lower)
# =====================================================================
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

created.append(upper.name)

# =====================================================================
# STEP 4 -- Upper secondary parts
# =====================================================================
upper_secondary = []

for tag, y in (("PosY", 69.0), ("NegY", -69.0)):
    name = f"RC_Boss_Upper_{tag}"
    boss = make_cylinder(name, radius=4.5, z_min=3.5, z_max=11.5, x=0.0, y=y)
    bore = make_bore_cutter(name, radius=1.8, z_bottom=3.5, z_top_target=11.5, top_overshoot=0.5, bottom_overshoot=0.5, x=0.0, y=y)
    boolean_diff_apply(boss, bore)
    upper_secondary.append(boss.name)

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
    upper_secondary.append(sup.name)

for i, (x, y) in enumerate(button_positions, start=1):
    name = f"RC_Collar_Hole{i}"
    collar = make_cylinder(name, radius=8.5, z_min=8.0, z_max=11.5, x=x, y=y)
    bore = make_bore_cutter(name, radius=7.0, z_bottom=8.0, z_top_target=11.5, top_overshoot=0.5, bottom_overshoot=0.5, x=x, y=y)
    boolean_diff_apply(collar, bore)
    upper_secondary.append(collar.name)

created.extend(upper_secondary)

# =====================================================================
# WIRE-ENTRY HOLE -- split across the seam
# Full circle radius 4.85mm, axis along Y, centered X=0, end wall Y=-87.5.
# Lower's cutter is centered at its own top rim (Z=15); Upper's cutter is
# centered at its own bottom rim (Z=0, local pre-shift coords). Since
# each shell's solid material only exists on one side of that plane, the
# Boolean difference naturally leaves a semicircular notch in each half
# -- together they form one full round hole when assembled.
# =====================================================================
WIRE_RADIUS = 4.85
WIRE_Y_MIN, WIRE_Y_MAX = -90.0, -83.0

def make_wire_cutter(name, z_center):
    depth = WIRE_Y_MAX - WIRE_Y_MIN
    y_center = (WIRE_Y_MIN + WIRE_Y_MAX) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=WIRE_RADIUS, depth=depth, vertices=48,
                                         location=(0.0, y_center, z_center),
                                         rotation=(math.radians(90), 0, 0))
    obj = bpy.context.active_object
    obj.name = unique_name(name)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    link_only(obj)
    return obj

lower_wire_cutter = make_wire_cutter("_cutter_wire_lower", z_center=15.0)
boolean_diff_apply(lower, lower_wire_cutter)

upper_wire_cutter = make_wire_cutter("_cutter_wire_upper", z_center=0.0)
boolean_diff_apply(upper, upper_wire_cutter)

# =====================================================================
# STEP 5 -- Final placement (translate Upper group by dX = -80mm)
# Corner joint posts stay with Lower (not shifted).
# =====================================================================
upper_group_names = [upper.name] + upper_secondary
for name in upper_group_names:
    obj = bpy.data.objects[name]
    obj.location.x += -80.0

bpy.context.view_layer.update()

# =====================================================================
# STEP 6 -- Flip Upper so it faces up (open skirt up, ceiling down),
# matching Lower's own "bowl up" orientation. This is a 180 degree
# rotation about a horizontal axis (X) through Upper's own center, so
# it flips in place rather than jumping elsewhere. Note: this also
# mirrors Upper's Y-axis feature layout (button holes, bosses, etc.) --
# that's the correct physical result of flipping a real part over, not
# a bug.
# =====================================================================
import mathutils

flip_cx = bpy.data.objects[upper.name].location.x
flip_pivot = mathutils.Vector((flip_cx, 0.0, 7.0))
flip_matrix = mathutils.Matrix.Rotation(math.radians(180), 4, 'X')

for name in upper_group_names:
    obj = bpy.data.objects[name]
    obj.matrix_world = (
        mathutils.Matrix.Translation(flip_pivot) @ flip_matrix @
        mathutils.Matrix.Translation(-flip_pivot) @ obj.matrix_world
    )

bpy.context.view_layer.update()

result = {
    "status": "ok",
    "collection": COLL_NAME,
    "object_count": len(coll.objects),
    "objects": sorted([o.name for o in coll.objects]),
    "lower_name": lower.name,
    "upper_name": upper.name,
}

print(result)
