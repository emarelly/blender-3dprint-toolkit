"""
STEP 6 of 7 -- Wire-entry hole, split across the seam.
Run this after step5. Cuts a semicircular notch into the top of Lower's
end wall and a matching one into the bottom of Upper's end wall -- look
at the -Y end (opposite the button holes) to see the two half-circles.
"""
import bpy, math

COLL_NAME = "RC_Remote_Case_Modifier"
if COLL_NAME not in bpy.data.collections:
    raise RuntimeError("Run step1_lower_shell.py first -- collection not found.")
coll = bpy.data.collections[COLL_NAME]

if "RC_Case_Lower" not in bpy.data.objects or "RC_Case_Upper" not in bpy.data.objects:
    raise RuntimeError("Run step1 and step4 first -- RC_Case_Lower / RC_Case_Upper not found.")

lower = bpy.data.objects["RC_Case_Lower"]
upper = bpy.data.objects["RC_Case_Upper"]

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

def boolean_diff_apply(obj, cutter, delete_cutter=True):
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if delete_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)

# ---------- Wire-entry hole ----------
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

print({"status": "ok", "step": 6, "collection_count": len(coll.objects)})
