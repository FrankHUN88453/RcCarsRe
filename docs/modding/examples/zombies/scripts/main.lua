-- Zombies: a tag / infection game mode (Lua API 1.4).
-- Everyone gets a head start; then one car (the player's or an AI's) becomes the zombie: it turns into a
-- Warhammer in its green camouflage paint (and drives like one). A grey-green fog hangs over the round.
-- A zombie that touches a survivor infects it. The zombies win when everyone is infected; the survivors
-- win when the time runs out. Pick "Zombies" in the Quick race's Mode row.

local ID = "zombies"

-- every text in the four languages of the game (rc.text / the API pick the current one, English as the fallback)
local T = {
  name        = {en = "Zombies", hu = "Zombik", ru = "Зомби", pl = "Zombie"},
  description = {en = "Run from the zombies! A zombie that touches you makes you one of them.",
                 hu = "Menekülj a zombik elől! Ha egy zombi hozzád ér, te is zombi leszel.",
                 ru = "Убегай от зомби! Если зомби коснётся тебя, ты станешь одним из них.",
                 pl = "Uciekaj przed zombie! Gdy zombie cię dotknie, staniesz się jednym z nich."},
  run         = {en = "Run!", hu = "Fuss!", ru = "Беги!", pl = "Uciekaj!"},
  outbreak    = {en = "Outbreak!", hu = "Járvány!", ru = "Заражение!", pl = "Epidemia!"},
  isZombie    = {en = "%s is the zombie!", hu = "%s a zombi!", ru = "%s — зомби!", pl = "%s jest zombie!"},
  youZombie   = {en = "You are the zombie! Catch them!", hu = "Te vagy a zombi! Kapd el őket!",
                 ru = "Ты зомби! Лови их!", pl = "Jesteś zombie! Łap ich!"},
  infected    = {en = "%s infected %s!", hu = "%s megfertőzte: %s!", ru = "%s заразил: %s!", pl = "%s zaraził: %s!"},
  youInfected = {en = "You are infected!", hu = "Megfertőződtél!", ru = "Ты заражён!", pl = "Zostałeś zarażony!"},
  survivor    = {en = "Survivor", hu = "Túlélő", ru = "Выживший", pl = "Ocalały"},
  zombie      = {en = "Zombie", hu = "Zombi", ru = "Зомби", pl = "Zombie"},
  survived    = {en = "Survived", hu = "Túlélte", ru = "Выжил", pl = "Przeżył"},
  patientZero = {en = "Patient zero", hu = "A nulladik beteg", ru = "Нулевой пациент", pl = "Pacjent zero"},
  infectedAt  = {en = "Infected at %s", hu = "Fertőzés: %s", ru = "Заражён в %s", pl = "Zarażony w %s"},
  zombiesWin  = {en = "Zombies win!", hu = "A zombik nyertek!", ru = "Зомби победили!", pl = "Zombie wygrywają!"},
  survivorsWin = {en = "Survivors win!", hu = "A túlélők nyertek!", ru = "Выжившие победили!",
                  pl = "Ocalali wygrywają!"},
  timeLimit   = {en = "Time limit (minutes)", hu = "Időkorlát (perc)", ru = "Лимит времени (минуты)",
                 pl = "Limit czasu (minuty)"},
  headStart   = {en = "Head start (seconds)", hu = "Előny (másodperc)", ru = "Фора (секунды)",
                 pl = "Przewaga (sekundy)"},
  contact     = {en = "Infection contact (km/h)", hu = "Fertőző ütközés (km/h)", ru = "Заражающий контакт (км/ч)",
                 pl = "Zarażający kontakt (km/h)"},
  fogOn       = {en = "Zombie fog", hu = "Zombiköd", ru = "Зомби-туман", pl = "Mgła zombie"},
  fogStrength = {en = "Fog strength", hu = "Köd sűrűsége", ru = "Плотность тумана", pl = "Gęstość mgły"},
  aggression  = {en = "Zombie AI aggression", hu = "Zombi MI agresszivitása", ru = "Агрессия ИИ-зомби",
                 pl = "Agresja SI zombie"},
  ambient     = {en = "Ambient sound", hu = "Háttérhang", ru = "Фоновый звук", pl = "Dźwięk tła"},
  ambientVol  = {en = "Ambient volume", hu = "Háttérhang hangereje", ru = "Громкость фона", pl = "Głośność tła"},
  caution     = {en = "Survivor AI caution", hu = "Túlélő MI óvatossága", ru = "Осторожность ИИ-выживших",
                 pl = "Ostrożność SI ocalałych"},
  heartbeat   = {en = "Heartbeat", hu = "Szívverés", ru = "Сердцебиение", pl = "Bicie serca"},
  heartRange  = {en = "Heartbeat range (m)", hu = "Szívverés hatótávja (m)", ru = "Дальность сердцебиения (м)",
                 pl = "Zasięg bicia serca (m)"},
  out         = {en = "Out", hu = "Kiesett", ru = "Выбыл", pl = "Odpadł"},
  outAt       = {en = "Out at %s", hu = "Kiesett: %s", ru = "Выбыл в %s", pl = "Odpadł w %s"},
  fellOut     = {en = "%s fell out!", hu = "%s kiesett!", ru = "%s выпал!", pl = "%s wypadł!"},
  drowned     = {en = "%s was taken by the deep!", hu = "%s-t elnyelte a mélység!", ru = "%s утянула пучина!",
                 pl = "%s pochłonęła głębia!"},
  fallRule    = {en = "A survivor who falls out", hu = "Kieső túlélő", ru = "Выпавший выживший", pl = "Ocalały, który wypadnie"},
  fallZombie  = {en = "becomes a zombie", hu = "zombi lesz", ru = "становится зомби", pl = "staje się zombie"},
  fallOut     = {en = "is out", hu = "kiesik", ru = "выбывает", pl = "odpada"},
  backDelay   = {en = "Zombie back on the road after (s)", hu = "Zombi vissza az útra (mp)",
                 ru = "Зомби обратно на дорогу через (с)", pl = "Zombie z powrotem na drogę po (s)"},
  endShot     = {en = "End camera", hu = "Zárókamera", ru = "Финальная камера", pl = "Kamera końcowa"},
  board       = {en = "Scoreboard", hu = "Eredménytábla", ru = "Таблица", pl = "Tabela wyników"},
  byWhom      = {en = "caught by %s", hu = "elkapta: %s", ru = "поймал %s", pl = "złapał %s"},
  lastOne     = {en = "Last survivor: %s", hu = "Utolsó túlélő: %s", ru = "Последний выживший: %s",
                 pl = "Ostatni ocalały: %s"},
  status      = {en = "Survivors: %d / Zombies: %d", hu = "Túlélők: %d / Zombik: %d", ru = "Выжившие: %d / Зомби: %d",
                 pl = "Ocalali: %d / Zombie: %d"},
  youAre      = {en = "You: %s", hu = "Te: %s", ru = "Ты: %s", pl = "Ty: %s"},
  totals      = {en = "%d survivor(s), %d zombie(s), %d out", hu = "%d túlélő, %d zombi, %d kiesett",
                 ru = "Выживших: %d, зомби: %d, выбыло: %d", pl = "Ocalałych: %d, zombie: %d, odpadło: %d"},
  best        = {en = "Your best survival: %s", hu = "A legjobb túlélésed: %s", ru = "Твой рекорд выживания: %s",
                 pl = "Twój rekord przetrwania: %s"},
}

