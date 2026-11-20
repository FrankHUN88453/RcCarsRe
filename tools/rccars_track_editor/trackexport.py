"""The Blender scene as a track of a mod: RCCarsDB\\<level>.sb (levelwrite.py), its textures, the sky, the Lua that
registers the track (scripts\\track_<level>.lua, which the game runs by itself: every *.lua of a mod's scripts\\
folder is an entry script) and, when the scene has opponents' paths, their profiles and AI layout (npc.py).

What goes in: every visible mesh object (modifiers applied) but the opponents' paths and the helpers. Per object:
Collision (default on; off: drawn only, the cars pass through). Per material: its image (the Image Texture node on the
Base Color, else the first one; none: a small picture of its colour); see-through when its alpha is used. A game
texture (an image named rc_<name> by the importer / the asset library) keeps its name and is not copied.
Checkpoints: empties with a checkpoint number (1 = the start / finish line, then in order around the lap, up to 256);
each gets the game's marker on the ground (a mesh ..._ACP<n>: the game lights the next one and stands its hologram
arrow over it).
The player's start: the NPC tool's "RC player start" arrow. The sky: a picture (.hdr, .exr, .png, .dds) on a dome
around the track. Blender (x, y, z) = game (-x, z, y)."""
import math
import os
import re
import shutil
import struct
import zlib

import bpy
import numpy as np
from mathutils import Vector

from . import cpfx
from . import csi
from . import levelwrite as lw

TEMPLATE = ('RCCarsDB\\urban_1.sb', 'urban_1')
GAME_LEVELS = {'beach_1', 'beach_2', 'beach_3', 'beach_4', 'country_1', 'country_2', 'country_3', 'country_4',
               'urban_1', 'urban_2'}
NAME_RE = re.compile(r'^[a-z0-9_]{1,24}$')
ACP_RE = re.compile(r'(^|_)ACP\d+', re.I)
SKY_EXT = ('.hdr', '.exr', '.png', '.dds')
# the surfaces a material can be (Material.rc_surface): the GLTX surface bits (gmdb.c gltxSurfaceBits) - the car's
# rolling / landing sounds by them, and dune sand's grip; with none (0) the car's sounds take it for being in the air
SURFACES = [('AUTO', 'Auto', 'The surface of an imported game texture; else guessed from the image name (sand, wood, '
                             'stone, metal, gravel ..), asphalt by default', -1),
            ('ASPHALT', 'Asphalt', '', 0x400), ('SAND', 'Sand', '', 0x20), ('WETSAND', 'Wet sand', '', 0x10),
            ('DUNE', 'Dune sand', 'Deep sand: less grip', 0x40), ('GRAVEL', 'Gravel', '', 0x200),
            ('WOOD', 'Wood', '', 0x80), ('STONE', 'Stone', '', 0x800), ('METAL', 'Metal', '', 0x1000),
            ('NONE', 'None', 'No surface (the sky, decals): on it the cars sound as if in the air', 0)]
SURFACE_BITS = {k: b for k, _, _, b in SURFACES}
DEFAULT_SURFACE = 0x400


def surface_bits(mat, img):
    choice = getattr(mat, 'rc_surface', 'AUTO') if mat is not None else 'AUTO'
    if choice != 'AUTO':
        return SURFACE_BITS[choice]
    if img is not None and img.get('rc_surface') is not None and int(img['rc_surface']):
        return int(img['rc_surface'])
    if img is not None:                 # (none known: guessed from the image's name, asphalt else)
        return surface_from_name(img.name) or DEFAULT_SURFACE
    return DEFAULT_SURFACE


# a texture's surface from its name (the PS2 levels' names, research\ps2\ps2surface.py; 0: none - sky, water, icons)
NAME_RULES = [
    (0, r'sky|cloud|backdrop|backgr|forest_back|icon_|^sea|_sea|water|stream|ryaska|star_'),
    (0x10, r'sand_wet|wet_'),
    (0x20, r'sand|seabed|samorodok'),
    (0x200, r'gravel|grnd|ground|grass|musor|cinder|dirt|moss|silt|hay|seno|bog|kochka|jngl|rubbish|underworld'),
    (0x80, r'wood|pile|beam|ford|lodka|plank|doski|skamya|skamia|polenia|kont_derev|veslo|bochk'),
    (0x1000, r'met|rust|iron|tin$|hangar|cistern|grate|girder|tower|conduit|vagon|trailer|treiler|btr80|t_64a|'
             r'refregerator|devisesbox|ventilator|pipe|culinder|gas'),
    (0x800, r'stone|stoun|rock|kamen|mont|cobble|brick|wall|colu|colo|stair|steps|border|plint|corni|arch|arc_|'
            r'battlement|lighthouse|plaster|baffle|vault|ceil|cascade|ruins|monument|grave|chimney|ridge'),
]


