"""A .sb database's meshes as Blender objects: a whole level (a track), or one model (a prop, a car, a road car).

Mesh chunks: 0x7411 float3 vertices, 0x7413 float2 texture coordinates, 0x0617 the faces (0x8218: 0x3419 vertex
indices, 0x063a texture layers: 0x023b {0x303d channel FourCC BAS1 / BAS2 / ALP1 / LM_1, 0x303c texture index,
0x343f UV indices}), 0x540b the TRS (position, scale, rotation in degrees). local = S Rx Ry Rz T (row vectors),
world = local * parent's world. GLTX objects name the textures (0x3408 dword 0 = their index).
Mesh 0x3408 dword 3: 0x800 collision-only walls, 0x1000 alpha blended.
Blender (x, y, z) = game (-x, z, y)."""
import math
import os
import re

import bpy
import numpy as np

from . import chunks as cc
from . import csi

FLAG_COLLISION = 0x800
FLAG_BLEND = 0x1000
IDENT = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


def mul(a, b):
    return [sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4)) for r in range(4) for c in range(4)]


def rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    if axis == 'x':
        return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]
    if axis == 'y':
        return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]
    return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def local_matrix(trs):
    px, py, pz, sx, sy, sz, rx, ry, rz = trs[:9]
    m = [sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, 0, 0, 0, 1]
    for axis, deg in (('x', rx), ('y', ry), ('z', rz)):
        if abs(deg) >= 1e-6:
            m = mul(m, rot(axis, deg))
    return mul(m, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, px, py, pz, 1])


def world_matrix(chain):
    w = None
    for node in chain:
        trs = node.get(0x0b, cc.FLOAT)
        if trs is None:
            w = None
            continue
        loc = local_matrix(trs.floats())
        w = loc if w is None else mul(loc, w)
    return w or IDENT


def det3(m):
    return (m[0] * (m[5] * m[10] - m[6] * m[9]) - m[1] * (m[4] * m[10] - m[6] * m[8]) +
            m[2] * (m[4] * m[9] - m[5] * m[8]))


def mesh_flags(mesh):
    d = mesh.get(0x08, cc.DWORD)
    return d.dwords()[3] if d and len(d.dwords()) > 3 else 0


class Textures:
    """the database's GLTX objects -> Blender images (loaded once a name; cached for the session)"""

    def __init__(self, fs, tree, cache_dir, scope=None):
        self.fs, self.cache_dir, self.scope = fs, cache_dir, scope
        self.gltx = {}
        for g, _ in cc.iter_objs(tree, 'GLTX'):
            d = g.get(0x08, cc.DWORD)
            if d and g.name():
                self.gltx[d.dwords()[0]] = g
        self.missing = set()

    def name(self, index):
        g = self.gltx.get(index)
        return g.name() if g else None

    def embedded(self, index):
        g = self.gltx.get(index)
        blob = g.get(0x32) if g else None
        return blob is not None and bytes(blob.raw[:4]) == b'MISC'

    def key(self, index):
        """the texture's name for images and materials: an embedded one (the light maps: every level has its own
        lightmap___rds_00 ..) with the level's name in front"""
        name = self.name(index)
        if name and self.scope and self.embedded(index):
            return '%s_%s' % (self.scope, name)
        return name

    def image(self, index):
        name = self.name(index)
        if not name:
            return None
        key = 'rc_' + self.key(index)
        if key in bpy.data.images:
            return bpy.data.images[key]
        g = self.gltx[index]
        blob = g.get(0x32)
        kind, data = (None, None)
        if blob is not None and bytes(blob.raw[:4]) == b'MISC':
            kind, data = 'csi', bytes(blob.raw)
        if data is None:
            kind, data = self.fs.texture(name)
        img = None
        if kind == 'csi':
            r = csi.decode(data)
            if r:
                w, h, rgba = r
                img = bpy.data.images.new(key, w, h, alpha=True)
                img.pixels.foreach_set((rgba[::-1].astype(np.float32) / 255.0).ravel())
                img.pack()
                img['rc_alpha'] = bool((rgba[..., 3] < 250).any())
        elif kind in ('png', 'dds'):
            path = os.path.join(self.cache_dir, name.replace('\\', '_') + '.' + kind)
            with open(path, 'wb') as f:
                f.write(data)
            img = bpy.data.images.load(path)
            img.name = key
            img.pack()
            px = np.empty(len(img.pixels), np.float32)
            img.pixels.foreach_get(px)
            img['rc_alpha'] = bool((px[3::4] < 0.98).any()) if img.channels == 4 else False
        if img is None:
            self.missing.add(name)
        return img


