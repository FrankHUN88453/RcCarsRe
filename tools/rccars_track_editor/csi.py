"""CREAT .csi pictures (the game's Textures.1 .. 3 and the GLTX blobs) to RGBA, with numpy.

    0x00 'MISC'   0x08 header size   0x10 width, height, bytes per pixel
    0x24 channel names (up to 4, the most significant first: 'ARGB', 'RGB', 'I' ..)
    0x2c one (lo bit, hi bit) pair a channel, in the same order
the pixel rows follow the header, the top row first (8-bit palette pictures - the PS2's - are not handled here)"""
import struct

import numpy as np


def decode(raw):
    """(width, height, rgba uint8 array h x w x 4) or None"""
    if raw[:4] != b'MISC':
        return None
    hsize = struct.unpack_from('<I', raw, 8)[0]
    w, h, bpp = struct.unpack_from('<III', raw, 0x10)
    if not (0 < w <= 4096 and 0 < h <= 4096 and bpp in (1, 2, 3, 4)):
        return None
    names = bytes(raw[0x24:0x28]).rstrip(b'\0').decode('latin1')
    chans = {ch: (raw[0x2c + 2 * i], raw[0x2d + 2 * i]) for i, ch in enumerate(names)}
    px = np.frombuffer(bytes(raw[hsize:hsize + w * h * bpp]), dtype=np.uint8)
    if px.size < w * h * bpp:
        return None
    px = px.reshape(h * w, bpp).astype(np.uint32)
    v = np.zeros(h * w, dtype=np.uint32)
    for i in range(bpp):
        v |= px[:, i] << (8 * i)

    def get(ch, default):
        if ch not in chans:
            return np.full(h * w, default, dtype=np.uint32)
        lo, hi = chans[ch]
        bits = hi - lo + 1
        x = (v >> lo) & ((1 << bits) - 1)
        return x * 255 // ((1 << bits) - 1)

    if 'I' in chans or 'L' in chans:
        r = g = b = get('I' if 'I' in chans else 'L', 0)
    else:
        r, g, b = get('R', 0), get('G', 0), get('B', 0)
    a = get('A', 255)
    rgba = np.stack([r, g, b, a], -1).astype(np.uint8).reshape(h, w, 4)
    return w, h, rgba
