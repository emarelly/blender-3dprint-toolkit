"""
utils_3d.py -- reusable Blender (bpy) helpers for parametric, 3D-printable models.

helpers for future designs. Everything is in MILLIMETRES (1 Blender unit = 1 mm
once setup_units_mm() has been called).

Typical use inside a Blender script:

    import sys
    sys.path.append(r"C:\\path\\to\\this\\folder")      # once
    import utils_3d as u                               # (importlib.reload(u) while editing it)

    u.setup_units_mm()
    u.use_collection("My_Design", clear=True)          # all new objects go here
    body = u.make_hollow_box("Body", -20, 20, -30, 30, 0, 15, wall=2, open_face="+Z", bevel=0.6)
    boss = u.make_boss("Boss", 0, 0, 2, 12, outer_r=3, bore_r=1.6)
    u.print_report([body, boss])
    u.export_all(basename="my_design")                 # .blend copy + STLs

Sections
    1. Scene / collection setup (collections, show-only / frame view, script folder)
    2. Primitive builders (box, cylinder, frustum, slot, stadium profile, prism along any axis,
       revolved profile, revolved ring with a hole)
    3. Modifier wrappers (bevel, boolean, array, solidify, multi-radius edge rounding) -- always
       applied/baked
    4. Print-oriented feature builders (hollow box, boss, holes, countersink, lid lip, finger notch...)
    5. Layout helpers (grid / line / circle / mirror positions)
    6. Transforms (move, rotate, flip, drop to bed, arrange, join, duplicate)
    7. Inspection (bounding box, manifold check, print report)
    8. Export / save (STL clean-up, STL, 3MF, .blend)
    9. Tolerances, screw/insert tables, Params
   10. Screw / insert / nut / magnet features, printed threads (threaded tubes, thread specs)
   11. Snap fits, vents, text
   12. Print-quality checks (min wall, overhang, bed fit, overlaps incl. pose sweeps,
       orientation, split)

Primitives are built with bmesh (no bpy.ops, no selection/context needed), and each
object's origin is placed at its geometric centre, like Blender's own primitives.
"""

import math
import os
import re
import zipfile
from xml.sax.saxutils import quoteattr

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

# =====================================================================
# 1. SCENE / COLLECTION SETUP
# =====================================================================

_active_collection = None


def setup_units_mm():
    """Metric, scale 0.001, millimetres -> 1 Blender unit == 1 mm (STL exports as mm)."""
    us = bpy.context.scene.unit_settings
    us.system = 'METRIC'
    us.scale_length = 0.001
    us.length_unit = 'MILLIMETERS'


def use_collection(name, clear=False, parent=None):
    """Get/create collection `name`, link it to the scene and make it the default
    target for every make_* function. clear=True deletes its existing objects.
    parent = name of a collection to nest it in (created and linked to the scene if needed)."""
    global _active_collection
    scene = bpy.context.scene
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    elif clear:
        clear_collection(coll)
    if parent:
        par = bpy.data.collections.get(parent) or bpy.data.collections.new(parent)
        if par.name not in {c.name for c in scene.collection.children_recursive}:
            scene.collection.children.link(par)
        if coll.name in scene.collection.children:
            scene.collection.children.unlink(coll)
        if coll.name not in par.children:
            par.children.link(coll)
    elif coll.name not in {c.name for c in scene.collection.children_recursive}:
        scene.collection.children.link(coll)
    _active_collection = coll
    return coll


def clear_collection(coll):
    """Delete every object in `coll` (and mesh data left with no users)."""
    for obj in list(coll.objects):
        delete_object(obj)


def delete_object(obj):
    """Remove an object and its mesh data if nothing else uses it."""
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and getattr(data, "users", 1) == 0 and isinstance(data, bpy.types.Mesh):
        bpy.data.meshes.remove(data)


def unique_name(name):
    """Return `name`, or `name_M`, `name_M2`... if an object already uses it."""
    if name not in bpy.data.objects:
        return name
    n, i = name + "_M", 2
    while n in bpy.data.objects:
        n = f"{name}_M{i}"
        i += 1
    return n


def link_only(obj, coll=None):
    """Link `obj` to exactly one collection (default: the one from use_collection)."""
    coll = coll or _active_collection or bpy.context.scene.collection
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def _walk_layer_collections(layer_coll):
    for lc in layer_coll.children:
        yield lc
        yield from _walk_layer_collections(lc)


def show_only_collection(name):
    """Hide every other collection in the viewport (builds that sit at the same coordinates
    would otherwise overlap); `name` itself and the collections nested in it are shown."""
    keep = {name}
    coll = bpy.data.collections.get(name)
    if coll is not None:
        keep |= {c.name for c in coll.children_recursive}
    for lc in _walk_layer_collections(bpy.context.view_layer.layer_collection):
        lc.hide_viewport = lc.collection.name not in keep


def frame_all():
    """Frame everything in every open 3D viewport (View All). No-op when running headless."""
    wm = bpy.context.window_manager
    for win in (wm.windows if wm else []):
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if region:
                    with bpy.context.temp_override(window=win, area=area, region=region):
                        bpy.ops.view3d.view_all()


def script_dir(name=None):
    """Folder of the calling script. Blender's text editor only gives a bare __file__, so the
    open texts are searched for a file called `name` (default: the caller's file name) first;
    then the caller's own path; then the current directory."""
    import sys
    caller = sys._getframe(1).f_code.co_filename
    base = os.path.basename(name or caller)
    for t in bpy.data.texts:
        if t.filepath and os.path.basename(t.filepath) == base:
            return os.path.dirname(bpy.path.abspath(t.filepath))
    if os.path.isabs(caller) and os.path.isfile(caller):
        return os.path.dirname(caller)
    return os.getcwd()


def _new_object(name, bm, location, coll):
    """Turn a bmesh into a linked mesh object (frees the bmesh)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.update()
    obj = bpy.data.objects.new(unique_name(name), me)
    obj.location = location
    return link_only(obj, coll)


# =====================================================================
# 2. PRIMITIVE BUILDERS
# =====================================================================

def make_box(name, x_min, x_max, y_min, y_max, z_min, z_max, coll=None):
    """Axis-aligned box from min/max coordinates (the 'stock box' of the RC case).
    Each min/max pair may be given in either order (handy for features mirrored with a sign)."""
    x_min, x_max = sorted((x_min, x_max))
    y_min, y_max = sorted((y_min, y_max))
    z_min, z_max = sorted((z_min, z_max))
    size =(x_max - x_min, y_max - y_min, z_max - z_min)
    center = ((x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    return _new_object(name, bm, center, coll)


def make_box_centered(name, center, size, coll=None):
    """Box from a centre point (cx, cy, cz) and (sx, sy, sz) size."""
    cx, cy, cz = center
    sx, sy, sz = size
    return make_box(name, cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2,
                    cz - sz / 2, cz + sz / 2, coll)


def _frustum_bm(r0, r1, length, verts):
    """Z-axis frustum centred on the origin: radius r0 at -length/2, r1 at +length/2."""
    bm = bmesh.new()
    h = length / 2.0
    ring0, ring1 = [], []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        ring0.append(bm.verts.new((r0 * math.cos(a), r0 * math.sin(a), -h)))
        ring1.append(bm.verts.new((r1 * math.cos(a), r1 * math.sin(a), h)))
    for i in range(verts):
        j = (i + 1) % verts
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
    bm.faces.new(list(reversed(ring0)))
    bm.faces.new(ring1)
    return bm


def make_frustum_between(name, r0, r1, p0, p1, verts=32, coll=None):
    """Cone/cylinder between 3D points p0 and p1 (radius r0 at p0, r1 at p1).
    Works along ANY direction -- this is how the wire-entry cutter (axis along Y) is made."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-9:
        raise ValueError("p0 and p1 must differ")
    bm = _frustum_bm(r0, r1, length, verts)
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bm.transform(rot)
    return _new_object(name, bm, (p0 + p1) / 2, coll)


def make_cylinder_between(name, radius, p0, p1, verts=32, coll=None):
    """Cylinder between two 3D points (any direction)."""
    return make_frustum_between(name, radius, radius, p0, p1, verts, coll)


def make_cylinder(name, radius, z_min, z_max, x=0.0, y=0.0, verts=32, coll=None):
    """Vertical (Z-axis) cylinder at (x, y) spanning z_min..z_max."""
    return make_cylinder_between(name, radius, (x, y, z_min), (x, y, z_max), verts, coll)


def make_cone(name, r_bottom, r_top, z_min, z_max, x=0.0, y=0.0, verts=32, coll=None):
    """Vertical cone/frustum (use r_top=0.001 for a point)."""
    return make_frustum_between(name, r_bottom, r_top, (x, y, z_min), (x, y, z_max), verts, coll)


