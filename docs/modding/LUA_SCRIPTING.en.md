# Lua scripting for mods

**English** | [Magyar](LUA_SCRIPTING.hu.md) | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

RcCarsRe can run small Lua scripts that come with a mod. A script can read the race (track, laps, cars,
positions, lap times), react to events (a lap, a checkpoint, a hit, a jump, an overtake, the pause, the race end
...) and do local things: draw texts, pictures and boxes on the HUD, play sounds, move the camera, change the fog,
the sun and the lights, rumble the gamepad, write to the log and keep its own settings and statistics.
Scripts cannot change the race, the cars or the game's files, with one exception: the script of a game mode
(chapter 6, API 1.4) runs the rules of its own races (single player, and since API 1.5 network races too).

The language is [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT licence, see
[LUA_LICENSE.txt](LUA_LICENSE.txt)). This page describes API version **1.14**.

## 1. Overview

- Every enabled mod (folder or zip in a `mods` folder, see [MODDING.md](../MODDING.md)) can hold `.lua` files.
- Each mod gets its own Lua state. Mods cannot see each other's global variables.
- Mods are loaded in the Mods screen's order from the bottom up: the lowest-priority mod first, the top mod last.
- The game calls the script's global event functions (`onFrame`, `onLap`, ...) when they exist.
- Everything a script does is local to your computer: HUD, sound, camera, fog, lights, gamepad, log, its own files.
  Scripts send nothing over the network and do not affect other players in a network race; the one exception
  is a game mode's script on the host (`rc.mode.send`, chapter 6 "Network races").

## 2. File layout

```
mods\
  my_mod\                 (or my_mod.zip with the same content)
    main.lua              entry script (any *.lua in the mod's root)
    scripts\
      hud.lua             entry script (any *.lua directly in scripts\)
      lib\util.lua        not loaded by itself: load it with rc.include("scripts/lib/util.lua")
    sounds\ding.wav       the mod's own sound for rc.playSound("ding")
    textures\icon.png     the mod's own picture for rc.hudImage(..., "icon", ...)
```

- Entry scripts: every `*.lua` in the mod's root and directly in `scripts\`, loaded in name order.
- Files in deeper folders are loaded only by `rc.include`.
- Scripts and texts are UTF-8. Texts are converted to the game font's code page of the current language.

## 3. Enabling

In `RcCarsRe.ini` (next to `RcCarsRe.exe`), section `[Modern]`:

| Key | Values | Default | Meaning |
|---|---|---|---|
| `Mods` | 0 / 1 | 1 | the mods folders are read (needed for scripts) |
| `LuaScripts` | 0 / 1 | 1 | the mods' Lua scripts run |
| `LuaBudget` | 10000 .. 100000000 | 1000000 | Lua instructions one event call may run |

The Mods screen (main menu, "Mods") switches mods on and off. **Apply** reloads every script at once: the old
states are closed and the new mod set is loaded.

The gamepad functions also follow your own gamepad settings in the same section: `Rumble` (0 = no vibration),
`LightBar` (`off` = the light bar is never changed) and `AdaptiveTriggers` (0 = no trigger effects). A script
cannot switch on what you switched off.

## 4. Events

Define these as global functions. All are optional.

