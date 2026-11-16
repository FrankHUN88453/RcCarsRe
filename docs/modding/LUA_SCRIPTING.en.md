# Lua scripting for mods

**English** | [Magyar](LUA_SCRIPTING.hu.md) | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

RcCarsRe can run small Lua scripts that come with a mod. A script can read the race (track, laps, cars,
positions, lap times), react to events (a lap, a checkpoint, a hit, a jump, an overtake, the pause, the race end
...) and do local things: draw texts, pictures and boxes on the HUD, play sounds, move the camera, change the fog,
the sun and the lights, rumble the gamepad, write to the log and keep its own settings and statistics.
Scripts cannot change the race, the cars or the game's files.

The language is [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT licence, see
[LUA_LICENSE.txt](LUA_LICENSE.txt)). This page describes API version **1.2**.

## 1. Overview

- Every enabled mod (folder or zip in a `mods` folder, see [MODDING.md](../MODDING.md)) can hold `.lua` files.
- Each mod gets its own Lua state. Mods cannot see each other's global variables.
- Mods are loaded in the Mods screen's order from the bottom up: the lowest-priority mod first, the top mod last.
- The game calls the script's global event functions (`onFrame`, `onLap`, ...) when they exist.
- Everything a script does is local to your computer: HUD, sound, camera, fog, lights, gamepad, log, its own files.
  Scripts never send anything over the network and do not affect other players in a network race.

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
| `rc.version` | the API version string (`"1.2"`) |
| `rc.modName` | the mod's name |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = the HUD's race timer in seconds (-1 before GO). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (player 1 finished), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, raceTime, place, isPlayer, isAi, isGhost, player, finished, name}` or `nil`. `speed` in km/h; `player` = 1 / 2 for a player's car; `raceTime` = the car's time since GO (it stops when the car finishes) |
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

## 6. Sandbox limits

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

## 7. Error handling

- A load error, a runtime error or an exceeded budget aborts only that call. The game goes on.
- Every error is logged as `Lua [mod] what: file:line: message` in `game_dbg.log` (with a traceback).
- After 5 errors the mod's scripts are switched off ("mod scripts disabled after repeated errors"). Fix the
  script, then press Apply on the Mods screen (or save the file in developer mode, see below).
- A call that used more than 80 % of the budget gives one warning.

## 8. Developer mode (`RcCarsRe.exe -dev`)

- Errors and warnings are shown on the console window: error lines red, warning lines yellow (Lua and game
  alike); errors also appear in the red overlay in the game.
- Console command `lua` lists the mods with scripts; `lua <code>` runs code in the last loaded mod's state,
  `lua <mod> <code>` in that mod's state, and prints the results (an expression such as `lua rc.race().state`
  works too).
- Hot reload: the `.lua` files of folder mods are checked once a second; when one changes, that mod's scripts are
  loaded again (zip mods: use Apply). A reload also ends every camera, weather and light-bar override.

## 9. Examples

`docs/modding/examples/` has four complete mods. Copy a folder into `mods\` next to `RcCarsRe.exe`:

- `laptime_hud`: the race time (the same as the HUD's timer), the current, last and best lap time of player 1 in a
  box, in the game's time format; options for the best lap, the size and the corner.
- `checkpoint_sound`: plays the mod's own `sounds\ding.wav` at each checkpoint of player 1 and flashes its number.
- `drift_air`: when player 1's car lands after a jump it shows the time in the air, gives a short rumble and a
  light-bar flash, and keeps the best air time per track and the jump count with `rc.stats`.
- `photo_mode`: a photo mode (P or the pad's Back / Share / Create): the race paused, the HUD hidden, a free camera, F12 / A for a photo, rc.stats counts them (API 1.2).

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

## 10. Troubleshooting

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
