"""A level database (.sb) of our own geometry, written into a copy of one of the game's levels (no bpy here).

The game's level (RCCarsDB\\urban_1.sb of the user's install) is the template: MODL <level> { GLTX x n (the textures, ids 0 .. n - 1), MESH <level>
(the root; its child meshes are the containers our meshes go into, with new ids 1 ..), COLL (the collision grid,
built again), FOLD "AI Characters" (left out), INST Player (our start), FOLD ground_noise (left out), FOLD
Checkpoints { MARK cp_1 .. } (ours), FOLD stones (emptied), HHID (left out) }.

Coordinates here are the game's: x, y (up), z; a face's corners (position, uv, normal[, colour 0xAARRGGBB]).
COLL: 0x3498 the voxel counts nx, ny, nz; 0x7099 / 0x709a the box; 0x309e the entry count; 0x809d u16 entries per
voxel, voxel = (ny * x + y) * nz + z; 0x809c the entries' mesh ids; 0x349f the entries' face counts; 0x1500 a bit
per face of that mesh (bit f of byte f >> 3): the faces that reach the voxel.
"""
import math
import struct

import numpy as np

from . import chunks as cc

CELL = (0.5, 0.9, 0.5)              # the collision voxels' size, metres (the game's levels: 0.5 .. 0.67 across, 0.92 high)
CELL_BUDGET = 24_000_000            # voxels at most (larger tracks get wider cells)
MAX_CHECKPOINTS = 256               # (RcCarsRe's race logic: "Too many checkpoints" above it; the original game: 8)
FLAG_BLEND = 0x1000
FLAG_COLLISION = 0x800              # (a collision-only mesh: never drawn)


class Raw:
    """a replacement chunk: tag, payload bytes, extra (4 bytes or None)"""

    def __init__(self, tag, payload, extra=None):
        self.tag, self.payload, self.extra = tag, payload, extra


def write(items, out, base=0):
    """Raw items and parsed chunks appended to out with their absolute end offsets"""
    for c in items:
        pos = len(out)
        out += struct.pack('<HI', c.tag, 0)
        if c.extra is not None:
            out += c.extra
        if isinstance(c, Raw):
            out += c.payload
        elif c.children is None:
            out += c.raw
        else:
            if c.prefix is not None:
                out += struct.pack('<H' if c.kind == cc.WORD else '<I', c.prefix)
            write(c.children, out, base)
        struct.pack_into('<I', out, pos + 2, base + len(out))
    return out


class Mesh:
    """a level mesh: welded positions (with their colour), texture coordinates and triangles"""

    def __init__(self, name=None, blended=False, collide=True):
        self.v, self.vi, self.t, self.ti, self.f, self.c = [], {}, [], {}, [], []
        self.name, self.blended, self.collide = name, blended, collide
        self.coll_only = False          # (drawn never: the database's flag 0x800, an invisible wall / floor)
        self.id = 0

    def add(self, tris, gltx, more=()):
        """tris: [(corner, corner, corner)], corner = (position, uv, normal[, colour[, (uv of each more layer)]]);
        gltx: the BAS1 texture's id; more: the face's further layers [(channel, texture id)] - ALP1 the mask and BAS2
        the second texture of a blended ground (the game: BAS1 x mask + BAS2 x (1 - mask)), LM_1 a light map"""
        for tri in tris:
            ids, uvs, nrs = [], [], []
            mores = [[] for _ in more]
            for corner in tri:
                p, uv, n = corner[:3]
                col = corner[3] if len(corner) > 3 else None
                key = (round(float(p[0]), 5), round(float(p[1]), 5), round(float(p[2]), 5))
                if col is not None:
                    key += (col,)
                k = self.vi.get(key)
                if k is None:
                    k = self.vi[key] = len(self.v)
                    self.v.append(key[:3])
                    self.c.append(col)
                ids.append(k)
                tk = (round(float(uv[0]), 5), round(float(uv[1]), 5))
                k = self.ti.get(tk)
                if k is None:
                    k = self.ti[tk] = len(self.t)
                    self.t.append(tk)
                uvs.append(k)
                for j in range(len(more)):
                    xk = (round(float(corner[4][j][0]), 5), round(float(corner[4][j][1]), 5))
                    k = self.ti.get(xk)
                    if k is None:
                        k = self.ti[xk] = len(self.t)
                        self.t.append(xk)
                    mores[j].append(k)
                ln = math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
                nrs.append((n[0] / ln, n[1] / ln, n[2] / ln) if ln > 1e-9 else (0.0, 1.0, 0.0))
            if len(set(ids)) < 3:
                continue
            a, b, c = (np.array(self.v[i]) for i in ids)
            fn = np.cross(b - a, c - a)
            ln = float(np.linalg.norm(fn))
            if ln < 1e-12:
                continue
            fn /= ln
            if float(np.dot(fn, np.sum(np.array(nrs), axis=0))) < 0:     # the game's winding: cross(b - a, c - a) out
                ids = [ids[0], ids[2], ids[1]]
                uvs = [uvs[0], uvs[2], uvs[1]]
                nrs = [nrs[0], nrs[2], nrs[1]]
                mores = [[u[0], u[2], u[1]] for u in mores]
                fn = -fn
            self.f.append((ids, nrs, tuple(float(x) for x in fn), gltx, uvs,
                           tuple((ch, g, tuple(u)) for (ch, g), u in zip(more, mores))))