| Event | When |
|---|---|
| `onLoad()` | after the mod's entry scripts were loaded |
| `onMenu(name)` | the top screen changed: `main`, `options`, `quickrace`, `multiplayer`, `twoplayers`, `twosetup`, `players`, `newplayer`, `credits`, `ghost`, `garage`, `championship`, `champwin`, `mods`, `modsettings`, `pause`, `race`, `results`, `none`, `other` |
| `onRaceStart(info)` | at GO; `info` is the table of `rc.race()` |
| `onFrame(dt)` | every frame (menus too); `dt` = frame time in seconds |
| `onLap(car, lap, lapTime)` | a car finished lap number `lap` in `lapTime` seconds |
| `onCheckpoint(car, index)` | a car passed checkpoint `index` (1 = the start/finish line) |
| `onHit(car, strength)` | the game awarded a hit: 1 = "Hit!", 2 = "Great hit!" |
| `onWater(car)` | a car came into the water |
| `onRespawn(car)` | a car was put back on the track |
| `onObjectHit(car, name)` | (1.9) a car knocked a loose object of the level (a can, a ball, a bottle ...); `name` is the object's name in the level. Once per knock |
| `onRaceEnd(results)` | once per race, when the finish script starts (all players finished) |
| `onOptionChanged(key, value)` | an option was changed on the mod's Settings page |
| `onBoost(car, on)` | (1.1) a car's booster started (`true`) or stopped (`false`) firing |
| `onJump(car)` | (1.1) a racing car has been in the air for 0.25 s (small bumps do not count) |
| `onLand(car, airTime)` | (1.1) that car is on the ground again; `airTime` = seconds in the air |
| `onOvertake(car, otherCar, newPlace)` | (1.1) `car` took the place `newPlace` from `otherCar` (checked once a frame while racing) |
| `onCollision(car1, car2, strength, kind)` | (1.1) a contact: `kind` = `"car"` (two racers; `strength` = closing speed in km/h) or `"roadcar"` (a racer against a road car; `car2` is `nil`, `strength` = the racer's speed in km/h). One call per pair while the contact goes on (again after 0.5 s without contact) |
| `onDogAttack(car)` | (1.1) a dog starts its attack on `car`: it stops and barks at it (the game's dogs do not bite; hitting a dog is a "Great hit!", see `onHit`) |
| `onPause(kind)` | (1.1) the race was paused: `kind` = `"menu"` (the pause menu) or `"quick"` (the quick pause) |
| `onResume()` | (1.1) the race goes on after a pause |
| `onChat(name, text)` | (1.1) a network chat line arrived (your own lines too); `name` = the sender, `""` for server and game lines. Read only |
| `onCountdown(n)` | (1.1) the race's countdown, at the same moment as its numbers and beeps: `n` = 3, 2, 1, and 0 at GO |

`car` is the car's number, 1 .. `rc.race().cars`. `results` is a list in place order; each entry has `car`,
`place`, `finished`, `time`, `bestLap` (missing when none), `lap`, `name`.

## 5. API reference (`rc` table)

### Reading

| Function | Returns |
|---|---|
| `rc.version` | the API version string (`"1.14"`) |
| `rc.modName` | the mod's name |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = the HUD's race timer in seconds (-1 before GO). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (player 1 finished), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, raceTime, place, isPlayer, isAi, isGhost, player, finished, name}` or `nil`. `speed` in km/h; `player` = 1 / 2 for a player's car; `raceTime` = the car's time since GO (it stops when the car finishes); (1.8) `airTime` = seconds since a wheel of the car last touched the ground (0 on the ground) and `vy` = its vertical speed in m/s (negative while it falls); both are 0 for the opponents; (1.9) `dir` and `up` = the car's forward and up axes as `{x, y, z}`, `spin` = its angular velocity in rad/s about the world's axes (0 for the opponents) |
| `rc.player(n)` | the car table of player `n` (1 or 2, default 1), or `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: render size in pixels, the current screen name, VR on, split screen |
| `rc.formatTime(seconds, format)` | (1.1) a time as the game writes it: `"m:ss.hh"` like the HUD's timer (`0:15.89`), or with `format = "short"` `"m:ss"` |

Lap times work as in the game: `lap` is 0 until the car crosses the start/finish line for the first time, and
every lap time (also lap 1's) counts from a crossing of that line. So during lap 1 `lapTime` is smaller than
`rc.race().time` by the time the car needed from its grid place to the line. The game's lap banner, its
results and `onLap` use the same lap times.

### HUD (drawn this frame only: call them every frame from `onFrame`)

Coordinates are a virtual 800 x 600 screen stretched over the whole picture (in split screen over both views,
in VR on the HUD layer). Colours are `0xAARRGGBB`.

| Function | Meaning |
|---|---|
| `rc.hudText(x, y, text, color, size, align)` | text in the game font; `size` 1 = the HUD's text size (it follows UI scale and `HudScale`); `align` = `"left"` (default), `"center"`, `"right"` (x is the left edge, the centre or the right edge) |
| `rc.hudRect(x, y, w, h, color)` | a filled rectangle (default colour `0x80000000`) |
| `rc.hudImage(x, y, w, h, texture, color, u0, v0, u1, v1)` | a picture; `texture` is the mod's own file (the name as a path, also with `.png` / `.dds` / `.csi` and under `textures\`) or else a game texture of that name; uv default 0, 0, 1, 1 |

At most 512 HUD items per frame and 64 pictures per mod.

### Sound and log

| Function | Meaning |
|---|---|
| `rc.playSound(name, volume)` | plays once: the mod's own file (the name as a path, also with `.wav` / `.ogg` / `.mp3` / `.au` and under `sounds\` or `sound\`), else the game's sound of that name; `volume` 0 .. 1 (default 1, times the game's effects volume). Returns `true` when it plays |
| `rc.log(...)` / `print(...)` | a line in `game_dbg.log` (and the -dev console) |
| `rc.warn(...)` / `warn(...)` | a warning line (yellow on the -dev console) |

### Camera (1.1)

| Function | Meaning |
|---|---|
| `rc.camera{pos =, offset =, target =, car =, fov =, blend =}` | player 1's race camera is replaced until `rc.camera(nil)`. `pos = {x, y, z}`: the camera's place in the world; or `offset = {x, y, z}` with `car`: the place relative to that car in its own axes (x right, y up, z forward); without both the game's camera place stays. `target = {x, y, z}` or `car = i`: what it looks at (without both the game's direction stays). `fov` = vertical field of view in degrees, 10 .. 150 (the game's single view is about 64). `blend` = seconds to glide from the game's camera (0: at once) |
| `rc.camera(nil)` | back to the game's camera (gliding back over the same `blend` time) |
| `rc.cameraInfo()` | `{pos = {x, y, z}, dir = {x, y, z}, fov, override, blend}` of player 1's race camera now, or `nil` outside a race. `pos` / `dir` also have `.x .y .z`; `override` = a script camera is on, `blend` 0 .. 1 |

The camera override acts only in a race and only on player 1's view: in the split screen player 2's view keeps
the game's camera, and in VR the headset moves the camera, so the override is ignored there (one warning in the
log). The menus' cameras are never changed. Leaving the race and a mod reload switch the override off.

### Weather and mood (1.1)

These change only what your computer draws. Each one is switched off by its reset function, by passing `nil`,
automatically when the race ends (just before `onRaceEnd`, so a script may set a new mood there), when the race
is left and when the mods are reloaded. When several mods set the same effect, the last call wins.

| Function | Meaning |
|---|---|
| `rc.fog{color =, near =, far =, density =}` | the level's fog: `color` = `0xRRGGBB`; `density` per metre 0 .. 1 (the game's fog is exponential, its levels use 0.006 .. 0.026); `near` / `far` in metres: with them and without `density` the fog is linear from `near` to `far`. Missing fields keep the level's values. The fog shows only when the game's fog is on (Video options) |
| `rc.resetFog()` | the level's fog again (as `rc.fog(nil)`) |
| `rc.sun{dir = {x, y, z}}` or `rc.sun{elevation =, azimuth =}` | the sun's direction (towards the sun; angles in degrees, azimuth turning from +z towards +x): the realtime shadows (`Shadows=realtime`) and the cars' light |
| `rc.resetSun()` | the level's sun again |
| `rc.lights{intensity =, color =}` | the levels' lamps (`PointLights=1` only): `intensity` 0 .. 8 times their strength, `color` = `0xRRGGBB` instead of their own. Returns `true` when the point lights are on |
| `rc.resetLights()` | the lamps' own light again |
| `rc.water{color =, alpha =}` | the sea: `color` = `0xRRGGBB` tint, `alpha` 0 .. 1 times its transparency (with `WaterFx=1` the tint also colours the shallow water) |
| `rc.resetWater()` | the sea's own look again |

### Gamepad feedback (1.1)

`player` is 1 or 2 (default 1). The functions return `true` when a pad can show the effect now.

| Function | Meaning |
|---|---|
| `rc.rumble(strength, seconds, player)` | a vibration pulse: `strength` 0 .. 1 (times your `Rumble` setting), at most 3 seconds. Felt only while the player's car races, like the game's own rumble |
| `rc.lightBar(r, g, b, player)` | the DualSense / DualShock 4 light bar in this colour (0 .. 255 each) until `rc.lightBar(nil, player)`. It wins over the game's colour; with `LightBar=off` nothing changes |
| `rc.triggers{right =, left =, player =}` | DualSense adaptive triggers while the player's car races: each trigger `"off"` or `{mode = "resistance", start = 0 .. 1, force = 0 .. 1}` (a continuous resistance from `start` of the travel). Until `rc.triggers(nil, player)`; ignored with `AdaptiveTriggers=0` |
| `rc.padHaptics(name, player, volume)` | the sound (the mod's own file or the game's) on the DualSense's voice-coil haptics, over Bluetooth and USB: needs `PadHaptics=1` and `Rumble` above 0; not while the game is in the background or the race is paused. `volume` 0 .. 1, times `PadHapticsVolume`. A DualShock 4 has no voice coils |

A mod reload ends the script light bar and the trigger effects.

### Files of the own mod

| Function | Meaning |
|---|---|
| `rc.readFile(path)` | the file's bytes as a string, or `nil, message`. Only the script's own mod is read |
| `rc.readUserFile(suffix)` | (1.2) the player's own file `Saves\Mods\<mod>.<suffix>` next to `RcCarsRe.exe` (for example `"controls.ini"`: settings that survive mod updates), or `nil, message`. Only that folder and the mod's own name; `suffix`: letters, digits, `_ . -` |
| `rc.include(path)` | runs a `.lua` file of the own mod once and returns its result (later calls return the same result), like `require` |

### Settings

Stored in `Saves\Mods\<mod>.ini` next to `RcCarsRe.exe` (`<mod>.zip.ini` for a zip mod), section `[Settings]`.

| Function | Meaning |
|---|---|
| `rc.setting(key, default)` | the stored value, converted to the type of `default` (boolean, number, string); without a stored value `default`, or the option's default |
| `rc.setSetting(key, value)` | stores a boolean, number or string (`nil` deletes it); it writes the file at once, so do not call it every frame |
| `rc.options{ ... }` | declares the options of the mod's Settings page (below) |

Keys: letters, digits, `_`, `.`, `-`, at most 63 characters. Values: at most 1000 bytes, no line breaks.

### Statistics (1.1)

Kept per mod in `Saves\Mods\<mod>.stats.ini` next to `RcCarsRe.exe` (`<mod>.zip.stats.ini` for a zip mod),
apart from the settings and never in a player's save. Values are numbers or strings (at most 1000 bytes), at most
1000 keys per mod, keys as for the settings. The changes are kept in memory and written in one go when the race
ends, when the race is left, when the mods are reloaded and when the game exits, so the functions can be called
as often as needed.

| Function | Meaning |
|---|---|
| `rc.stats.get(key, default)` | the stored value, or `default` (or `nil`) |
| `rc.stats.set(key, value)` | stores a number or a string; `nil` deletes the key |
| `rc.stats.add(key, n)` | adds `n` (default 1) to a number (a missing key counts as 0) and returns the new value |

### Settings page

```lua
rc.options{
  {key = "showLap", type = "bool", label = "Show lap time", default = true},
  {key = "size", type = "slider", min = 0, max = 10, step = 1, default = 5, label = "Size"},
  {key = "mode", type = "enum", values = {"small", "big"}, default = "small", label = "Mode",
   labels = {"Small", "Big"}},
}
```

- `label` (and each of `labels`) is a string or a table by language: `{en = "...", hu = "...", ru = "...", pl = "..."}`.
- A loaded mod with options gets an active **Settings** button on the Mods screen. Its page uses the game's own
  menu widgets (switches, sliders, buttons); changes are stored at once and `onOptionChanged(key, value)` runs.
- `rc.setting(key)` returns the option's value; **Default values** on the page restores the defaults.

### Input, pause, HUD and screenshots (1.2)

These are the building blocks of a photo mode, a replay camera and similar tools. All of them act only on your
computer.

| Function | Meaning |
|---|---|
| `rc.input.key(name)` | `true` while the key is held. Names: letters `"A"` .. `"Z"`, digits, `"F1"` .. `"F24"`, `"Space"`, `"Enter"`, `"Esc"`, `"Tab"`, `"Backspace"`, `"Shift"`, `"Ctrl"`, `"Alt"`, `"Up"`, `"Down"`, `"Left"`, `"Right"`, `"PageUp"`, `"PageDown"`, `"Home"`, `"End"`, `"Insert"`, `"Delete"`, `"Plus"`, `"Minus"`, `"Comma"`, `"Period"`, `"MouseLeft"`, `"MouseRight"`, `"MouseMiddle"` |
| `rc.input.pressed(name)` | `true` in the frame the key went down |
| `rc.input.mouse()` | `{dx, dy, wheel, left, right, middle}`: the mouse's movement and wheel notches in this frame, its buttons |
| `rc.input.pad(player)` | `{lx, ly, rx, ry, lt, rt, kind, buttons = {..}, pressed = {..}}` or `nil` without a pad. Sticks -1 .. 1 (up positive), triggers 0 .. 1, `kind` = `"xinput"`, `"ds4"`, `"dualsense"`. Button names (each also in `pressed`, true in the frame it went down): `a` / `cross`, `b` / `circle`, `x` / `square`, `y` / `triangle`, `lb` / `l1`, `rb` / `r1`, `back` / `view` / `share` / `create` / `select`, `start` / `menu` / `options`, `ls` / `l3`, `rs` / `r3`, `guide` / `ps`, `touchpad`, `mute`; `buttons` also has the D-pad as `up`, `down`, `left`, `right` |
| `rc.input.capture(on)` | while on, the car's controls and the pause menu's Esc / Start do not get the keys and buttons: the script uses them (for example the sticks for a free camera) |
| `rc.pause(on)` | freezes the race like the pause menu (race clock, physics, AI, water, particles, animations, sounds) without opening a menu. Returns `false` in a network race |
| `rc.timeScale(s)` | slow motion, `s` 0.05 .. 1 (1 = normal). Returns `false` in a network race. For a full stop use `rc.pause` |
| `rc.hud(show)` | `false` hides the game's own HUD (cockpit, dials, arrow, map, racer list, messages, chat lines, ShowFps); the script's `rc.hudText` / `rc.hudImage` / `rc.hudRect` still draw |
| `rc.screenshot{hideScriptHud =, scale =}` | saves the next frame as a PNG in `Screenshots` next to `RcCarsRe.exe` and returns the file name. `hideScriptHud` (default `true`) leaves the script's own HUD items out of that frame. Only `scale = 1` (the frame as shown) is made |
| `rc.graphics{shadows =, reflections =}` | (1.3) switches `Shadows` / `Reflections` for this session: `"original"`, `"realtime"` or `"off"` each (missing fields stay). `rc.graphics()` returns `{shadows, reflections}` now. The ini is not written: the game goes back to its values at the race's end, the race's exit, a mod reload and a script error. The first switch to realtime makes the shadow maps / reflection cubes (a short stall, a few hundred MB of video memory); they are kept for later switches. Allowed in network races (only your picture changes) |

- `rc.camera{...}` also takes `roll = degrees` (positive clockwise), and it keeps working while the race is paused.
- The input is read only while the game's window is in front and no text field (a menu's edit box, the network
  chat line) is being typed in. Keyboard-only and pad-only both work.