def _multiply(nt, a, b, x):
    """a Mix node (RGBA, Multiply, factor 1) of the two colour outputs; its colour output"""
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.location = (x, 0)
    mix.inputs[0].default_value = 1.0
    nt.links.new(a, mix.inputs[6])
    nt.links.new(b, mix.inputs[7])
    return mix.outputs[2]


def lit_material(key, tex, blended, two_sided, lm_key, lm_img, vcol):
    """the game's look of a level face: the base texture x its light map (LM_1, the second UV layer) x the baked
    vertex colours (the PS2 levels' light), unlit - the game draws its levels so (stage 1 MODULATE, no lights)"""
    mname = 'rc_%s%s%s%s%s' % (key or 'white', '__' + lm_key if lm_key else '', '_vc' if vcol else '',
                               '_blend' if blended else '', '_2s' if two_sided else '')
    if mname in bpy.data.materials:
        return bpy.data.materials[mname]
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    mat.use_backface_culling = not two_sided
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (700, 0)
    em = nt.nodes.new('ShaderNodeEmission')
    em.location = (300, -80)
    em.inputs['Strength'].default_value = 1.0
    colour, alpha = None, None
    if tex is not None:
        node = nt.nodes.new('ShaderNodeTexImage')
        node.image = tex
        node.location = (-500, 250)
        uv = nt.nodes.new('ShaderNodeUVMap')
        uv.uv_map = 'BAS1'
        uv.location = (-750, 250)
        nt.links.new(uv.outputs['UV'], node.inputs['Vector'])
        colour = node.outputs['Color']
        if blended or tex.get('rc_alpha'):
            alpha = node.outputs['Alpha']
        mat['rc_base'] = tex.name               # (the track export's base image: not the light map)
    if lm_img is not None:
        lm = nt.nodes.new('ShaderNodeTexImage')
        lm.image = lm_img
        lm.location = (-500, -50)
        uv2 = nt.nodes.new('ShaderNodeUVMap')
        uv2.uv_map = 'LM_1'
        uv2.location = (-750, -50)
        nt.links.new(uv2.outputs['UV'], lm.inputs['Vector'])
        colour = _multiply(nt, colour, lm.outputs['Color'], -150) if colour is not None else lm.outputs['Color']
    if vcol:
        va = nt.nodes.new('ShaderNodeVertexColor')
        va.layer_name = 'Col'
        va.location = (-500, -300)
        colour = _multiply(nt, colour, va.outputs['Color'], 50) if colour is not None else va.outputs['Color']
    if colour is not None:
        nt.links.new(colour, em.inputs['Color'])
    else:
        em.inputs['Color'].default_value = (0.6, 0.6, 0.6, 1)
    shader = em.outputs['Emission']
    if alpha is not None:
        clear = nt.nodes.new('ShaderNodeBsdfTransparent')
        clear.location = (300, 120)
        mix = nt.nodes.new('ShaderNodeMixShader')
        mix.location = (500, 0)
        nt.links.new(alpha, mix.inputs['Fac'])
        nt.links.new(clear.outputs[0], mix.inputs[1])
        nt.links.new(shader, mix.inputs[2])
        shader = mix.outputs[0]
        if hasattr(mat, 'surface_render_method'):
            mat.surface_render_method = 'DITHERED'
        else:
            mat.blend_method = 'HASHED'
    nt.links.new(shader, out.inputs['Surface'])
    return mat


