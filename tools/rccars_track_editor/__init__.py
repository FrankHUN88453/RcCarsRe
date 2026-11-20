"""RC Cars Track Editor: the game's assets in Blender and the opponents' paths.

- Preferences: the game folder (the DVD install's folder or the Steam release's with RCCars.pack) and, if the mods
  are elsewhere, the mods folder (where RcCarsRe.exe keeps its mods\\). Scan reads what is there: the base game, and
  whether the "extension" mod is installed - then its PS2 tracks, props and cars are offered too.
- Asset browser (3D View > sidebar > RC Cars): the assets by category, a search field, import at the 3D cursor
  (a model) or whole (a track, to design on).
- NPC paths: an opponent's path is a curve object (POLY or Bezier) with its car, driver, races and speed; import a
  track's paths (CarProfiles\\<folder>\\*.dat) as curves, edit them, add the player's start, and export them into
  a mod folder: <mods>\\<mod>\\CarProfiles\\<folder>\\<name>.dat, start.dat and Scripts\\<folder>_ai.ini (a mod's
  file replaces the game's of the same path, so the same names change a game track's opponents).
"""
import math
import os
import tempfile

import bpy
import numpy as np
from mathutils import Vector
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty,
                       StringProperty)

from . import catalog, cpfx, gamefs, library, npc, sbimport, trackexport

STATE = {'fs': None, 'assets': [], 'status': 'not scanned'}


def prefs(context=None):
    return (context or bpy.context).preferences.addons[__package__].preferences


def cache_dir():
    try:
        return bpy.utils.extension_path_user(__package__, path='cache', create=True)
    except Exception:
        d = os.path.join(tempfile.gettempdir(), 'rccars_track_editor')
        os.makedirs(d, exist_ok=True)
        return d


def library_dir():
    try:
        return bpy.utils.extension_path_user(__package__, path='library', create=True)
    except Exception:
        d = os.path.join(tempfile.gettempdir(), 'rccars_track_editor_library')
        os.makedirs(d, exist_ok=True)
        return d


def fs_or_scan(context):
    if STATE['fs'] is None:
        do_scan(context)
    return STATE['fs']


def do_scan(context):
    p = prefs(context)
    fs = gamefs.GameFS(bpy.path.abspath(p.game_dir), bpy.path.abspath(p.mods_dir))
    STATE['fs'] = fs
    if not fs.has_game_data:
        STATE['assets'] = []
        STATE['status'] = 'no RC Cars data found (RCCarsDB\\stone.sb): ' + '; '.join(fs.problems or ['check the folder'])
        refresh_list(context)
        return
    STATE['assets'] = catalog.scan(fs, progress=lambda n: print('RC Cars Track Editor: reading', n))
    ext = 'extension' in fs.mods
    base = 'RCCars.pack' if any(s.kind == 'pack' for s in fs.sources) else 'loose files'
    STATE['status'] = 'base game (%s); extension mod %s; %d assets' % (
        base, 'found' if ext else 'not installed', len(STATE['assets']))
    refresh_list(context)


def has_extension():
    fs = STATE['fs']
    return bool(fs and 'extension' in fs.mods)


def category_items(self, context):
    ext = has_extension()
    return [(k, n, d) for k, n, d, needs_ext in catalog.CATEGORIES if ext or not needs_ext]


def refresh_list(context):
    wm = context.window_manager
    wm.rc_assets.clear()
    cat = wm.rc_category
    for i, a in enumerate(STATE['assets']):
        if a.category == cat:
            it = wm.rc_assets.add()
            it.name = a.label
            it.index = i
            it.source = a.source
    wm.rc_asset_index = 0


def profile_folders(self, context):
    fs = STATE['fs']
    items = []
    if fs:
        seen = set()
        for s in fs.sources:
            for n in s.files:
                if n.startswith('carprofiles\\') and n.endswith('.dat') and n.count('\\') == 2:
                    d = n.split('\\')[1]
                    if d not in seen:
                        seen.add(d)
                        items.append((d, d, 'from %s' % s.label))
    items.sort(key=lambda x: x[0])
    return items or [('NONE', '(scan the game first)', '')]


# ---------------------------------------------------------------- properties

class RCAssetItem(bpy.types.PropertyGroup):
    index: IntProperty()
    source: StringProperty()


