"""The game's files as one tree: the game folder's loose files (the DVD install), RCCars.pack (the Steam release) and
the mods (mods\\<name>\\ folders or mods\\<name>.zip), a mod's file replacing the game's file of the same path, as
the game does. Paths are relative with backslashes, compared without case."""
import os
import struct
import zipfile

import numpy as np

TEX_DIRS = ('Textures.1', 'Textures.2', 'Textures.3')     # high to low quality


def _norm(p):
    return p.replace('/', '\\').strip('\\').lower()


def _decrypt(data, key):
    """the pack's XOR (RCCARS.exe 0x421190): the bytes XORed with the key's bytes in turn; after each pass over the key
    every key byte becomes k * 3 + 1. A pass ends before the key's next zero byte, so a key byte that has become 0
    shortens the passes (as the game does)."""
    k = list(key[:0x1f]) + [0] * (32 - len(key[:0x1f]))
    n0 = len(key[:0x1f])
    if not n0:
        return data
    parts, total = [], 0
    while total < len(data):
        p = 1
        while p < 32 and k[p]:
            p += 1
        parts.append(bytes(k[:p]))
        total += p
        for j in range(n0):
            k[j] = (k[j] * 3 + 1) & 0xff
    stream = np.frombuffer(b''.join(parts)[:len(data)], dtype=np.uint8)
    return (np.frombuffer(data, dtype=np.uint8) ^ stream).tobytes()


class Pack:
    """RCCars.pack: a chunk stream root 0x5210 with the key 0x4014 and a list 0x613 of entries {0x4021 name,
    0x3022 size, 0x3023 offset, 0x3024 type}; each file is a 0x1431 chunk whose extra dword is its size, its bytes
    XOR-encrypted when the type has 0x20 (the Steam release's textures)"""

    def __init__(self, path):
        self.path = path
        self.entries = {}
        self.key = b'CREATSTUDIOGames'
        with open(path, 'rb') as f:
            def chunk(pos):
                f.seek(pos)
                tag, end = struct.unpack('<HI', f.read(6))
                extra = None
                if tag & 0x400 or (tag >> 12) == 9:
                    extra = struct.unpack('<I', f.read(4))[0]
                return tag, end, extra, f.tell()
            tag, root_end, _, p = chunk(0)
            if tag != 0x5210:
                raise ValueError('not an RC Cars pack')
            p += 4
            while p < root_end:
                tag, end, extra, q = chunk(p)
                if tag == 0x613:
                    e = q
                    while e < end:
                        _, ee, _, r = chunk(e)
                        ent = {}
                        while r < ee:
                            t2, e2, _, s = chunk(r)
                            f.seek(s)
                            if t2 == 0x4021:
                                ent['name'] = f.read(e2 - s).split(b'\0')[0].decode('latin1')
                            elif t2 in (0x3022, 0x3023, 0x3024):
                                ent[t2] = struct.unpack('<I', f.read(4))[0]
                            r = e2
                        if 'name' in ent:
                            self.entries[_norm(ent['name'])] = (ent['name'], ent.get(0x3023, 0), ent.get(0x3022, 0),
                                                                ent.get(0x3024, 0))
                        e = ee
                elif tag == 0x4014:                 # the pack's own key (it replaces the default)
                    f.seek(q)
                    k = f.read(end - q).split(b'\0')[0]
                    if k:
                        self.key = k
                p = end

    def read(self, name):
        _, off, size, kind = self.entries[name]
        with open(self.path, 'rb') as f:
            f.seek(off)
            tag, end = struct.unpack('<HI', f.read(6))
            f.read(4)
            data = f.read(size)
        return _decrypt(data, self.key) if kind & 0x20 else data