def surface_from_name(name):
    n = os.path.splitext(name.lower())[0]
    if n.startswith('rc_'):
        n = n[3:]
    for bits, pat in NAME_RULES:
        if re.search(pat, n):
            return bits
    return DEFAULT_SURFACE


def to_game(v):
    return (-v[0], v[2], v[1])


def png_bytes(rgba):
    """an h x w x 4 uint8 array (top row first) as a PNG file"""
    h, w = rgba.shape[:2]
    raw = b''.join(b'\0' + rgba[y].tobytes() for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def image_rgba(img):
    """the image's pixels as uint8, top row first (a float image's linear light to sRGB)"""
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1]
    if img.is_float:
        rgb = np.clip(px[..., :3], 0, None)
        px[..., :3] = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    return (np.clip(px, 0, 1) * 255 + 0.5).astype(np.uint8)


def material_image(mat):
    """(image, alpha used) of a material"""
    if mat is None or not mat.use_nodes or not mat.node_tree:
        return None, False
    nt = mat.node_tree
    img, alpha = None, False
    # (an imported level's material that was alpha blended - its overlays: grass, sand, litter on the ground)
    blended = bool(mat.get('rc_blend', mat.name.startswith('rc_') and '_blend' in mat.name))
    base = bpy.data.images.get(mat.get('rc_base', ''))   # (an imported level's lit material: its base, not its light map)
    if base is not None:
        return base, bool(base.get('rc_alpha')) or blended
    for node in nt.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            for name in ('Base Color', 'Alpha'):
                sock = node.inputs.get(name)
                if sock and sock.is_linked:
                    src = sock.links[0].from_node
                    if src.type == 'TEX_IMAGE' and src.image:
                        if name == 'Base Color':
                            img = img or src.image
                        else:
                            alpha = True
    alpha = alpha or blended
    if img is None:
        img = next((n.image for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image), None)
    return img, alpha


def material_colour(mat):
    if mat is None:
        return (0.6, 0.6, 0.6, 1.0)
    if mat.use_nodes and mat.node_tree:
        b = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b is not None:
            return tuple(b.inputs['Base Color'].default_value)
    return tuple(mat.diffuse_color)