def stadium_profile(p0, p1, width, arc_segments=12):
    """2D outline of a stadium / obround (a slot with round ends): p0, p1 = centres of the two
    end arcs, width = slot width (= 2 x arc radius). Returns [(u, v), ...] for make_prism or
    make_slot. Horizontal slot of overall size L x H centred on (cx, cz):
    stadium_profile((cx - (L - H) / 2, cz), (cx + (L - H) / 2, cz), H)."""
    r = width / 2.0
    (x0, y0), (x1, y1) = p0, p1
    ang = math.atan2(y1 - y0, x1 - x0) if (x0, y0) != (x1, y1) else 0.0
    pts = []
    for k in range(arc_segments + 1):          # cap around p1
        a = ang - math.pi / 2 + math.pi * k / arc_segments
        pts.append((x1 + r * math.cos(a), y1 + r * math.sin(a)))
    for k in range(arc_segments + 1):          # cap around p0
        a = ang + math.pi / 2 + math.pi * k / arc_segments
        pts.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))
    return pts


def make_prism(name, pts, axis, lo, hi, location=(0, 0, 0), coll=None):
    """Extrude a closed 2D polygon along a world axis from lo to hi.
    pts are given in the two OTHER axes in XYZ order: axis 'X' -> (y, z), 'Y' -> (x, z),
    'Z' -> (x, y). Vertices are placed as given (origin at `location`, not the centre)."""
    i = "XYZ".index(axis.upper())
    others = [k for k in range(3) if k != i]

    def p3(a, b, t):
        p = [0.0, 0.0, 0.0]
        p[others[0]], p[others[1]], p[i] = a, b, t
        return p

    bm = bmesh.new()
    front = [bm.verts.new(p3(a, b, lo)) for a, b in pts]
    back = [bm.verts.new(p3(a, b, hi)) for a, b in pts]
    n = len(pts)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((front[k], front[j], back[j], back[k]))
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    return _new_object(name, bm, location, coll)


def make_slot(name, p0, p1, width, z_min, z_max, arc_segments=12, coll=None):
    """Stadium / obround prism (a slot with round ends), extruded along Z.
    p0, p1 = (x, y) centres of the two end arcs. Good for USB / switch / cable cut-outs.
    If p0 == p1 it is a plain cylinder. For a slot through a side wall use
    make_prism(name, stadium_profile(...), 'X' or 'Y', lo, hi)."""
    (x0, y0), (x1, y1) = p0, p1
    pts = stadium_profile(p0, p1, width, arc_segments)
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z_min + z_max) / 2
    h = (z_max - z_min) / 2
    bm = bmesh.new()
    bot = [bm.verts.new((px - cx, py - cy, -h)) for px, py in pts]
    top = [bm.verts.new((px - cx, py - cy, h)) for px, py in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    return _new_object(name, bm, (cx, cy, cz), coll)


def make_revolved(name, profile, x=0.0, y=0.0, z=0.0, verts=48, coll=None):
    """Lathe a closed (radius, z) profile around the Z axis at (x, y, z offset).
    The first and last profile points must lie on the axis (radius 0).
    Example countersink: [(0,0),(1.6,0),(1.6,2),(3.2,3.6),(3.2,5),(0,5)]."""
    if abs(profile[0][0]) > 1e-9 or abs(profile[-1][0]) > 1e-9:
        raise ValueError("first and last profile points must have radius 0")
    bm = bmesh.new()
    rings = []
    for r, pz in profile:
        if abs(r) < 1e-9:
            v = bm.verts.new((0, 0, pz))
            rings.append([v] * verts)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / verts),
                                        r * math.sin(2 * math.pi * i / verts), pz))
                          for i in range(verts)])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(verts):
            j = (i + 1) % verts
            uniq = []
            for v in (a[i], a[j], b[j], b[i]):
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    return _new_object(name, bm, (x, y, z), coll)


def make_revolved_ring(name, profile, x=0.0, y=0.0, z=0.0, verts=48, coll=None):
    """Lathe a closed (radius, z) polygon that does NOT touch the axis into a ring solid (a part
    with a hole through the middle), around the Z axis at (x, y, z offset). The polygon is closed
    implicitly (last point joins the first); either direction works.
    Draw bores, recesses, grooves and steps into the profile instead of cutting them with
    Booleans: on a lathe, cutter vertices land on the lathe's own edges and exact Booleans leave
    open / non-manifold edges. Example washer with a groove underneath:
        [(5, 0), (8, 0), (8, 1), (9, 1), (9, 0), (12, 0), (12, 3), (5, 3)]"""
    if any(r <= 1e-9 for r, _ in profile):
        raise ValueError("every profile radius must be > 0 (use make_revolved for solids on the axis)")
    bm = bmesh.new()
    rings = [[bm.verts.new((r * math.cos(2 * math.pi * i / verts),
                            r * math.sin(2 * math.pi * i / verts), pz)) for i in range(verts)]
             for r, pz in profile]
    n = len(rings)
    for k in range(n):
        a, b = rings[k], rings[(k + 1) % n]
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((a[i], a[j], b[j], b[i]))
    return _new_object(name, bm, (x, y, z), coll)


# =====================================================================
# 3. MODIFIER WRAPPERS (add -> apply -> object is plain mesh again)
# =====================================================================

def _activate(obj):
    if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def apply_modifier(obj, mod):
    """Apply modifier `mod` (object or name) on `obj`."""
    _activate(obj)
    name = mod if isinstance(mod, str) else mod.name
    bpy.ops.object.modifier_apply(modifier=name)


def apply_all_modifiers(obj):
    """Bake every modifier on obj (leaves len(obj.modifiers) == 0)."""
    for m in list(obj.modifiers):
        apply_modifier(obj, m)


def apply_bevel(obj, width=0.6, segments=4, angle_limit=None):
    """Round (segments>1) or chamfer (segments=1) edges. Default limit method: Angle."""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.limit_method = 'ANGLE'
    if angle_limit is not None:
        mod.angle_limit = angle_limit
    mod.width = width
    mod.segments = segments
    apply_modifier(obj, mod)