class RCNpcProps(bpy.types.PropertyGroup):
    is_path: BoolProperty(name='Opponent path', default=False)
    is_start: BoolProperty(name='Player start', default=False)
    car: EnumProperty(name='Car', items=npc.CAR_TYPES, default='1')
    driver: EnumProperty(name='Driver', items=npc.DRIVERS, default='4')
    easy: BoolProperty(name='Easy', default=True)
    normal: BoolProperty(name='Normal', default=True)
    hard: BoolProperty(name='Hard', default=True)
    speed: FloatProperty(name='Speed', description='The car\'s speed along the path (m/s; a point\'s radius scales '
                         'it there)', default=6.0, min=0.5, max=40.0, unit='VELOCITY')
    file: StringProperty(name='File name', description='The profile\'s name (CarProfiles\\<folder>\\<name>.dat)',
                         default='buggy1')


class RCTrackProps(bpy.types.PropertyGroup):
    collide: BoolProperty(name='Collision', default=True,
                          description='The cars drive on it and hit it (off: drawn only, the cars pass through)')
    checkpoint: IntProperty(name='Checkpoint', default=0, min=0, max=256,
                            description='This empty is checkpoint N (1 = the start / finish line; 0 = not one)')


class RCTrackEditorPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    game_dir: StringProperty(name='Game folder', subtype='DIR_PATH',
                             description='The RC Cars folder: RCCarsDB, Textures.1 .. 3 (DVD) or RCCars.pack (Steam)')
    mods_dir: StringProperty(name='Mods folder', subtype='DIR_PATH',
                             description='Optional: the mods folder when it is not <game folder>\\mods (the one '
                                         'next to RcCarsRe.exe)')

    def draw(self, context):
        col = self.layout.column()
        col.prop(self, 'game_dir')
        col.prop(self, 'mods_dir')
        col.operator('rccars.scan', icon='FILE_REFRESH')
        col.label(text=STATE['status'])


# ---------------------------------------------------------------- operators

class RC_OT_scan(bpy.types.Operator):
    bl_idname = 'rccars.scan'
    bl_label = 'Scan game folder'
    bl_description = 'Read the game folder and the mods: what is installed and which assets there are'

    def execute(self, context):
        do_scan(context)
        self.report({'INFO'}, STATE['status'])
        return {'FINISHED'}


class RC_OT_import_asset(bpy.types.Operator):
    bl_idname = 'rccars.import_asset'
    bl_label = 'Import'
    bl_description = 'Import the chosen asset (a model at the 3D cursor, a track whole)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager
        if not wm.rc_assets or wm.rc_asset_index >= len(wm.rc_assets):
            self.report({'WARNING'}, 'Choose an asset first')
            return {'CANCELLED'}
        a = STATE['assets'][wm.rc_assets[wm.rc_asset_index].index]
        fs = fs_or_scan(context)
        try:
            if a.model:
                ob, n, missing = sbimport.import_model(fs, a.path, a.model, cache_dir(),
                                                       context.scene.cursor.location.copy())
                for o in context.selected_objects:
                    o.select_set(False)
                ob.select_set(True)
                context.view_layer.objects.active = ob
                what = '%s: %d mesh(es)' % (a.model, n)
            else:
                coll, n, missing = sbimport.import_level(fs, a.path, cache_dir())
                what = '%s: %d mesh(es)' % (coll.name, n)
        except Exception as ex:
            self.report({'ERROR'}, 'Import failed: %s' % ex)
            return {'CANCELLED'}
        self.report({'INFO'}, what + ('; missing textures: %d' % len(missing) if missing else ''))
        return {'FINISHED'}


class RC_OT_build_library(bpy.types.Operator):
    bl_idname = 'rccars.build_library'
    bl_label = 'Build asset library'
    bl_description = ('Make the "RC Cars" library of the Blender Asset Browser: the models (drag them onto the track) '
                      'and the textures as materials (drag them onto any object). Takes a few minutes the first time')

    models: BoolProperty(name='Models', default=True)
    textures: BoolProperty(name='Textures', default=True)

    def execute(self, context):
        fs = fs_or_scan(context)
        if not STATE['assets']:
            self.report({'ERROR'}, 'Scan the game folder first')
            return {'CANCELLED'}
        what = [w for w, on in (('models', self.models), ('textures', self.textures)) if on]
        lib = library_dir()
        wm = context.window_manager
        wm.progress_begin(0, 100)
        try:
            done = library.build(fs, STATE['assets'], lib, cache_dir(), what,
                                 progress=lambda t: print('RC Cars Track Editor:', t))
            library.register_library(lib)
        except Exception as ex:
            self.report({'ERROR'}, 'Library failed: %s' % ex)
            return {'CANCELLED'}
        finally:
            wm.progress_end()
        STATE['library'] = done
        self.report({'INFO'}, 'RC Cars library: %s (%s)' % (done, lib))
        return {'FINISHED'}


