"""The "RC Cars" asset library for Blender's own Asset Browser: drag a model onto the track (it lands on the surface
under the mouse), drag a texture (a material) onto any object.

The library folder holds
    rc_models.blend     every model of the catalog (props, road cars, characters, cars; the extension's when it is
                        installed) as one object a model, its meshes joined, the origin at the model's origin; a
                        preview rendered from the front-left above
    rc_textures.blend   every texture as a material (the image on Base Color, its alpha when it has see-through
                        texels; no UV map named, so it uses any object's active UV map); the preview is the picture
    textures\\*.png     the game's .csi textures as PNG (the materials' images; the extension's PNGs are used where
                        they are, or copied out of a zipped mod)
    blender_assets.cats.txt   the catalogs: Models / <category>, Textures / Game, Textures / Extension / <group>
"""
import os
import re
import uuid

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import catalog, csi, sbimport
from .gamefs import TEX_DIRS, _norm

NS = uuid.UUID('6c1b5e0e-3d64-4a5e-9a42-7f0f6a1f2c11')
PREVIEW = 128
MODEL_CATS = {'PROPS': 'Models/Props', 'ROADCARS': 'Models/Road cars', 'CHARACTERS': 'Models/Characters',
              'CARS': 'Models/Cars', 'EXT_PROPS': 'Models/Extension props', 'EXT_CARS': 'Models/Extension cars'}


def cat_id(path):
    return str(uuid.uuid5(NS, path))


