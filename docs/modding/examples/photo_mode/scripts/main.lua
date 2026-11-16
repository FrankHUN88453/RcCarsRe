-- Photo mode: an example mod for the RcCarsRe Lua scripting, API 1.2 (docs/modding/LUA_SCRIPTING.en.md,
-- "Building a photo mode"). The game itself has no photo mode: this script builds one from rc.pause, rc.hud,
-- rc.input, rc.camera and rc.screenshot. Single-player races only (a network race can not be paused).
--
-- P (keyboard) or the pad's Back / View / Share / Create button (configurable) toggles it.
--   Move: W A S D / left stick     Look: mouse / right stick     Up / down: E / Q or the triggers
--   Roll: Z / C or the bumpers     FOV: mouse wheel / D-pad up and down     Faster: Shift / left stick click
--   Photo: F12 / the pad's A (Cross)     Leave: P, Esc, or the toggle button again
-- The photos go to Screenshots next to RcCarsRe.exe (without the help line); rc.stats counts them.

rc.options{
  {key = "fov", type = "slider", min = 20, max = 110, step = 5, default = 60,
   label = {en = "Start FOV", hu = "Kezdő látószög", ru = "Начальный угол обзора", pl = "Początkowe pole widzenia"}},
  {key = "speed", type = "slider", min = 1, max = 20, step = 1, default = 6,
   label = {en = "Camera speed (m/s)", hu = "Kamera sebessége (m/s)", ru = "Скорость камеры (м/с)", pl = "Prędkość kamery (m/s)"}},
  {key = "help", type = "bool", default = true,
   label = {en = "Show help", hu = "Súgó mutatása", ru = "Показывать подсказку", pl = "Pokaż pomoc"}},
  {key = "padToggle", type = "enum", values = {"back", "touchpad", "r3"}, default = "back",
   labels = {{en = "Back / Share / Create", hu = "Back / Share / Create", ru = "Back / Share / Create", pl = "Back / Share / Create"},
             {en = "Touchpad click", hu = "Touchpad kattintás", ru = "Нажатие тачпада", pl = "Kliknięcie touchpada"},
             {en = "Right stick click", hu = "Jobb kar kattintás", ru = "Нажатие правого стика", pl = "Kliknięcie prawej gałki"}},
   label = {en = "Pad button", hu = "Kontroller gomb", ru = "Кнопка геймпада", pl = "Przycisk pada"}},
}

local on = false
local pos, yaw, pitch, roll, fov = nil, 0, 0, 0, 60
local msg, msgTime = nil, 0

local function forward()
  return math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)
end

local function enter()
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
  rc.hud(false)
  rc.input.capture(true)
  pos = {c.pos.x, c.pos.y, c.pos.z}
  yaw = math.atan(c.dir.x, c.dir.z)
  pitch = math.asin(math.max(-1, math.min(1, c.dir.y)))
  roll = 0
  fov = rc.setting("fov", 60)
  on = true
  rc.log("photo mode on")
end

local function leave()
  rc.camera(nil)
  rc.hud(true)
  rc.input.capture(false)
  rc.pause(false)
  on = false
  rc.log("photo mode off")
end

local function togglePressed(pad)
  if rc.input.pressed("P") then return true end
  if pad then
    local b = rc.setting("padToggle", "back")
    return pad.pressed[b] == true
  end
  return false
end

function onFrame(dt)
  local pad = rc.input.pad(1)
  if not on then
    if togglePressed(pad) then enter() end
    return
  end
  if togglePressed(pad) or rc.input.pressed("Esc") then
    leave()
    return
  end
  dt = math.max(0, math.min(dt, 0.1))
  -- look
  local m = rc.input.mouse()
  local look = 0.003
  yaw = yaw + m.dx * look
  pitch = pitch - m.dy * look
  if pad then
    yaw = yaw + pad.rx * 2.0 * dt
    pitch = pitch + pad.ry * 1.5 * dt
  end
  pitch = math.max(-1.5, math.min(1.5, pitch))
  -- move
  local speed = rc.setting("speed", 6)
  if rc.input.key("Shift") or (pad and pad.buttons.ls) then speed = speed * 4 end
  local fx, fy, fz = forward()
  local rx, rz = math.cos(yaw), -math.sin(yaw)
  local mf, ms, mu = 0, 0, 0
  if rc.input.key("W") then mf = mf + 1 end
  if rc.input.key("S") then mf = mf - 1 end
  if rc.input.key("D") then ms = ms + 1 end
  if rc.input.key("A") then ms = ms - 1 end
  if rc.input.key("E") then mu = mu + 1 end
  if rc.input.key("Q") then mu = mu - 1 end
  if pad then
    mf = mf + pad.ly
    ms = ms + pad.lx
    mu = mu + pad.rt - pad.lt
  end
  local d = speed * dt
  pos[1] = pos[1] + (fx * mf + rx * ms) * d
  pos[2] = pos[2] + (fy * mf + mu) * d
  pos[3] = pos[3] + (fz * mf + rz * ms) * d
  -- roll and field of view
  if rc.input.key("Z") or (pad and pad.buttons.lb) then roll = roll - 45 * dt end
  if rc.input.key("C") or (pad and pad.buttons.rb) then roll = roll + 45 * dt end
  fov = fov - m.wheel * 5
  if pad and pad.buttons.up then fov = fov - 30 * dt end
  if pad and pad.buttons.down then fov = fov + 30 * dt end
  fov = math.max(15, math.min(120, fov))
  rc.camera{pos = pos, target = {pos[1] + fx, pos[2] + fy, pos[3] + fz}, fov = fov, roll = roll}
  -- the photo
  if rc.input.pressed("F12") or (pad and pad.pressed.a) then
    local file = rc.screenshot{hideScriptHud = true}
    local n = rc.stats.add("photos")
    msg, msgTime = "Photo " .. n .. ": " .. file, 2.5
  end
  -- help (not in the photo)
  if rc.setting("help", true) then
    rc.hudRect(0, 572, 800, 28, 0x80000000)
    rc.hudText(400, 576, "PHOTO MODE  WASD/stick move, mouse/right stick look, Q/E up/down, Z/C roll, wheel FOV, " ..
      "F12/A photo, P/Esc leave", 0xffffffff, 0.7, "center")
  end
  if msg and msgTime > 0 then
    msgTime = msgTime - dt
    rc.hudText(400, 20, msg, 0xffffd040, 0.8, "center")
  end
end

function onRaceEnd()
  on = false                                  -- (the game released the pause, HUD, capture and camera)
end

function onMenu(name)
  if name ~= "race" and on then on = false end
end

function onLoad()
  rc.log(string.format("photo_mode loaded (API %s): %d photo(s) so far", rc.version, rc.stats.get("photos", 0)))
end
