-- Lap time HUD: an example mod for the RcCarsRe Lua scripting (docs/modding/LUA_SCRIPTING.en.md), API 1.1.
-- Shows player 1's race time (the same value as the HUD's top timer), the current lap, the last lap and the best
-- lap in a box on the race screen, in the game's own time format (rc.formatTime).
-- Note: like the game, a lap time counts from the start/finish line, so lap 1 starts when the car crosses the
-- line after GO (a second or more after the race timer started).
-- Its options appear on the Mods screen (Settings) and are stored in Saves\Mods\laptime_hud.ini.

local last, best = nil, nil

rc.options{
  {key = "showBest", type = "bool", default = true,
   label = {en = "Show best lap", hu = "Legjobb kör", ru = "Лучший круг", pl = "Najlepsze okrążenie"}},
  {key = "size", type = "slider", min = 0.5, max = 2, step = 0.25, default = 1,
   label = {en = "Text size", hu = "Betűméret", ru = "Размер текста", pl = "Rozmiar tekstu"}},
  {key = "corner", type = "enum", values = {"left", "right"}, default = "left",
   labels = {{en = "Left", hu = "Bal", ru = "Слева", pl = "Lewo"}, {en = "Right", hu = "Jobb", ru = "Справа", pl = "Prawo"}},
   label = {en = "Position", hu = "Hely", ru = "Положение", pl = "Pozycja"}},
}

local function fmt(t)
  if not t then return "--:--.--" end
  return rc.formatTime(t)
end

function onLoad()
  rc.log("laptime_hud loaded, API " .. rc.version)
end

function onRaceStart(info)
  last, best = nil, nil
  rc.log("race on " .. info.track .. ", " .. info.laps .. " laps, " .. info.cars .. " cars")
end

function onLap(car, lap, lapTime)
  local p = rc.player(1)
  if p and p.index == car then
    last = lapTime
    if not best or lapTime < best then best = lapTime end
    rc.log(string.format("lap %d: %s", lap, fmt(lapTime)))
  end
end

function onOptionChanged(key, value)
  rc.log("option " .. key .. " = " .. tostring(value))
end

function onFrame(dt)
  local race = rc.race()
  if race.state ~= "racing" and race.state ~= "finished" then return end
  local p = rc.player(1)
  if not p then return end
  local size = rc.setting("size", 1)
  local right = rc.setting("corner", "left") == "right"
  local showBest = rc.setting("showBest", true)
  local w, lh = 190 * size, 20 * size
  local x = right and (790 - w) or 10
  local y = 210
  local lines = 3 + (showBest and 1 or 0)
  rc.hudRect(x, y, w, lh * lines + 8, 0x90000000)
  rc.hudText(x + 6, y + 4, "Race: " .. fmt(race.time), 0xffffffff, size)
  -- lap 0: the car has not crossed the start line yet
  rc.hudText(x + 6, y + 4 + lh, "Lap " .. p.lap .. ": " .. (p.lap > 0 and fmt(p.lapTime) or "--:--.--"), 0xffffffff, size)
  rc.hudText(x + 6, y + 4 + 2 * lh, "Last: " .. fmt(last), 0xffd0d0d0, size)
  if showBest then
    rc.hudText(x + 6, y + 4 + 3 * lh, "Best: " .. fmt(best), 0xffffff40, size)
  end
end