local GREEN = 0x40ff40
local ZOMBIE_CAR = {model = "Warhammer", paint = 4}   -- the Warhammer's green camouflage paint (car_askin34)
local FOG_COLOR = 0x56614f                            -- grey-green; the sky behind the fog darkens with it

rc.registerMode{
  id = ID, name = T.name, description = T.description,
  minCars = 2, maxCars = 6, checkpoints = false, laps = false, ai = "script",
  respawn = false,                      -- no car is put back by the game: onRespawnBlocked below decides
  hud = {racerList = false, place = false, lap = false, wrongWay = false},   -- the map, speedo, boost stay
}

rc.options{
  {key = "timeLimit", type = "slider", label = T.timeLimit, min = 1, max = 10, step = 1, default = 5},
  {key = "headStart", type = "slider", label = T.headStart, min = 3, max = 30, step = 1, default = 10},
  {key = "contact", type = "slider", label = T.contact, min = 0, max = 30, step = 1, default = 3},
  {key = "fog", type = "bool", label = T.fogOn, default = true},
  {key = "fogStrength", type = "slider", label = T.fogStrength, min = 1, max = 10, step = 1, default = 5},
  {key = "aggression", type = "slider", label = T.aggression, min = 1, max = 10, step = 1, default = 7},
  {key = "caution", type = "slider", label = T.caution, min = 1, max = 10, step = 1, default = 5},
  {key = "ambient", type = "bool", label = T.ambient, default = true},
  {key = "ambientVolume", type = "slider", label = T.ambientVol, min = 0, max = 100, step = 5, default = 50},
  {key = "heartbeat", type = "bool", label = T.heartbeat, default = true},
  {key = "heartRange", type = "slider", label = T.heartRange, min = 10, max = 80, step = 5, default = 40},
  {key = "fallRule", type = "enum", label = T.fallRule, values = {"zombie", "out"},
   labels = {T.fallZombie, T.fallOut}, default = "zombie"},
  {key = "backDelay", type = "slider", label = T.backDelay, min = 1, max = 10, step = 1, default = 3},
  {key = "endShot", type = "bool", label = T.endShot, default = true},
}