class Source:
    """one place files come from: a folder or a zip (a mod) or the pack"""

    def __init__(self, kind, path, label):
        self.kind, self.path, self.label = kind, path, label
        self.files = {}                     # normalised name -> its real name (for listing)
        if kind == 'dir':
            for root, dirs, files in os.walk(path):
                rel = os.path.relpath(root, path)
                if label == 'game folder' and rel.lower().split(os.sep)[0] in ('_re', '.git', 'saves', 'screenshots', 'mods'):
                    dirs[:] = []
                    continue
                for fn in files:
                    r = fn if rel == '.' else os.path.join(rel, fn)
                    self.files[_norm(r)] = r
        elif kind == 'zip':
            self.zip = zipfile.ZipFile(path)
            names = [n for n in self.zip.namelist() if not n.endswith('/')]
            # (a zip may hold the mod's folder itself: <name>/RCCarsDB/..)
            top = {n.split('/')[0] for n in names}
            self.strip = (list(top)[0] + '/') if len(top) == 1 and all('/' in n for n in names) else ''
            for n in names:
                self.files[_norm(n[len(self.strip):])] = n
        elif kind == 'pack':
            self.pack = Pack(path)
            self.files = {k: v[0] for k, v in self.pack.entries.items()}

    def read(self, norm):
        if self.kind == 'dir':
            with open(os.path.join(self.path, self.files[norm]), 'rb') as f:
                return f.read()
        if self.kind == 'zip':
            return self.zip.read(self.files[norm])
        return self.pack.read(norm)


class GameFS:
    def __init__(self, game_dir, mods_dir=''):
        self.game_dir = game_dir
        self.sources = []                   # the game first, the mods after (a later one wins)
        self.mods = {}                      # mod name -> Source
        self.problems = []
        if not game_dir or not os.path.isdir(game_dir):
            self.problems.append('the game folder does not exist')
            return
        pack = os.path.join(game_dir, 'RCCars.pack')
        if os.path.exists(pack):
            try:
                self.sources.append(Source('pack', pack, 'RCCars.pack'))
            except Exception as ex:
                self.problems.append('RCCars.pack: %s' % ex)
        self.sources.append(Source('dir', game_dir, 'game folder'))
        for mdir in self.mod_dirs(mods_dir):
            for entry in sorted(os.listdir(mdir)):
                p = os.path.join(mdir, entry)
                name = entry[:-4] if entry.lower().endswith('.zip') else entry
                if name.lower() in self.mods:
                    continue
                try:
                    if os.path.isdir(p):
                        src = Source('dir', p, 'mod ' + name)
                    elif entry.lower().endswith('.zip'):
                        src = Source('zip', p, 'mod ' + name)
                    else:
                        continue
                except Exception as ex:
                    self.problems.append('mod %s: %s' % (name, ex))
                    continue
                self.mods[name.lower()] = src
                self.sources.append(src)

    def mod_dirs(self, mods_dir):
        out = []
        for d in (mods_dir, os.path.join(self.game_dir, 'mods')):
            if d and os.path.isdir(d) and os.path.normcase(os.path.abspath(d)) not in \
                    [os.path.normcase(os.path.abspath(x)) for x in out]:
                out.append(d)
        return out

    @property
    def has_game_data(self):
        return self.exists('RCCarsDB\\stone.sb')

    def exists(self, path):
        n = _norm(path)
        return any(n in s.files for s in self.sources)

    def source_of(self, path):
        n = _norm(path)
        for s in reversed(self.sources):
            if n in s.files:
                return s
        return None

    def read(self, path):
        n = _norm(path)
        for s in reversed(self.sources):
            if n in s.files:
                return s.read(n)
        raise FileNotFoundError(path)

    def listdir(self, folder, ext=None, sources=None):
        """[(relative path, source)] of the files directly in the folder (the winning copy of each)"""
        pre = _norm(folder) + '\\'
        out = {}
        for s in sources or self.sources:
            for n, real in s.files.items():
                if n.startswith(pre) and '\\' not in n[len(pre):] and (not ext or n.endswith(ext)):
                    out[n] = (real.replace('/', '\\'), s)
        return sorted(out.values(), key=lambda v: v[0].lower())

    def texture(self, name):
        """(kind, bytes) of a texture by name: a mod's PNG / DDS first, then Textures.1 .. 3 csi"""
        for s in reversed(self.sources):
            if s.kind == 'pack' or s.label == 'game folder':
                continue
            for ext in ('.png', '.dds'):
                n = _norm('Textures\\' + name + ext)
                if n in s.files:
                    return ext[1:], s.read(n)
        for d in TEX_DIRS:
            n = _norm(d + '\\' + name + '.csi')
            for s in reversed(self.sources):
                if n in s.files:
                    return 'csi', s.read(n)
        return None, None