def round_edges(obj, radius, where='ALL', segments=6, profile=0.5):
    """Round (fillet) selected edges of a mesh object, directly on its mesh (no modifier).
    Best used on a plain box BEFORE cutting into it.
    where:
        'ALL'        every edge
        'VERTICAL'   edges parallel to Z (the four corner columns of a box)
        'HORIZONTAL' edges parallel to X or Y
        'TOP' / 'BOTTOM'   the horizontal edges around the top / bottom face
        'X' / 'Y' / 'Z'    edges parallel to that axis
        callable     f(v0, v1) -> bool on the edge's two end points (object-local coords)
    segments = smoothness (1 = chamfer); profile 0.5 = true circular arc."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    zs = [v.co.z for v in bm.verts]
    z_top, z_bot = max(zs), min(zs)
    eps = 1e-6

    def parallel(a, b, ax):
        d = b - a
        return all(abs(d[i]) < eps for i in range(3) if i != ax)

    def pick(e):
        a, b = e.verts[0].co, e.verts[1].co
        if callable(where):
            return bool(where(a, b))
        w = where.upper()
        if w == 'ALL':
            return True
        if w in ('X', 'Y', 'Z'):
            return parallel(a, b, "XYZ".index(w))
        if w == 'VERTICAL':
            return parallel(a, b, 2)
        if w == 'HORIZONTAL':
            return abs(a.z - b.z) < eps
        if w == 'TOP':
            return abs(a.z - z_top) < eps and abs(b.z - z_top) < eps
        if w == 'BOTTOM':
            return abs(a.z - z_bot) < eps and abs(b.z - z_bot) < eps
        raise ValueError(f"unknown edge selector: {where!r}")

    edges = [e for e in bm.edges if pick(e)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=radius, offset_type='OFFSET',
                        segments=segments, profile=profile, affect='EDGES')
    bm.to_mesh(me)
    bm.free()
    me.update()
    return obj


def round_edges_multi(obj, roundings, segments=6):
    """Several round_edges passes in order, each with its own radius / edge set / smoothness:
    roundings = [(radius, where), (radius, where, segments), ...]; `segments` is the default.
    Typical shell: [(10, 'VERTICAL', 8), (3, 'BOTTOM', 4), (0.6, 'TOP', 4)]
    (corners first, then the rims, so the rims follow the rounded corners)."""
    for item in roundings:
        r, where = item[0], item[1]
        seg = item[2] if len(item) > 2 else segments
        round_edges(obj, r, where, seg)
    return obj


def _round(obj, radius, where, segments):
    """radius = number (with `where`) or a round_edges_multi list; None/0 = no rounding."""
    if isinstance(radius, (list, tuple)):
        return round_edges_multi(obj, radius, segments)
    if radius:
        return round_edges(obj, radius, where, segments)
    return obj


def make_rounded_box(name, x_min, x_max, y_min, y_max, z_min, z_max, radius,
                     where='ALL', segments=6, coll=None):
    """Box with rounded edges in one call, e.g. where='VERTICAL' for rounded corners
    in plan view only (flat top and bottom), 'TOP' for a softened top rim.
    radius may also be a list for round_edges_multi (different radius per edge set)."""
    obj = make_box(name, x_min, x_max, y_min, y_max, z_min, z_max, coll)
    return _round(obj, radius, where, segments)


def boolean_apply(obj, cutter, operation='DIFFERENCE', delete_cutter=True, solver='EXACT', use_self=False):
    """Boolean `operation` ('DIFFERENCE' | 'UNION' | 'INTERSECT') of obj with cutter, applied.
    use_self=True lets the exact solver handle an operand that overlaps itself (several joined parts)."""
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = operation
    mod.object = cutter
    mod.solver = solver
    if use_self:
        mod.use_self = True
    apply_modifier(obj, mod)
    if delete_cutter:
        delete_object(cutter)


def boolean_diff_apply(obj, cutter, delete_cutter=True):
    """Subtract cutter from obj (same name/signature as the RC scripts)."""
    boolean_apply(obj, cutter, 'DIFFERENCE', delete_cutter)


def boolean_union_apply(obj, other, delete_other=True):
    """Fuse `other` into obj as one solid."""
    boolean_apply(obj, other, 'UNION', delete_other)


def boolean_intersect_apply(obj, other, delete_other=True):
    """Keep only the volume shared by obj and other."""
    boolean_apply(obj, other, 'INTERSECT', delete_other)


def cut_objects(objs, cutter, delete_cutter=True, margin=0.01):
    """Subtract one cutter from EVERY object in objs whose bounding box it touches (for a model
    kept as separate part meshes, where a cut can cross several parts). Returns the objects cut."""
    cmn, cmx = group_bbox([cutter])
    hit = []
    for o in objs:
        mn, mx = group_bbox([o])
        if all(cmn[k] <= mx[k] + margin and mn[k] <= cmx[k] + margin for k in range(3)):
            boolean_apply(o, cutter, 'DIFFERENCE', delete_cutter=False)
            hit.append(o)
    if delete_cutter:
        delete_object(cutter)
    return hit


def fuse_copies(objs, name, coll=None, clean=True):
    """One solid made from COPIES of objs (Boolean union, applied); the originals are untouched.
    Turns a model kept as separate part meshes into one printable mesh. Done as ONE union: the
    first part with all the others joined into a single (self-overlapping) operand, exact solver
    with self-intersection. Unioning part by part re-processed already-cut details and left open
    edges (socket-cut hinge knuckles on a shell). clean=True runs clean_for_stl on the result (the
    union leaves near-duplicate vertices that become doubled edges in the STL). Prints a warning if
    the result is not watertight."""
    objs = [o for o in objs if o.type == 'MESH']
    if not objs:
        raise ValueError("nothing to fuse")
    base = duplicate_object(objs[0], "_fuse_base", coll=coll)
    if len(objs) > 1:
        rest = join_objects([duplicate_object(o, "_fuse_part", coll=coll) for o in objs[1:]], "_fuse_rest")
        boolean_apply(base, rest, 'UNION', use_self=True)
    base.name = unique_name(name)
    base.data.name = base.name
    if clean:
        clean_for_stl(base)
    r = check_manifold(base)
    if not r["watertight"]:
        print(f"[WARN] fuse_copies({name}): result not watertight ({r['boundary_edges']} open, "
              f"{r['nonmanifold_edges']} non-manifold edges)")
    return base


def apply_array(obj, count, offset=(10.0, 0.0, 0.0)):
    """Repeat obj `count` times with a constant offset (mm), as one mesh."""
    mod = obj.modifiers.new(name="Array", type='ARRAY')
    mod.count = count
    mod.use_relative_offset = False
    mod.use_constant_offset = True
    mod.constant_offset_displace = offset
    apply_modifier(obj, mod)


def apply_solidify(obj, thickness, offset=-1.0):
    """Give a surface thickness (offset -1 grows inward, +1 outward). For open meshes / imports."""
    mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod.thickness = thickness
    mod.offset = offset
    apply_modifier(obj, mod)


# =====================================================================
# 4. PRINT-ORIENTED FEATURE BUILDERS
# =====================================================================

def make_bore_cutter(name, radius, z_bottom, z_top_target, top_overshoot=0.5,
                     bottom_overshoot=0.0, x=0, y=0, verts=32):
    """Cylinder cutter for a bore. Overshoot 0.5 on a side = open through that face;
    bottom_overshoot=0 = blind (closed) at that end. (Same convention as the RC build.)"""
    return make_cylinder(name + "_bore_cutter", radius,
                         z_bottom - bottom_overshoot, z_top_target + top_overshoot, x, y, verts)


def make_boss(name, x, y, z_min, z_max, outer_r, bore_r=None, bore='blind',
              overshoot=0.5, verts=32):
    """Screw boss / standoff / post. bore: 'blind' (closed at base, open top),
    'through' (open both ends) or None for a solid pin. Returns the finished object."""
    boss = make_cylinder(name, outer_r, z_min, z_max, x, y, verts)
    if bore_r and bore != 'none':
        bot_os = overshoot if bore == 'through' else 0.0
        cutter = make_bore_cutter(name, bore_r, z_min, z_max, overshoot, bot_os, x, y, verts)
        boolean_diff_apply(boss, cutter)
    return boss


def make_hollow_box(name, x_min, x_max, y_min, y_max, z_min, z_max, wall=2.5,
                    open_face='+Z', floor=None, bevel=None, bevel_segments=4, overshoot=2.0,
                    bevel_edges='ALL', inner_radius=None, inner_edges='VERTICAL'):
    """Hollow enclosure half: stock box -> optional bevel -> cavity cut (Boolean, applied).
    open_face: '+Z','-Z','+X','-X','+Y','-Y' or None (sealed, fully hollow).
    wall = thickness on the sides; floor = thickness of the face opposite the open one
    (defaults to wall). bevel = rounding width in mm (None = sharp);
    bevel_edges = which outer edges to round ('ALL', 'VERTICAL', 'TOP', ... see round_edges).
    inner_radius = fillet radius for the INSIDE cavity corners (inner_edges selects which,
    default the four vertical ones) -- stronger, easier to print, nicer to look at.
    bevel and inner_radius may also be round_edges_multi lists, e.g.
    bevel=[(10, 'VERTICAL', 8), (3, 'BOTTOM', 4), (0.6, 'TOP', 4)],
    inner_radius=[(7.6, 'VERTICAL', 8), (1.0, 'BOTTOM', 4)] (bevel_edges / inner_edges are then
    ignored). overshoot = how far the cavity cutter pokes out of the open face."""
    floor = wall if floor is None else floor
    obj = make_box(name, x_min, x_max, y_min, y_max, z_min, z_max)
    if isinstance(bevel, (list, tuple)):
        round_edges_multi(obj, bevel, bevel_segments)
    elif bevel:
        if bevel_edges == 'ALL':
            apply_bevel(obj, bevel, bevel_segments)
        else:                      # selective: 'VERTICAL', 'TOP', 'BOTTOM', ... see round_edges
            round_edges(obj, bevel, bevel_edges, bevel_segments)
    lo = [x_min + wall, y_min + wall, z_min + wall]
    hi = [x_max - wall, y_max - wall, z_max - wall]
    if open_face:
        axis = "XYZ".index(open_face[1])
        if open_face[0] == '+':
            hi[axis] = [x_max, y_max, z_max][axis] + overshoot
            lo[axis] = [x_min, y_min, z_min][axis] + floor
        else:
            lo[axis] = [x_min, y_min, z_min][axis] - overshoot
            hi[axis] = [x_max, y_max, z_max][axis] - floor
    cutter = make_box(name + "_cavity_cutter", lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    _round(cutter, inner_radius, inner_edges, bevel_segments)
    boolean_diff_apply(obj, cutter)
    return obj


def cut_cylinders(obj, positions, radius, z_min, z_max, verts=32):
    """Drill a round hole at each (x, y) -- e.g. button holes, screw-access holes."""
    for i, (x, y) in enumerate(positions, start=1):
        boolean_diff_apply(obj, make_cylinder(f"_cutter_hole_{i}", radius, z_min, z_max, x, y, verts))


def cut_boxes(obj, boxes):
    """Cut rectangular openings. boxes = [(x_min, x_max, y_min, y_max, z_min, z_max), ...]
    (display windows, USB-C / switch openings, vents)."""
    for i, b in enumerate(boxes, start=1):
        boolean_diff_apply(obj, make_box(f"_cutter_box_{i}", *b))


def cut_slots(obj, slots, width, z_min, z_max):
    """Cut round-ended slots. slots = [((x0, y0), (x1, y1)), ...]"""
    for i, (p0, p1) in enumerate(slots, start=1):
        boolean_diff_apply(obj, make_slot(f"_cutter_slot_{i}", p0, p1, width, z_min, z_max))


def make_countersink_cutter(name, x, y, z_top, shank_r, head_r, head_depth, shank_depth, overshoot=0.5):
    """Flat-head screw hole cutter, opening upward at z_top: cone of depth head_depth
    from head_r down to shank_r, then a shank_r bore shank_depth further down."""
    z_cone_bot = z_top - head_depth
    z_bot = z_cone_bot - shank_depth
    prof = [(0, z_bot), (shank_r, z_bot), (shank_r, z_cone_bot), (head_r, z_top),
            (head_r, z_top + overshoot), (0, z_top + overshoot)]
    return make_revolved(name, prof, x, y)


def make_counterbore_cutter(name, x, y, z_top, shank_r, head_r, head_depth, shank_depth, overshoot=0.5):
    """Socket-head screw hole cutter: wide head_r pocket head_depth deep, then shank_r bore."""
    z_cb = z_top - head_depth
    z_bot = z_cb - shank_depth
    prof = [(0, z_bot), (shank_r, z_bot), (shank_r, z_cb), (head_r, z_cb),
            (head_r, z_top + overshoot), (0, z_top + overshoot)]
    return make_revolved(name, prof, x, y)


def make_wire_cutter(name, radius, y_min, y_max, z_center, x=0.0, verts=48):
    """Cylinder cutter along Y (cable pass-through). Centre it on a seam edge and the
    Boolean leaves a half-round notch in each half (the RC split wire-entry hole)."""
    return make_cylinder_between(name, radius, (x, y_min, z_center), (x, y_max, z_center), verts)


def add_pcb_supports(positions, z_min, z_max, outer_r=2.5, bore_r=1.0, prefix="Support", bore='blind'):
    """Drop a post at each (x, y) -> list of objects (PCB / board standoffs)."""
    return [make_boss(f"{prefix}_{i}", x, y, z_min, z_max, outer_r, bore_r, bore)
            for i, (x, y) in enumerate(positions, start=1)]


def make_lid_lip(name, x_min, x_max, y_min, y_max, z_min, z_max, lip_t=1.2, corner_r=None,
                 segments=8):
    """Rectangular frame (outer box minus inner box) -- a lid lip / rim that drops into a case.
    corner_r rounds the outer vertical corners (match the cavity's corner radius minus the fit
    gap); the inner corners get corner_r - lip_t so the frame stays lip_t thick all round."""
    frame = make_box(name, x_min, x_max, y_min, y_max, z_min, z_max)
    cutter = make_box(name + "_cutter", x_min + lip_t, x_max - lip_t, y_min + lip_t, y_max - lip_t,
                      z_min - 1, z_max + 1)
    if corner_r:
        round_edges(frame, corner_r, 'VERTICAL', segments)
        if corner_r - lip_t > 1e-6:
            round_edges(cutter, corner_r - lip_t, 'VERTICAL', segments)
    boolean_diff_apply(frame, cutter)
    return frame


def chord_radius(width, depth):
    """Radius of the circle whose arc spans `width` and is `depth` deep (sagitta)."""
    return (width ** 2 / 4 + depth ** 2) / (2 * depth)


def cut_finger_notch(obj, p0, p1, width, depth, rim_z, verts=48):
    """Half-round finger scoop in a horizontal rim at height rim_z: an arc `width` wide at the
    rim and `depth` deep. p0, p1 = (x, y) points the cutter axis runs between, horizontally
    through the wall (start outside, stop just past the inner face so the scoop stays in the wall)."""
    r = chord_radius(width, depth)
    zc = rim_z - depth + r
    boolean_diff_apply(obj, make_cylinder_between("_cutter_notch", r, (p0[0], p0[1], zc),
                                                  (p1[0], p1[1], zc), verts=verts))


# =====================================================================
# 5. LAYOUT HELPERS (return lists of (x, y))
# =====================================================================

def grid_positions(nx, ny, dx, dy, center=(0.0, 0.0)):
    """nx x ny grid with spacing dx, dy, centred on `center` (vent grids, button matrices)."""
    ox = center[0] - dx * (nx - 1) / 2
    oy = center[1] - dy * (ny - 1) / 2
    return [(ox + i * dx, oy + j * dy) for j in range(ny) for i in range(nx)]


def linear_positions(n, step, start=(0.0, 0.0), direction=(0.0, 1.0)):
    """n points from `start`, `step` mm apart along `direction`."""
    d = Vector(direction).normalized()
    return [(start[0] + d.x * step * i, start[1] + d.y * step * i) for i in range(n)]


def polar_positions(n, radius, center=(0.0, 0.0), start_angle_deg=0.0):
    """n points evenly spaced on a circle (bolt circles, round button rings)."""
    return [(center[0] + radius * math.cos(math.radians(start_angle_deg + 360.0 * i / n)),
             center[1] + radius * math.sin(math.radians(start_angle_deg + 360.0 * i / n)))
            for i in range(n)]


def mirror_positions(positions, mirror_x=True, mirror_y=False):
    """Add mirrored copies (x -> -x and/or y -> -y); duplicates removed, order kept."""
    out = []
    for x, y in positions:
        cands = [(x, y)]
        if mirror_x:
            cands.append((-x, y))
        if mirror_y:
            cands += [(px, -py) for px, py in list(cands)]
        for c in cands:
            if not any(abs(c[0] - o[0]) < 1e-9 and abs(c[1] - o[1]) < 1e-9 for o in out):
                out.append(c)
    return out


# =====================================================================
# 6. TRANSFORMS
# =====================================================================

def translate_objects(objs, offset):
    """Move objects by (dx, dy, dz) -- the RC 'Upper dX = -80 mm' step."""
    for o in objs:
        o.location.x += offset[0]
        o.location.y += offset[1]
        o.location.z += offset[2]
    bpy.context.view_layer.update()


def rotate_objects(objs, axis, degrees, pivot=None):
    """Rotate a group rigidly about a world axis ('X'|'Y'|'Z') through `pivot`
    (default: the group's bounding-box centre)."""
    bpy.context.view_layer.update()        # matrix_world of just-created/moved objects is stale until then
    pivot = Vector(pivot) if pivot is not None else group_bbox_center(objs)
    rot = Matrix.Rotation(math.radians(degrees), 4, axis.upper())
    xf = Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot)
    for o in objs:
        o.matrix_world = xf @ o.matrix_world
    bpy.context.view_layer.update()


