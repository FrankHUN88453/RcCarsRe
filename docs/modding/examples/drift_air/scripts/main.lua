-- Drift air: an example mod for the RcCarsRe Lua scripting, API 1.1 (docs/modding/LUA_SCRIPTING.en.md).
-- When player 1's car lands after a jump it shows the time in the air, gives a short rumble and a light-bar flash
-- (DualSense / DualShock 4), and keeps the best air time per track and the jump count with rc.stats
-- (Saves\Mods\drift_air.stats.ini next to RcCarsRe.exe). Everything it does is local to this PC.

local MIN_AIR = 0.4          -- seconds: shorter hops are not shown
local shown, shownTime = nil, 0
local flash = 0              -- seconds of light-bar flash left
local record = false

rc.options{
  {key = "hud", type = "bool", default = true,
   label = {en = "Show air time", hu = "Repülési idő kiírása", ru = "Показывать время в воздухе", pl = "Pokaż czas w powietrzu"}},
  {key = "rumble", type = "bool", default = true,
   label = {en = "Rumble on landing", hu = "Rezgés landoláskor", ru = "Вибрация при приземлении", pl = "Wibracja przy lądowaniu"}},
  {key = "flash", type = "bool", default = true,
   label = {en = "Light-bar flash", hu = "Fénysáv villanás", ru = "Вспышка световой панели", pl = "Błysk paska świetlnego"}},
}

local function isPlayer(car)
  local p = rc.player(1)
  return p ~= nil and p.index == car
end

function onLoad()
  rc.log(string.format("drift_air loaded (API %s): %d jumps so far, %.2f s in the air in total",
    rc.version, rc.stats.get("jumps", 0), rc.stats.get("airTotal", 0)))
end

function onRaceStart(info)
  shown, record = nil, false
  local best = rc.stats.get("bestAir." .. info.track)
  if best then rc.log(string.format("best air on %s: %.2f s", info.track, best)) end
end

function onJump(car)
  if isPlayer(car) then rc.log("jump") end
end

function onLand(car, air)
  if not isPlayer(car) or air < MIN_AIR then return end
  local track = rc.race().track
  local key = "bestAir." .. track
  local best = rc.stats.get(key, 0)
  record = air > best
  if record then rc.stats.set(key, air) end
  rc.stats.add("jumps", 1)
  rc.stats.add("airTotal", air)
  shown, shownTime = air, 2.0
  rc.log(string.format("landed after %.2f s in the air%s", air, record and " (new record)" or ""))
  if rc.setting("rumble", true) then
    rc.rumble(math.min(1, 0.3 + air / 2), 0.25)
  end
  if rc.setting("flash", true) then
    if record then rc.lightBar(255, 200, 0) else rc.lightBar(255, 255, 255) end
    flash = 0.3
  end
end

function onFrame(dt)
  if flash > 0 then
    flash = flash - dt
    if flash <= 0 then rc.lightBar(nil) end      -- the game's colour again
  end
  if shown and shownTime > 0 then
    shownTime = shownTime - dt
    if rc.setting("hud", true) and rc.race().state == "racing" then
      local text = string.format("AIR %.2f s", shown)
      if record then text = text .. "  NEW RECORD" end
      rc.hudText(400, 120, text, record and 0xffffd040 or 0xffffffff, 1.5, "center")
    end
  end
end

function onRaceEnd(results)
  rc.log(string.format("race over: %d jumps, %.2f s in the air in total", rc.stats.get("jumps", 0),
    rc.stats.get("airTotal", 0)))
end
