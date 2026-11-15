# Making mods for RcCarsRe

**English** | [Magyar](MODDING.hu.md) | [Русский](MODDING.ru.md) | [Polski](MODDING.pl.md)

RcCarsRe (the rebuilt RC Cars exe) can load mods: files that replace the game's own files without touching the game's
folders. The original game has no mod support; this is a modern feature of the rebuild, switched by
`RcCarsRe.ini [Modern] Mods=1` (the default). With `Mods=0`, or without a `mods` folder, the game reads exactly the
files the original reads.

## Where mods go

Next to `RcCarsRe.exe`, a folder named `mods` (a `mods` folder in the game's own folder, e.g. the Steam copy's
`RCCars\mods`, is read too; the exe never writes into either):

```
RcCarsRe.exe
RcCarsRe.ini
mods\
    BetterSkins.zip            a mod as a zip archive
    LoudReset\                 a mod as a plain folder
        Sound\cp_reset.wav
```

A mod is either a folder `mods\<name>\` or an archive `mods\<name>.zip`. Inside it the files carry the game's own
relative paths, the same as under the game folder (the DVD install) or inside `RCCars.pack` (the Steam release):

| What                     | Path in the mod (examples)                                   |
|--------------------------|--------------------------------------------------------------|
| textures                 | `Textures.1\sand.csi`, `Textures.2\...`, `Textures.3\...`    |
| textures, every quality  | `Textures\sand.png` (stands in for Textures.1, .2 and .3)    |
| sounds                   | `Sound\cp_reset.au`, `Sound\snd.ini`                         |
| music and intro          | `Tracks\Dead_Track01.mp3`                                    |
| settings                 | `Settings\...`                                               |
| levels and database      | `RCCarsDB\...`, `RCCars.sb`                                  |
| language, fonts          | `Language\Game\English.tbl`, `Language\English\...`         |
| cars, road cars, people  | `CarProfiles\...`, `Profiles\...`                            |
| scripts, splines, faces  | `Scripts\...`, `Splines\...`, `FacesSys\...`, `Faces\...`   |
| start-up configuration   | `Config.gm`, `Autoexec.gm`                                   |

Any file the game reads can be replaced, and new files can be added to the folders the game lists (for example new
faces or font pages): they show up after the game's own files. Names are not case sensitive, and `/` and `\` are the
same. A zip that holds one top folder named like the mod itself (`BetterSkins.zip` containing `BetterSkins\Sound\...`)
is read as if that folder were not there.

## Scripts

A mod can also hold Lua scripts (`*.lua` in its root or in `scripts\`): HUD texts and pictures, sounds, its own
settings page in the Mods screen, and (API 1.1) the camera, fog, sun, lights, gamepad rumble / light bar and its own
statistics, all local to your PC. See [modding/LUA_SCRIPTING.en.md](modding/LUA_SCRIPTING.en.md).

## Formats

The game asks for its original file names; a mod may give the same file in another format under the same name with
another extension, and the exe converts it:

- **Textures** (the game asks for `name.csi`): `name.csi`, `name.png` or `name.dds`.
  - Quality folders: a mod may ship `Textures.1\x.csi`, `Textures.2\x.csi` and `Textures.3\x.csi` (each replaces the
    file of the same folder; the game reads the folders of the chosen texture quality, the best first), and / or
    `Textures\x.csi` (stands in for all three; a file in the quality folder itself wins over it). A mod's texture is
    used whatever the quality setting: when the mod has it only in another quality folder than the one preferred,
    that one is taken over the game's own.
  - The language folder's pictures (`Language\English\logoRC_Main.csi`, the menu logos and the race messages) are
    replaced the same way under the language's folder name.
  - A mod's own `.csi` is read leniently: any size; a header that names more mip levels than the file holds (as
    some tools write when they enlarge a picture: the header of the original with 8 levels, the file with only the
    first) gets the missing levels made (ARGB8888 files) or is read with the levels it has (other formats); a mip
    count of 0 counts as 1. A `.csi` that does not even hold its first level is refused (logged).
  - PNG through the Windows Imaging Component (built into Windows); 8 / 16-bit, palette, grey, with or without alpha.
  - DDS: BC1 (DXT1), BC2 (DXT2/3), BC3 (DXT4/5), BC4 (ATI1), BC5 (ATI2), BC7 (DX10 header), and uncompressed
    RGBA / RGB / BGRA / 565 / 1555 / 4444 / luminance / alpha. Mip levels are used as they are in the file; missing
    ones are made (2 x 2 average). BC4 is shown grey, BC5 as red / green. sRGB formats are taken as plain values.
  - Cube textures (the car paint's reflection `cubemap_racer`): the game reads `cubemap_racer.csi` and its six faces
    `cubemap_racer.1.csi` .. `.6.csi` (+X, -X, +Y, -Y, +Z, -Z). One cube-map DDS `cubemap_racer.dds` with all six
    faces replaces all seven files. If you replace them one by one, every face must have the size of
    `cubemap_racer.csi`.
- **Sounds and music** (the game asks for `.au` / `.wav` sound effects and `.mp3` music): any of `.au`, `.wav`,
  `.mp3`, `.ogg` stands in for any other.
  - WAV: PCM 8 / 16 / 24 / 32 bit, float 32 / 64 bit, WAVE_FORMAT_EXTENSIBLE, other WAV codecs through Media
    Foundation; `.au`: the game's own (a RIFF WAVE with an .au name) or a Sun / NeXT .au (mu-law, A-law, PCM, float);
    MP3 (and other formats Windows decodes) through Media Foundation; OGG Vorbis through stb_vorbis.
  - Any length, any sample rate, any number of channels. Sound effects are converted to 16-bit PCM (8 / 16-bit mono
    or stereo PCM stays exactly as it is); more than two channels are mixed down to stereo; a rate outside 100 ..
    200000 Hz is resampled to 48000 Hz. Music in a format DirectShow does not play by itself (.ogg, .au), or inside a
    zip, is written to a temporary .wav / copy in `%TEMP%\RcCarsRe_mods_<process id>\`, deleted when the game exits.

## When a mod's file fails

Whenever a mod's file cannot be opened, read, unpacked or decoded (a texture, a sound, a music track, a settings or
text file), the game reads its own original file instead and logs the reason once (`Mods: <mod>: <file> can't be
decoded (...); the game's own file is used`); the file is not offered again until the mods are applied anew. A texture
is never left missing because of a mod, and with mods on a missing interface texture no longer stops the start on the
loading screen (it is logged and the menus go on). Files whose contents the game itself cannot check (a level `.sb`
that is damaged inside, a script with wrong values) are still read as the mod gives them.

