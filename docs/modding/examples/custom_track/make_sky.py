"""An HDRI sky of our own (no download): Blender's physical sky texture rendered by Cycles through an equirectangular
camera, saved as Radiance .hdr and as OpenEXR in several codecs (for the engine's decoder tests).
blender -b --factory-startup --python gen_sky.py -- <out folder>"""
import math
import os
import sys

import bpy

out = sys.argv[sys.argv.index('--') + 1]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 16
sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = 2048, 1024
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('sky')
sc.world = w
w.use_nodes = True
nt = w.node_tree
bg = nt.nodes['Background']
sky = nt.nodes.new('ShaderNodeTexSky')
for t in ('NISHITA', 'MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'HOSEK_WILKIE'):
    try:
        sky.sky_type = t
        break
    except TypeError:
        continue
if hasattr(sky, 'sun_elevation'):
    sky.sun_elevation = math.radians(28)
    sky.sun_rotation = math.radians(140)
nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.0
cam = bpy.data.cameras.new('pano')
cam.type = 'PANO'
if hasattr(cam, 'panorama_type'):
    cam.panorama_type = 'EQUIRECTANGULAR'
else:
    cam.cycles.panorama_type = 'EQUIRECTANGULAR'
co = bpy.data.objects.new('pano', cam)
sc.collection.objects.link(co)
co.rotation_euler = (math.radians(90), 0, 0)        # (looking at the horizon: the panorama's middle row)
sc.camera = co
bpy.ops.render.render()
img = bpy.data.images['Render Result']
st = sc.render.image_settings


def save(name, fmt, codec=None, depth=None):
    st.file_format = fmt
    if codec:
        st.exr_codec = codec
    if depth:
        st.color_depth = depth
    p = os.path.join(out, name)
    img.save_render(p, scene=sc)
    print('SAVED', p, os.path.getsize(p))


save('sky.hdr', 'HDR')
for codec in ('ZIP', 'ZIPS', 'RLE', 'NONE', 'PIZ'):
    save('sky_%s_half.exr' % codec.lower(), 'OPEN_EXR', codec, '16')
save('sky_zip_float.exr', 'OPEN_EXR', 'ZIP', '32')
