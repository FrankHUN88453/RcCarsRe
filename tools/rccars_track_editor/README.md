# RC Cars Track Editor (Blender add-on)

Version 0.1.3, for Blender 4.2 or newer (tested with 5.3). It reads your own RC Cars installation; it contains no
game data.

## Install

Blender > Edit > Preferences > Get Extensions > the menu at the top right > *Install from Disk...* >
`rccars_track_editor-0.1.3.zip`. Then in the add-on's preferences (or in the 3D View's sidebar, tab **RC Cars**):

- **Game folder**: the RC Cars folder - the DVD install (with `RCCarsDB`, `Textures.1 .. 3`) or the Steam release
  (with `RCCars.pack`).
- **Mods folder** (optional): where your mods are when it is not `<game folder>\mods` (the `mods` folder next to
  `RcCarsRe.exe`).
- **Scan game folder**: reads the base game and the mods. When the **extension** mod is installed (a
  `mods\extension` folder or `mods\extension.zip`) its assets are offered too.

## Asset browser

3D View > sidebar (N) > **RC Cars** > *Asset browser*: choose a category, pick an asset (the list has a search
field), **Import**.

| Category | What | Needs the extension |
|---|---|---|
| Tracks | the game's 10 levels, imported whole (collision walls and the sky / clouds in hidden collections) | no |
| Props | cans, balls, buckets, cones, bottles .. (`stone.sb`) | no |
| Road cars | the traffic vehicles (`Roadcar.sb`) | no |
| Characters | people and animals (`AIChars.sb`, `people.sb`) | no |
| Cars | the racing cars (`Car.sb`) | no |
| PS2 tracks | the extension's 9 PS2 race levels and Fire Starter | yes |
| PS2 props | the PS2 props, the karts, the kid, the bugs | yes |
| PS2 cars | the PS2 cars and bodies | yes |

A model comes in at the 3D cursor under an empty named after it; a track in a collection of its own. Textures are
the game's (a mod's PNG / DDS before the game's `.csi`), packed into the .blend. A track's baked light comes too:
its light maps (the faces' second layer `LM_1`, a second UV map of that name; the level's own light map textures,
named after the level) or, on the PS2 levels, its vertex colours (the colour attribute `Col`). Such a material is
drawn as the game draws it: texture x light map (x vertex colour), unlit (an Emission shader) - so the track looks
the same in Material Preview and in a render with no lights in the scene. The water (the objects with "more" in
their name, which the game moves and waves) comes at the height the game draws it - its slider file's offset added
(the object moved: custom properties `rc_water`, `rc_water_offset`) - and of its overlapping levels of detail only the
finest is shown (the others in the hidden collection "water, coarser levels"). Coordinates: Blender (x, y, z) =
game (-x, z, y), 1 unit = 1 m.

## Asset library: model and texture browser, drag & drop

The sidebar's *Asset browser* box > **Build asset library** (once, after *Scan*; again after a new mod) turns the
game's assets into a Blender asset library named **RC Cars** (in the add-on's own user folder: `rc_models.blend`,
`rc_textures.blend`, a catalog file, previews). The base game's models are about 80, the textures about 1700 with
the extension; building them takes a few minutes.

