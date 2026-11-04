"""
check_stl.py -- independent integrity check of exported binary STL files (plain Python, no Blender).

    python check_stl.py part1.stl part2.stl ...

For every file it reports the triangle count, the signed volume (should be positive and match the
model's volume), the number of unpaired/mismatched directed edges (0 = watertight, every edge is
shared by exactly two triangles with opposite direction) and the number of zero-area triangles
(harmless slivers, but many of them hint at coplanar/tangent Boolean contacts).
Exit status is 1 if any file has mismatched edges or a non-positive volume.

Why it exists: the Blender-side checks look at the mesh topology; this one looks at what the slicer
will actually receive.
"""

import collections
import math
import struct
import sys


def check(path):
    data = open(path, "rb").read()
    n = struct.unpack("<I", data[80:84])[0]
    if len(data) != 84 + 50 * n:
        return None, "not a binary STL (ASCII STL is not supported)"
    tris = []
    for i in range(n):
        v = struct.unpack("<12f", data[84 + i * 50: 84 + i * 50 + 48])[3:]
        tris.append((v[0:3], v[3:6], v[6:9]))
    edges = collections.Counter()
    for a, b, c in tris:
        for p, q in ((a, b), (b, c), (c, a)):
            edges[(p, q)] += 1
    mismatched = sum(1 for (p, q), cnt in edges.items() if cnt != 1 or edges.get((q, p), 0) != 1)
    volume = 0.0
    degenerate = 0
    for a, b, c in tris:
        volume += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        u = [b[k] - a[k] for k in range(3)]
        v = [c[k] - a[k] for k in range(3)]
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        if math.sqrt(sum(x * x for x in cr)) / 2 < 1e-6:
            degenerate += 1
    return dict(tris=n, mismatched_edges=mismatched, volume=volume, degenerate=degenerate), None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python check_stl.py file.stl [more.stl ...]")
    failed = False
    for p in sys.argv[1:]:
        r, err = check(p)
        if err:
            print(f"[FAIL] {p}: {err}")
            failed = True
            continue
        ok = r["mismatched_edges"] == 0 and r["volume"] > 0
        failed |= not ok
        print(f"[{'OK ' if ok else 'FAIL'}] {p}: tris={r['tris']} mismatched_edges={r['mismatched_edges']} "
              f"volume={r['volume']:.1f} mm3 zero_area_tris={r['degenerate']}")
    sys.exit(1 if failed else 0)