def npc_collection(context):
    name = 'RC NPC paths'
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        context.scene.collection.children.link(c)
    return c


def new_path_object(context, name, points, closed, speeds=None, base_speed=6.0):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for p, pt in zip(sp.points, points):
        p.co = (pt[0], pt[1], pt[2], 1.0)
    if speeds:
        for p, v in zip(sp.points, speeds):
            p.radius = max(0.1, v / base_speed)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, cu)
    npc_collection(context).objects.link(ob)
    ob.rc_npc.is_path = True
    ob.rc_npc.speed = base_speed
    ob.rc_npc.file = name
    cu.bevel_depth = 0.0
    ob.show_in_front = True
    return ob


class RC_OT_new_path(bpy.types.Operator):
    bl_idname = 'rccars.new_path'
    bl_label = 'New opponent path'
    bl_description = 'A closed path (a curve) around the 3D cursor: move its points along the track'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c = context.scene.cursor.location
        r = 8.0
        pts = [(c.x + r * math.cos(a), c.y + r * math.sin(a), c.z)
               for a in [i * 6.283185 / 12 for i in range(12)]]
        n = sum(1 for o in bpy.data.objects if o.rc_npc.is_path) + 1
        ob = new_path_object(context, 'buggy%d' % n, pts, True)
        for o in context.selected_objects:
            o.select_set(False)
        ob.select_set(True)
        context.view_layer.objects.active = ob
        return {'FINISHED'}


class RC_OT_add_start(bpy.types.Operator):
    bl_idname = 'rccars.add_start'
    bl_label = 'Player start'
    bl_description = 'The player\'s start place (an arrow empty: the arrow is the car\'s forward; turn it about Z)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = bpy.data.objects.get('RC player start')
        if ob is None:
            ob = bpy.data.objects.new('RC player start', None)
            ob.empty_display_type = 'SINGLE_ARROW'
            ob.empty_display_size = 1.0
            npc_collection(context).objects.link(ob)
            ob.rotation_euler = (-1.5708, 0, 0)          # (the arrow along + Y: the forward)
        ob.location = context.scene.cursor.location
        ob.rc_npc.is_start = True
        return {'FINISHED'}


class RC_OT_import_paths(bpy.types.Operator):
    bl_idname = 'rccars.import_paths'
    bl_label = 'Import paths'
    bl_description = 'The opponents\' paths of a CarProfiles folder as curves (one lap each; the start too)'
    bl_options = {'REGISTER', 'UNDO'}

    folder: EnumProperty(name='Profiles folder', items=profile_folders)

    def invoke(self, context, event):
        fs_or_scan(context)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        fs = fs_or_scan(context)
        if self.folder == 'NONE':
            return {'CANCELLED'}
        rh = context.scene.rc_ride_height
        n = 0
        for rel, src in fs.listdir('CarProfiles\\' + self.folder, '.dat'):
            name = os.path.splitext(os.path.basename(rel))[0]
            try:
                prof = npc.read_profile(fs.read(rel))
            except Exception as ex:
                self.report({'WARNING'}, '%s: %s' % (rel, ex))
                continue
            if name.lower() == 'start' or len(prof['times']) < 10:
                ob = bpy.data.objects.get('RC player start') or bpy.data.objects.new('RC player start', None)
                if ob.name not in npc_collection(context).objects:
                    npc_collection(context).objects.link(ob)
                ob.empty_display_type = 'SINGLE_ARROW'
                g = prof['places'][0]
                ob.location = npc.to_blender((g[0], g[1] - rh, g[2]))
                ob.rotation_euler = (-math.pi / 2, 0.0, math.radians(npc.yaw_of(prof['quats'][0])))
                ob.rc_npc.is_start = True
                continue
            pts, sp = npc.path_points(prof, ride_height=rh)
            base = float(np.median(sp)) if sp else 6.0
            ob = new_path_object(context, name, pts, True, sp, base)
            ob.rc_npc.car = str(min(prof['car'], 2))
            n += 1
        context.scene.rc_npc_folder = self.folder
        self.report({'INFO'}, '%d path(s) from CarProfiles\\%s' % (n, self.folder))
        return {'FINISHED'}


