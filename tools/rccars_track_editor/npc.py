"""The opponents' paths (CarProfiles\\<folder>\\<name>.dat, the game's recorded car profiles) and the AI layout
script that names them.

A profile: root 0x2250 {u16 1, 0x260 info {0x2061 cycle start frame, 0x2069 car type, texts ..}, 0x263 record
header, 0x264 the frames, 0x265}. A frame is 0x88 bytes: float time, place xyz, rotation w x y z (the car's forward
is + z), linear momentum (the velocity, m/s), angular momentum, six spring lengths, their rates, the steering in
degrees at [25], six more wheel values, then a flag byte at 0x84 (bit 0: forward held). Frames are 0.01 s apart; the
game replays them from the start and loops from the cycle start frame. Car types: 0 Overkill, 1 Buggy, 2 Warhammer.
Game (x, y, z) = Blender (-x, z, y)."""
import math
import struct

import numpy as np

from . import chunks as cc

STEP = 0.01
CAR_TYPES = [('0', 'Overkill', 'The Overkill chassis'), ('1', 'Buggy', 'The Buggy chassis'),
             ('2', 'Warhammer', 'The Warhammer (six wheels)')]
CAR_CODE = {0: 'OVERKILL', 1: 'BUGGY', 2: 'HUMMER'}
DRIVERS = [('1', 'McJocker', ''), ('2', 'MaxXMad', ''), ('3', 'Doc', ''), ('4', 'BabyShark', ''), ('5', 'Rosy', ''),
           ('6', 'DaKilla', ''), ('7', 'Johny', '')]
DRIVER_CODE = {1: 'MCJOCKER', 2: 'MAXXMAD', 3: 'DOC', 4: 'BABYSHARK', 5: 'ROSY', 6: 'DAKILLA', 7: 'JOHNY'}
# the springs a chassis' paths keep (means of the game's own paths: Buggy, Overkill; the Warhammer has 6)
SPRINGS = {0: (0.15, 0.15, 0.13, 0.13, 0.0, 0.0), 1: (0.167, 0.168, 0.144, 0.144, 0.0, 0.0),
           2: (0.106, 0.106, 0.093, 0.093, 0.100, 0.100)}
WHEELBASE = 0.33                    # m, for the steering angle shown by the wheels
MAX_STEER = 29.0


def to_game(v):
    return (-v[0], v[2], v[1])


def to_blender(g):
    return (-g[0], g[2], g[1])


# ---- reading ----

def read_profile(data):
    """{'times', 'places' (game), 'speeds', 'cycle', 'car'} of a .dat"""
    tree = cc.parse(data)
    fr = cc.find(tree, 0x264)
    if fr is None:
        raise ValueError('no frames (0x264) in the profile')
    raw = bytes(fr.raw)
    n = len(raw) // 0x88
    F = np.frombuffer(raw[:n * 0x88], dtype='<f4').reshape(n, 34)
    cyc = cc.find(tree, 0x2061)
    car = cc.find(tree, 0x2069)
    return {'times': F[:, 0].copy(), 'places': F[:, 1:4].copy(), 'speeds': np.linalg.norm(F[:, 8:11], axis=1),
            'quats': F[:, 4:8].copy(),
            'cycle': struct.unpack('<H', bytes(cyc.raw[:2]))[0] if cyc is not None else 0,
            'car': struct.unpack('<H', bytes(car.raw[:2]))[0] if car is not None else 1}


def yaw_of(q):
    """the heading (degrees, the game's: atan2(forward x, forward z)) of a frame's rotation (w, x, y, z; the car's
    forward is its +z)"""
    w, x, y, z = (float(v) for v in q)
    fx, fz = 2 * (x * z + w * y), 1 - 2 * (x * x + y * y)
    return math.degrees(math.atan2(fx, fz))