def write_catalogs(lib_dir, paths):
    lines = ['# RC Cars Track Editor: the asset catalogs', 'VERSION 1', '']
    done = set()
    for p in sorted(paths):
        parts = p.split('/')
        for k in range(1, len(parts) + 1):
            sub = '/'.join(parts[:k])
            if sub not in done:
                done.add(sub)
                lines.append('%s:%s:%s' % (cat_id(sub), sub, sub.replace('/', '-')))
    with open(os.path.join(lib_dir, 'blender_assets.cats.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def set_preview(idb, rgba):
    """an ID's preview from an RGBA uint8 picture (top row first)"""
    h, w = rgba.shape[:2]
    ys = (np.arange(PREVIEW) * h // PREVIEW)
    xs = (np.arange(PREVIEW) * w // PREVIEW)
    small = rgba[ys][:, xs].astype(np.float32) / 255.0
    pv = idb.preview_ensure()
    pv.image_size = (PREVIEW, PREVIEW)
    pv.image_pixels_float.foreach_set(small[::-1].ravel())


def texture_group(name, ext_src):
    if ext_src is None:
        return 'Textures/Game'
    m = re.match(r'(alaska|area51|carib|croco|cuba|mediter|siberia|texas|yellow|tut)_', name)
    if m:
        lv = {'tut': 'Fire Starter'}.get(m.group(1), m.group(1))
        return 'Textures/Extension/Tracks/' + lv
    if name.startswith('ps2'):
        return 'Textures/Extension/Cars'
    return 'Textures/Extension/Props'


def build_textures(fs, lib_dir, progress=None):
    """the materials (in the current file, fake users off) and the catalogs they use"""
    tex_dir = os.path.join(lib_dir, 'textures')
    os.makedirs(tex_dir, exist_ok=True)
    entries = {}                                   # name -> (file path, group)
    for d in reversed(TEX_DIRS):                   # (Textures.1, the best, wins)
        for rel, src in fs.listdir(d, '.csi'):
            name = os.path.splitext(os.path.basename(rel))[0]
            entries[name] = (('csi', src, rel), 'Textures/Game')
    ext = fs.mods.get('extension')
    if ext:
        for rel, src in fs.listdir('Textures', '.png', sources=[ext]):
            name = os.path.splitext(os.path.basename(rel))[0]
            entries[name] = (('png', src, rel), texture_group(name, src))
    mats, groups = [], set()
    for i, (name, ((kind, src, rel), group)) in enumerate(sorted(entries.items())):
        if progress and i % 50 == 0:
            progress('textures %d / %d' % (i, len(entries)))
        rgba = None
        if kind == 'csi':
            path = os.path.join(tex_dir, name + '.png')
            r = csi.decode(src.read(_norm(rel)))
            if not r:
                continue
            rgba = r[2]
            if not os.path.exists(path):
                img = bpy.data.images.new('tmp_' + name, r[0], r[1], alpha=True)
                img.pixels.foreach_set((rgba[::-1].astype(np.float32) / 255.0).ravel())
                img.filepath_raw = path
                img.file_format = 'PNG'
                img.save()
                bpy.data.images.remove(img)
        elif src.kind == 'dir':
            path = os.path.join(src.path, src.files[_norm(rel)])
        else:
            path = os.path.join(tex_dir, name + '.png')
            if not os.path.exists(path):
                with open(path, 'wb') as f:
                    f.write(src.read(_norm(rel)))
        img = bpy.data.images.load(path, check_existing=True)
        img.name = 'RC ' + name
        if rgba is None:
            px = np.empty(img.size[0] * img.size[1] * 4, np.float32)
            img.pixels.foreach_get(px)
            rgba = (px.reshape(img.size[1], img.size[0], 4)[::-1] * 255).astype(np.uint8)
        alpha = bool((rgba[..., 3] < 250).any())
        mat = bpy.data.materials.new('RC ' + name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get('Principled BSDF')
        node = nt.nodes.new('ShaderNodeTexImage')
        node.image = img
        node.location = (-400, 200)
        nt.links.new(node.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.9
        if alpha:
            nt.links.new(node.outputs['Alpha'], bsdf.inputs['Alpha'])
            if hasattr(mat, 'surface_render_method'):
                mat.surface_render_method = 'DITHERED'
        mat.asset_mark()
        mat.asset_data.catalog_id = cat_id(group)
        mat.asset_data.tags.new('RC Cars')
        mat.asset_data.description = '%s (%dx%d)' % (rel, img.size[0], img.size[1])
        set_preview(mat, rgba)
        mats.append(mat)
        groups.add(group)
    return mats, groups


def render_preview(ob):
    """a small workbench picture of one object, as RGBA uint8"""
    scene = bpy.data.scenes.new('rc_preview')
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.resolution_x = scene.render.resolution_y = PREVIEW * 2
    scene.render.film_transparent = True
    scene.collection.objects.link(ob)
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = [min(v[i] for v in bb) for i in range(3)]
    hi = [max(v[i] for v in bb) for i in range(3)]
    ctr = Vector([(a + b) / 2 for a, b in zip(lo, hi)])
    size = max(max(b - a for a, b in zip(lo, hi)), 0.05)
    cam_data = bpy.data.cameras.new('rc_preview_cam')
    cam_data.lens = 50
    cam = bpy.data.objects.new('rc_preview_cam', cam_data)
    scene.collection.objects.link(cam)
    d = Vector((-1.0, -1.3, 0.9)).normalized()
    cam.location = ctr + d * size * 2.6
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_data.clip_start = size * 0.01
    cam_data.clip_end = size * 20
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or os.path.dirname(__file__), 'rc_preview.png')
    scene.render.filepath = path
    win_scene = bpy.context.window.scene if bpy.context.window else None
    bpy.ops.render.render(write_still=True, scene=scene.name)
    img = bpy.data.images.load(path)
    px = np.empty(img.size[0] * img.size[1] * 4, np.float32)
    img.pixels.foreach_get(px)
    rgba = (px.reshape(img.size[1], img.size[0], 4)[::-1] * 255).astype(np.uint8)
    bpy.data.images.remove(img)
    scene.collection.objects.unlink(ob)
    bpy.data.objects.remove(cam)
    bpy.data.cameras.remove(cam_data)
    bpy.data.scenes.remove(scene)
    if win_scene is not None:
        bpy.context.window.scene = win_scene
    return rgba


def build_models(fs, assets, cache_dir, progress=None):
    """one joined object a model (not linked to any scene), marked as an asset"""
    obs, groups = [], set()
    holder = bpy.data.collections.new('rc_library_build')
    bpy.context.scene.collection.children.link(holder)
    layer_coll = bpy.context.view_layer.layer_collection.children[holder.name]
    prev_active = bpy.context.view_layer.active_layer_collection
    bpy.context.view_layer.active_layer_collection = layer_coll
    try:
        todo = [a for a in assets if a.model and a.category in MODEL_CATS]
        for i, a in enumerate(todo):
            if progress:
                progress('model %d / %d: %s' % (i + 1, len(todo), a.label))
            try:
                empty, n, _ = sbimport.import_model(fs, a.path, a.model, cache_dir)
            except Exception as ex:
                print('RC library: %s: %s' % (a.label, ex))
                continue
            kids = [o for o in empty.children if o.type == 'MESH' and not o.hide_render]
            if not kids:
                for o in list(empty.children):
                    bpy.data.objects.remove(o)
                bpy.data.objects.remove(empty)
                continue
            # (join the meshes into one object at the model's origin)
            for o in kids:
                o.matrix_world = empty.matrix_world @ o.matrix_parent_inverse @ o.matrix_basis
            first = kids[0]
            with bpy.context.temp_override(active_object=first, selected_editable_objects=kids,
                                           selected_objects=kids):
                bpy.ops.object.join()
            first.parent = None
            first.matrix_world = Matrix.Identity(4)
            for o in list(empty.children):
                if o is not first:
                    bpy.data.objects.remove(o)
            bpy.data.objects.remove(empty)
            first.name = 'RC ' + a.label
            first.data.name = 'RC ' + a.label
            holder.objects.unlink(first)
            group = MODEL_CATS[a.category]
            first.asset_mark()
            first.asset_data.catalog_id = cat_id(group)
            first.asset_data.tags.new('RC Cars')
            first.asset_data.description = '%s in %s' % (a.model, a.path)
            try:
                set_preview(first, render_preview(first))
            except Exception as ex:
                print('RC library: no preview for %s: %s' % (a.label, ex))
            obs.append(first)
            groups.add(group)
    finally:
        bpy.context.view_layer.active_layer_collection = prev_active
        bpy.data.collections.remove(holder)
    return obs, groups


def build(fs, assets, lib_dir, cache_dir, what=('models', 'textures'), progress=None):
    os.makedirs(lib_dir, exist_ok=True)
    groups = set()
    report = []
    if 'models' in what:
        obs, g = build_models(fs, assets, cache_dir, progress)
        groups |= g
        bpy.data.libraries.write(os.path.join(lib_dir, 'rc_models.blend'), set(obs), fake_user=True, compress=True)
        report.append('%d models' % len(obs))
        for o in obs:
            me = o.data
            bpy.data.objects.remove(o)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
    if 'textures' in what:
        mats, g = build_textures(fs, lib_dir, progress)
        groups |= g
        bpy.data.libraries.write(os.path.join(lib_dir, 'rc_textures.blend'), set(mats), fake_user=True,
                                 path_remap='ABSOLUTE', compress=True)
        report.append('%d textures' % len(mats))
        for m in mats:
            img = m.node_tree.nodes['Image Texture'].image if 'Image Texture' in m.node_tree.nodes else None
            bpy.data.materials.remove(m)
            if img and img.users == 0:
                bpy.data.images.remove(img)
    # the catalogs of both files (the file holds all, the earlier build's too)
    old = os.path.join(lib_dir, 'blender_assets.cats.txt')
    if os.path.exists(old):
        for line in open(old, encoding='utf-8'):
            parts = line.strip().split(':')
            if len(parts) == 3 and not line.startswith('#'):
                groups.add(parts[1])
    write_catalogs(lib_dir, groups)
    return ', '.join(report)


def register_library(lib_dir, name='RC Cars'):
    libs = bpy.context.preferences.filepaths.asset_libraries
    for lib in libs:
        if lib.name == name:
            lib.path = lib_dir
            return lib
    lib = libs.new(name=name, directory=lib_dir)
    for method in ('APPEND_REUSE', 'APPEND'):       # (the enum's names differ between Blender versions)
        try:
            lib.import_method = method
            break
        except TypeError:
            continue
    return lib