def curve_points(ob):
    """the path's points in the world (game coordinates), its closedness and the points' speed factors"""
    mw = ob.matrix_world
    sp = ob.data.splines[0]
    pts, mul = [], []
    if sp.type == 'BEZIER':
        from mathutils.geometry import interpolate_bezier
        bp = list(sp.bezier_points)
        pairs = list(zip(bp, bp[1:] + ([bp[0]] if sp.use_cyclic_u else [])))
        for a, b in pairs:
            seg = interpolate_bezier(a.co, a.handle_right, b.handle_left, b.co, 12)[:-1]
            for k, p in enumerate(seg):
                pts.append(npc.to_game(mw @ p))
                mul.append(a.radius + (b.radius - a.radius) * k / 12)
        if not sp.use_cyclic_u:
            pts.append(npc.to_game(mw @ bp[-1].co))
            mul.append(bp[-1].radius)
    else:
        for p in sp.points:
            pts.append(npc.to_game(mw @ p.co.xyz))
            mul.append(p.radius)
    return pts, sp.use_cyclic_u, mul


def mods_folder(context):
    p = prefs(context)
    return bpy.path.abspath(p.mods_dir) or os.path.join(bpy.path.abspath(p.game_dir), 'mods')


def export_npc(context, fs, root, folder, write_ini=True):
    """the opponents' paths and the start into root\\CarProfiles\\<folder>\\ and the AI layout into
    root\\Scripts\\<folder>_ai.ini; (paths, start written, the AI layout's file name or '')"""
    sc = context.scene
    out = os.path.join(root, 'CarProfiles', folder)
    paths = [o for o in sc.objects if o.rc_npc.is_path and o.type == 'CURVE' and o.data.splines]
    start = next((o for o in sc.objects if o.rc_npc.is_start), None)
    if not paths and start is None:
        return 0, False, ''
    os.makedirs(out, exist_ok=True)
    opponents = []
    for ob in paths:
        pts, closed, mul = curve_points(ob)
        car = int(ob.rc_npc.car)
        try:
            rows, cyc = npc.sample(pts, closed, ob.rc_npc.speed, mul, ride_height=sc.rc_ride_height)
        except ValueError as ex:
            raise ValueError('%s: %s' % (ob.name, ex))
        name = bpy.path.clean_name(ob.rc_npc.file or ob.name)
        with open(os.path.join(out, name + '.dat'), 'wb') as f:
            f.write(npc.write_profile(rows, cyc, car))
        r = ob.rc_npc
        opponents.append((car, int(r.driver), (r.easy, r.normal, r.hard), name))
    if start is not None:
        fwd = start.matrix_world.to_3x3() @ Vector((0, 0, 1))     # (the arrow: the empty's local Z)
        g = npc.to_game(fwd)
        yaw = math.degrees(math.atan2(g[0], g[2]))
        pl = npc.to_game(start.matrix_world.translation)
        with open(os.path.join(out, 'start.dat'), 'wb') as f:
            f.write(npc.start_profile((pl[0], pl[1] + sc.rc_ride_height, pl[2]), yaw))
    ini = ''
    if write_ini and opponents:
        try:
            head = npc.ini_header(fs.read('Scripts\\AIlayouts.ini').decode('latin1'))
        except Exception:
            head = ''
        if head:
            sdir = os.path.join(root, 'Scripts')
            os.makedirs(sdir, exist_ok=True)
            ini = '%s_ai.ini' % folder
            with open(os.path.join(sdir, ini), 'w', encoding='latin1', newline='') as f:
                f.write(npc.ai_ini(head, folder, opponents))
    return len(paths), start is not None, ini