def subset(me, faces):
    """a new mesh of some of the mesh's faces (their vertices and coordinates renumbered)"""
    out = Mesh(me.name, me.blended, me.collide)
    out.coll_only = me.coll_only
    vmap, tmap = {}, {}
    for fi in faces:
        ids, nrs, fn, g, uvs, more = me.f[fi]
        ni = []
        for i in ids:
            if i not in vmap:
                vmap[i] = len(out.v)
                out.v.append(me.v[i])
                out.c.append(me.c[i])
            ni.append(vmap[i])
        def remap(ts):
            r = []
            for t in ts:
                if t not in tmap:
                    tmap[t] = len(out.t)
                    out.t.append(me.t[t])
                r.append(tmap[t])
            return r
        nu = remap(uvs)
        out.f.append((ni, nrs, fn, g, nu, tuple((ch, mg, tuple(remap(u))) for ch, mg, u in more)))
    return out


def tiles(me, size, most_faces=60000):
    """the mesh cut into square tiles of the ground plan (by the faces' middles): the collision grid stores a bit
    per face of a mesh in every voxel the mesh reaches, so a large collidable mesh would make it huge"""
    V = np.asarray(me.v, dtype=float)
    groups = {}
    for fi, f in enumerate(me.f):
        c = V[f[0]].mean(0)
        groups.setdefault((int(math.floor(c[0] / size)), int(math.floor(c[2] / size))), []).append(fi)
    out = []
    for key in sorted(groups):
        fl = groups[key]
        for k in range(0, len(fl), most_faces):
            out.append(subset(me, fl[k:k + most_faces]))
    return out


MESH_BUDGET = 1200                  # meshes at most (the game's levels have 250 .. 700; each is a draw call)


def fit(meshes, room):
    """the collidable meshes cut into tiles as small as MESH_BUDGET allows (8 m and up): the collision grid keeps
    a bit per face of a mesh in every voxel it reaches, so big meshes in fine voxels make it large (meshes beyond
    the template's room become copies of a container, build_level)"""
    room = max(room, MESH_BUDGET)
    solid = [m for m in meshes if m.collide and m.f]
    other = [m for m in meshes if not (m.collide and m.f) and m.f]
    size = 8.0
    while True:
        cut = [t for m in solid for t in tiles(m, size)]
        if len(cut) + len(other) <= room or size > 4096:
            return cut + other, size
        size *= 2