class Textures:
    """the level's texture names (their order is the GLTX ids) and the files to write"""

    def __init__(self, fs, level):
        self.fs, self.level = fs, level
        self.names, self.index, self.files, self.alpha = [], {}, {}, {}
        self.surf = {}                          # texture name -> its surface bits
        self.flags = {}                         # texture name -> its GLTX flags (the import's: clamp, light map)

    def _add(self, name):
        if name not in self.index:
            self.index[name] = len(self.names)
            self.names.append(name)
        return self.index[name]

    def _unique(self, base):
        base = re.sub(r'[^A-Za-z0-9_]', '_', base)[:31]
        name, k = base, 1
        while name in self.files and self.files[name][0] != 'pending':
            k += 1
            name = '%s_%d' % (base[:28], k)
        return name

    def of_material(self, mat):
        """the texture id and whether it is see-through"""
        img, alpha = material_image(mat)
        if img is not None:
            return self.of_image(img, alpha, mat)
        return self._of_colour(mat)

    def of_image(self, img, alpha=False, mat=None):
        """an image's texture id and whether it is see-through"""
        key = ('img', img.name, alpha)      # (an image both opaque and blended: once each way)
        if key in self.alpha:
            return self.index[self.alpha[key][0]], self.alpha[key][1]
        other = self.alpha.get(('img', img.name, not alpha))
        game = img.name[3:] if img.name.startswith('rc_') else None
        see = alpha or bool(img.get('rc_alpha'))
        if other is not None:                    # (the same texture, used the other way too)
            name = other[0]
        elif game and self.fs is not None and self.fs.texture(game)[0] is not None and \
                not self.fs.source_of('Textures\\' + game + '.png'):
            name = game                          # (the game's own texture: referenced, not copied)
        else:
            name = self._unique('%s_%s' % (self.level, os.path.splitext(img.name)[0]))
            # (a light map goes into the level itself, as the game's: the game reads the shade under a car from
            #  that picture - rend.c rendObjLightmapAt)
            self.files[name] = ('embed' if int(img.get('rc_gltx_flags', 0)) & 0x1000 else 'image', img)
        if not see and name in self.files and self.files[name][0] == 'image' and img.channels == 4 and img.size[0] * img.size[1] <= 4096 * 4096:
            px = np.empty(img.size[0] * img.size[1] * 4, np.float32)
            img.pixels.foreach_get(px)
            see = bool((px[3::4] < 0.5).mean() > 0.005)
        self.alpha[key] = (name, see, alpha)
        self.surf.setdefault(name, surface_bits(mat, img))
        self.flags.setdefault(name, int(img.get('rc_gltx_flags', 0)))
        return self._add(name), see

    def _of_colour(self, mat):
        col = material_colour(mat)
        key = ('col', tuple(round(c, 3) for c in col))
        if key in self.alpha:
            return self.index[self.alpha[key][0]], self.alpha[key][1]
        name = self._unique('%s_col_%02x%02x%02x' % ((self.level,) + tuple(int(c * 255) for c in col[:3])))
        self.files[name] = ('colour', col)
        self.alpha[key] = (name, False)
        self.surf.setdefault(name, surface_bits(mat, None))
        return self._add(name), False

    def surfaces(self):
        return [self.surf.get(n, 0) for n in self.names]

    def gltx_flags(self):
        return [self.flags.get(n, 0) for n in self.names]

    def pictures(self):
        """the embedded pictures (CSI bytes) by the texture order, None for the others"""
        out = []
        for n in self.names:
            kind, src = self.files.get(n, (None, None))
            out.append(csi.encode_rgb(image_rgba(src)) if kind == 'embed' else None)
        return out

    def sky(self, path):
        name = 'sky_%s' % self.level
        self.files[name] = ('file', path)
        return self._add(name)

    def write(self, folder):
        os.makedirs(folder, exist_ok=True)
        for name, (kind, src) in self.files.items():
            if kind == 'image':
                img = src
                raw = img.packed_file.data if img.packed_file else None
                path = bpy.path.abspath(img.filepath) if img.filepath else ''
                if raw is not None and raw[:8] == b'\x89PNG\r\n\x1a\n':
                    data = raw
                elif not raw and path.lower().endswith('.png') and os.path.isfile(path):
                    data = open(path, 'rb').read()
                else:
                    data = png_bytes(image_rgba(img))
                with open(os.path.join(folder, name + '.png'), 'wb') as f:
                    f.write(data)
            elif kind == 'embed':
                continue                        # (in the level's database)
            elif kind == 'colour':
                c = np.zeros((4, 4, 4), np.uint8)
                c[...] = [int(max(0, min(1, v)) * 255) for v in src[:3]] + [255]
                with open(os.path.join(folder, name + '.png'), 'wb') as f:
                    f.write(png_bytes(c))
            else:
                shutil.copyfile(src, os.path.join(folder, name + os.path.splitext(src)[1].lower()))


def track_objects(context):
    out = []
    for ob in context.scene.objects:
        if ob.type != 'MESH':
            continue
        # (an imported track's collision-only meshes - invisible walls, floors, ramps - go back in, hidden or not)
        if not ob.get('rc_collision_only') and (not ob.visible_get() or ob.hide_render):
            continue
        if ob.rc_npc.is_path or ob.rc_npc.is_start or ob.rc_track.checkpoint or ob.get(cpfx.FX):
            continue
        if ACP_RE.search(ob.name):      # (an imported track's checkpoint marker: the checkpoints make their own)
            continue
        out.append(ob)
    return out


# the heights the game's levels have over the ground under them (cpheight.py on beach_1 / beach_2 / urban_1):
# checkpoints 0.06 .. 0.49, the start 0.36 .. 0.48. A checkpoint is passed with the car's origin within 1.6 m of it
# (racelogic.c 0x4eaa40) and the corridors between them hold the car within +- 1 m of their line (0x4ebcb0), so
# both go on the ground at these heights wherever the empty is.
CP_LIFT, START_LIFT = 0.3, 0.4
CORRIDOR_STEP = 6.0                     # (metres between a corridor's sub-marks; at most 32 a checkpoint)