class RC_OT_export_paths(bpy.types.Operator):
    bl_idname = 'rccars.export_paths'
    bl_label = 'Export to mod'
    bl_description = 'Write the paths, the start and the AI layout script into the mod folder'

    def execute(self, context):
        sc = context.scene
        fs = fs_or_scan(context)
        if not sc.rc_npc_mod or not sc.rc_npc_folder or sc.rc_npc_folder == 'NONE':
            self.report({'ERROR'}, 'Give the mod\'s name and the profiles folder')
            return {'CANCELLED'}
        root = os.path.join(mods_folder(context), sc.rc_npc_mod)
        try:
            n, st, ini = export_npc(context, fs, root, sc.rc_npc_folder, sc.rc_npc_ini)
        except ValueError as ex:
            self.report({'ERROR'}, str(ex))
            return {'CANCELLED'}
        self.report({'INFO'}, '%d path(s)%s%s -> %s' % (n, ', start' if st else '', ', Scripts\\' + ini if ini else '',
                                                        root))
        return {'FINISHED'}


# ---------------------------------------------------------------- the track

class RC_OT_add_checkpoint(bpy.types.Operator):
    bl_idname = 'rccars.add_checkpoint'
    bl_label = 'Add checkpoint'
    bl_description = ('A checkpoint at the 3D cursor, numbered in order around the lap (1 is the start / finish line), '
                      'with the marker and hologram arrow of the game; turn it about Z to turn its marker')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cps = trackexport.checkpoints(context)
        if len(cps) >= 256:
            self.report({'ERROR'}, 'The game takes at most 256 checkpoints')
            return {'CANCELLED'}
        n = max([o.rc_track.checkpoint for o in cps] + [0]) + 1
        ob = bpy.data.objects.new('RC checkpoint %d' % n, None)
        ob.empty_display_type = 'SPHERE'
        ob.empty_display_size = 1.5
        ob.location = context.scene.cursor.location
        ob.rc_track.checkpoint = n
        ob.show_name = True
        npc_collection(context).objects.link(ob)
        if cps:                                 # (turned along the way from the previous one)
            d = ob.location - cps[-1].location
            if d.length > 1e-3:
                ob.rotation_euler = (0.0, 0.0, math.atan2(d.y, d.x) - math.pi / 2)
        cpfx.make_fx(context, ob, STATE['fs'])
        for o in context.selected_objects:
            o.select_set(False)
        ob.select_set(True)
        context.view_layer.objects.active = ob
        return {'FINISHED'}


class RC_OT_checkpoint_fx(bpy.types.Operator):
    bl_idname = 'rccars.checkpoint_fx'
    bl_label = 'Refresh checkpoints'
    bl_description = ('Make the markers and hologram arrows of every checkpoint again (after renumbering them, or in '
                      'a scene made before; the textures of the game come from the scanned game folder)')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        n = cpfx.refresh_all(context, fs_or_scan(context))
        self.report({'INFO'}, '%d checkpoint(s)' % n)
        return {'FINISHED'}


class RC_OT_preview_sky(bpy.types.Operator):
    bl_idname = 'rccars.preview_sky'
    bl_label = 'Show the sky'
    bl_description = 'The sky picture as the scene\'s world (as the game maps it onto its dome)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sc = context.scene
        path = bpy.path.abspath(sc.rc_sky)
        if not os.path.isfile(path):
            self.report({'ERROR'}, 'Choose a sky picture first')
            return {'CANCELLED'}
        w = bpy.data.worlds.get('RC sky') or bpy.data.worlds.new('RC sky')
        w.use_nodes = True
        nt = w.node_tree
        env = next((n for n in nt.nodes if n.type == 'TEX_ENVIRONMENT'), None) or nt.nodes.new('ShaderNodeTexEnvironment')
        env.image = bpy.data.images.load(path, check_existing=True)
        bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
        nt.links.new(env.outputs['Color'], bg.inputs['Color'])
        sc.world = w
        for area in context.screen.areas if context.screen else ():
            if area.type == 'VIEW_3D':
                sp = area.spaces.active
                if sp.shading.type in ('MATERIAL', 'RENDERED'):
                    sp.shading.use_scene_world = True
        return {'FINISHED'}