- Not available (no cheap way in the renderer): depth of field, `scale = 2` screenshots, exposure / saturation.
  For the mood use `rc.fog`, `rc.sun`, `rc.lights` and `rc.water`.
- Safety: the pause, the hidden HUD, the input capture, the time scale and the camera are released by the game when
  the race ends, when the race is left, when the mods are reloaded and when a script has errors or is switched off,
  so a broken script can never leave the game frozen or without its HUD.

### Building a photo mode

The example mod `photo_mode` (in `docs/modding/examples/`) is a complete photo mode in one script. Its core:

```lua
local on, pos, yaw, pitch = false, nil, 0, 0

local function enter()
  local c = rc.cameraInfo()
  if not c or not rc.pause(true) then return end      -- no race camera, or a network race
  rc.hud(false)
  rc.input.capture(true)
  pos = {c.pos.x, c.pos.y, c.pos.z}
  yaw, pitch = math.atan(c.dir.x, c.dir.z), math.asin(c.dir.y)
  on = true
end

local function leave()
  rc.camera(nil); rc.hud(true); rc.input.capture(false); rc.pause(false)
  on = false
end

function onFrame(dt)
  if rc.input.pressed("P") then if on then leave() else enter() end return end
  if not on then return end
  if rc.input.pressed("Esc") then leave() return end
  local m = rc.input.mouse()
  yaw, pitch = yaw + m.dx * 0.003, math.max(-1.5, math.min(1.5, pitch - m.dy * 0.003))
  local fx, fy, fz = math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)
  local go = (rc.input.key("W") and 1 or 0) - (rc.input.key("S") and 1 or 0)
  pos = {pos[1] + fx * go * 6 * dt, pos[2] + fy * go * 6 * dt, pos[3] + fz * go * 6 * dt}
  rc.camera{pos = pos, target = {pos[1] + fx, pos[2] + fy, pos[3] + fz}}
  if rc.input.pressed("F12") then rc.screenshot{hideScriptHud = true}; rc.stats.add("photos") end
  rc.hudText(400, 580, "F12 photo, P leave", 0xffffffff, 0.7, "center")
end
```