def path_points(profile, every=0.25, ride_height=0.0):
    """(Blender points, speeds) sampled every `every` seconds of the profile: one lap from the car's grid place (the
    first frame, behind the start line) to where the path comes back nearest to it (the exported path starts at its
    first point again: the game puts the car at the first frame)"""
    t, P, V = profile['times'], profile['places'], profile['speeds']
    n = len(t)
    cyc = profile['cycle'] if 0 <= profile['cycle'] < n - 10 else 0
    half = cyc + (n - cyc) // 2
    stop = half + int(np.argmin(np.linalg.norm(P[half:] - P[0], axis=1))) if n - half > 2 else n - 1
    pts, sp = [], []
    nxt = t[0]
    for i in range(0, stop + 1):
        if t[i] >= nxt:
            g = P[i]
            pts.append(to_blender((g[0], g[1] - ride_height, g[2])))
            sp.append(float(V[i]))
            nxt += every
    return pts, sp


# ---- writing ----

def _quat(yaw, pitch):
    """w x y z of yaw about y, then pitch (nose up positive) about the car's x"""
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(-pitch / 2), math.sin(-pitch / 2)
    # q = qy * qx
    return (cy * cp, cy * sp, sy * cp, -sy * sp)


def sample(points, closed, speed, speed_mul=None, extra=3.0, ride_height=0.18):
    """frames 0.01 s apart along a polyline (game coordinates) driven at speed (m/s, times speed_mul per point);
    a closed loop is driven once and `extra` seconds more (the cycle start is then where the lap begins again).
    Returns (rows, cycle frame)"""
    P = np.array(points, float)
    if closed:
        P = np.vstack([P, P[:1]])
    mul = np.array(speed_mul if speed_mul is not None else [1.0] * len(points), float)
    if closed:
        mul = np.append(mul, mul[:1])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    S = np.r_[0, np.cumsum(seg)]
    L = S[-1]
    if L < 1.0:
        raise ValueError('the path is shorter than 1 m')

    def at(s):
        if closed:
            s = s % L
        s = min(max(s, 0.0), L)
        i = min(int(np.searchsorted(S, s, side='right')) - 1, len(seg) - 1)
        u = (s - S[i]) / seg[i] if seg[i] > 0 else 0.0
        return P[i] + (P[i + 1] - P[i]) * u, mul[i] + (mul[i + 1] - mul[i]) * u, i

    rows, s, t = [], 0.0, 0.0
    total = L + (speed * extra if closed else 0.0)
    while s <= total:
        p, m, _ = at(s)
        v = max(0.5, speed * m)
        rows.append((t, p, v, s))
        s += v * STEP
        t += STEP
    # the cycle start: the first pass of the place where the frames end (the game loops from there to the end)
    cyc = 0
    if closed:
        s_end = rows[-1][3] - L
        cyc = next((k for k, r in enumerate(rows) if r[3] >= s_end), 0)
    out = []
    n = len(rows)
    for k, (t, p, v, s) in enumerate(rows):
        a = at(s - 0.3)[0]
        b = at(s + 0.3)[0]
        d = b - a
        hl = math.hypot(d[0], d[2]) or 1e-6
        yaw = math.atan2(d[0], d[2])
        pitch = math.atan2(d[1], hl)
        # the steering from the curvature ahead (the yaw's change over a metre)
        b2 = at(s + 1.3)[0] - at(s + 0.3)[0]
        dyaw = math.atan2(b2[0], b2[2]) - yaw
        dyaw = (dyaw + math.pi) % (2 * math.pi) - math.pi
        steer = max(-MAX_STEER, min(MAX_STEER, math.degrees(math.atan(WHEELBASE * dyaw / 1.0))))
        vel = np.array([d[0] / hl * v * math.cos(pitch), math.sin(pitch) * v, d[2] / hl * v * math.cos(pitch)])
        out.append((t + 0.02, (p[0], p[1] + ride_height, p[2]), _quat(yaw, pitch), vel, steer))
    return out, cyc


