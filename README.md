# RcCarsRe

**English** | [Magyar](README.hu.md) | [Русский](README.ru.md) | [Polski](README.pl.md)

RcCarsRe is a fan project that rebuilds the executable of the 2003 PC game **RC Cars** (Creat Studio) from
reconstructed C source, so the game can run on today's systems and be modified.

> This repository currently holds only this description. No source code has been published yet, and no part of the
> original game will ever be published here.

## What it is

- A new `RcCarsRe.exe`, written in C from the documented behaviour of the original game.
- It uses the data files of an installed, legally owned copy of the game (the DVD release or the Steam release).
  It does not work without one.
- The goal is behaviour faithful to the original. Core routines are compared bit for bit against the original's
  functions in a test harness.
- Modern changes are optional and can be switched in `RcCarsRe.ini`.

## Modern options

- Direct3D 11 renderer that emulates the original's Direct3D 8 calls
- Native resolution, borderless window, UI scaling
- Anti-aliasing (MSAA / FXAA), best texture quality
- Frame rate limit and VSync settings (no 64 fps cap), FPS counter
- HD menu font

## Status

Work in progress. It is not playable as a full game yet.

| Area | State |
|---|---|
| Intro, main menu, Options, Quick race screens | working |
| Music and interface sounds | working |
| Level loading, track rendering, animated water | working |
| AI cars following their recorded paths | working (interim) |
| Player car physics: level collision, suspension, tyres, engine, steering | working, being refined |
| Visible suspension and wheels | first car done, others in progress |
| Antenna, race camera | in progress |
| Start lights, laps, checkpoints, HUD | not started |
| Other game modes, garage, multiplayer | not started |

## What this repository will not contain

- The original game's executable, libraries, levels, models, textures, sounds or any other asset
- Tools for bypassing copy protection, or cheats

## Legal

RC Cars and all related names and assets belong to their respective owners. This is an unofficial,
non-commercial project that is not affiliated with or endorsed by them. You need your own legally obtained copy
of the game to use it.

## Languages

This description is available in English, Hungarian, Russian and Polish. The English version is the reference.