-- The mod's sounds (in its sounds\ folder; they are the mod author's own files and are not part of the public
-- example: bring your own; a missing one is skipped with a warning in the log):
--   zombie_ambient.mp3   the round's ambience (it replaces the level's own and the race music: rc.levelAmbient)
--   thunder01.wav        a new zombie, heard from where it happened all over the track
--   zombie_attack*.wav   the infecting contact, at both cars (one at random, never the same twice in a row)
--   heart_beat.wav       a survivor's heartbeat from the nearest zombie's direction, faster as it comes nearer
--   zombie_outro.mp3     the zombies win
--   humans_win.wav       the survivors win

-- the ambient sound, looped from the race's first frame through the end screen in place of the level's ambience
-- and the race music; the game stops it and gives those back when the race is left
local AMBIENT = "zombie_ambient"
local ambient
local function ambientStart()
  if ambient then rc.stopSound(ambient); ambient = nil end
  if not rc.setting("ambient", true) then return end
  local vol = rc.setting("ambientVolume", 50) / 100
  if vol <= 0 then return end
  ambient = rc.playSound(AMBIENT, {loop = true, volume = vol}) or nil
end

-- the round
local S                          -- nil outside a round

local function fmt(t, ...)       -- a localized text with arguments
  return string.format(rc.text(t), ...)
end

local function name(car)
  return rc.carName(car)
end