The full example flies freely: W / S along the view (up and down too), A / D sideways (level, roll does not turn
it), Shift / Ctrl straight up / down, Q / E roll, Space faster, the mouse looks, the wheel zooms, F12 takes a photo,
P / Esc leaves; on a pad the sticks, the triggers (down / up), the bumpers (roll), the D-pad (zoom), A (photo) and
Back / View / Share / Create (on / off). Without input the camera stands still: the sticks and triggers go through
dead zones (0.2 / 0.1) and there is no inertia.

Its bindings are in a plain text file of the mod, `photo_mode\controls.ini`, one `action=key` per line with a
comment (`[Keyboard]` and `[Pad]` sections, the dead zones as `deadzone=` / `triggerDeadzone=`). The script reads it
with `rc.readFile` when it loads (so on Apply and on the -dev hot reload too: a changed `.ini` / `.txt` of a folder
mod reloads its scripts) and each time the photo mode is switched on; an unknown name gives a yellow warning and the
default stays for that action. Key names: `A` .. `Z`, `0` .. `9`, `F1` .. `F12`, `Ctrl`, `Shift`, `Alt`, `Space`,
`Tab`, `Enter`, `Esc`, `Up`, `Down`, `Left`, `Right`, `MouseLeft`, `MouseRight`, `MouseMiddle`, `WheelUp`,
`WheelDown`, `None`; pad names as in `rc.input.pad`. A player's own copy in `Saves\Mods\photo_mode.controls.ini`
next to `RcCarsRe.exe` (read with `rc.readUserFile("controls.ini")`) wins over it and survives mod updates.

In photo mode R (pad Y / Triangle) switches realtime shadows and reflections on and off (`realtimeGfx=` in controls.ini); leaving restores the ini's values.

## 6. Game modes (1.4)

A mod can add a **game mode**: its own rules on a normal track, with the player against AI cars. A mod that calls
`rc.registerMode` in its `onLoad` is listed in the Quick race screen's **Mode** row (Race summary page, under the
opponents' skill): *Race* (the normal race) and every registered mode, by its name in the game's language. The
mode's race loads the chosen track as usual; the number of AI opponents comes from the skill (easy 3, normal 4,
hard 5), at most the mode's `maxCars`.

### Texts in four languages

Every text of the API can be a string or a language table `{en = "...", hu = "...", ru = "...", pl = "..."}`. The
game's current language picks the text (the same as the menus' language, `[Modern] Language`); without an entry
for it, or in another language, the English one is used, and without that the first one there is.

| Function | Meaning |
|---|---|
| `rc.lang()` | the game's language: `"en"`, `"hu"`, `"ru"`, `"pl"`, or the language folder's name in lower case |
| `rc.text(t)` | the text of a language table `t` in the current language (a string comes back as it is) |

### Registering a mode

```lua
rc.registerMode{
  id = "zombies",                                   -- letters, digits, _ . - (unique)
  name = {en = "Zombies", hu = "Zombik", ru = "Зомби", pl = "Zombie"},
  description = {en = "...", hu = "...", ru = "...", pl = "..."},
  minCars = 2, maxCars = 6,                          -- 1 .. 6
  checkpoints = false,                               -- no checkpoints, GPS arrow, laps or finish line
  laps = false,                                      -- no lap counter (default: as checkpoints)
  ai = "script",                                     -- "script": the AI cars obey rc.ai; "race": they race
  respawn = false,                                   -- the game puts no car back (default true)
  hidden = true,                                     -- (1.12) not in the Quick race's Mode row: only rc.startRace{mode =} starts it
  hud = {racerList = false, place = false, lap = false, wrongWay = false},   -- the HUD parts the mode hides
}
```

With `checkpoints = false` the race has no checkpoints, no GPS arrow, no wrong-way sign, no lap counting and no
finish line; the place picture is hidden. Only the start (3, 2, 1, GO) is the game's; after GO the mode's script
runs the race and ends it with `rc.mode.finish`. A car that falls into the water or off the track is put back on
the nearest point of the AI cars' driving lines (with `respawn = false` the mode decides instead).

### Mode events (only to the mode's own mod)