def flip_objects(objs, axis='X', pivot=None):
    """Turn a group over (180 degrees) about a world axis. NOTE: flipping about X mirrors Y,
    flipping about Y mirrors X (book-style closing of a case = flip about its long axis)."""
    rotate_objects(objs, axis, 180.0, pivot)


def group_bbox(objs):
    """World-space (min Vector, max Vector) of a group of objects."""
    bpy.context.view_layer.update()        # matrix_world of just-created/moved objects is stale until then
    mn = Vector((math.inf,) * 3)
    mx = Vector((-math.inf,) * 3)
    for o in objs:
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            mn = Vector((min(mn[i], w[i]) for i in range(3)))
            mx = Vector((max(mx[i], w[i]) for i in range(3)))
    return mn, mx


def group_bbox_center(objs):
    mn, mx = group_bbox(objs)
    return (mn + mx) / 2


def drop_to_bed(objs, z=0.0):
    """Shift a group vertically so its lowest point sits on Z=z (the print bed)."""
    mn, _ = group_bbox(objs)
    translate_objects(objs, (0, 0, z - mn.z))


def arrange_in_row(groups, gap=10.0, axis='X'):
    """Lay out parts side by side on the bed. `groups` = list of object lists (one per part,
    e.g. a shell + its bosses). Each group is moved so they sit in a row, `gap` mm apart,
    starting at the first group's position."""
    i = "XYZ".index(axis.upper())
    cursor = None
    for g in groups:
        mn, mx = group_bbox(g)
        if cursor is None:
            cursor = mx[i] + gap
            continue
        off = [0.0, 0.0, 0.0]
        off[i] = cursor - mn[i]
        translate_objects(g, off)
        cursor += (mx[i] - mn[i]) + gap