def layer_chunk(gltx, channel, uvidx):
    """a face's texture layer: its texture id, channel (BAS1, ALP1, BAS2, LM_1: a dword, big-endian letters) and the
    corners' indices into the mesh's coordinates"""
    return Raw(0x023b, bytes(write([
        Raw(0x303c, struct.pack('<I', gltx)), Raw(0x303d, channel.encode('ascii')[::-1]),
        Raw(0x303e, struct.pack('<I', 0)),
        Raw(0x343f, struct.pack('<3I', *uvidx), struct.pack('<I', 3))], bytearray())))


def face_chunk(idx, normals, fnorm, gltx, uvidx, more=()):
    layers = [layer_chunk(gltx, 'BAS1', uvidx)] + [layer_chunk(g, ch, u) for ch, g, u in more]
    return ('face', [
        Raw(0x3419, struct.pack('<3I', *idx), struct.pack('<I', 3)),
        Raw(0x741a, struct.pack('<9f', *[c for n in normals for c in n]), struct.pack('<I', 3)),
        Raw(0x3020, bytes.fromhex('b2b2b2ff')), Raw(0x3025, struct.pack('<I', 0)),
        Raw(0x7027, struct.pack('<3f', *fnorm)), Raw(0x3022, struct.pack('<I', 0)),
        ('layers', layers)])


def ser(items, out, base):
    for it in items:
        if isinstance(it, tuple) and it[0] == 'face':
            pos = len(out)
            out += struct.pack('<HI', 0x8218, 0) + struct.pack('<I', 3)
            ser(it[1], out, base)
            struct.pack_into('<I', out, pos + 2, base + len(out))
        elif isinstance(it, tuple) and it[0] == 'layers':
            pos = len(out)
            out += struct.pack('<HI', 0x063a, 0) + struct.pack('<I', len(it[1]))
            ser(it[1], out, base)
            struct.pack_into('<I', out, pos + 2, base + len(out))
        elif isinstance(it, Raw) and it.tag == 0x023b:
            # (its payload was built with base 0: the inner end offsets are written again here)
            pos = len(out)
            out += struct.pack('<HI', it.tag, 0)
            write(cc.parse(it.payload), out, base)
            struct.pack_into('<I', out, pos + 2, base + len(out))
        else:
            write([it], out, base)


def kids(c, cls=None):
    return [k for k in c.children or () if k.kind == cc.OBJ and (cls is None or k.cls == cls)]


def bounds_chunks(k, pts):
    w = np.asarray(pts, dtype=float)
    lo, hi = w.min(0), w.max(0)
    if k.id == 0x15:
        return Raw(k.tag, struct.pack('<10f', lo[1], hi[1], hi[0] + 0.005, hi[2] + 0.005, lo[0] - 0.005,
                                      hi[2] + 0.005, lo[0] - 0.005, lo[2] - 0.005, hi[0] + 0.005, lo[2] - 0.005),
                   k.extra)
    ctr = (lo + hi) / 2
    r = float(np.linalg.norm(w - ctr, axis=1).max())
    return Raw(k.tag, struct.pack('<4f', r, ctr[0], ctr[1], ctr[2]), k.extra)


