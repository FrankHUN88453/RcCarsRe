"""CREAT Studio chunk streams (.sb databases, .dat car profiles): reading and writing.

    u16 tag   low byte = field id, 0x0400 = an extra dword follows, tag >> 12 = kind
    u32 end   absolute offset one past the chunk
    u32 extra present if tag & 0x400 or kind == 9 (an object's class FourCC, stored reversed)
"""
import struct

LIST, WORD, DWORD, STR, FLOAT, FARR, BLOB, OBJ, VAR = 0x0, 0x2, 0x3, 0x4, 0x5, 0x7, 0x8, 0x9, 0xA


class Chunk:
    __slots__ = ('data', 'pos', 'tag', 'end', 'extra', 'p', 'prefix', 'children')

    def __init__(self, data, pos, tag, end, extra, p):
        self.data, self.pos, self.tag, self.end, self.extra, self.p = data, pos, tag, end, extra, p
        self.prefix = None
        self.children = None

    kind = property(lambda self: self.tag >> 12)
    id = property(lambda self: self.tag & 0xff)
    raw = property(lambda self: self.data[self.p:self.end])

    @property
    def cls(self):
        return self.extra[::-1].decode('latin1') if self.kind == OBJ else None

    @property
    def count(self):
        return struct.unpack('<I', self.extra)[0] if self.extra and self.kind != OBJ else None

    def str(self):
        return bytes(self.raw).split(b'\0')[0].decode('latin1')

    def dwords(self):
        r = self.raw
        return struct.unpack('<%dI' % (len(r) // 4), r[:len(r) // 4 * 4])

    def floats(self):
        r = self.raw
        return struct.unpack('<%df' % (len(r) // 4), r[:len(r) // 4 * 4])

    def vecs(self):
        f = self.floats()
        n = self.count or 1
        w = len(f) // n if n else len(f)
        return [f[i * w:(i + 1) * w] for i in range(n)]

    def get(self, ident, kind=None):
        for c in self.children or ():
            if c.id == ident and (kind is None or c.kind == kind):
                return c
        return None

    def name(self):
        s = self.get(0x03, STR)
        return s.str() if s else None


def _is_run(data, pos, end):
    n = 0
    while pos < end:
        if pos + 6 > end:
            return False
        tag, e = struct.unpack_from('<HI', data, pos)
        hdr = 10 if (tag & 0x400 or tag >> 12 == 9) else 6
        if e < pos + hdr or e > end:
            return False
        pos = e
        n += 1
    return n > 0


def parse(data, pos=None, end=None):
    if pos is None:
        pos = 4 if data[:4] == b'CSRC' else 0
    if end is None:
        end = len(data)
    out = []
    while pos + 6 <= end:
        tag, e = struct.unpack_from('<HI', data, pos)
        if e <= pos or e > end:
            break
        p = pos + 6
        extra = None
        if tag & 0x400 or tag >> 12 == 9:
            extra = bytes(data[p:p + 4])
            p += 4
        c = Chunk(data, pos, tag, e, extra, p)
        k = tag >> 12
        if k in (LIST, OBJ, BLOB, VAR) and (p == e or _is_run(data, p, e)):
            c.children = parse(data, p, e) if p < e else []
        elif tag & 0x200 and k in (WORD, DWORD, FLOAT, BLOB):
            vsize = 2 if k == WORD else 4
            if e - p > vsize and _is_run(data, p + vsize, e):
                c.prefix = struct.unpack_from('<H' if vsize == 2 else '<I', data, p)[0]
                c.children = parse(data, p + vsize, e)
        out.append(c)
        pos = e
    return out


def iter_objs(chunks, cls=None, path=()):
    """(chunk, ancestor objects) of every object of the class, depth first"""
    for c in chunks:
        if c.kind == OBJ:
            if cls is None or c.cls == cls:
                yield c, path
            if c.children:
                yield from iter_objs(c.children, cls, path + (c,))
        elif c.children:
            yield from iter_objs(c.children, cls, path)


def find(chunks, tag):
    for c in chunks:
        if c.tag == tag:
            return c
        if c.children:
            r = find(c.children, tag)
            if r is not None:
                return r
    return None


def model_names(data):
    """the names of the top-level MODL objects of a database, quickly (no full parse)"""
    out = []
    for m, parents in iter_objs(parse(data), 'MODL'):
        n = m.name()
        # (a model inside another model is a part of it; MOD_MODEL is the database's own root)
        if n and n != 'MOD_MODEL' and not any(p.cls == 'MODL' and p.name() != 'MOD_MODEL' for p in parents):
            out.append(n)
    return out


# ---- writing (the car profiles) ----

def write(chunks, base=0):
    """chunks: [tag, payload] with payload bytes, or [tag, [head bytes, children]]"""
    out = bytearray()
    for tag, payload in chunks:
        pos = len(out)
        out += struct.pack('<HI', tag, 0)
        if isinstance(payload, list):
            head, kids = payload
            out += head
            out += write(kids, base + len(out))
        else:
            out += payload
        struct.pack_into('<I', out, pos + 2, base + len(out))
    return bytes(out)