def join_objects(objs, name=None):
    """Merge several mesh objects into one (no boolean; overlapping parts stay overlapping).
    For a true fused solid, use boolean_union_apply."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    if name:
        result.name = unique_name(name)
    return result


def duplicate_object(obj, name=None, offset=(0, 0, 0), coll=None):
    """Independent copy of a mesh object (own mesh data), optionally moved by offset."""
    new = obj.copy()
    new.data = obj.data.copy()
    new.name = unique_name(name or obj.name)
    new.location = new.location + Vector(offset)
    return link_only(new, coll)


# =====================================================================
# 7. INSPECTION
# =====================================================================

def _world_bmesh(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    ev.to_mesh_clear()
    bm.transform(obj.matrix_world)
    bm.normal_update()      # transform() leaves face normals stale (wrong after a flip/rotation)
    return bm


def check_manifold(obj):
    """Watertight test for printing. Returns dict: boundary_edges (holes), nonmanifold_edges
    (3+ faces / wire), watertight (bool), volume_mm3, dimensions (x, y, z), modifiers."""
    bm = _world_bmesh(obj)
    boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) == 0 or len(e.link_faces) > 2)
    vol = abs(bm.calc_volume())
    bm.free()
    return {"name": obj.name, "boundary_edges": boundary, "nonmanifold_edges": nonman,
            "watertight": boundary == 0 and nonman == 0, "volume_mm3": round(vol, 2),
            "dimensions": tuple(round(v, 3) for v in obj.dimensions),
            "modifiers": len(obj.modifiers)}


def print_report(objs=None, min_wall=None, bed=None, overhang_deg=None):
    """Print one line per mesh object: size, volume, watertight, leftover modifiers.
    Optional extra checks (slower): min_wall=mm flags walls thinner than that,
    bed=(x, y, z) flags parts bigger than the print bed, overhang_deg=45 reports
    unsupported-overhang area. Returns the list of result dicts.
    Default objs: every object in the active collection."""
    if objs is None:
        objs = list(_active_collection.objects) if _active_collection else list(bpy.context.scene.objects)
    rows = [check_manifold(o) for o in objs if o.type == 'MESH']
    for r in rows:
        o = bpy.data.objects[r["name"]]
        extra, ok = "", r["watertight"] and r["modifiers"] == 0
        if min_wall is not None:
            t, _ = min_wall_thickness(o)
            r["min_wall_mm"] = None if t == math.inf else round(t, 3)
            extra += f" min_wall={r['min_wall_mm']}"
            ok = ok and (t == math.inf or t >= min_wall)
        if bed is not None:
            fit = check_bed_fit([o], bed)
            r["fits_bed"] = fit["fits"]
            extra += "" if fit["fits"] else " TOO_BIG_FOR_BED"
            ok = ok and fit["fits"]
        if overhang_deg is not None:
            oh = overhang_report(o, overhang_deg)
            r["overhang_area_mm2"] = oh["area_mm2"]
            extra += f" overhang={oh['area_mm2']:.0f}mm2"
        flag = "OK " if ok else "BAD"
        print(f"[{flag}] {r['name']:<34} dims={r['dimensions']} vol={r['volume_mm3']:>10.1f} mm3 "
              f"open_edges={r['boundary_edges']} nonmanifold={r['nonmanifold_edges']} mods={r['modifiers']}{extra}")
    return rows


# =====================================================================
# 8. EXPORT / SAVE
# =====================================================================

def default_output_dir(sub="exports"):
    """<folder of the saved .blend>/exports, or <cwd>/exports if the file is unsaved."""
    base = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
    return os.path.join(base, sub)


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def safe_filename(name):
    return re.sub(r"[^\w\-.]+", "_", name)


def clean_for_stl(obj, dist=1e-4):
    """Merge vertices closer than `dist` mm, dissolve degenerate (zero-area / zero-length) faces and
    edges, and triangulate (BEAUTY), in place. Use it on Boolean results before exporting: a union
    can leave near-duplicate vertices that Blender treats as separate (mesh reads watertight) but
    that become identical in the STL's 32-bit floats, so the STL gets doubled / unpaired edges
    (~220 on the G9 dome adapter; 0 after this). Do not run it on meshes you still want to edit as
    quads. fuse_copies does it by default."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=dist)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def export_stl(filepath, objs=None, ascii_format=False, apply_modifiers=True):
    """Export the given objects (default: active collection) as ONE STL, in mm.
    Works on Blender 4.2+ (wm.stl_export) and older (export_mesh.stl). Selection is restored."""
    if objs is None:
        objs = list(_active_collection.objects) if _active_collection else list(bpy.context.scene.objects)
    objs = [o for o in objs if o.type == 'MESH']
    if not objs:
        raise ValueError("nothing to export")
    _ensure_dir(os.path.dirname(os.path.abspath(filepath)))

    vl = bpy.context.view_layer
    prev_sel = [o for o in vl.objects if o.select_get()]
    prev_active = vl.objects.active
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]
    try:
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=filepath, export_selected_objects=True,
                                  ascii_format=ascii_format, apply_modifiers=apply_modifiers,
                                  global_scale=1.0)
        else:
            bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True, ascii=ascii_format,
                                    use_mesh_modifiers=apply_modifiers, global_scale=1.0)
    finally:
        for o in vl.objects:
            o.select_set(False)
        for o in prev_sel:
            o.select_set(True)
        vl.objects.active = prev_active
    return filepath


def export_stl_per_object(folder, objs=None, prefix="", **kw):
    """One STL per object (what you normally slice/print separately). Returns the paths."""
    if objs is None:
        objs = list(_active_collection.objects) if _active_collection else list(bpy.context.scene.objects)
    _ensure_dir(folder)
    paths = []
    for o in objs:
        if o.type == 'MESH':
            p = os.path.join(folder, safe_filename(prefix + o.name) + ".stl")
            export_stl(p, [o], **kw)
            paths.append(p)
    return paths


def save_blend(filepath=None, copy=False):
    """Save the .blend. filepath=None re-saves the current file (must already have a path).
    copy=True writes a copy and keeps the open file pointing where it was."""
    if filepath is None:
        if not bpy.data.filepath:
            raise ValueError("file has never been saved: pass a filepath")
        bpy.ops.wm.save_mainfile()
        return bpy.data.filepath
    _ensure_dir(os.path.dirname(os.path.abspath(filepath)))
    bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=copy)
    return filepath


def export_all(out_dir=None, basename="model", objs=None, per_part=True, combined=True,
               blend=True, ascii_format=False, threemf=False):
    """One call to save everything: <basename>.blend (a copy), <basename>_all.stl, and a
    parts/ folder with one STL per object; threemf=True also writes <basename>.3mf (all parts
    in one multi-object file). Returns {'blend':..., 'combined':..., 'parts':[...], '3mf':...}."""
    out_dir = _ensure_dir(out_dir or default_output_dir())
    result = {}
    if blend:
        result["blend"] = save_blend(os.path.join(out_dir, basename + ".blend"), copy=True)
    if combined:
        result["combined"] = export_stl(os.path.join(out_dir, basename + "_all.stl"), objs,
                                        ascii_format=ascii_format)
    if per_part:
        result["parts"] = export_stl_per_object(os.path.join(out_dir, "parts"), objs,
                                                ascii_format=ascii_format)
    if threemf:
        result["3mf"] = export_3mf(os.path.join(out_dir, basename + ".3mf"), objs)
    print("exported ->", out_dir)
    return result


def export_3mf(filepath, objs=None):
    """Export the objects as ONE .3mf file (millimetres, each object kept separate so the slicer
    can move/colour them individually). Self-contained writer: no Blender add-on needed."""
    if objs is None:
        objs = list(_active_collection.objects) if _active_collection else list(bpy.context.scene.objects)
    objs = [o for o in objs if o.type == 'MESH']
    if not objs:
        raise ValueError("nothing to export")
    res, items = [], []
    for idx, o in enumerate(objs, start=1):
        verts_w, tris_w, _, _ = _world_tris(o)
        verts = "".join(f'<vertex x="{v.x:.6f}" y="{v.y:.6f}" z="{v.z:.6f}"/>' for v in verts_w)
        tris = "".join(f'<triangle v1="{i}" v2="{j}" v3="{k}"/>' for i, j, k in tris_w)
        res.append(f'<object id="{idx}" name={quoteattr(o.name)} type="model"><mesh>'
                   f'<vertices>{verts}</vertices><triangles>{tris}</triangles></mesh></object>')
        items.append(f'<item objectid="{idx}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(res)}</resources><build>{"".join(items)}</build></model>')
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                     '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    _ensure_dir(os.path.dirname(os.path.abspath(filepath)))
    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
    return filepath


# =====================================================================
# 9. TOLERANCES, SCREW / INSERT TABLES, PARAMETERS
# =====================================================================

# Clearance (mm, added to the DIAMETER or per side as noted in each helper). FDM starting
# points -- print a small test piece and adjust for your printer / filament.
TOL_PRESS = 0.10     # tight press fit (pins, magnets)
TOL_SNUG = 0.15      # snug, hand assembly
TOL_SLIDE = 0.25     # sliding fit (lids, nut traps)
TOL_LOOSE = 0.40     # loose / easy

# Typical metric screw data (mm). clear = clearance hole dia, pilot = self-tapping pilot dia in
# plastic, insert = heat-set insert hole dia, insert_depth = pocket depth, head_d/head_h = cap head,
# nut_af/nut_h = hex nut across-flats / height. Approximate: check your insert/screw supplier.
SCREWS = {
    'M2':   dict(d=2.0, clear=2.4, pilot=1.7, insert=3.2, insert_depth=4.0, head_d=3.8, head_h=2.0, nut_af=4.0, nut_h=1.6),
    'M2.5': dict(d=2.5, clear=2.9, pilot=2.1, insert=3.6, insert_depth=4.0, head_d=4.5, head_h=2.5, nut_af=5.0, nut_h=2.0),
    'M3':   dict(d=3.0, clear=3.4, pilot=2.5, insert=4.2, insert_depth=5.0, head_d=5.5, head_h=3.0, nut_af=5.5, nut_h=2.4),
    'M4':   dict(d=4.0, clear=4.5, pilot=3.3, insert=5.6, insert_depth=6.0, head_d=7.0, head_h=4.0, nut_af=7.0, nut_h=3.2),
    'M5':   dict(d=5.0, clear=5.5, pilot=4.2, insert=6.4, insert_depth=7.0, head_d=8.5, head_h=5.0, nut_af=8.0, nut_h=4.0),
}

# Typical build volumes (x, y, z mm) for check_bed_fit.
BEDS = {'ender3': (220, 220, 250), 'prusa_mk4': (250, 210, 220), 'bambu': (256, 256, 256),
        'small': (180, 180, 180)}