def rebuild_mesh(c, p):
    """a mesh object's chunks with the new content (p: me, trs, below, newid, flags, name)"""
    out = []
    me, trs, below = p.get('me'), p.get('trs'), p.get('below')
    renamed = False
    for k in c.children:
        if k.kind == cc.OBJ:
            out.append(('obj', k))
            continue
        tid = k.id
        if tid == 0x03 and k.kind == cc.STR and p.get('name') and not renamed:
            out.append(Raw(k.tag, p['name'].encode('latin1') + b'\0', k.extra))
            renamed = True
        elif tid == 0x0b and trs and k.kind == cc.FLOAT:
            out.append(Raw(k.tag, struct.pack('<9f', *trs), k.extra))
        elif tid == 0x38 and trs and k.kind == cc.FLOAT:
            out.append(Raw(k.tag, struct.pack('<9f', *(trs[0:3] + trs[6:9] + trs[3:6])), k.extra))
        elif tid == 0x11 and k.kind == cc.FARR and 'me' in p:
            v = me.v if me else []
            out.append(Raw(k.tag, struct.pack('<%df' % (len(v) * 3), *[x for q in v for x in q]),
                           struct.pack('<I', len(v))))
            if me and v and all(x is not None for x in me.c):
                # (RcCarsRe's own chunk 0x34f0, not the original game's: a colour a vertex)
                out.append(Raw(0x34f0, struct.pack('<%dI' % len(v), *me.c), struct.pack('<I', len(v))))
        elif tid == 0x13 and k.kind == cc.FARR and 'me' in p:
            t = me.t if me else []
            out.append(Raw(k.tag, struct.pack('<%df' % (len(t) * 2), *[x for q in t for x in q]),
                           struct.pack('<I', len(t))))
        elif tid == 0x17 and k.kind == cc.LIST and 'me' in p:
            out.append(('faces', k.tag, [face_chunk(*f) for f in (me.f if me else [])]))
        elif tid in (0x15, 0x16) and k.kind == cc.BLOB and below is not None and len(below):
            out.append(bounds_chunks(k, below))
        elif k.tag == 0x7414 and below is not None and len(below):
            # the box (bmin, bmax: the game's R3DOBJ bbox, r3dobj.c): tested before the faces by the rays - the
            # respawn's ray down to the ground (carphys.c 0x508d50) - and by the culling; the template's own was
            # left here before, so the respawn found no ground and dropped the car from 2 m
            w = np.asarray(below, dtype=float)
            lo, hi = w.min(0), w.max(0)
            out.append(Raw(k.tag, struct.pack('<6f', *lo, *hi), k.extra))
        elif tid == 0x08 and k.kind == cc.DWORD and 'newid' in p:
            w = list(k.dwords())
            w[0] = p['newid']
            w[3] = (w[3] & ~(FLAG_BLEND | FLAG_COLLISION)) | p.get('flags', 0)
            out.append(Raw(k.tag, struct.pack('<%dI' % len(w), *w), k.extra))
        else:
            out.append(k)
    for k, pp in p.get('extra', ()):          # (more containers than the template has: copies of one)
        out.append(('objcopy', k, pp))
    return out


def keys_chunk(keys):
    """an object's key list (chunk 0x0604, the count in its extra): 0x0a05 entries {0x4806 key, 0x4807 value}, the
    end offsets from 0 (written again where it lands, emit_item)"""
    out = bytearray()
    for key, value in keys:
        p = len(out)
        out += struct.pack('<HI', 0x0a05, 0)
        for tag, text in ((0x4806, key), (0x4807, value)):
            q = len(out)
            out += struct.pack('<HI', tag, 0) + text.encode('latin1') + b'\0'
            struct.pack_into('<I', out, q + 2, len(out))
        struct.pack_into('<I', out, p + 2, len(out))
    return Raw(0x0604, bytes(out), struct.pack('<I', len(keys)))


def cp_mark(tm, name, pos, keys, subs=()):
    """a checkpoint MARK (a copy of the template's) at pos with its key list and its corridor's sub-marks
    <name>_1 .. inside it (the game: the corridors run from the mark through its sub-marks to the next checkpoint)"""
    ch = []
    for x in tm.children:
        if x.kind == cc.OBJ:
            continue
        if x.id == 0x03:
            ch.append(Raw(x.tag, name.encode('latin1') + b'\0', x.extra))
        elif x.id == 0x0b:
            ch.append(Raw(x.tag, struct.pack('<9f', pos[0], pos[1], pos[2], 1, 1, 1, 0, 0, 0), x.extra))
        elif (x.tag & 0xfff) == 0x604:
            continue
        else:
            ch.append(x)
    if keys:
        ch.append(keys_chunk(keys))
    for i, q in enumerate(subs):
        ch.append(cp_mark(tm, '%s_%d' % (name, i + 1), q, keys))
    return ('copy', tm, ch)


