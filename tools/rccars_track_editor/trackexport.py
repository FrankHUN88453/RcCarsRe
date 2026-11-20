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
from . import levelwrite as lw

TEMPLATE = ('RCCarsDB\\urban_1.sb', 'urban_1')
GAME_LEVELS = {'beach_1', 'beach_2', 'beach_3', 'beach_4', 'country_1', 'country_2', 'country_3', 'country_4',
               'urban_1', 'urban_2'}
NAME_RE = re.compile(r'^[a-z0-9_]{1,24}$')
ACP_RE = re.compile(r'(^|_)ACP\d+', re.I)
SKY_EXT = ('.hdr', '.exr', '.png', '.dds')
# the surfaces a material can be (Material.rc_surface): the GLTX surface bits (gmdb.c gltxSurfaceBits) - the car's
# rolling / landing sounds by them, and dune sand's grip; with none (0) the car's sounds take it for being in the air
SURFACES = [('AUTO', 'Auto', 'The surface of an imported game texture; asphalt for anything else', -1),
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
    base = bpy.data.images.get(mat.get('rc_base', ''))   # (an imported level's lit material: its base, not its light map)
    if base is not None:
        return base, bool(base.get('rc_alpha'))
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
            key = ('img', img.name)
            if key in self.alpha:
                return self.index[self.alpha[key][0]], self.alpha[key][1]
            game = img.name[3:] if img.name.startswith('rc_') else None
            if game and self.fs is not None and self.fs.texture(game)[0] is not None and \
                    not self.fs.source_of('Textures\\' + game + '.png'):
                name = game                          # (the game's own texture: referenced, not copied)
                see = bool(img.get('rc_alpha')) or alpha
            else:
                name = self._unique('%s_%s' % (self.level, os.path.splitext(img.name)[0]))
                self.files[name] = ('image', img)
                see = alpha or bool(img.get('rc_alpha'))
                if not see and img.channels == 4 and img.size[0] * img.size[1] <= 4096 * 4096:
                    px = np.empty(img.size[0] * img.size[1] * 4, np.float32)
                    img.pixels.foreach_get(px)
                    see = bool((px[3::4] < 0.5).mean() > 0.005)
            self.alpha[key] = (name, see)
            self.surf.setdefault(name, surface_bits(mat, img))
            return self._add(name), see
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
            g = groups.get((gid, see, collide, water, coll_only))
            if g is None:
                g = groups[(gid, see, collide, water, coll_only)] = lw.Mesh(water, see and not water and not coll_only,
                                                                            collide)
                g.coll_only = coll_only
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
                    corners.append(((-p[0], p[2], p[1]), (uv[L][0], 1.0 - uv[L][1]), (-n[0], n[2], n[1]), c))
                out.append(corners)
            g.add(out, gid)
        return nt
    finally:
        ev.to_mesh_clear()


def checkpoints(context):
    cps = sorted((ob.rc_track.checkpoint, ob.name, ob) for ob in context.scene.objects if ob.rc_track.checkpoint)
    return [c[2] for c in cps]


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
    for ob in track_objects(context):
        tris += object_meshes(context, ob, tex, groups)
    meshes = list(groups.values())
    if not meshes:
        raise ValueError('no visible mesh objects')
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
        corners = [(to_game(p), (u, 1.0 - v), (0.0, 1.0, 0.0), 0xffffffff) for p, (u, v) in zip(pts, uvs)]
        mk = lw.Mesh('NOSHDW_LM0_NC_TRANSPB_ACP%d' % (i + 1), blended=True, collide=False)
        mk.add([(corners[0], corners[1], corners[2]), (corners[0], corners[2], corners[3])], gid)
        meshes.append(mk)
    fwd = start.matrix_world.to_3x3() @ Vector((0, 0, 1))     # (the arrow: the empty's local Z)
    g = to_game(fwd)
    yaw = math.degrees(math.atan2(g[0], g[2]))
    sp = to_game(start.matrix_world.translation)
    place = (sp[0], sp[1] + 0.4, sp[2])
    cp = [to_game(o.matrix_world.translation) for o in cps]
    data, info = lw.build_level(fs.read(TEMPLATE[0]), TEMPLATE[1], level, meshes, list(zip(tex.names, tex.surfaces())),
                                [(p[0], p[1] + 0.3, p[2]) for p in cp], place, yaw)
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
    ai = report('npc', level)                     # (the opponents: the NPC tool's export; its AI layout's name)

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