def screw_spec(screw):
    """Dict of dimensions for 'M2' .. 'M5' (see SCREWS)."""
    try:
        return SCREWS[screw]
    except KeyError:
        raise ValueError(f"unknown screw {screw!r}; known: {list(SCREWS)}")


def clearance(diameter, tol=TOL_SLIDE):
    """Diameter to model for a hole that must accept a part of `diameter` (adds tol)."""
    return diameter + tol


class Params(dict):
    """Design parameters in one place with attribute access and a printable summary:
        P = Params(width=57.5, wall=2.5); P.height = 15; print(P.width); P.report()"""
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        self[k] = v

    def report(self):
        for k, v in self.items():
            print(f"  {k:<24} = {v}")


# =====================================================================
# 10. SCREW / INSERT / NUT / MAGNET FEATURES
# =====================================================================

def make_screw_boss(name, x, y, z_min, z_max, screw='M3', kind='pilot', outer_r=None, wall=1.6):
    """Boss sized from the screw table. kind: 'pilot' (self-tapping, blind, open top),
    'insert' (heat-set insert pocket from the top, insert_depth deep), 'clearance' (through).
    outer_r defaults to hole radius + wall."""
    s = screw_spec(screw)
    hole_d = {'pilot': s['pilot'], 'insert': s['insert'], 'clearance': s['clear']}[kind]
    outer_r = outer_r or hole_d / 2 + wall
    boss = make_cylinder(name, outer_r, z_min, z_max, x, y)
    if kind == 'insert':
        cutter = make_cylinder(name + "_cutter", hole_d / 2, max(z_min, z_max - s['insert_depth']), z_max + 0.5, x, y)
    else:
        cutter = make_bore_cutter(name, hole_d / 2, z_min, z_max, 0.5, 0.5 if kind == 'clearance' else 0.0, x, y)
    boolean_diff_apply(boss, cutter)
    return boss


def make_screw_hole_cutter(name, x, y, z_top, screw='M3', style='clearance', depth=10.0):
    """Cutter for a screw hole opening upward at z_top. style: 'clearance' (plain),
    'countersink' (flat head, 90 deg), 'counterbore' (socket/cap head). depth = total hole depth."""
    s = screw_spec(screw)
    r = s['clear'] / 2
    if style == 'clearance':
        return make_cylinder(name, r, z_top - depth, z_top + 0.5, x, y)
    if style == 'countersink':
        hr = s['head_d'] / 2 + 0.2
        return make_countersink_cutter(name, x, y, z_top, r, hr, hr - r, depth - (hr - r))
    if style == 'counterbore':
        return make_counterbore_cutter(name, x, y, z_top, r, s['head_d'] / 2 + 0.3, s['head_h'] + 0.3,
                                       depth - s['head_h'] - 0.3)
    raise ValueError(f"unknown style {style!r}")


def make_nut_trap_cutter(name, x, y, z_bottom, screw='M3', tol=TOL_SLIDE, slide_len=0.0, slide_angle_deg=0.0):
    """Hex pocket for a captive nut, starting at z_bottom and as tall as the nut. slide_len > 0
    adds a slot so the nut can slide in sideways, in direction slide_angle_deg (0 = +X).
    Add a screw hole separately (make_screw_hole_cutter / make_bore_cutter)."""
    s = screw_spec(screw)
    af = s['nut_af'] + tol
    h = s['nut_h'] + tol
    hexa = make_cylinder(name, af / math.sqrt(3), z_bottom, z_bottom + h, x, y, verts=6)
    if slide_len > 0:
        slot = make_box(name + "_slot", x, x + slide_len, y - af / 2, y + af / 2, z_bottom, z_bottom + h)
        boolean_union_apply(hexa, slot)
    hexa.rotation_euler.z = math.radians(slide_angle_deg)
    return hexa


def make_magnet_pocket_cutter(name, x, y, z_bottom, dia, thickness, tol=TOL_PRESS, open_top=True):
    """Round pocket for a disc magnet. Depth = thickness + tol; open_top adds 0.5 mm overshoot."""
    return make_cylinder(name, (dia + tol) / 2, z_bottom, z_bottom + thickness + tol + (0.5 if open_top else 0.0), x, y)


# ---------------------------------------------------------------------
# 10b. Printed threads (built directly from rings, no Boolean)
# ---------------------------------------------------------------------
# A thread surface is r(angle, z) = r_min + (r_max - r_min) * amp * form(z / pitch - angle / 2pi)
# (right hand; left=True mirrors it). form(t) is one pitch of profile, 0 = root, 1 = crest.
# Threads are vertical in print (axis = Z): best quality, no supports. Values are typical
# starting points: print a short test piece and adjust the clearance.