def copy_with(k, raws):
    """an object's own chunks (not its sub-objects) with some replaced: {field id: payload}"""
    ch = []
    for x in k.children:
        if x.kind == cc.OBJ:
            continue
        ch.append(Raw(x.tag, raws[x.id], x.extra) if x.id in raws else x)
    return ('copy', k, ch)


def emit(c, out, base, plan, override=None):
    p = override if override is not None else plan.get(id(c))
    if p is not None and p.get('skip'):
        return
    pos = len(out)
    out += struct.pack('<HI', c.tag, 0)
    if c.extra is not None:
        out += c.extra
    if p is not None and 'gltx' in p:
        # the template's first texture object, once a texture: (name, id)
        for vi, (vname, vindex, vsurf, vflags, vpic) in enumerate(p['gltx']):
            if vi:
                struct.pack_into('<I', out, pos + 2, base + len(out))
                pos = len(out)
                out += struct.pack('<HI', c.tag, 0)
                if c.extra is not None:
                    out += c.extra
            for k in c.children:
                if k.kind == cc.STR and k.id == 0x03:
                    write([Raw(k.tag, vname.encode('latin1') + b'\0', k.extra)], out, base)
                elif k.kind == cc.DWORD and k.id == 0x08:
                    w = list(k.dwords())
                    w[0] = vindex
                    if len(w) > 4:
                        w[4] = vsurf            # (the surface bits: gmdb.c gltxSurfaceBits)
                    if len(w) > 3:
                        w[3] = vflags           # (gmdb.c gltxTexBits: 4 / 8 clamp u / v, 0x1000 a light map ..)
                    write([Raw(k.tag, struct.pack('<%dI' % len(w), *w), k.extra)], out, base)
                elif k.kind == cc.OBJ:
                    continue                    # (a texture object's own sub-objects: none in the levels)
                elif vpic is not None and (k.tag & 0xff) in (0x34, 0x31, 0x32, 0x33):
                    continue                    # (an embedded picture: no file name, its own size)
                else:
                    write([k], out, base)
            if vpic is not None:                # (the picture in the database, as the levels' light maps)
                w_, h_ = struct.unpack_from('<II', vpic, 0x10)
                write([Raw(0x2431, struct.pack('<II', w_, h_)), Raw(0x8232, vpic)], out, base)
    elif p is not None and 'chunks' in p:
        write(p['chunks'], out, base)           # (every own chunk given anew: the collision grid)
    elif p is not None and 'children' in p:
        # an object whose sub-objects are given anew: its own chunks, then the given ones
        for k in c.children:
            if k.kind != cc.OBJ:
                write([Raw(k.tag, p['name'].encode('latin1') + b'\0', k.extra)] if p.get('name') and k.kind == cc.STR
                      and k.id == 0x03 else [k], out, base)
        for item in p['children']:
            emit_item(item, out, base, plan)
    elif p is not None:
        for k in rebuild_mesh(c, p):
            emit_item(k, out, base, plan)
    elif c.children is None:
        out += c.raw
    else:
        if c.prefix is not None:
            out += struct.pack('<H' if c.kind == cc.WORD else '<I', c.prefix)
        for k in c.children:
            emit(k, out, base, plan)
    struct.pack_into('<I', out, pos + 2, base + len(out))