class RC_OT_export_track(bpy.types.Operator):
    bl_idname = 'rccars.export_track'
    bl_label = 'Export track to mod'
    bl_description = ('The visible meshes as a track of the mod (RCCarsDB\\<level>.sb, textures, the sky, the Lua that '
                      'registers it) and the opponents\' paths, if any')

    def execute(self, context):
        sc = context.scene
        fs = fs_or_scan(context)
        if fs is None or not fs.has_game_data:
            self.report({'ERROR'}, 'Set the game folder first (the level template is read from it)')
            return {'CANCELLED'}
        root = os.path.join(mods_folder(context), sc.rc_npc_mod)

        def report(kind, level):
            if kind == 'npc':
                n, st, ini = export_npc(context, fs, root, level, True)
                return ini
            return None
        try:
            msg = trackexport.export(context, fs, mods_folder(context), sc.rc_npc_mod, sc.rc_level, sc.rc_track_name,
                                     sc.rc_track_desc, sc.rc_sky, sc.rc_sky_radius, report)
        except (ValueError, OSError) as ex:
            self.report({'ERROR'}, str(ex))
            return {'CANCELLED'}
        # (a car passes a checkpoint only within 1.6 m of it - an AI car 2.88 m: a path that misses one never ends
        # its lap; the game's own check, racelogic 0x4eaa40)
        cps = [npc.to_game(o.matrix_world.translation) for o in trackexport.checkpoints(context)]
        miss = []
        for ob in sc.objects:
            if ob.rc_npc.is_path and ob.type == 'CURVE' and ob.data.splines:
                pts = np.array(curve_points(ob)[0], dtype=float)
                if len(pts) > 1:            # (the path sampled every 0.2 m at most)
                    seg = [pts[i] + (pts[i + 1] - pts[i]) * t for i in range(len(pts) - 1)
                           for t in np.linspace(0, 1, max(2, int(np.linalg.norm(pts[i + 1] - pts[i]) / 0.2) + 1))]
                    P = np.array(seg)
                    for k, c in enumerate(cps):
                        d = float(np.min(np.linalg.norm(P - np.array(c), axis=1)))
                        if d > 2.5:
                            miss.append('%s misses checkpoint %d by %.1f m' % (ob.name, k + 1, d))
        self.report({'INFO'}, msg)
        for m in miss[:6]:
            self.report({'WARNING'}, m + ' (an opponent must pass within 2.8 m, the player within 1.6 m)')
        STATE['track'] = msg + (' | %d warning(s): %s' % (len(miss), miss[0]) if miss else '')
        return {'FINISHED'}


# ---------------------------------------------------------------- panels

class RC_UL_assets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        a = STATE['assets'][item.index] if item.index < len(STATE['assets']) else None
        ic = 'WORLD' if a and not a.model else 'OBJECT_DATA'
        layout.label(text=item.name, icon=ic)
        if item.source.startswith('mod '):
            layout.label(text=item.source[4:])