def thread_form_round(t):
    """Rounded (sinusoidal) thread profile: glass / lamp-shade threads, coarse forgiving fits."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * t)


def thread_form_iso(t):
    """ISO metric 60-degree trapezoid profile (crest P/8, root P/4), 0 = root, 1 = crest."""
    t %= 1.0
    if t < 0.125:
        return 1.0
    if t < 0.4375:
        return 1.0 - (t - 0.125) / 0.3125
    if t < 0.6875:
        return 0.0
    return (t - 0.6875) / 0.3125


THREAD_FORMS = {'round': thread_form_round, 'iso': thread_form_iso}

METRIC_COARSE_PITCH = {'M3': 0.5, 'M4': 0.7, 'M5': 0.8, 'M6': 1.0, 'M8': 1.25, 'M10': 1.5,
                       'M12': 1.75, 'M16': 2.0, 'M20': 2.5}

# Non-metric threads: nominal major / minor diameters (not verified hardware data; measure yours).
THREADS = {
    'G9_shade': dict(major=20.8, minor=19.2, pitch=2.0, form='round'),   # M20.8 x 2 G9 lamp-shade ring
}


def thread_spec(name, internal=False, clearance=0.2):
    """Thread section dict for make_threaded_tube: r_min, r_max, pitch, form.
    name: 'M10' (coarse pitch), 'M10x1' (fine), or a key of THREADS ('G9_shade').
    internal=True: a printed NUT thread (the hole), radii grow by `clearance` mm per side;
    internal=False: a printed BOLT thread, radii shrink by `clearance`. ISO minor diameters:
    internal d - 1.0825 P, external d - 1.2269 P. Example: thread_spec('M10x1', internal=True)
    -> r 4.659 .. 5.2 (minor 9.317 / major 10.4)."""
    if name in THREADS:
        t = THREADS[name]
        major, minor, pitch, form = t['major'], t['minor'], t['pitch'], t['form']
    else:
        m = re.fullmatch(r"M(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?", name)
        if not m:
            raise ValueError(f"unknown thread {name!r}: use 'M10', 'M10x1' or one of {list(THREADS)}")
        major = float(m.group(1))
        if m.group(2):
            pitch = float(m.group(2))
        elif f"M{m.group(1)}" in METRIC_COARSE_PITCH:
            pitch = METRIC_COARSE_PITCH[f"M{m.group(1)}"]
        else:
            raise ValueError(f"no coarse pitch known for {name!r}: give it as 'M{m.group(1)}x<pitch>'")
        minor = major - (1.0825 if internal else 1.2269) * pitch
        form = 'iso'
    c = clearance if internal else -clearance
    return dict(r_min=minor / 2 + c, r_max=major / 2 + c, pitch=pitch, form=form)


def thread_radii(z, r_min, r_max, pitch, form='iso', amp=1.0, segments=96, left=False):
    """One ring of `segments` radii of a thread surface at height z (see the section note).
    amp (0..1) scales the thread height, e.g. for a lead-in."""
    f = THREAD_FORMS[form] if isinstance(form, str) else form
    s = 1.0 if left else -1.0
    return [r_min + (r_max - r_min) * amp * f(z / pitch + s * i / segments) for i in range(segments)]


def thread_z_steps(z0, z1, pitch, steps_per_pitch=16):
    """Ring heights from z0 to z1 (both included), steps_per_pitch rings per pitch."""
    k = max(1, int(math.ceil((z1 - z0) / pitch * steps_per_pitch)))
    return [z0 + (z1 - z0) * i / k for i in range(k + 1)]


def make_ring_tube(name, outer, inner, x=0.0, y=0.0, z=0.0, coll=None):
    """Watertight tube from rings, no Boolean. outer / inner = [(z, [radius per angle]), ...] from
    bottom to top, every ring the same length (angle 0 on +X). Two consecutive rings at the same z
    make a flat step. Flat ring faces join the first outer ring to the first inner ring (bottom)
    and the last to the last (top), so both lists must start and end at the same z. Inner radii
    must stay below the outer ones. Low-level: make_threaded_tube builds the ring lists for you."""
    n = len(outer[0][1])
    if any(len(r) != n for _, r in outer + inner):
        raise ValueError("every ring must have the same number of radii")
    bm = bmesh.new()

    def ring(pz, radii):
        return [bm.verts.new((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), pz))
                for i, r in enumerate(radii)]

    def band(a, b):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))

    o = [ring(pz, rr) for pz, rr in outer]
    m = [ring(pz, rr) for pz, rr in inner]
    for k in range(len(o) - 1):
        band(o[k], o[k + 1])
    for k in range(len(m) - 1):
        band(m[k], m[k + 1])
    band(o[0], m[0])
    band(o[-1], m[-1])
    return _new_object(name, bm, (x, y, z), coll)


def _thread_rings(z0, z1, surface, segments, steps_per_pitch):
    """Ring list (z, radii) for one surface of make_threaded_tube."""
    if isinstance(surface, (int, float)):
        surface = [dict(r=float(surface))]
    elif isinstance(surface, dict):
        surface = [surface]
    rings, start = [], z0
    for idx, sec in enumerate(surface):
        end = z1 if idx == len(surface) - 1 else sec['z1']
        if end <= start:
            raise ValueError(f"thread section {idx} ends at z={end}, not above its start z={start}")
        if 'r' in sec:
            new = [(start, [sec['r']] * segments), (end, [sec['r']] * segments)]
        else:
            leadin, leadout = sec.get('leadin', 0.0), sec.get('leadout', 0.0)
            new = []
            for pz in thread_z_steps(start, end, sec['pitch'], steps_per_pitch):
                amp = 1.0
                if leadin > 0:
                    amp = min(amp, (pz - start) / leadin)
                if leadout > 0:
                    amp = min(amp, (end - pz) / leadout)
                new.append((pz, thread_radii(pz, sec['r_min'], sec['r_max'], sec['pitch'],
                                             sec.get('form', 'iso'), amp, segments, sec.get('left', False))))
        if rings and rings[-1][1] == new[0][1]:     # same ring twice would make zero-area faces
            new = new[1:]
        rings += new
        start = end
    return rings


def make_threaded_tube(name, z0, z1, outer, inner, segments=96, steps_per_pitch=16,
                       x=0.0, y=0.0, coll=None):
    """Tube along Z from z0 to z1 with threaded and/or plain outer and inner surfaces, built
    directly from rings (watertight, no Boolean: exact-Boolean thread cutters left slivers and open
    edges). Each surface is
      * a number: plain radius, or
      * a section dict: plain {'r': 6.2} or thread {'r_min', 'r_max', 'pitch', 'form' ('iso' |
        'round' | callable), optional 'leadin' / 'leadout' (mm over which the thread fades in at
        the section's bottom / out at its top), 'left': True}; thread_spec() makes these, or
      * a list of section dicts from bottom to top; each but the last gives its top 'z1' (the last
        ends at z1). A change of radius between sections is a flat step.
    The thread phase is absolute in z, so tubes built with the same values mesh with each other.
    Example (G9 dome adapter spigot): G9 shade thread outside, M10x1 nut thread inside up to z=0,
    then a plain dia 12.4 bore:
        make_threaded_tube("Spigot", -15, 1.05,
            outer=dict(thread_spec('G9_shade', clearance=0.1), leadin=2.0),
            inner=[dict(thread_spec('M10x1', internal=True), z1=0.0), dict(r=6.2)])"""
    out = _thread_rings(z0, z1, outer, segments, steps_per_pitch)
    inn = _thread_rings(z0, z1, inner, segments, steps_per_pitch)
    return make_ring_tube(name, out, inn, x, y, 0.0, coll)


# =====================================================================
# 11. SNAP FITS, VENTS, TEXT
# =====================================================================

def make_prism_xz(name, pts_xz, y_min, y_max, location=(0, 0, 0), coll=None):
    """Extrude a 2D polygon given as (x, z) points along Y from y_min to y_max
    (= make_prism(name, pts_xz, 'Y', y_min, y_max))."""
    return make_prism(name, pts_xz, 'Y', y_min, y_max, location, coll)


_DIRS = {'+X': (1, 0), '-X': (-1, 0), '+Y': (0, 1), '-Y': (0, -1)}


def make_snap_hook(name, x, y, z_base, width=6.0, length=8.0, thickness=1.2, hook_depth=0.8,
                   hook_height=1.5, angle_deg=0.0, coll=None, direction='+X', hanging=False,
                   pointed=False):
    """Cantilever snap hook. (x, y, z_base) = root of the arm's BACK face (the face away from the
    tip), centred across its width. The arm is `thickness` thick in the flex direction, `length`
    long, `width` wide; the tip protrudes `hook_depth` toward `direction` ('+X' | '-X' | '+Y' | '-Y')
    with a flat catch face toward the root and a ramp toward the free end for easy insertion.
    hanging=False: the arm stands UP from z_base; True: it hangs DOWN from z_base (a lid hook).
    pointed=False: the ramp covers only the tip (flat arm end); True: the ramp runs from the
    back face at the free end all the way to the tip (a wedge, no flat end).
    angle_deg additionally turns the object about Z (object rotation, around the root point).
    To fuse the hook into a part, start it inside the part (z_base a little into the material).
    Rule of thumb: length >= 6 x hook_depth, thickness 1.0-1.5 for PLA/PETG."""
    t, L, hd, hh = thickness, length, hook_depth, hook_height
    if pointed:
        prof = [(0, 0), (t, 0), (t, L - hh), (t + hd, L - hh), (0, L)]
    else:
        prof = [(0, 0), (t, 0), (t, L - hh), (t + hd, L - hh), (t, L), (0, L)]
    try:
        dx, dy = _DIRS[direction.upper()]
    except KeyError:
        raise ValueError(f"direction must be one of {list(_DIRS)}")
    wx, wy = -dy, dx                           # width direction = Z x direction
    up = -1.0 if hanging else 1.0
    bm = bmesh.new()
    rings = []
    for side in (-width / 2, width / 2):
        rings.append([bm.verts.new((uu * dx + side * wx, uu * dy + side * wy, up * s)) for uu, s in prof])
    a, b = rings
    n = len(prof)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    obj = _new_object(name, bm, (x, y, z_base), coll)
    obj.rotation_euler.z = math.radians(angle_deg)
    return obj


def make_snap_catch_cutter(name, x, y, z_center, width=6.0, depth=1.2, height=2.0, tol=TOL_SLIDE,
                           angle_deg=0.0, coll=None):
    """Rectangular window the snap hook's tip clicks into (cut it into the mating wall)."""
    obj = make_box_centered(name, (x, y, z_center), (depth + tol, width + tol, height + tol), coll)
    obj.rotation_euler.z = math.radians(angle_deg)
    return obj


def cut_vent_slots(obj, center, n, slot_len, slot_w, pitch, z_min, z_max, along='Y'):
    """Row of n parallel vent slots centred on `center` (x, y). Slots run along 'Y' (side by
    side in X) or along 'X' (stacked in Y); pitch = centre-to-centre spacing."""
    cx, cy = center
    half = (slot_len - slot_w) / 2
    slots = []
    for i in range(n):
        off = (i - (n - 1) / 2) * pitch
        if along.upper() == 'Y':
            slots.append(((cx + off, cy - half), (cx + off, cy + half)))
        else:
            slots.append(((cx - half, cy + off), (cx + half, cy + off)))
    cut_slots(obj, slots, slot_w, z_min, z_max)


def cut_hex_vents(obj, nx, ny, across_flats, z_min, z_max, web=1.2, center=(0.0, 0.0)):
    """Honeycomb vent pattern: nx columns x ny rows of hex holes (across_flats mm) separated by
    `web` mm of material, centred on `center`."""
    af2 = across_flats + web
    r_pitch = af2 / math.sqrt(3)
    r_hole = across_flats / math.sqrt(3)
    pts = []
    for i in range(nx):
        for j in range(ny):
            pts.append((i * 1.5 * r_pitch, j * af2 + (af2 / 2 if i % 2 else 0.0)))
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    for k, (px, py) in enumerate(pts, start=1):
        boolean_diff_apply(obj, make_cylinder(f"_cutter_hex_{k}", r_hole, z_min, z_max,
                                              center[0] + px - mx, center[1] + py - my, verts=6))


def make_text(name, text, size=5.0, depth=1.0, x=0.0, y=0.0, z=0.0, align='CENTER',
              font_path=None, coll=None, rot_deg=0.0):
    """3D text mesh lying in the XY plane, `depth` thick, bottom at z, centred on (x, y).
    rot_deg turns it about Z (90 = reads along +Y). engrave_text / emboss_text pass it through."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = text
    cu.size = size
    cu.extrude = depth / 2.0
    cu.align_x = align
    cu.align_y = 'CENTER'
    if font_path:
        cu.font = bpy.data.fonts.load(font_path)
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(deps), depsgraph=deps)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    obj = bpy.data.objects.new(unique_name(name), me)
    obj.location = (x, y, z + depth / 2.0)
    obj.rotation_euler.z = math.radians(rot_deg)
    return link_only(obj, coll)


def engrave_text(obj, text, x, y, z_surface, size=5.0, depth=0.6, **kw):
    """Cut text DEEPER into a top-facing surface at z_surface (e.g. a lid label)."""
    t = make_text("_text_cutter", text, size, depth + 0.3, x, y, z_surface - depth, **kw)
    boolean_diff_apply(obj, t)


def emboss_text(obj, text, x, y, z_surface, size=5.0, height=0.6, **kw):
    """Raise text above a top-facing surface at z_surface (fused to obj). Keep strokes >= 0.8 mm."""
    t = make_text("_text_add", text, size, height + 0.3, x, y, z_surface - 0.3, **kw)
    boolean_union_apply(obj, t)


# =====================================================================
# 12. PRINT-QUALITY CHECKS
# =====================================================================

def _world_tris(obj):
    """World-space triangles using Blender's own tessellation (the same one the viewport and the
    STL exporter use). bmesh.ops.triangulate mishandles big concave faces (plates with many holes),
    so every analysis below works from these. Returns (verts, tris, normals, areas): vertex
    positions, index triples, unit triangle normals (from the winding) and triangle areas."""
    bm = _world_bmesh(obj)
    bm.verts.index_update()
    verts = [v.co.copy() for v in bm.verts]
    tris, normals, areas = [], [], []
    for lt in bm.calc_loop_triangles():
        i, j, k = (l.vert.index for l in lt)
        n = (verts[j] - verts[i]).cross(verts[k] - verts[i])
        a = n.length / 2.0
        if a < 1e-9:
            continue
        tris.append((i, j, k))
        normals.append(n.normalized())
        areas.append(a)
    bm.free()
    return verts, tris, normals, areas


def min_wall_thickness(obj, max_dist=20.0):
    """Estimate the thinnest wall: from every triangle, shoot a ray into the solid and measure the
    distance to the far side. Returns (thickness_mm, location Vector) -- (inf, None) if no hit.
    Sampled at triangle centres, so it is an estimate; very small features can be missed, and the
    tapering edge of a rounded plate can still read thin by nature (the edge, not a wall defect)."""
    verts, tris, normals, _ = _world_tris(obj)
    tree = BVHTree.FromPolygons(verts, tris)
    best, where = math.inf, None
    eps = 1e-3
    for (i, j, k), n in zip(tris, normals):
        c = (verts[i] + verts[j] + verts[k]) / 3.0
        hit = tree.ray_cast(c - n * eps, -n, max_dist)
        # count only hits on a face that roughly opposes the ray (a real wall), not grazing hits on
        # a perpendicular neighbour (rims of holes, rounded edges)
        if hit[0] is not None and hit[1].dot(n) < -0.7 and hit[3] + eps < best:
            best, where = hit[3] + eps, c.copy()
    return best, where


def overhang_report(obj, max_angle_deg=45.0):
    """Area of down-facing surfaces steeper than max_angle_deg from vertical (they need supports),
    ignoring faces resting on the bed. Returns dict(area_mm2, fraction, faces)."""
    verts, tris, normals, areas = _world_tris(obj)
    z_min = min(v.z for v in verts)
    limit = -math.sin(math.radians(max_angle_deg))
    area = 0.0
    faces = 0
    for (i, j, k), n, a in zip(tris, normals, areas):
        if n.z < limit and (verts[i].z + verts[j].z + verts[k].z) / 3.0 > z_min + 0.01:
            area += a
            faces += 1
    total = sum(areas)
    return {"area_mm2": round(area, 2), "fraction": round(area / total, 4) if total else 0.0, "faces": faces}


def check_bed_fit(objs, bed=(220, 220, 250)):
    """Does the group's bounding box fit the build volume? bed = (x, y, z) or a BEDS key.
    Returns dict(fits, size, bed). Rotating 90 degrees about Z is allowed."""
    bed = BEDS[bed] if isinstance(bed, str) else bed
    mn, mx = group_bbox(objs)
    size = tuple(round(v, 2) for v in (mx - mn))
    fits = size[2] <= bed[2] and (
        (size[0] <= bed[0] and size[1] <= bed[1]) or (size[0] <= bed[1] and size[1] <= bed[0]))
    return {"fits": fits, "size": size, "bed": tuple(bed)}


def split_object(obj, axis='X', position=0.0, pin_positions=(), pin_r=2.0, pin_len=6.0,
                 tol=TOL_SLIDE, delete_original=True):
    """Cut a too-large part in two at world coordinate `position` along axis ('X'|'Y'|'Z').
    pin_positions = [(u, v), ...] in the cut plane (the two OTHER axes in XYZ order) add alignment
    pins on half A with matching holes in half B. Returns (A, B): A is the low side, B the high."""
    i = "XYZ".index(axis.upper())
    big = 10000.0

    def half(low):
        lo, hi = [-big] * 3, [big] * 3
        if low:
            hi[i] = position
        else:
            lo[i] = position
        return make_box("_split_box", lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])

    a = duplicate_object(obj, obj.name + "_A")
    b = duplicate_object(obj, obj.name + "_B")
    boolean_intersect_apply(a, half(True))
    boolean_intersect_apply(b, half(False))
    others = [k for k in range(3) if k != i]

    def pt(pu, pv, t):
        p = [0.0, 0.0, 0.0]
        p[others[0]], p[others[1]], p[i] = pu, pv, t
        return tuple(p)

    for k, (pu, pv) in enumerate(pin_positions, start=1):
        pin = make_cylinder_between(f"_pin_{k}", pin_r, pt(pu, pv, position - pin_len), pt(pu, pv, position + pin_len))
        boolean_union_apply(a, pin)
        hole = make_cylinder_between(f"_pinhole_{k}", pin_r + tol / 2, pt(pu, pv, position - 0.5),
                                     pt(pu, pv, position + pin_len + tol))
        boolean_diff_apply(b, hole)
    if delete_original:
        delete_object(obj)
    return a, b


def overlap_volume(a, b):
    """Volume (mm3) shared by two objects (Boolean intersection on temporary copies)."""
    mn1, mx1 = group_bbox([a])
    mn2, mx2 = group_bbox([b])
    if any(mx1[k] < mn2[k] or mx2[k] < mn1[k] for k in range(3)):
        return 0.0
    ca = duplicate_object(a, "_ov_a")
    cb = duplicate_object(b, "_ov_b")
    boolean_intersect_apply(ca, cb)
    bm = _world_bmesh(ca)
    vol = abs(bm.calc_volume()) if bm.faces else 0.0
    bm.free()
    delete_object(ca)
    return vol


def overlap_at_offsets(fixed, moving, offsets, ndigits=3):
    """Overlap (mm3) of `fixed` with a copy of `moving` shifted by each (dx, dy, dz) in offsets --
    lift tests (latches, drop-in hinges) or a dummy part pushed to its extreme positions.
    Neither object is changed. Returns {offset tuple: mm3}."""
    out = {}
    for off in offsets:
        probe = duplicate_object(moving, "_probe_offset")
        translate_objects([probe], off)
        out[tuple(off)] = round(overlap_volume(fixed, probe), ndigits)
        delete_object(probe)
    return out


def overlap_at_rotations(fixed, moving, axis, angles, pivot, ndigits=3):
    """Overlap (mm3) of `fixed` with a copy of `moving` rotated by each angle (degrees) about the
    world axis ('X'|'Y'|'Z') through `pivot` -- hinge swing test (0 everywhere = free swing).
    Neither object is changed. Returns {angle: mm3}."""
    out = {}
    for ang in angles:
        probe = duplicate_object(moving, "_probe_rotation")
        rotate_objects([probe], axis, ang, pivot=pivot)
        out[ang] = round(overlap_volume(fixed, probe), ndigits)
        delete_object(probe)
    return out


def find_overlaps(objs, min_mm3=0.01, ignore=None):
    """All pairs of objects that interpenetrate by more than min_mm3. ignore(a, b) -> True skips a
    pair that is meant to overlap (e.g. a boss fused into a floor). Returns [(name_a, name_b, mm3)]."""
    objs = [o for o in objs if o.type == 'MESH']
    out = []
    for i, a in enumerate(objs):
        for b in objs[i + 1:]:
            if ignore and ignore(a, b):
                continue
            v = overlap_volume(a, b)
            if v > min_mm3:
                out.append((a.name, b.name, round(v, 3)))
    for n1, n2, v in out:
        print(f"[OVERLAP] {n1} x {n2}: {v} mm3")
    return out


def orient_flat_face_down(objs, ref=None):
    """Rotate a group so the largest flat face of `ref` (default objs[0]) lies on the bed (Z=0).
    Returns dict(normal, face_area_mm2, overhang). Check the overhang area and try other
    orientations by hand if it is large."""
    ref = ref or objs[0]
    _, _, normals, areas = _world_tris(ref)
    groups = {}
    for n, a in zip(normals, areas):
        key = tuple(round(c, 3) for c in n)
        groups[key] = groups.get(key, 0.0) + a
    normal, area = max(groups.items(), key=lambda kv: kv[1])
    rot = Vector(normal).rotation_difference(Vector((0, 0, -1))).to_matrix().to_4x4()
    pivot = group_bbox_center(objs)
    xf = Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot)
    for o in objs:
        o.matrix_world = xf @ o.matrix_world
    bpy.context.view_layer.update()
    drop_to_bed(objs)
    return {"normal": normal, "face_area_mm2": round(area, 1), "overhang": overhang_report(ref)}
