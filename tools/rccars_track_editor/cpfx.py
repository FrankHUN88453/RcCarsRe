"""The checkpoints' in-game look in Blender: under each checkpoint empty its marker on the ground (icon_start for the
start / finish line, icon_chp_1 for the others, as the game's levels have them) and the hologram arrow that the game
stands over the next checkpoint (cp_ar_3 red at the start / finish line, cp_ar_2 green at the others; in the game a
quad turned to the camera, blinking - here two crossed quads whose glow pulses as the game's 0.8 s cycle).
The game's textures are read from the scanned game folder; without one the parts get plain colours.
The sizes are the game's (Settings anim_cp: Size 1.46 = the hologram's half size, Shift 1.28 = its height above the
marker; the levels' markers are about 3 x 3 m)."""
import math

import bpy
import numpy as np

from . import csi

MARK_SIZE = 3.0                     # m, the marker on the ground (the game's levels: 2.6 .. 3.8 m)
HOLO_HALF = 1.46                    # m, Settings anim_cp Size
HOLO_SHIFT = 1.28                   # m, Settings anim_cp Shift: the hologram's middle above the marker
FX = 'rc_fx'                        # (the custom property of the parts: the export leaves them out)


def game_image(fs, name):
    """the game's texture as a packed Blender image rc_<name> (None without the game folder)"""
    key = 'rc_' + name
    img = bpy.data.images.get(key)
    if img is not None:
        return img
    if fs is None:
        return None
    kind, data = fs.texture(name)
    if kind != 'csi':
        return None
    r = csi.decode(data)
    if not r:
        return None
    w, h, rgba = r
    img = bpy.data.images.new(key, w, h, alpha=True)
    img.pixels.foreach_set((rgba[::-1].astype(np.float32) / 255.0).ravel())
    img.pack()
    img['rc_alpha'] = True
    return img


def material(name, img, colour, glow):
    """a see-through material of the image (or the colour); glow: the hologram's pulsing emission"""
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (400, 0)
    mix = nt.nodes.new('ShaderNodeMixShader')
    mix.location = (200, 0)
    clear = nt.nodes.new('ShaderNodeBsdfTransparent')
    clear.location = (0, 120)
    em = nt.nodes.new('ShaderNodeEmission')
    em.location = (0, -60)
    nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    if img is not None:
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = img
        tex.location = (-300, 0)
        nt.links.new(tex.outputs['Color'], em.inputs['Color'])
        nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
    else:
        em.inputs['Color'].default_value = colour
        mix.inputs['Fac'].default_value = 0.6
    em.inputs['Strength'].default_value = 1.0
    if glow:
        # (the game's blink: the next checkpoint's alpha swings 50 .. 250 in 0.8 s = 20 frames at 25 fps)
        d = em.inputs['Strength'].driver_add('default_value').driver
        d.type = 'SCRIPTED'
        d.expression = '1.3 + 0.7 * sin(frame * 0.314)'
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'BLENDED'
    else:
        mat.blend_method = 'BLEND'
    mat.use_backface_culling = False
    if hasattr(mat, 'show_transparent_back'):
        mat.show_transparent_back = True
    mat.diffuse_color = colour
    return mat


def _quad(name, corners, uvs):
    me = bpy.data.meshes.new(name)
    me.from_pydata(corners, [], [list(range(len(corners)))] if len(corners) == 4 else
                   [[0, 1, 2, 3], [4, 5, 6, 7]])
    uv = me.uv_layers.new(name='UVMap')
    for li, loop in enumerate(me.loops):
        uv.data[li].uv = uvs[loop.vertex_index]
    me.update()
    return me


def clear_fx(ob):
    for ch in list(ob.children):
        if ch.get(FX):
            me = ch.data if ch.type == 'MESH' else None
            bpy.data.objects.remove(ch)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)


def make_fx(context, ob, fs):
    """the marker and the hologram under the checkpoint empty ob (made again)"""
    clear_fx(ob)
    first = ob.rc_track.checkpoint == 1
    mark_img = game_image(fs, 'icon_start' if first else 'icon_chp_1')
    holo_img = game_image(fs, 'cp_ar_3_f1' if first else 'cp_ar_2_f1')
    mark_mat = material('RC cp marker start' if first else 'RC cp marker', mark_img,
                        (0.9, 0.8, 0.1, 1.0) if first else (0.9, 0.9, 0.2, 1.0), False)
    holo_mat = material('RC cp hologram start' if first else 'RC cp hologram', holo_img,
                        (0.9, 0.1, 0.1, 1.0) if first else (0.2, 0.9, 0.1, 1.0), True)
    s = MARK_SIZE / 2
    mark = bpy.data.objects.new('%s marker' % ob.name, _quad(
        '%s marker' % ob.name, [(-s, -s, 0.03), (s, -s, 0.03), (s, s, 0.03), (-s, s, 0.03)],
        [(0, 0), (1, 0), (1, 1), (0, 1)]))
    mark.data.materials.append(mark_mat)
    h, z0 = HOLO_HALF, HOLO_SHIFT - HOLO_HALF
    holo = bpy.data.objects.new('%s hologram' % ob.name, _quad(
        '%s hologram' % ob.name,
        [(-h, 0, z0), (h, 0, z0), (h, 0, z0 + 2 * h), (-h, 0, z0 + 2 * h),
         (0, -h, z0), (0, h, z0), (0, h, z0 + 2 * h), (0, -h, z0 + 2 * h)],
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 1)]))
    holo.data.materials.append(holo_mat)
    for part in (mark, holo):
        part[FX] = True
        for c in ob.users_collection:
            c.objects.link(part)
        part.parent = ob
        part.hide_select = True
        part.hide_render = True
    # (the empty's own scale would scale the parts: they keep the game's size)
    sc = ob.scale
    for part in (mark, holo):
        part.scale = (1 / sc.x if sc.x else 1, 1 / sc.y if sc.y else 1, 1 / sc.z if sc.z else 1)
    return mark, holo


def checkpoint_objects(scene):
    return sorted((o for o in scene.objects if o.type == 'EMPTY' and o.rc_track.checkpoint),
                  key=lambda o: (o.rc_track.checkpoint, o.name))


def refresh_all(context, fs):
    n = 0
    for ob in checkpoint_objects(context.scene):
        make_fx(context, ob, fs)
        n += 1
    return n


def marker_corners(matrix_world):
    """the game's marker quad of a checkpoint empty: (Blender world corners, uvs) - its Z turn only"""
    loc = matrix_world.translation
    fwd = matrix_world.to_3x3().col[1]
    ang = math.atan2(fwd.y, fwd.x) - math.pi / 2
    c, s = math.cos(ang), math.sin(ang)
    h = MARK_SIZE / 2
    pts = []
    for x, y in ((-h, -h), (h, -h), (h, h), (-h, h)):
        pts.append((loc.x + c * x - s * y, loc.y + s * x + c * y, loc.z + 0.03))
    return pts, [(0, 0), (1, 0), (1, 1), (0, 1)]