class RC_PT_game(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RC Cars'
    bl_label = 'Game'

    def draw(self, context):
        p = prefs(context)
        col = self.layout.column()
        col.prop(p, 'game_dir', text='')
        col.prop(p, 'mods_dir', text='Mods')
        col.operator('rccars.scan', icon='FILE_REFRESH')
        box = col.box()
        for line in STATE['status'].split('; '):
            box.label(text=line)


class RC_PT_assets(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RC Cars'
    bl_label = 'Asset browser'

    def draw(self, context):
        wm = context.window_manager
        col = self.layout.column()
        if not STATE['assets']:
            col.label(text='Scan the game folder first')
            return
        col.prop(wm, 'rc_category', text='')
        col.template_list('RC_UL_assets', '', wm, 'rc_assets', wm, 'rc_asset_index', rows=10)
        col.operator('rccars.import_asset', icon='IMPORT')
        if wm.rc_assets and wm.rc_asset_index < len(wm.rc_assets):
            a = STATE['assets'][wm.rc_assets[wm.rc_asset_index].index]
            col.label(text=a.path, icon='FILE')
        box = col.box()
        box.label(text='Asset Browser (drag & drop)', icon='ASSET_MANAGER')
        box.operator('rccars.build_library', icon='FILE_REFRESH')
        if STATE.get('library'):
            box.label(text=STATE['library'])
        box.label(text='Asset Browser > library "RC Cars":')
        box.label(text='models onto the track, textures onto objects')


class RC_PT_npc(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RC Cars'
    bl_label = 'NPC paths'

    def draw(self, context):
        sc = context.scene
        col = self.layout.column()
        row = col.row(align=True)
        row.operator('rccars.new_path', icon='CURVE_PATH')
        row.operator('rccars.add_start', icon='EMPTY_SINGLE_ARROW')
        col.operator('rccars.import_paths', icon='IMPORT')
        ob = context.active_object
        if ob is not None and ob.rc_npc.is_path:
            box = col.box()
            box.label(text=ob.name, icon='CURVE_PATH')
            r = ob.rc_npc
            box.prop(r, 'file')
            box.prop(r, 'car')
            box.prop(r, 'driver')
            box.prop(r, 'speed')
            row = box.row(align=True)
            row.prop(r, 'easy', toggle=True)
            row.prop(r, 'normal', toggle=True)
            row.prop(r, 'hard', toggle=True)
            box.label(text='A point\'s radius (Alt+S) scales the speed there', icon='INFO')
        paths = [o for o in sc.objects if o.rc_npc.is_path]
        col.label(text='%d path(s)%s in the scene' % (len(paths), ', start set' if any(
            o.rc_npc.is_start for o in sc.objects) else ''))
        box = col.box()
        box.label(text='Export')
        box.prop(sc, 'rc_npc_mod')
        box.prop(sc, 'rc_npc_folder')
        box.prop(sc, 'rc_ride_height')
        box.prop(sc, 'rc_npc_ini')
        box.operator('rccars.export_paths', icon='EXPORT')


class RC_PT_track(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RC Cars'
    bl_label = 'Track export'

    def draw(self, context):
        sc = context.scene
        col = self.layout.column()
        col.prop(sc, 'rc_level')
        col.prop(sc, 'rc_track_name')
        col.prop(sc, 'rc_track_desc')
        col.prop(sc, 'rc_npc_mod')
        box = col.box()
        box.label(text='Sky (HDR / EXR / PNG / DDS)', icon='WORLD')
        box.prop(sc, 'rc_sky', text='')
        row = box.row(align=True)
        row.prop(sc, 'rc_sky_radius')
        row.operator('rccars.preview_sky', text='', icon='HIDE_OFF')
        box = col.box()
        cps = trackexport.checkpoints(context)
        box.label(text='%d checkpoint(s), start %s' % (len(cps), 'set' if any(
            o.rc_npc.is_start for o in sc.objects) else 'missing'), icon='SPHERE')
        row = box.row(align=True)
        row.operator('rccars.add_checkpoint', icon='ADD')
        row.operator('rccars.add_start', icon='EMPTY_SINGLE_ARROW')
        box.operator('rccars.checkpoint_fx', icon='FILE_REFRESH')
        ob = context.active_object
        if ob is not None and ob.type == 'MESH':
            box.prop(ob.rc_track, 'collide', text='%s: collision' % ob.name)
        elif ob is not None and ob.type == 'EMPTY' and ob.rc_track.checkpoint:
            box.prop(ob.rc_track, 'checkpoint')
        n = len(trackexport.track_objects(context))
        col.label(text='%d mesh object(s) go in' % n)
        col.operator('rccars.export_track', icon='EXPORT')
        if STATE.get('track'):
            col.label(text=STATE['track'][:60])


SURFACE_ITEMS = [(k, n, d, i) for i, (k, n, d, b) in enumerate(trackexport.SURFACES)]
SURFACE_NAME = {b: n for k, n, d, b in trackexport.SURFACES if k != 'AUTO'}


class RC_OT_set_surface(bpy.types.Operator):
    bl_idname = 'rccars.set_surface'
    bl_label = 'Set surface'
    bl_description = 'The surface of every material of the selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    surface: EnumProperty(name='Surface', items=SURFACE_ITEMS)

    def execute(self, context):
        mats = {s.material for o in context.selected_objects if o.type == 'MESH' for s in o.material_slots if s.material}
        for m in mats:
            m.rc_surface = self.surface
        self.report({'INFO'}, '%d material(s): %s' % (len(mats), self.surface.lower()))
        return {'FINISHED'}


class RC_PT_surfaces(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RC Cars'
    bl_label = 'Surfaces'

    def draw(self, context):
        col = self.layout.column()
        col.label(text='What the cars drive on (sounds, dune grip)', icon='INFO')
        ob = context.active_object
        if ob is None or ob.type != 'MESH':
            col.label(text='Select a mesh object')
        elif not ob.material_slots:
            col.label(text='%s has no material: asphalt' % ob.name)
        else:
            box = col.box()
            box.label(text=ob.name, icon='OBJECT_DATA')
            for slot in ob.material_slots:
                m = slot.material
                if m is None:
                    continue
                row = box.row(align=True)
                row.label(text=m.name, icon='MATERIAL')
                row.prop(m, 'rc_surface', text='')
                if m.rc_surface == 'AUTO':
                    img = trackexport.material_image(m)[0]
                    bits = trackexport.surface_bits(m, img)
                    row.label(text='= %s' % SURFACE_NAME.get(bits, hex(bits)))
        n = sum(1 for o in context.selected_objects if o.type == 'MESH')
        row = col.row()
        row.enabled = n > 0
        row.operator_menu_enum('rccars.set_surface', 'surface', text='Set on %d selected object(s)' % n,
                               icon='BRUSH_DATA')


CLASSES = (RCAssetItem, RCNpcProps, RCTrackProps, RCTrackEditorPrefs, RC_OT_scan, RC_OT_import_asset, RC_OT_new_path,
           RC_OT_add_start, RC_OT_import_paths, RC_OT_export_paths, RC_OT_add_checkpoint, RC_OT_checkpoint_fx, RC_OT_preview_sky,
           RC_OT_export_track, RC_OT_set_surface, RC_OT_build_library, RC_UL_assets, RC_PT_game, RC_PT_assets, RC_PT_npc,
           RC_PT_track, RC_PT_surfaces)


def _category_update(self, context):
    refresh_list(context)


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.rc_assets = CollectionProperty(type=RCAssetItem)
    bpy.types.WindowManager.rc_asset_index = IntProperty()
    bpy.types.WindowManager.rc_category = EnumProperty(name='Category', items=category_items, update=_category_update)
    bpy.types.Object.rc_npc = PointerProperty(type=RCNpcProps)
    bpy.types.Scene.rc_npc_mod = StringProperty(name='Mod', default='my_track',
                                                description='The mod folder the paths go into (in the mods folder)')
    bpy.types.Scene.rc_npc_folder = StringProperty(name='Profiles folder', default='',
                                                   description='CarProfiles\\<folder>: the track\'s AI path folder '
                                                               '(the same as the game\'s to replace a track\'s paths)')
    bpy.types.Scene.rc_ride_height = FloatProperty(name='Ride height', default=0.18, min=0.0, max=1.0, unit='LENGTH',
                                                   description='How high over the drawn path the car\'s middle goes')
    bpy.types.Scene.rc_npc_ini = BoolProperty(name='Write the AI layout script', default=True)
    bpy.types.Object.rc_track = PointerProperty(type=RCTrackProps)
    bpy.types.Material.rc_surface = EnumProperty(
        name='Surface', default='AUTO',
        items=[(k, n, d, i) for i, (k, n, d, b) in enumerate(trackexport.SURFACES)],
        description='What the cars drive on there: their rolling and landing sounds, and the grip of dune sand')
    bpy.types.Scene.rc_level = StringProperty(name='Level', default='my_track',
                                              description='The level\'s file name (RCCarsDB\\<level>.sb) and the track\'s '
                                                          'id: small letters, digits, _')
    bpy.types.Scene.rc_track_name = StringProperty(name='Name', default='My track',
                                                   description='The track\'s name on the Quick race page')
    bpy.types.Scene.rc_track_desc = StringProperty(name='Description', default='',
                                                   description='The track\'s description (\\n breaks a line)')
    bpy.types.Scene.rc_sky = StringProperty(name='Sky', subtype='FILE_PATH', default='',
                                            description='An equirectangular sky picture: .hdr / .exr (the game brings '
                                                        'its light into range by itself), .png or .dds')
    bpy.types.Scene.rc_sky_radius = FloatProperty(name='Radius', default=500.0, min=50.0, max=5000.0, unit='LENGTH',
                                                  description='The sky dome\'s radius (at least 3/4 of the track\'s size)')


def unregister():
    for attr in ('rc_assets', 'rc_asset_index', 'rc_category'):
        delattr(bpy.types.WindowManager, attr)
    del bpy.types.Object.rc_npc
    del bpy.types.Object.rc_track
    del bpy.types.Material.rc_surface
    for attr in ('rc_npc_mod', 'rc_npc_folder', 'rc_ride_height', 'rc_npc_ini', 'rc_level', 'rc_track_name',
                 'rc_track_desc', 'rc_sky', 'rc_sky_radius'):
        delattr(bpy.types.Scene, attr)
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