def emit_item(k, out, base, plan):
    if isinstance(k, tuple) and k[0] == 'obj':
        emit(k[1], out, base, plan)
    elif isinstance(k, tuple) and k[0] == 'objcopy':
        emit(k[1], out, base, plan, k[2])
    elif isinstance(k, tuple) and k[0] == 'faces':
        p2 = len(out)
        out += struct.pack('<HI', k[1], 0) + struct.pack('<I', len(k[2]))
        ser(k[2], out, base)
        struct.pack_into('<I', out, p2 + 2, base + len(out))
    elif isinstance(k, tuple) and k[0] == 'copy':
        src, ch = k[1], k[2]
        p2 = len(out)
        out += struct.pack('<HI', src.tag, 0)
        if src.extra is not None:
            out += src.extra
        for it in ch:
            if isinstance(it, tuple):
                emit_item(it, out, base, plan)          # (a sub-object: a checkpoint's sub-marks)
            elif isinstance(it, Raw) and it.tag == 0x0604:
                p3 = len(out)                           # (a key list: its inner end offsets written again)
                out += struct.pack('<HI', it.tag, 0) + (it.extra or b'')
                write(cc.parse(it.payload), out, base)
                struct.pack_into('<I', out, p3 + 2, base + len(out))
            else:
                write([it], out, base)
        struct.pack_into('<I', out, p2 + 2, base + len(out))
    elif isinstance(k, Raw):
        write([k], out, base)
    else:
        emit(k, out, base, plan)


def sky_dome(radius, centre, gltx, rings=24, segments=48):
    """an inside-out sphere (the game's coordinates) with an equirectangular picture: u along the horizon as
    Blender's world maps it (Blender's -x at u 0.5... u = atan2(by, -bx) / 2 pi + 0.5), v 0 at the zenith"""
    me = Mesh(name='NOSHDW_LM0_NC_skydome', blended=False, collide=False)
    cx, cy, cz = centre
    grid = []
    for r in range(rings + 1):
        lat = math.pi / 2 - math.pi * r / rings            # +90 .. -90 degrees
        row = []
        for s in range(segments + 1):
            u = s / segments
            az = (u - 0.5) * 2 * math.pi                    # Blender: atan2(by, -bx) = az
            bx, by, bz = -math.cos(az) * math.cos(lat), math.sin(az) * math.cos(lat), math.sin(lat)
            gx, gy, gz = -bx, bz, by                         # Blender -> the game
            row.append(((cx + gx * radius, cy + gy * radius, cz + gz * radius), (u, r / rings),
                        (-gx, -gy, -gz), 0xffffffff))
        grid.append(row)
    tris = []
    for r in range(rings):
        for s in range(segments):
            a, b, c, d = grid[r][s], grid[r][s + 1], grid[r + 1][s], grid[r + 1][s + 1]
            if r > 0:
                tris.append((a, b, c))
            if r < rings - 1:
                tris.append((b, d, c))
    me.add(tris, gltx)
    return me