def material(key, tex, blended, two_sided=False):
    mname = 'rc_%s%s%s' % (key or 'untextured', '_blend' if blended else '', '_2s' if two_sided else '')
    if mname in bpy.data.materials:
        return bpy.data.materials[mname]
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    mat.use_backface_culling = not two_sided
    nt = mat.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    if bsdf is None:
        return mat
    bsdf.inputs['Roughness'].default_value = 0.9
    img = tex
    if img is not None:
        node = nt.nodes.new('ShaderNodeTexImage')
        node.image = img
        node.location = (-400, 200)
        uv = nt.nodes.new('ShaderNodeUVMap')
        uv.uv_map = 'BAS1'
        uv.location = (-650, 200)
        nt.links.new(uv.outputs['UV'], node.inputs['Vector'])
        nt.links.new(node.outputs['Color'], bsdf.inputs['Base Color'])
        if blended or img.get('rc_alpha'):
            nt.links.new(node.outputs['Alpha'], bsdf.inputs['Alpha'])
            if hasattr(mat, 'surface_render_method'):
                mat.surface_render_method = 'DITHERED'
            else:
                mat.blend_method = 'HASHED'
    else:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1)
    return mat


def build_mesh(mesh, matrix, tex):
    """a Blender mesh of one MESH object (its faces with their BAS1 texture), or None"""
    verts = mesh.get(0x11, cc.FARR)
    flist = mesh.get(0x17, cc.LIST)
    if not verts or not flist or not flist.children:
        return None
    m = matrix
    reverse = det3(m) < 0
    co = [(-(x * m[0] + y * m[4] + z * m[8] + m[12]),
           x * m[2] + y * m[6] + z * m[10] + m[14],
           x * m[1] + y * m[5] + z * m[9] + m[13]) for x, y, z in (v[:3] for v in verts.vecs())]
    uvs = mesh.get(0x13, cc.FARR)
    uvl = uvs.vecs() if uvs else []
    blended = bool(mesh_flags(mesh) & FLAG_BLEND)
    # the baked light: a light map layer LM_1 on the faces (the PC levels; its texture is embedded in the level's
    # GLTX, its coordinates are in the same array as BAS1's), or a colour a vertex (chunk 0x34f0: RcCarsRe's own,
    # the PS2 levels' light)
    vc = mesh.get(0xf0)
    vcols = list(vc.dwords()) if vc is not None and vc.kind == cc.DWORD else None
    if vcols is not None and len(vcols) != len(co):
        vcols = None
    faces, face_uv, face_lm, mat_idx, slots = [], [], [], [], []
    seen = set()
    two_sided = False
    for f in flist.children:
        idx = f.get(0x19, cc.DWORD)
        if not idx:
            continue
        vi = list(idx.dwords())
        if len(vi) < 3 or len(set(vi)) != len(vi) or max(vi) >= len(co):
            continue
        # (a face on the same vertices again - in the PS2 levels every face is there twice, once each way round:
        #  Blender keeps only one of them, so the mesh is drawn from both sides instead)
        fk = frozenset(vi)
        if fk in seen:
            two_sided = True
            continue
        seen.add(fk)
        texi, ti, lmi, li = None, None, None, None
        layers = f.get(0x3a, cc.LIST)
        for layer in (layers.children if layers else ()):
            ch = layer.get(0x3d, cc.DWORD)
            cn = ch.dwords()[0].to_bytes(4, 'big') if ch else b''
            if cn in (b'BAS1', b'LM_1'):
                t = layer.get(0x3c, cc.DWORD)
                u = layer.get(0x3f, cc.DWORD)
                if t and u and len(u.dwords()) == len(vi) and max(u.dwords()) < len(uvl):
                    if cn == b'BAS1':
                        texi, ti = t.dwords()[0], list(u.dwords())
                    else:
                        lmi, li = t.dwords()[0], list(u.dwords())
        if reverse:
            vi.reverse()
            if ti:
                ti.reverse()
            if li:
                li.reverse()
        key = (tex.key(texi) if texi is not None else None, tex.key(lmi) if lmi is not None else None)
        if key not in slots:
            slots.append(key)
        faces.append(vi)
        face_uv.append(ti)
        face_lm.append(li)
        mat_idx.append(slots.index(key))
    if not faces:
        return None
    me = bpy.data.meshes.new(mesh.name() or 'mesh')
    me.from_pydata(co, [], faces)
    for lname, per_face in (('BAS1', face_uv), ('LM_1', face_lm)):
        if lname == 'LM_1' and not any(per_face):
            continue
        uv = me.uv_layers.new(name=lname)
        flat = []
        for f, ti in zip(faces, per_face):
            for k in range(len(f)):
                u, v = (uvl[ti[k]][0], uvl[ti[k]][1]) if ti else (0.0, 0.0)
                flat += (u, 1.0 - v)
        uv.data.foreach_set('uv', flat)
    me.uv_layers.active = me.uv_layers['BAS1']
    if vcols is not None:                       # (0xAARRGGBB, sRGB like the textures)
        ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'POINT')
        a = np.array(vcols, dtype=np.uint32)
        rgba = np.stack([(a >> 16) & 255, (a >> 8) & 255, a & 255, np.full_like(a, 255)], -1) / 255.0
        ca.data.foreach_set('color_srgb', rgba.astype(np.float32).ravel())
        me.color_attributes.active_color = ca
    index_of = {tex.key(i): i for i in tex.gltx}
    for key, lm_key in slots:
        img = tex.image(index_of[key]) if key in index_of else None
        if lm_key is None and vcols is None:
            me.materials.append(material(key, img, blended, two_sided))
        else:
            lm_img = tex.image(index_of[lm_key]) if lm_key in index_of else None
            me.materials.append(lit_material(key, img, blended, two_sided, lm_key, lm_img, vcols is not None))
    me.polygons.foreach_set('material_index', mat_idx)
    me.validate()
    me.update()
    return me


