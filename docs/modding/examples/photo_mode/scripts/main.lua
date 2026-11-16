-- Photo mode: an example mod for the RcCarsRe Lua scripting, API 1.2 (docs/modding/LUA_SCRIPTING.en.md,
-- "Building a photo mode"). The game itself has no photo mode: this script builds one from rc.pause, rc.hud,
-- rc.input, rc.camera and rc.screenshot. Single-player races only (a network race can not be paused).
--
-- The controls are in the mod's controls.ini (and, if present, Saves\Mods\photo_mode.controls.ini next to
-- RcCarsRe.exe, which survives mod updates). Defaults:
--   P / pad Back-Share-Create: on / off     Esc: leave     W A S D: fly (W / S along the view)     mouse: look
--   Shift / Ctrl: up / down     Q / E: roll     Space: faster     wheel: zoom     F12 / pad A: photo
--   R / pad Y (Triangle): realtime shadows and reflections on / off (the ini's own values again when leaving)
--   Pad: left stick move, right stick look, triggers down / up, bumpers roll, D-pad up / down zoom, L3 faster.
-- The photos go to Screenshots next to RcCarsRe.exe (without the help line); rc.stats counts them.

rc.options{
  {key = "fov", type = "slider", min = 20, max = 110, step = 5, default = 60,
   label = {en = "Start FOV", hu = "Kezdő látószög", ru = "Начальный угол обзора", pl = "Początkowe pole widzenia"}},
  {key = "speed", type = "slider", min = 1, max = 20, step = 1, default = 6,
   label = {en = "Camera speed (m/s)", hu = "Kamera sebessége (m/s)", ru = "Скорость камеры (м/с)", pl = "Prędkość kamery (m/s)"}},
  {key = "help", type = "bool", default = true,
   label = {en = "Show help", hu = "Súgó mutatása", ru = "Показывать подсказку", pl = "Pokaż pomoc"}},
}

-- ---- the controls (controls.ini) ----

local DEFAULT_KEYS = {
  toggle = "P", leave = "Esc", forward = "W", back = "S", left = "A", right = "D", up = "Shift", down = "Ctrl",
  rollLeft = "Q", rollRight = "E", fast = "Space", fovIn = "WheelUp", fovOut = "WheelDown", photo = "F12",
  realtimeGfx = "R",
}
local DEFAULT_PAD = {
  toggle = "back", photo = "a", fast = "ls", rollLeft = "lb", rollRight = "rb", fovIn = "up", fovOut = "down",
  leave = "None", realtimeGfx = "y",
}
local PAD_NAMES = {
  a = 1, cross = 1, b = 1, circle = 1, x = 1, square = 1, y = 1, triangle = 1, lb = 1, l1 = 1, rb = 1, r1 = 1,
  back = 1, view = 1, share = 1, create = 1, select = 1, start = 1, menu = 1, options = 1, ls = 1, l3 = 1,
  rs = 1, r3 = 1, guide = 1, ps = 1, touchpad = 1, mute = 1, up = 1, down = 1, left = 1, right = 1,
}
local keys, pad = {}, {}
local stickDz, triggerDz = 0.2, 0.1                   -- (controls.ini [Pad] deadzone / triggerDeadzone)

local function keyOk(name)
  if name == "None" or name == "WheelUp" or name == "WheelDown" then return true end
  return pcall(rc.input.key, name)                    -- (an unknown name raises an error)
end

-- one ini text into the tables; "where" names the file for the warnings
local function parse(text, where)
  local section
  local n = 0
  for line in (text .. "\n"):gmatch("([^\r\n]*)\r?\n") do
    line = line:gsub(";.*$", ""):match("^%s*(.-)%s*$")
    local sec = line:match("^%[(.-)%]$")
    if sec then
      section = sec:lower()
    elseif line ~= "" then
      local k, v = line:match("^([%w_]+)%s*=%s*(.-)$")
      if not k then
        rc.warn(string.format("photo_mode: %s: line not understood: %s", where, line))
      elseif section == "keyboard" then
        if DEFAULT_KEYS[k] == nil then
          rc.warn(string.format("photo_mode: %s: unknown action '%s'", where, k))
        elseif not keyOk(v) then
          rc.warn(string.format("photo_mode: %s: unknown key '%s' for %s, the default %s stays", where, v, k,
            DEFAULT_KEYS[k]))
        else
          keys[k] = v
          n = n + 1
        end
      elseif section == "pad" and (k == "deadzone" or k == "triggerDeadzone") then
        local x = tonumber(v)
        if not x or x < 0 or x > 0.9 then
          rc.warn(string.format("photo_mode: %s: %s must be a number 0 .. 0.9, the default stays", where, k))
        elseif k == "deadzone" then
          stickDz = x
          n = n + 1
        else
          triggerDz = x
          n = n + 1
        end
      elseif section == "pad" then
        local lv = v:lower()
        if DEFAULT_PAD[k] == nil then
          rc.warn(string.format("photo_mode: %s: unknown pad action '%s'", where, k))
        elseif lv ~= "none" and not PAD_NAMES[lv] then
          rc.warn(string.format("photo_mode: %s: unknown pad button '%s' for %s, the default %s stays", where, v, k,
            DEFAULT_PAD[k]))
        else
          pad[k] = lv
          n = n + 1
        end
      end
    end
  end
  return n
end

local function loadControls()
  for k, v in pairs(DEFAULT_KEYS) do keys[k] = v end
  for k, v in pairs(DEFAULT_PAD) do pad[k] = v:lower() end
  stickDz, triggerDz = 0.2, 0.1
  local text = rc.readFile("controls.ini")
  local n = text and parse(text, "controls.ini") or 0
  local user = rc.readUserFile("controls.ini")
  if user then
    n = n + parse(user, "Saves\\Mods\\" .. rc.modName .. ".controls.ini")
    rc.log("photo_mode: the player's own controls file read")
  end
  rc.log(string.format("photo_mode: controls: %d binding(s) read; up=%s down=%s rollLeft=%s rollRight=%s fast=%s",
    n, keys.up, keys.down, keys.rollLeft, keys.rollRight, keys.fast))
end

local wheel = 0                                       -- this frame's wheel notches

local function held(action)
  local k = keys[action]
  if k == "None" then return false end
  if k == "WheelUp" then return wheel > 0 end
  if k == "WheelDown" then return wheel < 0 end
  return rc.input.key(k)
end

local function hit(action)
  local k = keys[action]
  if k == "None" then return false end
  if k == "WheelUp" then return wheel > 0 end
  if k == "WheelDown" then return wheel < 0 end
  return rc.input.pressed(k)
end

local function padHeld(p, action)
  local b = pad[action]
  return p ~= nil and b ~= "none" and p.buttons[b] == true
end

local function padHit(p, action)
  local b = pad[action]
  return p ~= nil and b ~= "none" and p.pressed[b] == true
end

local logTime = 0

-- a stick through a radial dead zone (the rest stretched to 0 .. 1)
local function deadzone2(x, y, dz)
  local m = math.sqrt(x * x + y * y)
  if m <= dz then return 0, 0 end
  local k = math.min(1, (m - dz) / (1 - dz)) / m
  return x * k, y * k
end

local function deadzone1(v, dz)
  if v <= dz then return 0 end
  return math.min(1, (v - dz) / (1 - dz))
end

-- ---- the photo mode ----

local on = false
local pos, yaw, pitch, roll, fov = nil, 0, 0, 0, 60
local iniGfx, gfxOn = nil, false                    -- the graphics before the photo mode; realtime switched on
local msg, msgTime = nil, 0

local function enter(how)
  local r = rc.race()
  if r.state ~= "racing" and r.state ~= "finished" and r.state ~= "prestart" then return end
  if rc.screen().split or rc.screen().vr then
    rc.warn("photo mode: not in the split screen or VR")
    return
  end
  local c = rc.cameraInfo()
  if not c then return end
  if not rc.pause(true) then
    rc.warn("photo mode: the race can not be paused here (network race)")
    return
  end
  loadControls()                                      -- (the files' latest version)
  rc.hud(false)
  rc.input.capture(true)
  pos = {c.pos.x, c.pos.y, c.pos.z}
  yaw = math.atan(c.dir.x, c.dir.z)
  pitch = math.asin(math.max(-1, math.min(1, c.dir.y)))
  roll = 0
  fov = rc.setting("fov", 60)
  iniGfx, gfxOn = rc.graphics(), false                -- (the ini's Shadows / Reflections, to go back to)
  on = true
  rc.log("photo mode on (" .. how .. ")")
end

-- realtime shadows and reflections on, or the ini's own values again (rc.graphics, API 1.3)
local function setRealtime(want)
  gfxOn = want
  if want then
    rc.graphics{shadows = "realtime", reflections = "realtime"}
  elseif iniGfx then
    rc.graphics(iniGfx)
  end
  rc.log("photo mode: realtime shadows and reflections " .. (want and "on" or "off"))
end

local function leave(how)
  if gfxOn then setRealtime(false) end
  rc.camera(nil)
  rc.hud(true)
  rc.input.capture(false)
  rc.pause(false)
  on = false
  rc.log("photo mode off (" .. how .. ")")
end

function onFrame(dt)
  local p = rc.input.pad(1)
  local m = rc.input.mouse()
  wheel = m.wheel
  if not on then
    if hit("toggle") then enter("key " .. keys.toggle) elseif padHit(p, "toggle") then enter("pad " .. pad.toggle) end
    return
  end
  if hit("toggle") or hit("leave") then
    leave("key " .. (hit("toggle") and keys.toggle or keys.leave))
    return
  end
  if padHit(p, "toggle") or padHit(p, "leave") then
    leave("pad " .. (padHit(p, "toggle") and pad.toggle or pad.leave))
    return
  end
  dt = math.max(0, math.min(dt, 0.1))
  -- the pad's sticks and triggers through the dead zones of controls.ini (worn sticks drift a little at rest)
  local lx, ly, rx2, ry2, lt, rt = 0, 0, 0, 0, 0, 0
  if p then
    lx, ly = deadzone2(p.lx, p.ly, stickDz)
    rx2, ry2 = deadzone2(p.rx, p.ry, stickDz)
    lt, rt = deadzone1(p.lt, triggerDz), deadzone1(p.rt, triggerDz)
  end
  -- look
  yaw = yaw - m.dx * 0.003 - rx2 * 2.0 * dt   -- (mouse right / stick right turn right)
  pitch = math.max(-1.5, math.min(1.5, pitch - m.dy * 0.003 + ry2 * 1.5 * dt))
  -- move: forward / back along the view (up and down too), sideways along the view's horizontal right,
  -- up / down straight (no inertia: without input the camera stands still)
  local speed = rc.setting("speed", 6)
  if held("fast") or padHeld(p, "fast") then speed = speed * 4 end
  local fx, fy, fz = math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)
  local sx, sz = -math.cos(yaw), math.sin(yaw)        -- to the right, horizontal (roll does not turn it; the game's x axis points left of the view)
  local mf, ms, mu = 0, 0, 0
  if held("forward") then mf = mf + 1 end
  if held("back") then mf = mf - 1 end
  if held("right") then ms = ms + 1 end
  if held("left") then ms = ms - 1 end
  if held("up") then mu = mu + 1 end
  if held("down") then mu = mu - 1 end
  mf, ms, mu = mf + ly, ms + lx, mu + rt - lt
  local d = speed * dt
  pos[1] = pos[1] + (fx * mf + sx * ms) * d
  pos[2] = pos[2] + (fy * mf + mu) * d
  pos[3] = pos[3] + (fz * mf + sz * ms) * d
  -- the inputs once a second (where a drift would come from)
  logTime = logTime + dt
  if logTime >= 1 then
    logTime = 0
    rc.log(string.format("photo mode inputs: mouse %d %d wheel %.1f, pad %s lx %.2f ly %.2f rx %.2f ry %.2f lt %.2f " ..
      "rt %.2f (after the dead zones %.2f %.2f %.2f %.2f %.2f %.2f), keys f%d s%d u%d; camera %.3f %.3f %.3f",
      m.dx, m.dy, m.wheel, p and p.kind or "-", p and p.lx or 0, p and p.ly or 0, p and p.rx or 0, p and p.ry or 0,
      p and p.lt or 0, p and p.rt or 0, lx, ly, rx2, ry2, lt, rt, mf - ly, ms - lx, mu - rt + lt, pos[1], pos[2],
      pos[3]))
  end
  -- roll and field of view
  if held("rollLeft") or padHeld(p, "rollLeft") then roll = roll - 45 * dt end
  if held("rollRight") or padHeld(p, "rollRight") then roll = roll + 45 * dt end
  if keys.fovIn == "WheelUp" or keys.fovOut == "WheelDown" then
    fov = fov - wheel * 5                             -- (the wheel: 5 degrees a notch)
  else
    if held("fovIn") then fov = fov - 30 * dt end
    if held("fovOut") then fov = fov + 30 * dt end
  end
  if padHeld(p, "fovIn") then fov = fov - 30 * dt end
  if padHeld(p, "fovOut") then fov = fov + 30 * dt end
  fov = math.max(15, math.min(120, fov))
  rc.camera{pos = pos, target = {pos[1] + fx, pos[2] + fy, pos[3] + fz}, fov = fov, roll = roll}
  -- realtime shadows and reflections
  if hit("realtimeGfx") or padHit(p, "realtimeGfx") then setRealtime(not gfxOn) end
  -- the photo
  if hit("photo") or padHit(p, "photo") then
    local file = rc.screenshot{hideScriptHud = true}
    local n = rc.stats.add("photos")
    msg, msgTime = "Photo " .. n .. ": " .. file, 2.5
  end
  -- help (not in the photo)
  if rc.setting("help", true) then
    rc.hudRect(0, 572, 800, 28, 0x80000000)
    rc.hudText(400, 576, string.format("PHOTO MODE  %s%s%s%s move, mouse look, %s/%s up/down, %s/%s roll, %s fast, " ..
      "wheel zoom, %s realtime: %s, %s photo, %s/%s leave", keys.forward, keys.left, keys.back, keys.right, keys.up,
      keys.down, keys.rollLeft, keys.rollRight, keys.fast, keys.realtimeGfx, gfxOn and "on" or "off", keys.photo,
      keys.toggle, keys.leave), 0xffffffff, 0.7, "center")
  end
  if msg and msgTime > 0 then
    msgTime = msgTime - dt
    rc.hudText(400, 20, msg, 0xffffd040, 0.8, "center")
  end
end

function onRaceEnd()
  on = false                                          -- (the game released the pause, HUD, capture and camera)
end

function onMenu(name)
  if name ~= "race" and on then on = false end
end

function onLoad()
  loadControls()
  rc.log(string.format("photo_mode loaded (API %s): %d photo(s) so far", rc.version, rc.stats.get("photos", 0)))
end