| Event | When |
|---|---|
| `onModeLoad(info)` | the mode's race came up (from its first frame, before the start's countdown), and again at *Race again*. Set the mode's look here (fog, ambience) |
| `onModeStart(info)` | at GO. `info` = the `rc.race()` table plus `id`, `player` (the player's car), `minCars`, `maxCars` |
| `onModeFrame(dt)` | every frame while the race runs (not while paused, not after the finish) |
| `onModeTimer()` | the timer of `rc.mode.timer` reached 0 |
| `onModeEnd()` | once after `rc.mode.finish` |
| `onRespawnBlocked(car, reason)` | with `respawn = false`: the game would have put the car back. `reason` = `"water"` (2 s under water), `"bounds"` (out of the level), `"zone"` (a fall-off volume), `"key"` (the player's Reset key), `"flip"` (a car on its roof could not be set upright), `"stuck"` (the physics found it stuck), `"timed"`, `"aiemu"`. At most once a second per car |

The normal events (`onRaceStart`, `onCollision`, `onFrame`, ...) keep coming to every mod.

### Mode control (only the running mode's own script may call these)

| Function | Meaning |
|---|---|
| `rc.mode.countdown(seconds, text)` | a big countdown in the middle of the screen (the cockpit's number font), then `text` for 1.5 s |
| `rc.mode.message(text, seconds, color)` | a message under the middle of the screen (default 3 s, white; `0xRRGGBB`) |
| `rc.mode.timer(seconds)` | the HUD's top timer shows the remaining time (red in its last 10 s); `nil` / 0 switches it off |
| `rc.mode.timeLeft()` | the remaining seconds, `nil` without a timer |
| `rc.mode.clock()` | seconds since the mode's start (GO), without the pauses |
| `rc.mode.active()` | the running mode's id, `nil` in a normal race (any mod may call it) |
| `rc.mode.freeze(car, on)` | holds a car (no throttle, the brake), e.g. for a head start |
| `rc.mode.listText(car, text, color)` | the HUD's racer list shows this text instead of the gap (`nil`: the gap again) |
| `rc.mode.finish(results, title, options)` | ends the race: every car finishes, then the game's finish and its results page with these rows. `results` = `{{car =, place =, text =}, ...}`; `title` (default: the mode's name) heads the text column. `options = {resultsDelay = s}` holds the results page that long (an end shot), `rc.mode.showResults()` lets it come at once |
| `rc.mode.holdEnd{seconds =, skippable =}` | after `rc.mode.finish`: the game's results page comes `seconds` (default 20, at most 60) later, for an end shot. `skippable = false` (the default): the player's keys and buttons do nothing meanwhile and the pause menu does not open (closing the window still quits). A script error or a reload ends the hold at once |
| `rc.mode.showResults()` | the held results page now |
| `rc.mode.holdStart(on)` | (1.13) while `on`, the start's countdown (3, 2, 1, GO) waits, for an intro (camera shots, texts) before the race; the level's road cars already drive meanwhile. Off again with `false`, by itself after 90 s of game frames, when the race is left, or when the mode's race comes up again (`onModeLoad` and *Race again* reset it: set it in `onModeLoad` or later). Single player only (ignored in network races). Returns the new state; the log shows "Game modes: the start's countdown held / released" |
| `rc.mode.respawn(on)` | the game's car resets on / off for this race (the start value is `registerMode`'s `respawn`). Off, a car on its side or roof is still set upright where it is after 2 s (the player's too), but never moved elsewhere |
| `rc.mode.respawnCar(car)` | the mode puts the car back on the nearest point of the AI driving lines (works with `respawn = false` too) |
| `rc.setCarTeam(car, n)` | the car's team (any number; `rc.car(i).team`) |
| `rc.setCar(car, {model =, paint =, physics =})` | the car turns into another RC car of the game: `model` = `"Overkill"`, `"Buggy"` or `"Warhammer"`, `paint` = 1 .. 4 (the garage's paints), `physics` = `true` (default: it drives with that car's physics profile too) or `false` (only the look). `rc.setCar(car, nil)`: its own car again. The car keeps its upgrades, its sounds and its motion |
| `rc.carName(car)` | the racer's name |
| `rc.distance(car1, car2)` | metres between two cars |

An intro before the start (1.13):

```lua
function onModeLoad(info) rc.mode.holdStart(true) end   -- then rc.mode.holdStart(false) when the intro ends
```

`rc.car(i)` also has (1.4) `team`, `model` (`""` its own), `paint` (0 its own), `frozen` and `contacts`: the cars
it touched this frame (`{2, 4}`).

### AI orders (`ai = "script"`)

`rc.ai(car, order)` drives an AI car (a player's car is never driven; returns `false` then). The AI drives on a
road graph made of the track's AI driving lines (with the points beside water and edges marked: it slows there
and keeps off that side), finds its ways with shortest paths, reverses and turns when stuck, and is put back on
the graph when it stays stuck or in deep water.

| Order | Meaning |
|---|---|
| `{mode = "chase", target = car}` | drives into that car: along the road while it is far, straight at it (a little ahead by its speed) within 8 m |
| `{mode = "chase", targets = {cars}}` | the same for the nearest of these cars by the road; it changes target only when another is clearly nearer (default: every car of another team) |
| `{mode = "flee", from = {cars}, caution = m}` | drives away from these cars (default: every car of another team): to the place within 30 m by the road that is farthest from them (the nearest one counts most) and whose way keeps `caution` metres (default 6) from them; when cornered, the way with the most room, past the chaser; it also steers round a chaser just ahead |
| `{mode = "stop"}` | stands with the brake |
| `{mode = "path"}` | the normal racing line again |

Every order takes `speed` = 0.1 .. 1, the throttle (default 1). A stuck car (no progress for about 2 s) probes left
and right ahead (the level's walls, water and edges count as blocked), backs off turning its nose away from the
obstacle, drives a waypoint round it on the freer side and then goes on; for 4 s it keeps to that side so it does
not take the same line again. With respawns allowed a car stuck three times within 12 s is put back.

### Sounds and the level's ambience (1.4)

| Function | Meaning |
|---|---|
| `rc.playSound(name, {volume =, loop =, car =, pos =, object =, minDist =, maxDist =, pan =, panTo =})` | the sound with a handle (`false` when it does not play). `loop = true`: until `rc.stopSound`. `car = i` / `pos = {x, y, z}`: placed in the world through DirectSound 3D like the game's own sounds: full volume within `minDist` (5) metres of the camera, quieter down to -20 dB at `maxDist` (60) and never quieter, from its direction (a car's sound follows the car; in the split screen without direction). (1.14) `object = "name"`: placed at the level object of that name (an instance of the level, e.g. a road car or a prop) and following it as a car's sound follows the car; an error when the level has no such object. `pan` = -1 .. 1, or `panTo = {x, y, z}`: from that direction as seen by the camera. At most 16 a mod at a time; all stop when the race is left |
| `rc.stopSound(handle)` | stops it |
| `rc.soundPlaying(handle)` | `true` while it plays |
| `rc.object(name)` | (1.14) a level object (an instance of the level by its name) in the race: `{x, y, z, roadcar, driving}`; `roadcar` = `true` for a road car, `driving` = `true` while that road car drives on its path (not idle or hidden); `nil` when the level has no such object or no race is on |
| `rc.roadcarSound(name, on)` | (1.14) `false` silences the road car's own class sound (the level's Roadcar / Roadcar_slow channel), for a script that gives it a sound of its own (`rc.playSound(name, {object = ..., loop = true})`); `true` (or no argument) gives it back. Returns `true` when the level has that road car; kept until the level is left |
| `rc.listModFiles(folder, pattern)` | the mod's own files in that folder whose names match (`*`, `?`), e.g. `rc.listModFiles("sounds", "hit*.wav")`; empty files are left out (with a warning) |
| `rc.levelAmbient(on, music)` | `false` mutes the level's looping ambience (its background loops, the sea, streams and waterfalls; one-shot sounds such as a prop's or a stone's hit and voices stay, as do the cars', effects' and scripts' sounds); `music` = dB for the race's music (0 as set, -100 silent; the menus' music stays). Given back when the race is left, at a reload and when the mod's scripts stop |
| `rc.fog{...}` | (1.4) returns `true` when the game's fog shows (Options / Video fog on) |
| `rc.hudParts{racerList =, place =, lap =, gps =, map =, timer =, speedo =, boost =, wrongWay =}` | `false` hides that part of the game's HUD (the racer list, the place, the lap counter, the GPS arrow, the minimap, the timer, the speedometer, the boost gauge, the wrong-way sign and its sound), `true` shows it again; without an argument the table of what shows. Given back when the race is left, at *Race again*, at a reload and when the scripts stop |
| `rc.textWidth(text, size)` | the width of a `rc.hudText` text in the 800 x 600 units at that size (UI scale and HudScale included), to centre or line up texts; `rc.hudText` also takes `{align = "center"}` (or `"right"`) as its last argument |
| `rc.replaceTexture(gameTexture, modFile)` | the game texture of that name (one already loaded, e.g. a pedestrian's or a seagull's skin) shows the mod's picture (`.png` / `.dds` / `.csi`, also under `textures\` or `skins\`) until `rc.restoreTexture(name)` / `rc.restoreTextures()`; kept through a texture reload; given back automatically when the race is left, at *Race again*, at a reload and when the scripts stop. Unlike a file in the mod's `Textures\` folder it acts only while the script wants it |

### Camera paths (1.4)

| Function | Meaning |
|---|---|
| `rc.cameraPath{points = {{pos =, target =, fov =, roll =}, ...}, duration =, ease =, blend =}` | player 1's race camera flies through the points: a smooth curve through the places and one through the targets, `fov` / `roll` in between, in `duration` seconds (default 10), `ease` = `"inout"` (default), `"in"`, `"out"`, `"linear"`, from the game's camera in `blend` seconds. Then it stays at the last point. At most 16 points; `rc.camera(...)` or `rc.cameraPath(nil)` ends it; it ends with the race |

A mode's fog, sun, lights, water and camera stay on its end screen (a normal race resets them at the finish);
they are reset when the race is left, at *Race again* and at a reload. *Race again* (on the results page, the
pause menu's restart, a network race's race again) releases everything as leaving the race does: the camera and its
path, the end's hold, the pause and the time scale, the hidden HUD and its parts, the input capture, the look, the
sounds and the ambience, the `rc.setCar` swaps (every car its own model, paint and physics again), the teams, list
texts, AI orders, the respawn block, the timers and the messages; then the mode starts afresh (`onModeLoad`,
`onModeStart`). While a
mode keeps the race music silent (`rc.levelAmbient(false, -100)`), the results page's music stays silent too, so a
mode's own ending sound is heard; the music comes back when the race is left. Sound files: `.wav` (PCM or
Microsoft ADPCM), `.ogg`, `.mp3`, `.au`.

### Network races (1.5)

A mode also runs in a network race. The host picks it in the lobby with the chat command `/mode <id>` (`/mode`
lists the modes, `/mode race` is the normal race again); every player needs the mode's mod. In the race **every
machine runs the mode's script, but only the host's decides**:

| Call / event | What it does |
|---|---|
| `rc.mode.host()` | `true` on the machine whose script decides: always in single player, only on the host in a network race |
| `rc.mode.send(name, ...)` | the deciding script tells what it decided: `onModeEvent(name, ...)` runs here at once and on every client when the message arrives. Values: `nil`, booleans, numbers, strings (at most 32, 1000 bytes). On a client it does nothing and returns `false` |
| `onModeEvent(name, ...)` | change the round here (`rc.setCar`, `rc.setCarTeam`, `rc.mode.freeze` / `listText` / `message` / `timer` / `finish` ...), so every machine makes the same calls |
| `onModeLoad(info)` / `onModeStart(info)` | `info.network` (a network race) and `info.host` (this machine decides) |

- Decide only where `rc.mode.host()` is true (`onCollision`, `onModeTimer`, the checks in `onModeFrame`), and send the
  time or the random choice along instead of taking it again on each machine.
- `onCollision` on the host also gets the contacts the clients report about their own cars; `onRespawnBlocked` runs
  on the host only (a client tells it about its own car); `rc.mode.respawnCar(car)` on the host puts another player's
  car back through that player's machine.
- `rc.options`: an option with `perPlayer = true` (look, sound) stays each player's own; every other option has the
  host's value on all machines during the race (`rc.setting`).
- A network race has no AI cars (`rc.ai` returns `false`), `rc.setCar` changes the physics only of the machine's own
  car, and a car put back goes to its start place (the road points come from the AI's paths).

### The Zombies example

`docs\modding\examples\zombies` is a tag game: after a 10 s head start ("Run!") a random car (yours or an AI's)
becomes the zombie: a Warhammer in its green camouflage paint, driving like one. A zombie that touches a survivor
(a car-car contact of at least the set strength) infects it. The zombies win when everyone is infected; the
survivors win when the time (default 5:00) runs out. The results show who survived and who was infected when.
AI zombies chase the nearest survivor they can reach by the road, AI survivors flee. A grey-green fog lies over
the round, thicker as the survivors get fewer; your gamepad's light bar turns green and it rumbles when you are
infected; `rc.stats` counts the rounds and the wins as zombie / survivor. In place of the racer list it shows its
own status (survivors / zombies, the time left, your role). Its Settings page: time limit (1 .. 10
min), head start, infection strength, fog on / strength, zombie AI aggression, survivor AI caution, ambience on /
volume, heartbeat on / range, what happens to a survivor who falls out (becomes a zombie / is out), the delay before
a fallen zombie is back on the road, end camera on / off. All texts are in the four languages. The game puts no
car back in this mode (`respawn = false`): a car on its roof is set upright where it is. When the round ends, an end
shot (not in VR): the zombies' win rises from the last victim over the gathered zombies, the survivors' win
orbits them; a scoreboard (survival times, who caught whom, the last survivor, the totals, your best survival time
from `rc.stats`) slides in; it can not be skipped and lasts the shot or the ending's sound (at most 30 s), then
the results page comes. To play it, copy the folder `zombies` into the game's `mods` folder.

Its sounds are the mod author's own files and are **not** part of the public example; put your own into the
mod's `sounds\` folder (each missing one is skipped with a warning): `zombie_ambient.mp3` (the round's ambience in
place of the level's), `thunder01.wav` (a new zombie, heard over the whole track from where it happened),
`zombie_attack*.wav` (the infecting contact, at both cars), `heart_beat.wav` (your heartbeat from the nearest
zombie's direction, faster as it comes nearer), `zombie_outro.mp3` (the zombies win), `humans_win.wav` (the
survivors win).

## 6a. Added cars, bodies and skins (1.6)

A mod can add cars, bodies and paints without replacing the game's own. Call these when the script loads:

```lua
-- a car with a chassis of its own (it drives as its base car unless it gives physics values)
rc.registerCar{
  id = "mycar", name = {en = "My car", hu = "Az autóm"},
  base = "Buggy",                   -- "Overkill", "Buggy" or "Warhammer" (or 1 .. 3)
  file = "RCCarsDB/mycar.sb",       -- a scene database of the mod
  model = "MyCar",                  -- its models: MyCar, MyCarLOD1, MyCarLOD2, MyCarLOD3
  skin = "mycar_sk", paints = 3,    -- the paints: textures mycar_sk1 .. mycar_sk3
  physics = {springLength = 0.17, wheelRad = {0.063, 0.063, 0.063, 0.063}},   -- optional: its own values
  physicsScale = {speedBaseMax = 0.93, tyresFront = 0.77, tyresRear = 0.77}, -- optional: factors on the base car's
}
-- one more body for a car (the game's or an added one): the same chassis and physics
rc.registerBody{id = "mybody", name = "My body", car = "Buggy",
                file = "RCCarsDB/mybody.sb", model = "MyBody", skin = "mybody_sk", paints = 2}
-- one more paint for a car's own body, or (body = "mybody") for an added body
rc.registerSkin{car = "Buggy", name = "Blue", texture = "myskin_a", texture2 = "myskin_b"}
```

- **`rc.registerCar`**: a car with its own chassis. It uses its `base` car's place in the player's profile (it can
  be raced when the player owns the base car), sounds and upgrades; nothing new is saved. Without `physics` /
  `physicsScale` it drives exactly like the base car.
- **`rc.registerBody`**: another body on an existing chassis: `car` is one of the game's cars or an added car's
  `id`. It drives like that car.
- **`rc.registerSkin`**: one more paint. `car` alone: for that car's own body; `body`: for an added body.
  `texture2` is the second (B) texture of the game's Buggy and Warhammer, whose bodies use two.
- The Quick race's car chooser lists the game's cars, each followed by its added bodies, then the added cars with
  theirs. The **Skin** row under the preview picks the paint ("-" = the paint of the player's profile). The choices
  are not saved. The network game, the split screen, the garage and the championship use the game's cars.
- `file` is a scene database (`.sb`) in the mod with the models `<model>`, `<model>LOD1` .. `<model>LOD3`: the
  whole car (chassis and body), for a body too. The model objects follow the base car's (`WHEEL_FRONT_LEFT`, the
  axles, the `booster_N` / `compressor_N` upgrade parts ...): the game takes the wheels' places from the model.
- Give the model's textures names of the mod's own, so no texture of another car is replaced. `skin` is the
  beginning of the paints' texture names; the model must list all of them (`<skin>1` .. `<skin><paints>`).
- `physics` sets values in the game's own units, `physicsScale` multiplies the base car's. Names: `speedBaseMax`, `speedBoostMax` (km/h), `boostSpeedUp`, `boostSpeedDown`, `boosters`, `resonators`, `resonatorsForce`, `tyreUpgrades` (4 each), `tyresFront`, `tyresRear`, `angleDriftOn`, `speedDriftOn`, `coeffDriftRear`, `coeffDeepSand`, `coeffWater`, `speedAngMaxRel`, `frictionBearings`, `airResistance`, `angleSteer`, `springLength`, `springLenMin`, `springLenMax`, `springKPos`, `springKSpeed`, `springDx`, `springTouchPoint`, `springDz`, `coeffMomentOX`, `coeffMomentOZ`, `lenAxe`, `angleUpMax`, `angleDownMax`, `wheelRad` (6), `bodyRad` (4), `bodyPos` (4 x {x, y, z}), `centreMass`.
- Jet drive (for a car with jets, like the PS2 game's CCCP): giving `jetForceForward` in `physics` turns it on for that car. It follows the PS2 game's code and works **only in the air** (no wheel touching); on the ground the car drives by its wheels like any other. In the air: the car flies where it points (its sideways drift is taken away within `jetSideDecayTime`), the accelerator pushes it along its level heading with `jetForceForward` (reverse with half of it), steering pushes with `jetForceRotate` at the jet `jetLeverLen` to the side until the turning momentum reaches `jetMaxYawImpulse`, and the car is turned level (heading kept) at up to 160 degrees a second, so it lands on its wheels. The forces are not multiplied by the car's mass. Accepted but not used (the PS2 code read does not use them either): `jetStabYawSpeed`, `jetStabRollSpeed`, `jetStabRollAngle`, `jetRotateMinSpeed`, `jetCoeffSand`, `jetCoeffGrass`; `jetPitchDecayTime` is the old name of `jetSideDecayTime`. `jetGravitySpeed = {..}` with `jetGravity = {..}` (up to six points, speeds in km/h rising) make the car's gravity depend on its speed, as the PS2 car's does (the game's gravity is 10); the car then also jumps higher and further.
- Sounds (1.7), for `rc.registerCar` and `rc.registerBody`: `sound = "Overkill" | "Buggy" | "Warhammer"` (or 1 .. 3) picks which game car's engine sound set the car uses (default: its base car's); `sounds = {motor_accel1 = "mycar_accel", ...}` plays single sounds from the mod's own files: the key is the game's sound name (the Overkill's names work for every set: `motor_accel1`, `motor_engine`, `motor_idle`, `motor_off`, `motor_reverse`, `motor_decel1` .. `3`, `motor_accel1_ws`, `motor_engine_ws`, `motor_decel1_ws`, `Motor_flying2`, `Motor_flying_end2`, `car_boost`, `car_boost_end`, `car_flying`, `car_landing`, `car_break`, `car_cdt_*`, `car_surf_*`, `car_hit_*`), the value a file name without extension in the mod's `Sound` folder (`Sound/mycar_accel.wav`). A file that is missing is logged and the game's own sound is played. A body without sound settings sounds as its car. Only the player's car uses them (the opponents share the game's AI sounds). The engine has no pitch change: the game enters `motor_accel1` at 0 / 1.38 / 3.35 / 6.81 s by the speed band, so a replacement should rise in the same way.
- Each call returns `true`; a car / body of the same `id` is replaced. At most 16 cars, 48 bodies, 96 skins.

## 6b. Main menu entries, starting a race, object hits (1.9)

```lua
rc.registerMenu{id = "tutorial", name = {en = "Tutorial", hu = "Oktató"}, onSelect = function()
  rc.startRace{track = "beach_1", car = "Buggy", laps = 3, mode = "my_mode"}
end}

function onObjectHit(car, name)            -- a car knocked a can, a ball, a bottle ...
  rc.log(rc.carName(car) .. " hit " .. name)
end
```

| Function | Description |
|---|---|
| `rc.registerMenu{id =, name =, onSelect =}` | adds a button to the main menu, between Mods and Credits. `name` is a text or a language table; `onSelect` runs when the button is pressed. The menu has room for two such buttons in all (over every mod); a third is left out with a warning and the call returns `false`. With an entry the menu's buttons move a little closer together |
| `rc.startRace{track =, car =, laps =, mode =, paint =}` | starts a Quick race from the menus. `track`: one of the game's ten (`"beach_1"` .. `"country_4"`, the display name, or 1 .. 10); `car`: 1 .. 3, `"Overkill"` / `"Buggy"` / `"Warhammer"`, or the id of an added car or body (default: the player's car); `laps`: the lap count; `mode`: the id of a game mode registered with `rc.registerMode` (default: a plain race). Returns `true` when the start is queued (it happens within a second), or `false` and a reason (a race is running, a network game, no player chosen) (1.14) `paint`: the car's / body's paint, 1 .. as the Quick race's skin chooser counts them (default: the player's own choice). |
| `rc.leaveRace()` | (1.14) leaves the race as the pause menu's *Quit* does (nothing saved), at the start of the next frame; then the menu comes back (`onMenu`). Single player races only; `false` when not in such a race |
| `rc.addSpin(car, x, y, z)` | changes the car's angular velocity by that much (rad/s about the world's axes), e.g. to let the player turn the car in the air. Only a car with its own physics (the players'), not in a network race; returns `true` when done |

### Added tracks (1.10)

```lua
rc.registerTrack{id = "tutorial", name = {en = "Tutorial", hu = "Oktatópálya"},
  description = {en = "Learn to drive.", hu = "Tanulj meg vezetni."},
  level = "tutorial",                    -- RCCarsDB/tutorial.sb of the mod
  picture = "tutorial_pic",              -- the selection picture on the Quick race page
  loading = "tutorial_load",             -- the loading screen's big picture
  shots = {"tutorial_s1", "tutorial_s2"},  -- up to four more small pictures of the loading screen
  ai = "tutorial_ai.ini"}                -- Scripts/tutorial_ai.ini of the mod: the opponents
```

`rc.registerTrack` adds a track of the mod to the Quick race page, after the game's ten (at most 8 added tracks in all). Everything it names is in the game's own formats, in the mod's folders:

- `level`: the level database `RCCarsDB/<level>.sb`, built like the game's levels (its `Checkpoints` folder with the marks `cp_1` .. `cp_8`, the `Player` instance, and so on).
- `picture`: the texture shown when the track is chosen (in the mod's `Textures`). `loading`: the loading screen's big picture; `shots`: up to four more small pictures of the loading screen. What is left out is the `picture`; without `picture` the first game track's pictures are used.
- `ai`: an AI layout script in the mod's `Scripts` folder, written like the game's `Scripts/AIlayouts.ini`: the `AIPlayer<n>` sections and one section `AIRace1` with `PlayerPath`, `AI<n>Path` (recorded car profiles in `CarProfiles/`), `AI<n>Car`, `AI<n>Ref`, `AI<n>Races` and so on. Without `ai` the track has no opponents and the player starts at the level's `Player` instance.
- `name`, `description`: a text or a language table.

`rc.startRace{track = "<id>"}` starts an added track by its id. Added tracks are not in the Championship, the Ghost race or the multiplayer pages, and no records or statistics are kept for them.

### Models of a mod (1.11)

```lua
rc.registerModel("MyCan", "RCCarsDB\\my_props.sb")
```

`rc.registerModel(name, file)` tells the game that the model `name` is in the mod's own database file. A level can then use it as the prototype of its instances: the props of an added track (cans, balls and so on, built like the models of the game's `stone.sb`, with their script and sound channel). The name must not be one of the game's own models; the file path is relative, as mods give their files.

## 7. Sandbox limits

- Available: the Lua base functions, `table`, `string`, `math`, `utf8`, `coroutine`, and `os.clock`, `os.time`,
  `os.date`.
- Not available: `io`, the rest of `os`, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- `load` takes text chunks only (a string; no binary chunks).
- `collectgarbage` only accepts `"count"`.
- Memory: 64 MB per mod.
- Time: `LuaBudget` Lua instructions per event call. Long work inside one library call (for example a huge
  `string.rep` or a complex pattern) is not counted by instructions; keep scripts simple.
- Scripts never write game files, mod files or player saves; the only files written are the mod's settings and
  statistics files.

## 8. Error handling

- A load error, a runtime error or an exceeded budget aborts only that call. The game goes on.
- Every error is logged as `Lua [mod] what: file:line: message` in `game_dbg.log` (with a traceback).
- After 5 errors the mod's scripts are switched off ("mod scripts disabled after repeated errors"). Fix the
  script, then press Apply on the Mods screen (or save the file in developer mode, see below).
- A call that used more than 80 % of the budget gives one warning.

## 9. Developer mode (`RcCarsRe.exe -dev`)

- Errors and warnings are shown on the console window: error lines red, warning lines yellow (Lua and game
  alike); errors also appear in the red overlay in the game.
- Console command `lua` lists the mods with scripts; `lua <code>` runs code in the last loaded mod's state,
  `lua <mod> <code>` in that mod's state, and prints the results (an expression such as `lua rc.race().state`
  works too).
- Hot reload: the `.lua` files of folder mods are checked once a second; when one changes, that mod's scripts are
  loaded again (zip mods: use Apply). A reload also ends every camera, weather and light-bar override.

## 10. Examples

`docs/modding/examples/` has four complete mods. Copy a folder into `mods\` next to `RcCarsRe.exe`:

- `laptime_hud`: the race time (the same as the HUD's timer), the current, last and best lap time of player 1 in a
  box, in the game's time format; options for the best lap, the size and the corner.
- `checkpoint_sound`: plays the mod's own `sounds\ding.wav` at each checkpoint of player 1 and flashes its number.
- `drift_air`: when player 1's car lands after a jump it shows the time in the air, gives a short rumble and a
  light-bar flash, and keeps the best air time per track and the jump count with `rc.stats`.
- `photo_mode`: a photo mode (P or the pad's Back / Share / Create): the race paused, the HUD hidden, a free camera, F12 / A for a photo, rc.stats counts them (API 1.2).
- `zombies`: a game mode (API 1.5): a tag / infection game against the AI or, in a network race, the other
  players; see "Game modes".

A minimal script:

```lua
function onLap(car, lap, t)
  local p = rc.player(1)
  if p and p.index == car then rc.log("lap " .. lap .. ": " .. rc.formatTime(t)) end
end

function onLand(car, air)
  local p = rc.player(1)
  if p and p.index == car and air > 0.5 then
    rc.rumble(0.6, 0.2)
    rc.stats.add("jumps")
  end
end

function onFrame(dt)
  if rc.race().state == "racing" then
    rc.hudText(400, 20, "Hello from Lua", 0xffffff40, 1, "center")
  end
end
```

## 11. Troubleshooting

| Problem | Check |
|---|---|
| Nothing happens | `LuaScripts=1` and `Mods=1` in `RcCarsRe.ini`; the mod is on in the Mods screen; the file is in the mod's root or in `scripts\`; `game_dbg.log` has `Lua [mod]: ... loaded` |
| "mod scripts disabled after repeated errors" | read the first `Lua [mod]` error lines in `game_dbg.log`, fix the script, press Apply |
| "instruction budget exceeded" | the event did too much work at once; split it over frames or raise `LuaBudget` |
| HUD item not visible | HUD calls work for one frame only: call them from `onFrame`; check the alpha byte of the colour (`0xFF......` is opaque) |
| "texture ... not found" / "sound ... not found" (yellow) | the file name and folder in the mod; PNG, DDS or CSI pictures; WAV, OGG, MP3 or AU sounds |
| Text shows `?` | write the script in UTF-8; the game font only has the characters of its language's code page |
| Lap 1's time is shorter than the HUD's timer | as in the game, lap times count from the start/finish line; the race time is `rc.race().time` |
| The camera does not change | only in a race, only player 1's view, not in VR |
| No rumble / light bar | a pad must be connected; `Rumble`, `LightBar`, `AdaptiveTriggers` in `RcCarsRe.ini`; rumble and triggers act only while the car races |
| Errors on the -dev console | error lines are red, warnings yellow; the same lines are in `game_dbg.log` |