## Sizes

There are no size limits of the game's own: a 4096 x 4096 texture can replace a 256 x 256 one and is used at its
own size, at every texture quality (`TexQual`, `Textures.1 / .2 / .3`: a mod's texture wins in every quality
folder). Textures need not be square or a power of two. The limit is Direct3D 11's: 16384 texels per side. A texture
gets at most 10 mip levels (the .csi format's limit), which goes down to 1 / 512 of the size: plenty for sampling.
Memory: a 4096 x 4096 texture takes about 85 MB while it loads and 85 MB of video memory.

Things that keep their meaning in pixels: the font pages (`Language\...` Smash fonts and the cockpit font) are cut
into letter cells of a fixed pixel size, so a font page must keep the original's size and layout. Some pictures are
also read pixel by pixel by the game's code (the levels' light maps, the racers' face pictures in `Faces` /
`FacesSys`): for those, other sizes have not been tested; keep the original size to be safe.

## Load order

The load order is a list whose **top is the most important mod**: if two mods have the same file (in any of its
formats), the file of the mod nearer the top is used. Inside one mod, the file with the requested extension wins over
its other formats.

1. `[Modern] ModOrder=A,B,C` (optional): these mods are on top, in this order: `A` wins over `B`, `B` over `C`.
   (Changed 2026-11-15: before, a later name won.)
2. The mods ModOrder does not name come below them, sorted by name (not case sensitive; the first by name wins among
   them). A folder and a zip of the same name: the folder comes first.
