# Lua scripting for mods

**English** | [Magyar](LUA_SCRIPTING.hu.md) | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

RcCarsRe can run small Lua scripts that come with a mod. A script can read the race (track, laps, cars,
positions, lap times), react to events (a lap, a checkpoint, a hit, the water, a respawn, the race end) and do
local things: draw texts, pictures and boxes on the HUD, play sounds, write to the log and keep its own settings.
Scripts cannot change the race, the cars or the game's files.

The language is [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT licence, see
[LUA_LICENSE.txt](LUA_LICENSE.txt)).

## 1. Overview

- Every enabled mod (folder or zip in a `mods` folder, see [MODDING.md](../MODDING.md)) can hold `.lua` files.
- Each mod gets its own Lua state. Mods cannot see each other's global variables.
- Mods are loaded in the Mods screen's order from the bottom up: the lowest-priority mod first, the top mod last.
- The game calls the script's global event functions (`onFrame`, `onLap`, ...) when they exist.
- Everything a script does is local to your computer: HUD, sound, log, its settings file. Scripts never send
  anything over the network and do not affect other players in a network race.

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

`car` is the car's number, 1 .. `rc.race().cars`. `results` is a list in place order; each entry has `car`,
`place`, `finished`, `time`, `bestLap` (missing when none), `lap`, `name`.

## 5. API reference (`rc` table)

### Reading

| Function | Returns |
|---|---|
| `rc.version` | the API version string (`"1.0"`) |
| `rc.modName` | the mod's name |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = seconds since GO (-1 before). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (player 1 finished), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, place, isPlayer, isAi, isGhost, player, finished, name}` or `nil`. `speed` in km/h; `player` = 1 / 2 for a player's car |
| `rc.player(n)` | the car table of player `n` (1 or 2, default 1), or `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: render size in pixels, the current screen name, VR on, split screen |

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

### Files of the own mod

| Function | Meaning |
|---|---|
| `rc.readFile(path)` | the file's bytes as a string, or `nil, message`. Only the script's own mod is read |
| `rc.include(path)` | runs a `.lua` file of the own mod once and returns its result (later calls return the same result), like `require` |

### Settings

Stored in `Saves\Mods\<mod>.ini` next to `RcCarsRe.exe` (`<mod>.zip.ini` for a zip mod), section `[Settings]`.
Nothing else is written.

| Function | Meaning |
|---|---|
| `rc.setting(key, default)` | the stored value, converted to the type of `default` (boolean, number, string); without a stored value `default`, or the option's default |
| `rc.setSetting(key, value)` | stores a boolean, number or string (`nil` deletes it); it writes the file at once, so do not call it every frame |
| `rc.options{ ... }` | declares the options of the mod's Settings page (below) |

Keys: letters, digits, `_`, `.`, `-`, at most 63 characters. Values: at most 1000 bytes, no line breaks.

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

## 6. Sandbox limits

- Available: the Lua base functions, `table`, `string`, `math`, `utf8`, `coroutine`, and `os.clock`, `os.time`,
  `os.date`.
- Not available: `io`, the rest of `os`, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- `load` takes text chunks only (a string; no binary chunks).
- `collectgarbage` only accepts `"count"`.
- Memory: 64 MB per mod.
- Time: `LuaBudget` Lua instructions per event call. Long work inside one library call (for example a huge
  `string.rep` or a complex pattern) is not counted by instructions; keep scripts simple.
- Scripts never write game files, mod files or player saves; the only file written is the mod's settings file.

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
  loaded again (zip mods: use Apply).

## 9. Examples

`docs/modding/examples/` has two complete mods. Copy a folder into `mods\` next to `RcCarsRe.exe`:

- `laptime_hud`: current, last and best lap time of player 1 in a box; options for the best lap, the size and
  the corner.
- `checkpoint_sound`: plays the mod's own `sounds\ding.wav` at each checkpoint of player 1 and flashes its number.

A minimal script:

```lua
function onLap(car, lap, t)
  local p = rc.player(1)
  if p and p.index == car then rc.log(string.format("lap %d: %.2f s", lap, t)) end
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
| Errors on the -dev console | error lines are red, warnings yellow; the same lines are in `game_dbg.log` |
