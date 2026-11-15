-- Checkpoint sound: an example mod for the RcCarsRe Lua scripting (docs/modding/LUA_SCRIPTING.en.md).
-- Plays the mod's own sounds\ding.wav when player 1 passes a checkpoint, and flashes the checkpoint's number.

local flash, shown = 0, 0

rc.options{
  {key = "volume", type = "slider", min = 0, max = 100, step = 10, default = 80,
   label = {en = "Ding volume", hu = "Hangerő", ru = "Громкость", pl = "Głośność"}},
}

function onCheckpoint(car, index)
  local p = rc.player(1)
  if not p or p.index ~= car then return end
  rc.playSound("ding", rc.setting("volume", 80) / 100)
  flash, shown = 1.0, index
end

function onFrame(dt)
  if flash <= 0 then return end
  flash = flash - dt
  local a = math.floor(math.max(flash, 0) * 255)
  rc.hudText(400, 120, "Checkpoint " .. shown, (a << 24) | 0x40ff40, 1.5, "center")
end