Open an Asset Browser editor (any area's editor type > *Asset Browser*), choose the library **RC Cars**:

- **Models** (Cars, Characters, Props, Road cars, and with the extension: Extension cars, Extension props): drag one
  into the 3D View; it lands on the surface under the mouse (the track's ground), as one object "RC <name>".
- **Textures** (Game, and with the extension: Extension > Cars / Props / Tracks > <level>): a texture is a material
  "RC <name>" (the image with its alpha). Drag it onto any mesh (a shape you made, a track part): the mesh gets
  that material. Use UV Editing to fit it.

## NPC paths (the opponents)

An opponent drives a recorded path: `CarProfiles\<folder>\<name>.dat`, replayed frame by frame (every 0.01 s:
place, rotation, speed, springs, steering). The track's AI layout script names the paths and the cars.

- **New opponent path**: a closed curve around the 3D cursor. Move its points along the track (Edit Mode); add
  points with E / subdivide. **The first point is the car's place on the starting grid** (behind the start line);
  the path is a closed lap back to it.
- **Player start**: an arrow empty; the arrow is the car's forward (turn it about Z).
- **Import paths**: all paths of a `CarProfiles` folder as curves (the game's or a mod's), one lap from the grid
  place, and its `start.dat` as the player start. The points' radius holds the recorded speed relative to the path's
  speed.
- Per path (select it): **File name** (`<name>.dat`), **Car** (Overkill / Buggy / Warhammer), **Driver**, the races
  it drives in (Easy / Normal / Hard), **Speed** (m/s). A point's radius (Alt+S in Edit Mode) scales the speed at
  that point (1 = the path's speed): slow down before tight turns.
- **Export to mod**: writes into `<mods folder>\<Mod>\`:
  - `CarProfiles\<Profiles folder>\<name>.dat` for every path, and `start.dat`;
  - `Scripts\<Profiles folder>_ai.ini` (when *Write the AI layout script* is on): an AI layout with one `AIRace1`
    section naming up to 5 opponents (the head of it - the car codes and the drivers - is copied from the game's
    `Scripts\AIlayouts.ini`).

  *Ride height*: how high over the drawn path the car's middle goes (0.18 m: draw the path on the ground).

To change a track's opponents, use its own profiles folder name and the same file names: a mod's file replaces the
game's file of the same path (e.g. the extension's tracks: `CarProfiles\cuba\buggy1.dat`). For a mod's new track,
`rc.registerTrack{..., ai = "<folder>_ai.ini"}` takes the exported script.

What is generated: the place along the curve, the rotation from the curve's direction and slope, the speed, the
chassis' usual spring lengths and the steering from the curvature; the game's own recorded paths also hold the car's
small body movements, which a drawn path does not have.

## Track export (your own track)

3D View > sidebar > **RC Cars** > *Track export*: any scene becomes a track of a mod - model it, import an FBX / OBJ
(scaled to the cars: 1 unit = 1 m, an RC car is about 0.4 m long), drag props and textures from the asset library.

- **What goes in**: every visible mesh object (modifiers applied), except the opponents' paths and the helpers.
  Per object **Collision** (on: the cars drive on it and hit it; off: drawn only). Per material its image (the
  Image Texture node on the Base Color); a material without one gets a small picture of its colour; a material that
  uses its alpha is drawn see-through. Vertex colours (the active colour attribute) are the baked light; without
  them the faces are lit fully. A game texture (an image named `rc_<name>` by the importer or the library) is
  referenced by its name, every other image is written as a PNG.
- **Checkpoints**: *Add checkpoint* puts a numbered checkpoint at the 3D cursor; 1 is the start / finish line, then
  in order around the lap; at least 2, up to 256 (RcCarsRe 0.2.0; the original game takes 8).
  Each shows what the game shows: its marker on the ground (the game's `icon_start` / `icon_chp_1`) and the hologram
  arrow over it (red at the start / finish line, green at the others; in the game it stands over the next checkpoint
  and blinks, here its glow pulses when the animation plays). Turn a checkpoint about Z to turn its marker;
  *Refresh checkpoints* makes the markers again (after renumbering, or in an older scene). The export writes each
  marker into the level (a mesh `..._ACP<n>`), so the game lights them as on its own tracks.
  Put them in the middle of the way: **a car passes a checkpoint only within 1.6 m of its centre** (an opponent
  within 2.8 m) - the export warns when an opponent's path misses one.
- **Player start**: the NPC panel's *Player start* arrow (needed).
- **Sky**: an equirectangular picture - `.hdr` or `.exr` (high dynamic range: the game picks the exposure itself;
  EXR with ZIP, ZIPS, RLE or no compression), or `.png` / `.dds`. It goes on a dome of the given radius around the
  track. The eye button shows it as the scene's world in Blender, mapped the same way.
- **Level** (the file name and the track's id: small letters, digits, `_`, not one of the game's levels), **Name**,
  **Description** (`\n` breaks a line), **Mod** (the mod folder).
- **Export track to mod** writes into `<mods folder>\<Mod>\`:
  - `RCCarsDB\<level>.sb`: the level, built on a copy of the game's `urban_1.sb` read from your install (its
    meshes, collision grid, checkpoints and start replaced; its people, sounds and props left out). The collision
    grid has the game's own resolution (0.5 x 0.9 x 0.5 m voxels); the collidable meshes are cut into square tiles
    (8 m and up), because the grid keeps a bit per face of each mesh in every voxel the mesh reaches;
  - `Textures\<level>_<image>.png` and `Textures\sky_<level>.hdr / .exr / ..`;
  - `scripts	rack_<level>.lua`: `rc.registerTrack{...}` - the game runs every `.lua` of a mod's `scripts` folder,
    so the track is on the Quick race page at the next start;
  - when the scene has opponents' paths: `CarProfiles\<level>\*.dat`, `start.dat` and `Scripts\<level>_ai.ini`.

The track's picture on the Quick race page and its map on the race screen are not made yet (the first track's
picture is shown); they can be added by hand in the Lua file (`picture =`, `map =`, see LUA_SCRIPTING).

## Changes

- **0.1.3**: a finer collision grid, as the game's own levels have: 0.5 x 0.9 x 0.5 m voxels (were 1 x 1.5 x 1 m);
  the collidable meshes cut into 8 m tiles and more meshes allowed (up to 1200, beyond the template's room), so the
  grid's face bits stay small; the voxels' counts a byte each when they fit. A very large track (over 24 million
  voxels) gets wider cells instead of an error.
- **0.1.2**: an imported track keeps its baked light: the light maps (`LM_1`) of the PC levels and the vertex
  colours of the PS2 levels, multiplied onto the textures as in the game.
  The water: imported at the height the game draws it (its `Settings\WLOD_<level>_<object>` offset), only its
  finest level of detail shown; exported again as the game's water (named after its object, at its rest height,
  its settings file copied under the new level's name) - it stood 0.37 m too high on beach_1 before. An imported
  track's checkpoint markers (`..._ACP<n>`) are left out of the export (the checkpoints make their own).
- **0.1.1**: with the Steam release (`RCCars.pack`) the textures were not loaded - the imported tracks and models
  had no textures and the asset library none either: the pack's textures are XOR-encrypted, as the game reads them
  they are now decrypted.
- 0.1.0: the first version.

## Not in this version

- Props as game objects: a prop placed in the scene is exported as part of the track's geometry (it stands still),
  not as the game's pushable object; water surfaces, light maps and the game's special materials are not made.
- The PS2 levels hold every face twice (once each way round); the importer keeps one and draws those meshes
  from both sides (their materials end in `_2s`, backface culling off).
- The game's special materials (water waves, blending modes) and the second texture layers (`BAS2` blended by
  `ALP1`: some ground patches) are left out of the imported materials. A track exported again keeps its vertex
  colours but not its light maps.