def collision_grid(meshes):
    """the COLL chunks' payloads for the collidable meshes (faces facing down are left out, as the PS2 levels':
    a car over the ground is behind them)"""
    cm = [m for m in meshes if m.collide and m.f]
    if not cm:
        raise ValueError('no collidable faces: the cars would fall through')
    pts = np.array([v for m in cm for v in m.v], dtype=float)
    lo, hi = pts.min(0) - 2.0, pts.max(0) + 2.0
    lo[1], hi[1] = pts[:, 1].min() - 1.0, pts[:, 1].max() + 4.0
    size = list(CELL)
    n = [max(1, int(math.ceil((hi[k] - lo[k]) / size[k]))) for k in range(3)]
    if n[0] * n[1] * n[2] > CELL_BUDGET:
        # (a very large track: the cells grow across, the height's stay - the grid's memory in the game is 6 bytes
        # a cell, so it stays within CELL_BUDGET)
        f = math.sqrt(n[0] * n[1] * n[2] / CELL_BUDGET)
        size[0], size[2] = size[0] * f, size[2] * f
        n = [max(1, int(math.ceil((hi[k] - lo[k]) / size[k]))) for k in range(3)]
    cell = [(hi[k] - lo[k]) / n[k] for k in range(3)]
    cells = {}
    for m in cm:
        V = np.asarray(m.v, dtype=float)
        nb = ((len(m.f) - 1) >> 3) + 1
        for fi, (ids, nrs, fn, g, uvs, _more) in enumerate(m.f):
            if fn[1] < -0.5:
                continue
            P = V[ids]
            a = [max(0, min(n[k] - 1, int((P[:, k].min() - 0.05 - lo[k]) / cell[k]))) for k in range(3)]
            b = [max(0, min(n[k] - 1, int((P[:, k].max() + 0.05 - lo[k]) / cell[k]))) for k in range(3)]
            for x in range(a[0], b[0] + 1):
                for y in range(a[1], b[1] + 1):
                    for z in range(a[2], b[2] + 1):
                        e = cells.setdefault((n[1] * x + y) * n[2] + z, {})
                        bits = e.get(m.id)
                        if bits is None:
                            bits = e[m.id] = (m, bytearray(nb))
                        bits[1][fi >> 3] |= 1 << (fi & 7)
    ncell = n[0] * n[1] * n[2]
    counts = np.zeros(ncell, dtype='<u2')
    obj, nfaces, bits = [], [], bytearray()
    for c in sorted(cells):
        ent = cells[c]
        counts[c] = len(ent)
        for mid in sorted(ent):
            m, b = ent[mid]
            obj.append(mid)
            nfaces.append(len(m.f))
            bits += b
    # the counts a byte each when none is above 255: the chunk 0x809b, which the game reads as well (mod.c 0x424e90:
    # MODB_COLL_STARTVOX as bytes) - half the size of 0x809d's 16-bit ones
    small = counts.max() <= 255 if ncell else True
    return {0x98: (struct.pack('<3I', *n), struct.pack('<I', 3)),
            0x99: (struct.pack('<3f', *lo), None),
            0x9a: (struct.pack('<3f', *hi), None),
            0x9e: (struct.pack('<I', len(obj)), None),
            0x9d: (counts.astype('<u1').tobytes() if small else counts.tobytes(), None, 0x809b if small else None),
            0x9c: (struct.pack('<%dH' % len(obj), *obj), None),
            0x9f: (struct.pack('<%dI' % len(nfaces), *nfaces), struct.pack('<I', len(nfaces))),
            0x00: (bytes(bits), struct.pack('<I', len(bits)))}, (n, cell)