local function survivors()
  local list = {}
  for i = 1, S.cars do if not S.zombie[i] and not S.out[i] then list[#list + 1] = i end end
  return list
end

local function zombies()
  local list = {}
  for i = 1, S.cars do if S.zombie[i] then list[#list + 1] = i end end
  return list
end

-- the fog: from the race's first frame (onModeLoad), denser as the survivors get fewer (density per metre; the
-- game's levels use 0.006 .. 0.026). It stays on the end screen; the game resets it when the race is left.
local fogDensity, fogWarned
local function setFog(infected)            -- infected: 0 .. 1 of the cars
  if not rc.setting("fog", true) then return end
  local d = (0.012 + rc.setting("fogStrength", 5) * 0.006) * (1.0 + 0.6 * infected)
  if d > 0.12 then d = 0.12 end
  if fogDensity and math.abs(d - fogDensity) < 0.0005 then return end
  fogDensity = d
  if not rc.fog{color = FOG_COLOR, density = d} and not fogWarned then
    fogWarned = true
    rc.log("ZOMBIES: the game's fog is off in the Video options: no zombie fog")
  end
end

local function fog()
  setFog(1.0 - #survivors() / S.cars)
end

local attacks, lastAttack = {}, nil     -- the zombie_attack*.wav files there are

function onModeLoad(info)
  if info.id ~= ID then return end
  fogDensity = nil
  setFog(0.0)
  rc.levelAmbient(false, -100)          -- the level's ambience and the race music off for the round
  ambientStart()
  -- the people and the seagulls in zombie skins (skins\ of the mod, the user's own pictures, not in the public
  -- example), for this mode's races only: the game gives its own pictures back when the race is left
  for _, tex in ipairs({"man_1new", "man_2new", "woman_1new", "woman_2new", "seagullsitting"}) do
    rc.replaceTexture(tex, "skins\\" .. tex .. ".png")
  end
  attacks = rc.listModFiles("sounds", "zombie_attack*.wav")
  rc.log(string.format("ZOMBIES: %d attack sound(s)", #attacks))
end

function onMenu(name)                    -- (the race was left: the game has stopped the sound already)
  if name ~= "race" and name ~= "pause" and name ~= "results" then ambient = nil end
end

-- the AI orders: a zombie chases the nearest survivor it can reach by the road (the game picks it and switches only
-- when another gets clearly nearer); a survivor flees from all zombies, keeping "caution" metres of clearance
local function orders()
  local zs, ss = zombies(), survivors()
  local speed = 0.7 + 0.03 * rc.setting("aggression", 7)      -- 0.73 .. 1.0 of the throttle
  local caution = 2 + 1.2 * rc.setting("caution", 5)          -- 3.2 .. 14 m
  for i = 1, S.cars do
    if i ~= S.player then
      if S.out[i] then
        rc.ai(i, {mode = "stop"})
      elseif S.zombie[i] then
        if #ss > 0 then rc.ai(i, {mode = "chase", targets = ss, speed = speed})
        else rc.ai(i, {mode = "stop"}) end
      elseif #zs > 0 then
        rc.ai(i, {mode = "flee", from = zs, caution = caution})
      elseif not S.out[i] then
        rc.ai(i, {mode = "flee", caution = caution})   -- (no zombie yet: away from everyone, spread out)
      else
        rc.ai(i, {mode = "stop"})
      end
    end
  end
end

-- the thunder of a new zombie where it happened, heard over the whole track (full within 15 m, -20 dB at 400 m and
-- never lower), with a short lightning flash; the game's sound when the mod has none
local flashUntil = 0
local function thunder(car, fallback)
  local c = rc.car(car)
  if not rc.playSound("thunder01", {pos = {c.x, c.y, c.z}, minDist = 15, maxDist = 400}) then
    rc.playSound(fallback)
  end
  flashUntil = rc.mode.clock() + 0.3
end

-- the infecting contact: one of the attack sounds at both cars (3D, each where its car is)
local function attackSound(z, s)
  if #attacks == 0 then return end
  local k = math.random(1, #attacks)
  if #attacks > 1 and attacks[k] == lastAttack then k = k % #attacks + 1 end
  lastAttack = attacks[k]
  local snd = "sounds\\" .. attacks[k]
  rc.playSound(snd, {car = z, minDist = 6, maxDist = 80})
  rc.playSound(snd, {car = s, minDist = 6, maxDist = 80})
end

-- the heartbeat of the player while a survivor: from the nearest zombie's direction, within heartRange metres; one
-- beat every 1.2 s at the edge down to every 0.35 s close by, louder as it comes nearer, a light rumble each beat
local beatAt, beat = 0, nil
local function heartStop()
  if beat then rc.stopSound(beat); beat = nil end
end

local function heartbeat(now)
  if not rc.setting("heartbeat", true) or S.zombie[S.player] then return end
  local best, bd
  for _, z in ipairs(zombies()) do
    local d = rc.distance(S.player, z)
    if not bd or d < bd then best, bd = z, d end
  end
  local range = rc.setting("heartRange", 40)
  if not best or bd > range or now < beatAt then return end
  local k = 1 - bd / range                      -- 0 at the edge .. 1 at the zombie
  local interval, vol = 1.2 - 0.85 * k, 0.3 + 0.7 * k
  local z = rc.car(best)
  heartStop()                                   -- (one beat at a time)
  beat = rc.playSound("heart_beat", {volume = vol, panTo = {z.x, z.y, z.z}}) or nil
  beatAt = now + interval
  rc.rumble(0.15 + 0.35 * k, 0.08)
  rc.log(string.format("ZOMBIES: heartbeat: zombie %d at %.1f m, a beat every %.2f s, volume %.2f", best, bd,
                       interval, vol))
end

local function infect(car, by, fell)
  if S.zombie[car] then return end
  S.zombie[car] = true
  S.when[car] = rc.mode.clock()
  S.by[car] = by
  rc.setCar(car, ZOMBIE_CAR)
  rc.setCarTeam(car, 1)
  rc.mode.listText(car, T.zombie, GREEN)
  rc.mode.freeze(car, true)              -- the infection takes hold: a short stop
  S.thaw[car] = rc.mode.clock() + (by and 1.5 or 3.0)
  if by then
    rc.log(string.format("ZOMBIES: %.2f s: racer %d (%s) infected racer %d (%s)", S.when[car], by, name(by), car,
                         name(car)))
    rc.mode.message(car == S.player and T.youInfected or fmt(T.infected, name(by), name(car)), 3, GREEN)
    attackSound(by, car)
    thunder(car, "dog_attack")
  elseif fell then
    rc.log(string.format("ZOMBIES: %.2f s: racer %d (%s) fell out and turned", S.when[car], car, name(car)))
    S.by[car] = 0
    thunder(car, "dog_attack")
  else
    rc.log(string.format("ZOMBIES: %.2f s: racer %d (%s) is patient zero", S.when[car], car, name(car)))
    rc.mode.message(car == S.player and T.youZombie or fmt(T.isZombie, name(car)), 4, GREEN)
    thunder(car, "roadcar_siren")
  end
  if car == S.player then
    heartStop()
    rc.lightBar(0, 255, 0)
    rc.rumble(1.0, 0.6)
  end
  orders()
  fog()
end

local cinematicStart                  -- (below)

local function finish(zombiesWon)
  if S.over then return end
  S.over = true
  local res = {}
  for _, s in ipairs(survivors()) do
    res[#res + 1] = {car = s, text = T.survived, order = 1e9}
  end
  for i = 1, S.cars do
    if S.out[i] then res[#res + 1] = {car = i, text = fmt(T.outAt, rc.formatTime(S.outAt[i], "short")),
                                      order = S.outAt[i] - 1000} end
  end
  for _, z in ipairs(zombies()) do        -- the later infected, the better
    local text = S.by[z] and fmt(T.infectedAt, rc.formatTime(S.when[z], "short")) or rc.text(T.patientZero)
    res[#res + 1] = {car = z, text = text, order = S.when[z]}
  end
  table.sort(res, function(a, b) return a.order > b.order end)
  for i, r in ipairs(res) do r.place = i end
  local verdict = zombiesWon and T.zombiesWin or T.survivorsWin
  rc.log(string.format("ZOMBIES: %.2f s: %s (%d survivor(s), %d zombie(s))", rc.mode.clock(), rc.text(verdict),
                       #survivors(), #zombies()))
  rc.mode.message(verdict, 5, zombiesWon and GREEN or 0xffd040)
  heartStop()
  -- the ending's sound (the zombies' outro or the survivors' win): the ambient stops so it is clear; it plays
  -- over the end shot and the results until it ends or the race is left (the race music stays muted)
  if ambient then rc.stopSound(ambient); ambient = nil end
  S.endSound = rc.playSound(zombiesWon and "zombie_outro" or "humans_win", {volume = 1.0}) or nil
  rc.stats.add("rounds")
  if S.zombie[S.player] and zombiesWon then rc.stats.add("winsAsZombie") end
  if not S.zombie[S.player] and not zombiesWon then rc.stats.add("winsAsSurvivor") end
  local shot = rc.setting("endShot", true) and not rc.screen().vr
  S.verdict = verdict
  rc.mode.finish(res, rc.text(verdict))   -- (the results' title: the verdict alone, it fits the column)
  if shot then                           -- the end can not be skipped: the shot (18 / 20 s) or the ending's sound,
    rc.mode.holdEnd{seconds = 30, skippable = false}   -- whichever is longer, at most 30 s
    cinematicStart(zombiesWon)
  end
end

function onModeStart(info)
  if info.id ~= ID then return end
  if rc.setting("testShots", false) then rc.screenshot{hideScriptHud = false} end   -- (test aid: GO)
  local minutes = rc.setting("timeLimit", 5)
  local test = rc.setting("testSeconds", 0)     -- (a test aid: a shorter round, not on the Settings page)
  S = {cars = info.cars, player = info.player, zombie = {}, when = {}, by = {}, thaw = {}, over = false,
       out = {}, outAt = {}, back = {},
       headStart = rc.setting("headStart", 10), contact = rc.setting("contact", 3),
       limit = test > 0 and test or minutes * 60, started = false, next = 0}
  rc.log(string.format("ZOMBIES: round start on %s: %d car(s), head start %d s, time limit %d s", info.track,
                       info.cars, S.headStart, S.limit))
  for i = 1, S.cars do rc.mode.listText(i, T.survivor) end
  rc.mode.message(T.run, 2.5, 0xffd040)
  rc.mode.countdown(S.headStart, T.outbreak)
  rc.lightBar(nil)
  orders()
  fog()
end

function onModeFrame(dt)
  if not S or S.over then return end
  local now = rc.mode.clock()
  if not S.started then
    if now < S.headStart then return end
    S.started = true
    local first = rc.setting("testZombie", 0)  -- (a test aid: patient zero's car, not on the Settings page)
    first = (first >= 1 and first <= S.cars) and first or math.random(1, S.cars)
    infect(first, nil)
    if rc.setting("testCamera", false) then S.camera = first end
    rc.mode.timer(S.limit)
  end
  if now < flashUntil then             -- (the flash: white, fading out over 0.3 s)
    local a = math.floor(110 * (flashUntil - now) / 0.3)
    rc.hudRect(0, 0, 800, 600, (a << 24) | 0xffffff)
  end
  if S.camera then                     -- (a test aid, testCamera: the camera behind the first zombie)
    rc.camera{car = S.camera, offset = {0, 0.9, -2.2}}
  end
  for car, t in pairs(S.back) do
    if now >= t then
      S.back[car] = nil
      rc.mode.respawnCar(car)
      rc.log(string.format("ZOMBIES: %.2f s: zombie %d back on the road", now, car))
    end
  end
  for car, t in pairs(S.thaw) do
    if now >= t then rc.mode.freeze(car, false); S.thaw[car] = nil end
  end
  if S.contact <= 0 then                 -- (threshold 0: every touch of the frame counts)
    for _, z in ipairs(zombies()) do
      for _, c in ipairs(rc.car(z).contacts) do
        if not S.zombie[c] and not S.thaw[z] then infect(c, z) end
      end
    end
  end
  if #survivors() == 0 then finish(true) return end
  heartbeat(now)
  if now >= S.next then S.next = now + 1.0; orders() end
end

function onCollision(a, b, strength, kind)
  if not S or S.over or not S.started or kind ~= "car" or rc.mode.active() ~= ID then return end
  if strength < S.contact then return end
  if S.zombie[a] and not S.zombie[b] and not S.thaw[a] then infect(b, a)
  elseif S.zombie[b] and not S.zombie[a] and not S.thaw[b] then infect(a, b) end
  if #survivors() == 0 then finish(true) end
end

function onModeTimer()
  if S and not S.over then finish(false) end
end

function onModeEnd()
  rc.lightBar(nil)
end

function onRaceEnd()
  if S then rc.lightBar(nil) end
end

-- ---- the game puts no car back in this mode (respawn = false); the mode's rules instead ----
-- a survivor who falls into deep water or off the track becomes a zombie there (fallRule "zombie") or is out
-- ("out"); a zombie is put back on the nearest road point backDelay seconds later; a flip, the Reset key and a stuck
-- car are ignored: the game sets a car on its side upright where it is
function onRespawnBlocked(car, reason)
  if not S or S.over or not S.started then return end
  rc.log(string.format("ZOMBIES: %.2f s: racer %d (%s): respawn blocked (%s)", rc.mode.clock(), car, name(car), reason))
  if reason ~= "water" and reason ~= "bounds" and reason ~= "zone" then return end
  if not S.zombie[car] and not S.out[car] then
    if rc.setting("fallRule", "zombie") == "out" then
      S.out[car] = true
      S.outAt[car] = rc.mode.clock()
      rc.mode.listText(car, T.out, 0x909090)
      rc.mode.freeze(car, true)
      rc.mode.message(fmt(T.fellOut, name(car)), 3, 0xffd040)
      if #survivors() == 0 then finish(#zombies() > 0) end
      return
    end
    rc.mode.message(fmt(T.drowned, name(car)), 3, GREEN)
    infect(car, nil, true)
  end
  if S.zombie[car] and not S.back[car] then
    S.back[car] = rc.mode.clock() + rc.setting("backDelay", 3)
  end
end

-- ---- the round's own status in place of the racer list: the counts, the time left, the player's role ----
local function statusHud()
  if not S or S.over or rc.race().state ~= "racing" then return end
  local role = S.out[S.player] and T.out or S.zombie[S.player] and T.zombie or T.survivor
  rc.hudRect(10, 78, 190, 70, 0x90000000)
  rc.hudText(18, 84, fmt(T.status, #survivors(), #zombies()), 0xffffffff, 0.9)
  local left = rc.mode.timeLeft()
  if left then rc.hudText(18, 106, rc.formatTime(left, "short"), left < 10 and 0xffff4040 or 0xffffd040, 0.9) end
  rc.hudText(18, 126, fmt(T.youAre, rc.text(role)), S.zombie[S.player] and (0xff000000 | GREEN) or 0xffc8c8c8, 0.9)
end

-- ---- the end shot: a slow camera over the scene while a scoreboard slides in, then the results ----
-- the zombies win: from close above the last victim the camera rises and drifts backwards over the zombies, the
-- view tilted down, a slight roll and a narrowing field of view; the survivors win: a calm orbit round them. After
-- the shot a slow drift goes on until the race is left. It can not be skipped (rc.mode.holdEnd): the results page
-- comes when the shot and the ending's sound are over (at most 30 s). Not in VR (the results come at once there).
local C                               -- the shot's state, nil when none

local function centre(list)
  local x, y, z, n = 0, 0, 0, 0
  for _, i in ipairs(list) do
    local c = rc.car(i)
    if c then x, y, z, n = x + c.x, y + c.y, z + c.z, n + 1 end
  end
  if n == 0 then return nil end
  return {x / n, y / n, z / n}
end

local function orbit(ctr, radius, height, from, turn, n, fov)
  local pts = {}
  for k = 0, n - 1 do
    local a = from + turn * k / (n - 1)
    pts[#pts + 1] = {pos = {ctr[1] + radius * math.sin(a), ctr[2] + height, ctr[3] + radius * math.cos(a)},
                     target = {ctr[1], ctr[2] + 0.3, ctr[3]}, fov = fov}
  end
  return pts
end

cinematicStart = function(zombiesWon)
  local now = rc.mode.clock()
  C = {t0 = now, zombies = zombiesWon, drift = false}
  rc.hud(false)
  if zombiesWon then
    local last, lt = nil, -1
    for i = 1, S.cars do if S.zombie[i] and S.when[i] > lt then last, lt = i, S.when[i] end end
    local v = rc.car(last or 1)
    local ctr = centre(zombies()) or {v.x, v.y, v.z}
    local dx, dz = v.x - ctr[1], v.z - ctr[3]          -- away from the crowd, past the victim
    local l = math.sqrt(dx * dx + dz * dz)
    if l < 0.5 then dx, dz, l = 0, 1, 1 end
    dx, dz = dx / l, dz / l
    C.centre = ctr
    rc.cameraPath{duration = 18, ease = "inout", blend = 1.0, points = {
      {pos = {v.x - dz * 0.6, v.y + 1.2, v.z + dx * 0.6}, target = {v.x, v.y, v.z}, fov = 62},
      {pos = {v.x + dx * 2.5, v.y + 3.0, v.z + dz * 2.5}, target = {v.x, v.y, v.z}, fov = 58, roll = 1},
      {pos = {v.x + dx * 6, v.y + 6.5, v.z + dz * 6}, target = {(v.x + ctr[1]) / 2, ctr[2], (v.z + ctr[3]) / 2},
       fov = 52, roll = 2},
      {pos = {ctr[1] + dx * 13, ctr[2] + 11, ctr[3] + dz * 13}, target = {ctr[1], ctr[2], ctr[3]}, fov = 44, roll = 3},
    }}
  else
    local ctr = centre(survivors()) or {rc.car(1).x, rc.car(1).y, rc.car(1).z}
    C.centre = ctr
    rc.cameraPath{duration = 20, ease = "linear", blend = 1.5, points = orbit(ctr, 6, 2.5, 0, math.pi * 1.5, 8, 55)}
  end
  -- the personal record: the player's survival time
  local mine = S.zombie[S.player] and S.when[S.player] or (S.out[S.player] and S.outAt[S.player]) or now
  C.mine = mine
  C.best = rc.stats.get("bestSurvival", 0)
  if mine > C.best then rc.stats.set("bestSurvival", mine); C.best = mine; C.record = true end
  rc.log(string.format("ZOMBIES: end shot (%s), the player survived %.1f s (best %.1f s)",
                       zombiesWon and "the zombies' rise" or "an orbit of the survivors", mine, C.best))
end

-- the verdict as the title at the top and the scoreboard under it, both centred on the 800 x 600 HUD (so on every
-- resolution and aspect): every car by its survival, who caught whom, the last survivor, the totals, the record;
-- the board fades and rises in after 2 s, its columns measured with rc.textWidth
local function scoreboard(t)
  local title = rc.text(S.verdict or T.name)
  rc.hudText(400, 66, title, S.zombie[S.player] and S.verdict == T.zombiesWin and (0xff000000 | GREEN) or 0xffffd040,
             2.0, {align = "center"})
  local k = math.min(1, math.max(0, (t - 2.0) / 0.6))
  if k <= 0 then return end
  local rows = {}
  local wName, wHow = rc.textWidth(rc.text(T.board), 1.3), 0
  for i = 1, S.cars do
    local surv = S.zombie[i] and S.when[i] or (S.out[i] and S.outAt[i]) or C.t0
    local how
    if S.out[i] then how = rc.text(T.out)
    elseif S.zombie[i] and S.by[i] and S.by[i] > 0 then how = fmt(T.byWhom, name(S.by[i]))
    elseif S.zombie[i] and S.by[i] == 0 then how = rc.text(T.zombie)
    elseif S.zombie[i] then how = rc.text(T.patientZero)
    else how = rc.text(T.survived) end
    rows[#rows + 1] = {car = i, surv = surv, how = how}
    wName = math.max(wName, rc.textWidth(name(i)))
    wHow = math.max(wHow, rc.textWidth(how, 0.85))
  end
  table.sort(rows, function(a, b) return a.surv > b.surv end)
  local last, lt = nil, -1
  for i = 1, S.cars do
    local surv = S.zombie[i] and S.when[i] or (S.out[i] and S.outAt[i]) or 1e9
    if surv > lt then last, lt = i, surv end
  end
  local nOut = 0
  for i = 1, S.cars do if S.out[i] then nOut = nOut + 1 end end
  local foot = {
    {last and fmt(T.lastOne, name(last)) or "", 0xffffd040},
    {fmt(T.totals, #survivors(), #zombies(), nOut), 0xffc8c8c8},
    {fmt(T.best, rc.formatTime(C.best, "short")), C.record and 0xff60ff60 or 0xffc8c8c8},
  }
  local w = wName + 70 + wHow
  for _, f in ipairs(foot) do w = math.max(w, rc.textWidth(f[1], 0.9)) end
  w = math.min(w, 760)
  local x = 400 - w / 2
  local top = 112 + 20 * (1 - k)                  -- rises into place
  local function fade(c) return (math.floor(((c >> 24) & 255) * k) << 24) | (c & 0xffffff) end
  local h = 96 + 26 * #rows
  rc.hudRect(x - 14, top, w + 28, h, (math.floor(0xa0 * k) << 24))
  rc.hudText(400, top + 6, rc.text(T.board), fade(0xffffd040), 1.3, {align = "center"})
  for n, r in ipairs(rows) do
    local y = top + 40 + 26 * (n - 1)
    local col = r.car == S.player and 0xffffffff or 0xffc8c8c8
    rc.hudText(x, y, name(r.car), fade(col))
    rc.hudText(x + wName + 60, y, rc.formatTime(r.surv, "short"), fade(col), 1, {align = "right"})
    rc.hudText(x + wName + 70, y, r.how, fade(S.zombie[r.car] and (0xff000000 | GREEN) or col), 0.85)
  end
  local y = top + 48 + 26 * #rows
  for n, f in ipairs(foot) do
    rc.hudText(400, y + 20 * (n - 1), f[1], fade(f[2]), 0.9, {align = "center"})
  end
end

function onFrame(dt)
  statusHud()
  if not C then return end
  if rc.race().state == "menu" then C = nil return end     -- (the race was left)
  local t = rc.mode.clock() - C.t0
  if rc.setting("testShots", false) then  -- (a test aid: pictures of the end shot at 0, 5, 10 and 15 s)
    for _, at in ipairs({0.2, 5, 10, 15}) do
      if t >= at and not C["shot" .. at] then C["shot" .. at] = true; rc.screenshot{hideScriptHud = false} end
    end
  end
  rc.hudRect(0, 0, 800, 56, 0xff000000)                    -- the letterbox
  rc.hudRect(0, 544, 800, 56, 0xff000000)
  scoreboard(t)
  if not C.drift and t > (C.zombies and 18 or 20) then     -- after the shot: a slow drift round the scene
    C.drift = true
    rc.cameraPath{duration = 90, ease = "linear", points = orbit(C.centre, 15, 10, 0, math.pi, 10, 46)}
  end
  local shotLen = C.zombies and 18 or 20
  if t >= 30 or (t >= shotLen and not (S.endSound and rc.soundPlaying(S.endSound))) then
    rc.log(string.format("ZOMBIES: end shot over at %.1f s: the results", t))
    C = nil
    rc.hud(true)
    rc.mode.showResults()                 -- (the camera keeps drifting under the results page)
  end
end