def untextured(me):
    """a mesh without any texture: a helper (the physics boxes of the models), not drawn by the game"""
    return all(m is None or m.name.startswith('rc_untextured') for m in me.materials)


LOD_RE = re.compile(r'LOD(\d+)', re.I)


def slider_value(text, key):
    """a slider file's value (Key "<key>" / Values min max value), or None"""
    m = re.search(r'Key\s+"%s"\s*\n\s*Values\s+(\S+)\s+(\S+)\s+(\S+)' % re.escape(key), text, re.I)
    return float(m.group(3)) if m else None


def water_settings(fs, level, record):
    """the water record's slider file as the game looks for it (WLOD_<level>_<record>, else WLOD_<level>, else
    WaterLOD; the text ones): (its path, its text) or (None, None)"""
    for name in ('WLOD_%s_%s' % (level, record), 'WLOD_%s' % level, 'WaterLOD'):
        p = 'Settings\\%s.ini' % name
        if fs.exists(p):
            try:
                return p, fs.read(p).decode('latin1')
            except Exception:
                pass
    return None, None


def import_level(fs, path, cache_dir, collection_name=None):
    """every mesh of a level database, in a collection of its own (collision walls hidden).
    The water (the game's 'WTRL': every top-level object of the environment with "more" in its name) is put where the
    game draws it: its slider file's offset (value x 0.01 - 0.5 m) added to its height - the object moved, its mesh
    kept, so the track export can take it back; of its levels of detail (LOD1 coarse .. LOD3 fine, overlapping) the
    finest is shown, the others go into a hidden collection"""
    tree = cc.parse(fs.read(path))
    level = os.path.splitext(os.path.basename(path))[0]
    name = collection_name or level
    tex = Textures(fs, tree, cache_dir, level)
    root = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(root)
    coll = bpy.data.collections.new(name + ' collision and helpers')
    root.children.link(coll)
    sky = bpy.data.collections.new(name + ' sky')        # (the sky dome, clouds, backdrop: they hide the track
    root.children.link(sky)                              #  when looked at from above)
    lods = bpy.data.collections.new(name + ' water, coarser levels')
    root.children.link(lods)
    count = 0
    water = {}                                          # record -> (offset, settings path)
    finest = {}                                         # a LOD group (the meshes' parent) -> its finest level
    for mesh, parents in cc.iter_objs(tree, 'MESH'):
        k = LOD_RE.search(mesh.name() or '')
        if k and parents:
            finest[id(parents[-1])] = max(finest.get(id(parents[-1]), 0), int(k.group(1)))
    for mesh, parents in cc.iter_objs(tree, 'MESH'):
        chain = [p for p in parents if p.cls == 'MESH'][1:] + [mesh]    # (without the level's root mesh)
        top = next((p for p in chain if 'more' in (p.name() or '').lower()), None)   # (the outermost "more")
        rec = top.name() if top is not None else None
        if rec and rec not in water:
            sp, text = water_settings(fs, level, rec)
            v = slider_value(text, 'offset') if text else None
            off = min(0.5, max(-0.5, v * 0.01 - 0.5)) if v is not None else 0.0
            water[rec] = (off, sp)
        me = build_mesh(mesh, world_matrix(list(parents) + [mesh]), tex)
        if me is None:
            continue
        ob = bpy.data.objects.new(me.name, me)
        mats = ' '.join(m.name.lower() for m in me.materials if m)
        if mesh_flags(mesh) & FLAG_COLLISION or untextured(me):
            target = coll
        elif any(k in mats for k in ('sky', 'cloud', 'backdrop', 'backgr')):
            target = sky
        else:
            target = root
        if rec:
            off, sp = water[rec]
            ob.location.z += off
            ob['rc_water'] = rec
            ob['rc_water_offset'] = off
            ob['rc_water_level'] = level
            if sp:
                ob['rc_water_settings'] = sp
            k = LOD_RE.search(mesh.name() or '')
            best = finest.get(id(parents[-1]), 0) if parents else 0
            if k and int(k.group(1)) != best and target is root:
                target = lods
        target.objects.link(ob)
        ob['rc_source'] = path
        count += 1
    for c in (coll, sky, lods):
        c.hide_viewport = True
        c.hide_render = True
    if not lods.objects:
        bpy.data.collections.remove(lods)
    root['rc_level'] = path
    return root, count, tex.missing