3. `[Modern] ModsDisabled=A,B` (optional): these mods are not loaded. `A` names the folder and the zip named A,
   `A.zip` only the zip, `A\` only the folder (the same forms work in ModOrder).
4. A mod of the same name in both mods folders (next to the exe and in the game folder) is taken once, the one next
   to the exe.

## The Mods screen

With `[Modern] ModsMenu=1` (the default) the main menu's "Demo play" item (the demo race is not rebuilt yet) is
**Mods** (Modok / Моды / Mody in the game's language). The screen lists every mod found, loaded or not, in the load
order (the top wins), with its number of files, how many of the game's files it replaces and a red `!` when some of
its files cannot be decoded (the details of the chosen mod are shown under the list; the reasons are in
`game_dbg.log`). On the first row, **Mods** switches the whole mod support (`[Modern] Mods`).

- Up / Down (or the mouse) choose a mod, PgUp / PgDn scroll a page; Left / Right, Enter or Space (the pad's A)
  switch it on or off;
- **Move up** / **Move down** (the menu buttons on the right) move the chosen mod in the list;
- **Refresh** lists both mods folders again: mods added since appear at the bottom of the list, switched on; mods
  removed disappear; every mod's counts are made again. The order and the switches you have not applied yet are kept.
  Nothing is loaded by Refresh: that is Apply's job;
- **Apply** writes `Mods`, `ModOrder` (every mod, the top first) and `ModsDisabled` into `RcCarsRe.ini` (when they
  changed), shows "Applying mods...", loads the mods in the new way at once and tells "Mods applied", then returns to
  the main menu. Apply without a change loads the mods' files again too (use it after editing a mod's files);
  **Main menu** (or Esc / the pad's B) drops the changes.

The screen writes only `RcCarsRe.ini`, never the mods folders or the game's folders.

### What Apply reloads at once (no restart)

- every texture read from the texture folders and the language folder (menus, logos, buttons, car skins, the
  `cubemap_racer` faces, the interface's pictures), the Smash fonts' pages and the racers' faces (`FacesSys`, `Faces`);
- the sound effects (`Sound\*`, also the menus' own sounds) and the tables `snd.ini` / `chn.ini`;
- the music: every track's file is looked up again (a mod's MP3 / OGG / WAV in place of a track) and the menus' music
  starts again;
- the slider files `Settings\*` (read again when next used; your own settings in the Options pages live in
  `RCCars.crs` and stay as they are);
- the language table `Language\Game\<language>.tbl` (the main menu's texts at once, the other screens when opened);
- `Scripts\championship.ini` and `Scripts\AIlayouts.ini`.

Everything of a race (levels, cars, their `.sb`, AI paths, `CarProfiles`, `Profiles`, `UPGRADES.ini`, level scripts)
is read when a race loads, so the next race takes the mods' files.

### What needs a restart

Files that the game reads only at its start: `Config.gm`, `Autoexec.gm` (and any `*.gm`: the folders, the variables,
the music's track list), the scene databases `RCCars.sb`, `Interface.sb` and `RaceTextures.sb` (their objects, the main
menu's cars, their embedded pictures, the interface's list of textures and its sound channels) and `Splines\`. When a
mod changes one of these, Apply says so ("Some files need a restart") and `game_dbg.log` names the files. Pictures
embedded in a database (`.sb`) keep coming from the database, as at the start. The intro videos play at the start
only. The language's folder (`Language\<name>\`, from string 2 of the table) stays the start's.

## What cannot be modded

- Player saves (`Players\`, every `*.scp`), the ghost records (`GhostRecords\`) and the settings store `RCCars.crs`
  (`RCCars.crs.bak`): the game writes these, so a mod's copy is ignored (and logged).
- Files outside the game folder (an absolute path in `Config.gm`), the exe and its DLLs, `RcCarsRe.ini`.
- Zip archives: only "stored" and "deflate" entries, no encryption, no ZIP64 (archives over 4 GB / 65535 files).
- The level files' embedded textures are read from the `.sb` file itself: replace the whole `.sb`, or the textures the
  levels name, which are looked up in the `Textures.*` folders like every other texture.

## The log

`game_dbg.log` next to the exe lists at the start: every mod found (zip or folder, its number of files), every file
and what it replaces (`Mods: BetterSkins: Textures\car_askin11.png replaces textures.1\car_askin11.csi`), new files,
files hidden by a later mod, ignored files, and files that cannot be decoded (with the reason; the game's own file is
used for those), then a summary. Conversions are logged when the game loads the file (`decoded (PNG 2048x2048)`,
`converted to a ...-byte WAVE`).

Nothing is ever written into the `mods` folder or the game's folders.

## Credits and licences

- `third_party\stb\stb_vorbis.c` v1.24: Ogg Vorbis decoder by Sean Barrett and contributors, public domain (or MIT,
  at your choice). Built unchanged as its own unit (`src\sound\oggdec.c`).
- `third_party\openxr` 1.1.65: the Khronos OpenXR loader (`openxr_loader.dll` / `.lib`) and headers, Copyright The
  Khronos Group Inc., Apache-2.0 OR MIT (the NuGet package OpenXR.Loader). Used unchanged for the optional VR mode
  (`src\modern\vr.c`), delay-loaded; the DLL is shipped next to the exe.
- `third_party\lua` 5.4.9: Lua.org, PUC-Rio, MIT (see [modding/LUA_LICENSE.txt](modding/LUA_LICENSE.txt)). Built
  unchanged for the mod scripts.
- DualSense haptics over Bluetooth (`PadHaptics`): the protocol knowledge comes from SAxense by egormanga / Sdore
  (MPL-2.0, https://github.com/egormanga/SAxense, https://apps.sdore.me/SAxense), the first public description of it;
  the report layout is our own implementation (no SAxense code in the tree). The USB channel layout follows the facts
  shown by streetpea / chiaki-ng; controllers.fandom.com and psdevwiki were the references for the pads' reports.
- Everything else of the mod support (zip inflate, DDS / BC7 decoders, the converters) is the rebuild's own code;
  PNG decoding (WIC) and MP3 decoding (Media Foundation) are Windows' own components.
