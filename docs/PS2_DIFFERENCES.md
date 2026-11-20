# RC Cars (PC) and Smash Cars (PS2): what differs

*Other languages: [Magyar](PS2_DIFFERENCES.hu.md), [Русский](PS2_DIFFERENCES.ru.md), [Polski](PS2_DIFFERENCES.pl.md)*

The PlayStation 2 game **Smash Cars** (2003) is the console version of the PC game **RC Cars**. This page lists
the differences found while the PS2 game's cars were being brought into the rebuilt PC game as a mod.

**How this was found.** The PC game's files were compared with the files of the European PS2 disc (SLES-51800):
its models, textures, sound banks, settings records, and parts of its program, which still has its function
names. The PS2 game itself was not played for this, so anything that only shows while playing (menus, game
modes, rules, difficulty) is not covered. Where something is a reading and not a certainty, it says so.

## At a glance

| | PC (RC Cars) | PS2 (Smash Cars) |
|---|---|---|
| Cars | 3: Overkill, Buggy, Warhammer | 13: four chassis with three bodies each, plus the jet car CCCP |
| Paint jobs | several per car | 3 per body, 8 for CCCP |
| Tracks | 10 (beach 1-4, country 1-4, urban 1-2) | 13 levels |
| Engine sounds | three sets, one per car, 44.1 kHz | one set for every car, 22 kHz, shorter recordings |
| Music | MP3 files | 7 tracks |
| Driving in the air | none | air control with trick scores and a slow-motion "Matrix mode" |
| Jets | none | CCCP steers and pushes itself with jets while in the air |
| Texture detail | higher resolution, full colour | 256-colour textures, 64 to 256 pixels |

## Cars

The PS2 game builds twelve of its cars from four chassis and three bodies each; the thirteenth has its own.
Three of the chassis are the PC game's three cars: the same suspension rig, measured to within a millimetre.

| Chassis | PC car | PS2 bodies |
|---|---|---|
| Over | Overkill | Road Rage, Redneck, Beatle |
| Buggy | Buggy | Tornado, HotShot, Razor |
| Hummer | Warhammer | Warhammer, Skull Tank, Rockarolla |
| Half | not in the PC game | Sting, Flashback, Blazer |
| Super | not in the PC game | CCCP (three wheels, two jets) |

The Half is built like the Buggy (independent wheels) but with two springs per wheel and no upper arms.
The Super has one wide rear wheel.

## Physics

- Both games use the same physics. Each chassis has one settings record with the same values in the same order
  as the PC game's car settings (speeds, grip, springs, wheel sizes, collision shape, upgrades).
- The collision shapes of the three shared cars are identical in the two games. Their tuned values (top
  speed, grip, upgrade factors) are not: the PS2 game set them differently.
- The Half and the Super use the Overkill's collision shape.
- The PS2 record has a few extra values the PC game does not have; only the Super uses them (for its jets).

## CCCP's jets

Read from the PS2 program:

- The jets work **only in the air**. On the ground CCCP drives by its wheels like every other car.
- In the air the car flies where it points: its sideways drift is taken away at once.
- The accelerator pushes it forward along its level heading; reverse pushes back with half the force.
- Steering fires the jet of one side, which turns the car.
- The car is turned level while it flies, so it lands on its wheels.
- Its gravity gets weaker as it speeds up: about half the normal at a standstill, close to none at top speed, so it jumps high and far. (That the gravity follows the speed is in the program; which of the game's curves it uses was picked by its values, not traced.)

## Air tricks and "Matrix mode"

The PS2 program has an air-control system for all cars that the PC game does not have: the car can be turned in
the air, and turns and height are scored.

"Matrix mode" is a slow motion during jumps. Read from the PS2 program, it switches on when all of these hold:

- it is turned on in the options menu (a two-way setting of the player);
- a race is running, and it is not one of two race types (which ones was not identified);
- the player's car has had no wheel and no roof contact for more than 0.02 seconds;
- the car has been falling for 0.1 seconds, that is, just after the top of the jump.

Time then slows to one fifth within 0.2 seconds. When the car touches the ground, time returns to normal within
half a second. A minimum trick score for it exists in the settings but is set to 0.

## Sounds

- The PC game has three engine sound sets (one per car). The PS2 game has one set, used by every car, with the
  names of the PC's Overkill set; the recordings are shorter and of lower quality.
- No PS2 car has sounds of its own, CCCP included.
- The PS2 game has a few car sounds the PC game lacks: skidding on asphalt and on dirt, hitting grass, and
  `motor_flying_matrix`, the engine sound of flying in slow motion.
- Every PS2 level has its own sound bank; the level's animals and objects are in it.

## Models and textures

- The PS2 draws both sides of every surface, the PC only the front. Mirrored PS2 parts (the right side of a
  car) are stored inside out, so they have to be turned round for the PC.
- PS2 textures have 256 colours: body paints 256 x 256, chassis 128 x 128, tyres 64 x 64. The PC textures of the
  shared cars are larger and are not the same pictures.
- PS2 cars have separate, simple shadow models.

## Levels

Read from the PS2 tutorial level (a fenced yard, which the PC game does not have):

- **Light.** PC levels are lit by light maps, a second texture layer. PS2 levels have their light baked into a
  colour for every corner of the geometry.
- **Textures.** Most PS2 level textures have 256 colours; the see-through ones (fence nets, trees, signs on the
  ground) are 16-bit or 32-bit pictures.
- **Grass.** The PS2 game has a grass system the PC game lacks: thousands of small plants (about 2,600 in the
  tutorial yard), eight kinds cut from one picture. They sway, and they bend away under the cars.
- **Props.** The pushable things are the same kinds in both games: cans, balls, buckets, cones. The PS2 level
  stores each one's place and collision shape; it also has a helmet, which the PC game has no model for.
- **Checkpoints.** The PS2 level has a plain list of points; the PC level has marker objects.
- **Characters.** The tutorial yard has a boy riding a tricycle (an animated model with its own sound) and two
  karts with a driver, which drive their recorded loops (Kart.StartProfile).

## Files

| | PC | PS2 |
|---|---|---|
| Scenes and cars | `.sb` databases | `.S_A` ... model files, one `.SBF` index per level |
| Sounds | one file per sound | one `.MSB` bank per level |
| Music | MP3 | `TRACK1` - `TRACK7` |
| Videos | `Intro.dat` | three video files |

## In the rebuilt PC game

The mod `extension` adds the PS2 game to the rebuilt game: the PS2 tutorial yard as a track (in the main menu the "Tutorial" button with its intro and three tasks, switchable in the mod's config.ini) and the PS2 cars: Sting and CCCP as new cars with their own physics
values, the other eight bodies as extra bodies of the three PC cars and of Sting. Its Lua functions are described
in [modding/LUA_SCRIPTING.en.md](modding/LUA_SCRIPTING.en.md), section 6a. The converted cars are made from the
user's own PS2 disc and are not distributed.

The mod has its own `config.ini`: `[SlowMotion]` `SlowMotion=1` turns on the slow motion of Matrix mode in jumps (single
player), `Tutorial=1` shows the main menu's "Tutorial" button for the PS2 tutorial.

The tutorial level is converted into a PC level: its geometry, textures, baked light, checkpoints, the grass (it
sways and can be trampled), the props (the PS2's cans, balls, bucket, cone and helmet as models), the opponents,
the boy on the tricycle and the two karts on their PS2 paths, and the tutorial's three tasks with the PS2's time
limits and stunt scoring. The yard now also has its bugs (they walk and flee, as the PC game's spiders do; they do
not fly off as on the PS2), the litter on the ground, the boy's and the karts' own sounds (pedalling, the bell,
the kart engines) and the tasks' hints on a key (H or the pad's Back). As everything else, these are made from the
user's own PS2 disc and are not distributed.

Not brought over: the other PS2 tracks, the air-trick scoring outside the tutorial, the PS2 sounds other than the
tutorial yard's, the tutorial intro's short demo race and its rewards.