class Ground:
    """the ground of the exported track: its collidable faces that face up (game coordinates) - what the game's
    collision has, the invisible floors included and the water left out (Blender's ray skips hidden objects)"""

    def __init__(self, meshes):
        tri = []
        for m in meshes:
            if not m.collide or not m.f:
                continue
            V = np.asarray(m.v, dtype=np.float64)
            for f in m.f:
                if f[2][1] > 0.3:
                    tri.append(V[f[0][:3]])
        self.t = np.array(tri) if tri else np.zeros((0, 3, 3))
        a, b, c = self.t[:, 0], self.t[:, 1], self.t[:, 2]
        self.den = (b[:, 2] - c[:, 2]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 2] - c[:, 2])
        self.ok = np.abs(self.den) > 1e-12
        self.den = np.where(self.ok, self.den, 1.0)
        self.lo, self.hi = self.t.min(1), self.t.max(1)

    def y(self, p, up=2.0, down=8.0):
        """the ground the game point p is on (up above .. down below it), or None"""
        x, y0, z = p
        sel = self.ok & (self.lo[:, 0] <= x) & (self.hi[:, 0] >= x) & (self.lo[:, 2] <= z) & (self.hi[:, 2] >= z)
        if not sel.any():
            return None
        t = self.t[sel]
        a, b, c, den = t[:, 0], t[:, 1], t[:, 2], self.den[sel]
        w0 = ((b[:, 2] - c[:, 2]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (z - c[:, 2])) / den
        w1 = ((c[:, 2] - a[:, 2]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (z - c[:, 2])) / den
        h = w0 * a[:, 1] + w1 * b[:, 1] + (1 - w0 - w1) * c[:, 1]
        h = h[(w0 >= -1e-6) & (w1 >= -1e-6) & (w0 + w1 <= 1 + 1e-6) & (h <= y0 + up) & (h >= y0 - down)]
        # (the surface the point is on: the highest one at most 0.5 above it - under a pier or a bridge the ground
        #  below, not the deck - else the nearest one above)
        below = h[h <= y0 + 0.5]
        if len(below):
            return float(below.max())
        return float(h.min()) if len(h) else None


def on_track(ground, bp, lift, up=2.0, down=8.0):
    """a Blender point put lift over the ground under it (game coordinates); where there is none, lift over itself"""
    g = to_game(bp)
    y = ground.y(g, up, down)
    return (g[0], (g[1] if y is None else y) + lift, g[2]), y is not None


def path_polyline(ob):
    """an AI path curve's points (Blender world) and whether it is closed"""
    mw = ob.matrix_world
    sp = ob.data.splines[0]
    pts = []
    if sp.type == 'BEZIER':
        from mathutils.geometry import interpolate_bezier
        bp = list(sp.bezier_points)
        pairs = list(zip(bp, bp[1:] + ([bp[0]] if sp.use_cyclic_u else [])))
        for a, b in pairs:
            pts += [mw @ q for q in interpolate_bezier(a.co, a.handle_right, b.handle_left, b.co, 12)[:-1]]
        if not sp.use_cyclic_u:
            pts.append(mw @ bp[-1].co)
    else:
        pts = [mw @ q.co.xyz for q in sp.points]
    return pts, sp.use_cyclic_u


def resample(pts, step):
    """points every `step` along a polyline, without its two ends"""
    out, carry = [], step
    for a, b in zip(pts, pts[1:]):
        seg = (b - a).length
        t = carry
        while t < seg - 1e-6:
            out.append(a.lerp(b, t / seg))
            t += step
        carry = t - seg
    if out and (pts[-1] - out[-1]).length < step * 0.4:
        out.pop()                           # (not right before the next checkpoint)
    return out


def corridors(context, ground, cps):
    """per checkpoint the sub-marks of its corridor to the next one (game coordinates, on the ground): along the
    first AI path when it passes both checkpoints (within 6 m), else the straight line - the game's own levels
    have such chains (beach_1: 2 .. 6 a checkpoint), so the car stays inside a corridor over hills and round bends"""
    path = next((o for o in context.scene.objects if o.rc_npc.is_path and o.type == 'CURVE' and o.data.splines),
                None)
    poly, closed = path_polyline(path) if path is not None else ([], False)
    locs = [o.matrix_world.translation.copy() for o in cps]
    near = []
    for c in locs:
        if not poly:
            near.append(None)
            continue
        k = min(range(len(poly)), key=lambda i: (poly[i] - c).length)
        near.append(k if (poly[k] - c).length <= 6.0 else None)
    out = []
    n = len(cps)
    for i in range(n):
        a, b = locs[i], locs[(i + 1) % n]
        ia, ib = near[i], near[(i + 1) % n]
        if ia is not None and ib is not None and ia != ib and (closed or ib > ia):
            seg = [a]
            k = ia
            while k != ib:
                k = (k + 1) % len(poly)
                seg.append(poly[k].copy())
            seg[-1] = b
        else:
            seg = [a, b]
        length = sum((q - p_).length for p_, q in zip(seg, seg[1:]))
        step = max(CORRIDOR_STEP, length / 33.0)
        out.append([on_track(ground, q, CP_LIFT)[0] for q in resample(seg, step)])
    return out


def on_ground(context, p, track, up=1.5, down=3.0, lift=0.03):
    """a checkpoint marker's corner laid on the track surface under it (the game's markers lie on the ground, tilted
    with it): the first face of an exported object within `up` above .. `down` below, `lift` over it; else as it was"""
    names = {ob.name for ob in track}
    dg = context.evaluated_depsgraph_get()
    origin, left = Vector((p[0], p[1], p[2] + up)), up + down
    for _ in range(16):
        hit, loc, _n, _i, ob, _m = context.scene.ray_cast(dg, origin, Vector((0, 0, -1)), distance=left)
        if not hit:
            break
        if ob is not None and ob.name in names:
            return (p[0], p[1], loc.z + lift)
        left -= origin.z - loc.z + 1e-3
        origin = Vector((loc.x, loc.y, loc.z - 1e-3))
        if left <= 0:
            break
    return (p[0], p[1], p[2])


# running water: the game's kinds by the object's name (water.c / lvlmath.c g_streamKind, the first the name holds):
# a stream and a waterfall's sheet (wtr_fall) run along their texture's v, a pool circles; at most 8 in a level
RUNNING = ('stream', 'wtr_fall', 'pool')
RUNNING_MAX = 8


def running_water(name):
    """the mesh name of an object that is running water by its name (the game's test is case-sensitive: the kind is
    put in front when the name has it in other letters), else None"""
    low = name.lower()
    kind = next((k for k in RUNNING if k in low), None)
    if kind is None:
        return None
    clean = re.sub(r'[^A-Za-z0-9_]', '_', name)
    return clean if kind in clean else '%s_%s' % (kind, clean)


def object_meshes(context, ob, tex, groups):
    """the object's triangles into groups[(texture id, see-through, collide)] (corners in the game's space)"""
    dg = context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        if not nt:
            return 0
        mw = ob.matrix_world
        nm = mw.to_3x3().inverted_safe().transposed()
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        M = np.array(mw)
        co = co @ M[:3, :3].T + M[:3, 3]
        tl = np.empty(nt * 3, np.int32)
        me.loop_triangles.foreach_get('loops', tl)
        tv = np.empty(nt * 3, np.int32)
        me.loop_triangles.foreach_get('vertices', tv)
        tm = np.empty(nt, np.int32)
        me.loop_triangles.foreach_get('material_index', tm)
        nl = len(me.loops)
        ln = np.empty(nl * 3, np.float32)
        try:
            me.corner_normals.foreach_get('vector', ln)
        except AttributeError:
            me.loops.foreach_get('normal', ln)
        ln = ln.reshape(-1, 3) @ np.array(nm).T
        uv = np.zeros((nl, 2), np.float32)
        if me.uv_layers.active:
            a = np.empty(nl * 2, np.float32)
            me.uv_layers.active.data.foreach_get('uv', a)
            uv = a.reshape(-1, 2)
        uvmaps = {}                     # (a blended ground's mask and second texture: their own UV maps)
        for lname in ('ALP1', 'BAS2', 'LM_1'):
            if lname in me.uv_layers:
                a = np.empty(nl * 2, np.float32)
                me.uv_layers[lname].data.foreach_get('uv', a)
                uvmaps[lname] = a.reshape(-1, 2)
        col = None
        ca = me.color_attributes.active_color if hasattr(me, 'color_attributes') else None
        if ca is not None:
            a = np.empty(len(ca.data) * 4, np.float32)
            ca.data.foreach_get('color_srgb', a)
            a = (np.clip(a.reshape(-1, 4), 0, 1) * 255 + 0.5).astype(np.uint32)
            packed = a[:, 3] << 24 | a[:, 0] << 16 | a[:, 1] << 8 | a[:, 2]
            col = packed if ca.domain == 'CORNER' else packed  # (POINT: by vertex below)
            point = ca.domain == 'POINT'
        slots = [ms.material for ms in ob.material_slots] or [None]
        collide = ob.rc_track.collide
        coll_only = bool(ob.get('rc_collision_only'))
        if coll_only:
            collide = True
        # the water: an imported track's (rc_water: its record, moved by the game's offset) or any object with "more"
        # in its name - a mesh of its own named after it (the game's water takes the top-level objects with "more"),
        # not collidable, at its rest height (the import's offset taken back: the game adds it again)
        water = ob.get('rc_water') or (re.sub(r'[^A-Za-z0-9_]', '_', ob.name) if 'more' in ob.name.lower() else None)
        run = running_water(ob.name) if not water else None
        if run:
            # (running water - the game finds it by the object's name, water.c streamScan: a mesh of its own named
            #  after it, one side only, faces welded: the game walks its outline and fades the sheet towards it)
            water = run
        if water:
            collide = False
            dz = float(ob.get('rc_water_offset', 0.0))
            if dz:
                co = co - np.array([0.0, 0.0, dz], dtype=np.float32)
        per_mat = {}
        for k in range(nt):
            per_mat.setdefault(int(tm[k]) if tm[k] < len(slots) else 0, []).append(k)
        for mi, tris in per_mat.items():
            gid, see = tex.of_material(slots[mi])
            # an imported two-sided material (the PS2 levels: every face there both ways round, one kept on import):
            # both sides written again; also an older import's (rc_ material, backface culling off)
            sm = slots[mi]
            two = sm is not None and (bool(sm.get('rc_two_sided')) or
                                      (sm.name.startswith('rc_') and not sm.use_backface_culling)) and not run
            # an imported blended ground (rc_alp1 / rc_bas2: the level's ALP1 mask and BAS2 texture, UV maps of
            # those names): its layers written again - the game mixes BAS1 x mask + BAS2 x (1 - mask)
            more = ()
            if sm is not None and all(k in uvmaps for k in ('ALP1', 'BAS2')):
                al, b2 = bpy.data.images.get(sm.get('rc_alp1', '')), bpy.data.images.get(sm.get('rc_bas2', ''))
                if al is not None and b2 is not None:
                    more = (('ALP1', tex.of_image(al)[0]), ('BAS2', tex.of_image(b2)[0]))
            # an imported light map (rc_lm: the level's baked light and shadows, the UV map LM_1): its layer again,
            # last as in the levels (the game multiplies it in)
            lmi = bpy.data.images.get(sm.get('rc_lm', '')) if sm is not None and 'LM_1' in uvmaps else None
            if lmi is not None:
                more = more + (('LM_1', tex.of_image(lmi)[0]),)
            gk = (gid, see, collide, water, coll_only, more)
            g = groups.get(gk)
            if g is None:
                g = groups[gk] = lw.Mesh(water, see and not water and not coll_only, collide)
                g.coll_only = coll_only
                g.more = more
            out = []
            for k in tris:
                corners = []
                for j in range(3):
                    L, V = tl[k * 3 + j], tv[k * 3 + j]
                    p = co[V]
                    n = ln[L]
                    c = 0xffffffff
                    if col is not None:
                        c = int(col[V] if point else col[L])
                    xs = tuple((uvmaps[ch][L][0], 1.0 - uvmaps[ch][L][1]) for ch, _ in more)
                    corners.append(((-p[0], p[2], p[1]), (uv[L][0], 1.0 - uv[L][1]), (-n[0], n[2], n[1]), c, xs))
                out.append(corners)
                if two:     # (the other side too: the collision grid takes only the faces that do not face down)
                    out.append([(q, t, (-nn[0], -nn[1], -nn[2]), cc_, x) for q, t, nn, cc_, x in reversed(corners)])
            g.add(out, gid, more)
        return nt
    finally:
        ev.to_mesh_clear()


def checkpoints(context):
    cps = sorted((ob.rc_track.checkpoint, ob.name, ob) for ob in context.scene.objects if ob.rc_track.checkpoint)
    return [c[2] for c in cps]


MARK_RE = re.compile(r'^(WATER_FALL|water_splash|water_wave|SUN_AF)(?:_\d+)?')
MARK_MAX = {'WATER_FALL': 100, 'water_splash': 16, 'water_wave': 100, 'SUN_AF': 1}


def scene_marks(context):
    """the scene's effect marks (an imported level's, rc_mark, or empties named WATER_FALL_<n>, water_splash_<n>,
    water_wave_<n>): [(name numbered again from 1 a kind, game position, (rx, ry, rz) degrees)], and a waterfall
    mark's slider file (the source level's WLOD_<level>_wtr_fall) or None"""
    found = {}
    settings = None
    for ob in context.scene.objects:
        if ob.type != 'EMPTY':
            continue
        m = MARK_RE.match(ob.name)
        kind = ob.get('rc_mark') or (m.group(1) if m else None)
        if kind not in MARK_MAX:
            continue
        rot = list(ob.get('rc_mark_rot', (0.0, 0.0, 0.0)))
        rot[1] = -math.degrees(ob.matrix_world.to_euler('XYZ').z)
        found.setdefault(kind, []).append((ob.name, to_game(ob.matrix_world.translation), tuple(rot)))
        settings = settings or ob.get('rc_mark_settings')
    out = []
    for kind, lst in sorted(found.items()):
        lst.sort(key=lambda e: (int(re.search(r'(\d*)$', e[0]).group(1) or 0), e[0]))   # (by their numbers)
        for i, (_n, p, r) in enumerate(lst[:MARK_MAX[kind]]):
            out.append((kind if kind == 'SUN_AF' else '%s_%d' % (kind, i + 1), p, r))
    return out, settings


def export(context, fs, mods_dir, mod, level, name, description, sky_path, sky_radius, report):
    """the track into <mods_dir>\\<mod>\\; the summary text"""
    if not NAME_RE.match(level) or level in GAME_LEVELS:
        raise ValueError('the level name must be 1 .. 24 small letters, digits or _ and not one of the game\'s')
    if not mod or re.search(r'[\\/:*?"<>|]', mod):
        raise ValueError('give the mod\'s folder name')
    cps = checkpoints(context)
    if len(cps) < 2:
        raise ValueError('put at least 2 checkpoints (Add checkpoint; 1 = the start / finish line)')
    if len(cps) > lw.MAX_CHECKPOINTS:
        raise ValueError('at most %d checkpoints' % lw.MAX_CHECKPOINTS)
    start = next((o for o in context.scene.objects if o.rc_npc.is_start), None)
    if start is None:
        raise ValueError('put the player\'s start (NPC paths > Player start)')
    root = os.path.join(mods_dir, mod)
    tex = Textures(fs, level)
    groups = {}
    tris = 0
    track = track_objects(context)
    for ob in track:
        tris += object_meshes(context, ob, tex, groups)
    meshes = list(groups.values())
    if not meshes:
        raise ValueError('no visible mesh objects')
    # running water: at most RUNNING_MAX meshes (with more the game's level load fails) - the rest drawn as ground
    runs = [m for m in meshes if m.name and any(k in m.name for k in RUNNING)]
    for m in runs[RUNNING_MAX:]:
        m.name = None
    marks, fall_settings = scene_marks(context)
    if any(n.startswith('WATER_FALL_') for n, _, _ in marks):
        for t in ('fog_base', 'fog_twist'):                # (the mist's textures: waterfall.c)
            if fs.texture(t)[0] is not None:
                tex._add(t)
    if sky_path:
        sky_path = bpy.path.abspath(sky_path)
        if not os.path.isfile(sky_path) or os.path.splitext(sky_path)[1].lower() not in SKY_EXT:
            raise ValueError('the sky must be a .hdr, .exr, .png or .dds file')
        allv = np.array([v for m in meshes for v in m.v], dtype=float)
        lo, hi = allv.min(0), allv.max(0)
        centre = ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)
        radius = max(sky_radius, float(np.linalg.norm(hi - lo)) * 0.75)
        meshes.append(lw.sky_dome(radius, centre, tex.sky(sky_path)))
    # the checkpoints' markers: the game's own textures, a quad each, named ..._ACP<n> (cpmark.c of RcCarsRe and the
    # original look for that name part)
    for i, o in enumerate(cps):
        tname = 'icon_start' if i == 0 else 'icon_chp_1'
        if fs.texture(tname)[0] is None:
            continue
        gid = tex._add(tname)
        pts, uvs = cpfx.marker_corners(o.matrix_world)
        # (laid on the ground; a corner off a ledge or on a step keeps it flat at the ground under the checkpoint)
        mid = on_ground(context, tuple(o.matrix_world.translation), track)
        laid = [on_ground(context, p, track) for p in pts]
        if all(abs(q[2] - mid[2]) <= 0.4 for q in laid):
            pts = laid
        else:
            pts = [(p[0], p[1], mid[2]) for p in pts]
        corners = [(to_game(p), (u, 1.0 - v), (0.0, 1.0, 0.0), 0xffffffff) for p, (u, v) in zip(pts, uvs)]
        mk = lw.Mesh('NOSHDW_LM0_NC_TRANSPB_ACP%d' % (i + 1), blended=True, collide=False)
        mk.add([(corners[0], corners[1], corners[2]), (corners[0], corners[2], corners[3])], gid)
        meshes.append(mk)
    fwd = start.matrix_world.to_3x3() @ Vector((0, 0, 1))     # (the arrow: the empty's local Z)
    g = to_game(fwd)
    yaw = math.degrees(math.atan2(g[0], g[2]))
    # the start and the checkpoints on the ground under their empties (see CP_LIFT); the corridors between them
    ground = Ground(meshes)
    place = on_track(ground, start.matrix_world.translation, START_LIFT)[0]
    cp = [on_track(ground, o.matrix_world.translation, CP_LIFT)[0] for o in cps]
    lanes = corridors(context, ground, cps)
    data, info = lw.build_level(fs.read(TEMPLATE[0]), TEMPLATE[1], level, meshes, list(zip(tex.names, tex.surfaces(), tex.gltx_flags(), tex.pictures())),
                                cp, place, yaw, marks, lanes)
    os.makedirs(os.path.join(root, 'RCCarsDB'), exist_ok=True)
    with open(os.path.join(root, 'RCCarsDB', level + '.sb'), 'wb') as f:
        f.write(data)
    tex.write(os.path.join(root, 'Textures'))
    # the water's settings (waves, offset): the source level's slider file under the new level's name
    wrote = set()
    for ob in track_objects(context):
        rec, src = ob.get('rc_water'), ob.get('rc_water_settings')
        if rec and src and rec not in wrote:
            try:
                data = fs.read(src)
            except Exception:
                continue
            os.makedirs(os.path.join(root, 'Settings'), exist_ok=True)
            with open(os.path.join(root, 'Settings', 'WLOD_%s_%s.ini' % (level, rec)), 'wb') as f:
                f.write(data)
            wrote.add(rec)
    if fall_settings and any(n.startswith('WATER_FALL_') for n, _, _ in marks):
        try:                                        # (the mist's sliders: the source level's under the new name)
            data = fs.read(fall_settings)
            os.makedirs(os.path.join(root, 'Settings'), exist_ok=True)
            with open(os.path.join(root, 'Settings', 'WLOD_%s_wtr_fall.ini' % level), 'wb') as f:
                f.write(data)
        except Exception:
            pass
    ai = report('npc', level, ground)             # (the opponents: the NPC tool's export, on the ground)

    def s(v):
        return '"' + v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    lua = ['-- The track "%s", made by the RC Cars Track Editor (Blender add-on): every *.lua of a mod\'s scripts' % name,
           '-- folder runs at the game\'s start, so this registers the track for the Quick race page.',
           'rc.registerTrack{id = %s, name = %s, description = %s, level = %s%s}' % (
               s(level), s(name or level), s((description or '').replace('\\n', '\n')), s(level),
               ', ai = %s' % s(ai) if ai else ''), '']
    os.makedirs(os.path.join(root, 'scripts'), exist_ok=True)
    with open(os.path.join(root, 'scripts', 'track_%s.lua' % level), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lua))
    return ('%s: %d triangles in %d meshes (%.0f m tiles), %d textures%s, %d checkpoints%s -> %s' % (
        level, info['faces'], info['meshes'], info['tile'], info['textures'], ', the sky' if sky_path else '',
        len(cp), ', opponents %s' % ai if ai else '', root))