def write_profile(rows, cycle, car, start=False):
    """the .dat bytes of frames [(time, place, quat w x y z, velocity, steer)]"""
    count = len(rows)
    F = np.zeros((count, 34), dtype='<f4')
    spr = SPRINGS.get(car, SPRINGS[1])
    for k, (t, p, q, vel, st) in enumerate(rows):
        F[k, 0] = t
        F[k, 1:4] = p
        F[k, 4:8] = q
        F[k, 8:11] = vel
        F[k, 14:20] = spr
        F[k, 26] = st
    raw = bytearray(F.tobytes())
    if not start:
        for k in range(count):
            raw[k * 0x88 + 0x84] = 1
    dist = lambda a, b: float(np.linalg.norm(np.diff(F[a:b + 1, 1:4], axis=0), axis=1).sum()) if b > a else 0.0

    def word(tag, v):
        return [tag, struct.pack('<H', v & 0xffff)]

    def text(tag, s):
        return [tag, s.encode('latin1') + b'\0']

    info = [word(0x2061, cycle), word(0x2069, car),
            text(0x4074, 'Time path FULL: %f' % (F[-1, 0] - F[0, 0])),
            text(0x4075, 'Time path CYCLE: %f' % (F[-1, 0] - F[cycle, 0])),
            text(0x4076, 'Distance FULL: %f' % dist(0, count - 1)),
            text(0x4077, 'Distance CYCLE: %f' % dist(cycle, count - 1)),
            text(0x4078, 'Cycle NMB=%d, x=%f;y=%f;z=%f' % (cycle, F[cycle, 1], F[cycle, 2], F[cycle, 3])),
            word(0x2070, 0), word(0x2071, 0), word(0x2072, 0), word(0x2073, 0),
            word(0x2066, 0x24), word(0x2067, 0x88), word(0x2068, 0xc)]
    rec = struct.pack('<IfIIIIIII', count, float(F[-1, 0]), 0, 0, 0, count, 0, 1, 0)
    top = [[0x2250, [struct.pack('<H', 1), [[0x260, [b'', info]], [0x263, rec], [0x264, bytes(raw)],
                                            [0x265, bytes(12)]]]]]
    return cc.write(top)


def start_profile(place, yaw_deg, car=0):
    """the player's start: a two-frame profile at a place (game) facing yaw (degrees, game: atan2(x, z))"""
    q = _quat(math.radians(yaw_deg), 0.0)
    rows = [(0.0, place, q, np.zeros(3), 0.0), (STEP, place, q, np.zeros(3), 0.0)]
    return write_profile(rows, 0, car, start=True)


def ai_ini(header, folder, opponents):
    """an AI layout script: the game's AIlayouts.ini head (the codes and the AIPlayer sections) and one AIRace1 with
    the opponents [(car code, driver code, races, path name)]"""
    races_txt = lambda r: ' + '.join(x for x, on in zip(('EASY', 'NORMAL', 'HARD'), r) if on) or 'EASY + NORMAL + HARD'
    b = ['// AI paths made with the RC Cars Track Editor (Blender)', 'Section Keys "AIRace1"', '',
         'CoeffCommonOpponents(float) = 0.85', '',
         'DefaultPath(string) = "%s"' % folder, 'GhostPath(string) = "%s"' % folder,
         'PlayerPath(string) = "%s\\start"' % folder, '']
    for i, (car, ref, races, name) in enumerate(opponents[:5], 1):
        b += ['AI%dCar  (int) = %s' % (i, CAR_CODE[car]), 'AI%dRef  (int) = %s' % (i, DRIVER_CODE[ref]),
              'AI%dRaces(int) = %s' % (i, races_txt(races)), 'AI%dPath (string) = "%s\\%s"' % (i, folder, name),
              'AI%dBoost(int) = 0' % i, 'AI%dReson(int) = 0' % i, 'AI%dTires(int) = 0' % i]
    b += ['', 'End // Section', '']
    return header.rstrip() + '\r\n\r\n' + '\r\n'.join(b)


def ini_header(text):
    """the part of the game's AIlayouts.ini before its first AIRace section"""
    i = text.find('Section Keys "AIRace')
    head = text[:i] if i > 0 else text
    # (the comment line just above the first AIRace section belongs to it)
    return head