def import_model(fs, path, model, cache_dir, location=(0, 0, 0)):
    """one model (MODL) of a database: its meshes under an empty named after it, placed at location"""
    tree = cc.parse(fs.read(path))
    tex = Textures(fs, tree, cache_dir)
    target = None
    for m, parents in cc.iter_objs(tree, 'MODL'):
        if m.name() == model:
            target = (m, parents)
            break
    if target is None:
        raise KeyError('no model %s in %s' % (model, path))
    modl, mparents = target
    tex = Textures(fs, [modl], cache_dir)          # (the model's own textures: each model numbers its GLTX from 0)
    if not tex.gltx:
        tex = Textures(fs, tree, cache_dir)
    empty = bpy.data.objects.new(model, None)
    empty.empty_display_type = 'ARROWS'
    empty.empty_display_size = 0.3
    empty.location = location
    empty['rc_model'] = model
    empty['rc_source'] = path
    bpy.context.collection.objects.link(empty)
    count = 0
    for mesh, parents in cc.iter_objs([modl], 'MESH'):
        chain = list(parents) + [mesh]
        # (the model's own transforms only: from the model down)
        if chain and chain[0] is modl:
            chain = chain[1:]
        me = build_mesh(mesh, world_matrix(chain), tex)
        if me is None:
            continue
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.collection.objects.link(ob)
        ob.parent = empty
        if mesh_flags(mesh) & FLAG_COLLISION or untextured(me):     # (collision walls, the helpers' boxes)
            ob.hide_set(True)
            ob.hide_render = True
        count += 1
    return empty, count, tex.missing