def build_level(template, tmodel, newname, meshes, texnames, checkpoints, start, yaw, marks=(), corridors=None,
                cp_keys=(('width', '6'), ('height', '1.5'), ('expand', '3'))):
    """the new level's bytes. template: the game level's bytes; tmodel: its model's name (urban_1); meshes: Mesh
    objects (their faces' gltx index into texnames); checkpoints: [(x, y, z)] (cp_1 the start / finish line);
    start: the player's place (x, y, z), yaw in degrees; marks: [(name, (x, y, z), (rx, ry, rz) degrees)] - MARK
    objects the game's effects find by name anywhere in the model (WATER_FALL_<n>, water_splash_<n> ..), written
    after the checkpoints; corridors: per checkpoint the points of its corridor towards the next one (its sub-marks,
    at most 32 each), None: straight; cp_keys: the checkpoint marks' corridor sizes (width / height / expand:
    half sizes, metres; the game's levels: width 4 .. 10, expand 3)"""
    if not texnames:
        raise ValueError('no textures')
    if len(checkpoints) > MAX_CHECKPOINTS:
        raise ValueError('at most %d checkpoints' % MAX_CHECKPOINTS)
    tree = cc.parse(template)
    model = [c for c, _ in cc.iter_objs(tree, 'MODL') if c.name() == tmodel][0]
    root = kids(model, 'MESH')[0]
    plan = {}
    # ---- the textures: the template's texture 0 written once a name, the others left out
    gl = kids(model, 'GLTX')
    base = [k for k in gl if k.get(0x08, cc.DWORD).dwords()[0] == 0][0]
    texnames = [(tuple(t) + (0, 0, None))[:4] if isinstance(t, tuple) else (t, 0, 0, None) for t in texnames]
    plan[id(base)] = {'gltx': [(n, i, sb, fl, pic) for i, (n, sb, fl, pic) in enumerate(texnames)]}
    for k in gl:
        if k is not base:
            plan[id(k)] = {'skip': True}
    # ---- the containers: the template's ordinary child meshes with faces
    conts = []
    for k in kids(root, 'MESH'):
        f = k.get(0x17)
        w = k.get(0x08, cc.DWORD).dwords()
        if f is not None and (f.count or 0) > 0 and k.get(0x13) is not None and tuple(w[2:5]) == (0x4001, 0x100060, 0):
            conts.append(k)
    meshes, tile = fit([m for m in meshes if m.f], len(conts))
    ident = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    for k in kids(root):
        if k.cls != 'MESH':
            plan[id(k)] = {'skip': True}
    used = set()
    allv = []
    extra = []
    for num, me in enumerate(meshes):
        # (the scene's mesh table has a place for each MESH object of the model and a mesh is entered by its id:
        # 0 the root, 1 .. ours; when there are more of ours than containers, copies of the first one are added)
        me.id = num + 1
        mp = {'me': me, 'trs': ident, 'below': me.v, 'newid': me.id,
              'flags': (FLAG_BLEND if me.blended else 0) | (FLAG_COLLISION if me.coll_only else 0), 'name': me.name}
        allv.extend(me.v)
        if num < len(conts):
            k = conts[num]
            plan[id(k)] = mp
            used.add(id(k))
            for sub in kids(k):
                plan[id(sub)] = {'skip': True}
        else:
            extra.append((conts[0], mp))
    for k in kids(root, 'MESH'):
        if id(k) not in used:
            plan[id(k)] = {'skip': True}
    plan[id(root)] = {'trs': ident, 'below': allv, 'newid': 0, 'extra': extra}
    # ---- the collision grid
    coll = kids(model, 'COLL')[0]
    rep, (ngrid, cellsize) = collision_grid(meshes)
    plan[id(coll)] = {'chunks': [Raw((rep[k.id][2] if len(rep[k.id]) > 2 and rep[k.id][2] else k.tag), rep[k.id][0],
                                     rep[k.id][1]) if k.id in rep else k
                                 for k in coll.children if k.kind != cc.OBJ]}
    # ---- the rest: no people, sounds or visibility sets of the template; our start, checkpoints; no props
    for k in kids(model):
        if k.cls == 'HHID' or (k.cls == 'FOLD' and k.name() in ('AI Characters', 'ground_noise')):
            plan[id(k)] = {'skip': True}
        elif k.cls == 'FOLD' and k.name() == 'stones':
            plan[id(k)] = {'children': []}
        elif k.cls == 'FOLD' and k.name() == 'Checkpoints':
            tm = kids(k, 'MARK')[0]
            plan[id(k)] = {'children': [cp_mark(tm, 'cp_%d' % (i + 1), p, list(cp_keys),
                                                (corridors[i] if corridors and i < len(corridors) else ())[:32])
                                        for i, p in enumerate(checkpoints)] +
                                       [copy_with(tm, {0x03: name.encode('latin1') + b'\0',
                                                       0x0b: struct.pack('<9f', p[0], p[1], p[2], 1, 1, 1, *r)})
                                        for name, p, r in marks]}
        elif k.cls == 'INST' and k.name() == 'Player':
            plan[id(k)] = {'trs': list(start) + [1.0, 1.0, 1.0, 0.0, yaw, 0.0], 'below': None}
    plan[id(model)] = {'children': [], 'name': newname}
    plan[id(model)]['children'] = [k for k in model.children if k.kind == cc.OBJ]
    out = bytearray(b'CSRC' if template[:4] == b'CSRC' else b'')
    for c in tree:
        emit(c, out, 0, plan)
    back = cc.parse(bytes(out))
    if not back:
        raise ValueError('the written level does not parse')
    return bytes(out), {'meshes': len(meshes), 'faces': sum(len(m.f) for m in meshes),
                        'textures': len(texnames), 'grid': ngrid, 'cell': cellsize, 'room': len(conts), 'tile': tile,
                        'added': len(extra)}
