"""The assets the editor offers: the base game's (tracks, props, road cars, characters, cars) and, when the
"extension" mod is installed, its PS2 tracks, props and cars too."""
import os
import re

from . import chunks as cc
from .gamefs import _norm

LOD = re.compile(r'LOD\d|_lod\d|antenna', re.I)  # (a model's coarser copies and its antenna: not offered)
BASE_TRACKS = ['beach_1', 'beach_2', 'beach_3', 'beach_4', 'country_1', 'country_2', 'country_3', 'country_4',
               'urban_1', 'urban_2']
BASE_MODEL_FILES = [('PROPS', 'stone.sb'), ('ROADCARS', 'Roadcar.sb'), ('CHARACTERS', 'AIChars.sb'),
                    ('CHARACTERS', 'people.sb'), ('CARS', 'Car.sb')]
CATEGORIES = [
    ('TRACKS', 'Tracks', 'The game\'s levels, to design on (imported whole)', False),
    ('PROPS', 'Props', 'Cans, balls, buckets, cones ..', False),
    ('ROADCARS', 'Road cars', 'The traffic vehicles', False),
    ('CHARACTERS', 'Characters', 'People and animals', False),
    ('CARS', 'Cars', 'The racing cars', False),
    ('EXT_TRACKS', 'PS2 tracks (extension)', 'The PS2 race levels of the extension mod', True),
    ('EXT_PROPS', 'PS2 props (extension)', 'The PS2 props, karts, the kid, the bugs', True),
    ('EXT_CARS', 'PS2 cars (extension)', 'The PS2 cars and bodies', True),
]


class Asset:
    __slots__ = ('category', 'label', 'path', 'model', 'source')

    def __init__(self, category, label, path, model, source):
        self.category, self.label, self.path, self.model, self.source = category, label, path, model, source


def extension_levels(fs, ext):
    """the levels the extension mod registers (rc.registerTrack{level = ..} in its scripts) with their names"""
    out = {}
    for n in list(ext.files):
        if n.startswith('scripts\\') and n.endswith('.lua'):
            text = ext.read(n).decode('utf-8', 'replace')
            names = [(n.start(), n.group(1)) for n in re.finditer(r'\bname\s*=\s*(?:\{\s*en\s*=\s*)?"([^"]+)"', text)]
            for m in re.finditer(r'level\s*=\s*"(\w+)"', text):
                lv = m.group(1)
                # (the track's name: the nearest name = .. of the same table, before or after the level)
                near = [(abs(pos - m.start()), n) for pos, n in names if abs(pos - m.start()) < 400]
                out.setdefault(lv, min(near)[1] if near else lv)
    return out


def scan(fs, progress=None):
    """[Asset] for the game folder (and the extension mod when it is there)"""
    out = []
    for lv in BASE_TRACKS:
        p = 'RCCarsDB\\%s.sb' % lv
        if fs.exists(p):
            out.append(Asset('TRACKS', lv, p, '', fs.source_of(p).label))
    for cat, fn in BASE_MODEL_FILES:
        p = 'RCCarsDB\\' + fn
        if not fs.exists(p):
            continue
        if progress:
            progress(fn)
        try:
            for name in cc.model_names(fs.read(p)):
                if not LOD.search(name):
                    out.append(Asset(cat, name, p, name, fs.source_of(p).label))
        except Exception:
            pass
    ext = fs.mods.get('extension')
    if ext:
        levels = extension_levels(fs, ext)
        for rel, src in fs.listdir('RCCarsDB', '.sb', sources=[ext]):
            base = os.path.splitext(os.path.basename(rel))[0]
            if base in levels:
                out.append(Asset('EXT_TRACKS', '%s (%s)' % (levels[base], base), rel, '', src.label))
                continue
            if progress:
                progress(base)
            cat = 'EXT_PROPS' if base.startswith('ps2_') else 'EXT_CARS'
            try:
                names = cc.model_names(src.read(_norm(rel)))
            except Exception:
                names = []
            for name in names:
                if not LOD.search(name):
                    out.append(Asset(cat, name, rel, name, src.label))
    return out
