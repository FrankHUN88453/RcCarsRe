# Lua szkriptek a modokban

[English](LUA_SCRIPTING.en.md) | **Magyar** | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

Az RcCarsRe futtatni tudja a modokhoz mellékelt kis Lua szkripteket. Egy szkript olvashatja a versenyt (pálya,
körök, autók, helyezések, köridők), reagálhat eseményekre (kör, ellenőrzőpont, ütközés, ugrás, előzés, szünet, a
verseny vége ...), és helyi dolgokat tehet: szöveget, képet és téglalapot rajzol a HUD-ra, hangot játszik le,
mozgatja a kamerát, megváltoztatja a ködöt, a napot és a fényeket, rezegteti a kontrollert, a naplóba ír, és
megőrzi a saját beállításait és statisztikáit. A szkriptek nem változtathatják meg a versenyt, az autókat és a
játék fájljait.

A nyelv a [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT-licenc, lásd
[LUA_LICENSE.txt](LUA_LICENSE.txt)). Ez a leírás az API **1.1**-es verziójáé.

## 1. Áttekintés

- Minden bekapcsolt mod (mappa vagy zip egy `mods` mappában, lásd [MODDING.hu.md](../MODDING.hu.md)) tartalmazhat `.lua` fájlokat.
- Minden mod saját Lua állapotot kap. A modok nem látják egymás globális változóit.
- A modok a Modok képernyő sorrendjében töltődnek be alulról felfelé: először a legkisebb prioritású, utoljára a
  lista teteje.
- A játék meghívja a szkript globális eseményfüggvényeit (`onFrame`, `onLap`, ...), ha léteznek.
- Minden, amit egy szkript tesz, a saját gépeden marad: HUD, hang, kamera, köd, fények, kontroller, napló, a saját
  fájljai. A szkriptek soha nem küldenek semmit a hálózaton, és nem hatnak a többi játékosra egy hálózati versenyben.

## 2. Fájlok elrendezése

```
mods\
  my_mod\                 (vagy my_mod.zip ugyanezzel a tartalommal)
    main.lua              belépő szkript (bármely *.lua a mod gyökerében)
    scripts\
      hud.lua             belépő szkript (bármely *.lua közvetlenül a scripts\ mappában)
      lib\util.lua        magától nem töltődik be: rc.include("scripts/lib/util.lua") tölti be
    sounds\ding.wav       a mod saját hangja az rc.playSound("ding") híváshoz
    textures\icon.png     a mod saját képe az rc.hudImage(..., "icon", ...) híváshoz
```

- Belépő szkriptek: minden `*.lua` a mod gyökerében és közvetlenül a `scripts\` mappában, név szerinti sorrendben.
- A mélyebb mappák fájljait csak az `rc.include` tölti be.
- A szkriptek és a szövegek UTF-8 kódolásúak. A szövegek a játék betűtípusának az aktuális nyelvhez tartozó
  kódlapjára alakulnak.

## 3. Bekapcsolás

A `RcCarsRe.ini` fájlban (a `RcCarsRe.exe` mellett), a `[Modern]` szakaszban:

| Kulcs | Értékek | Alapérték | Jelentés |
|---|---|---|---|
| `Mods` | 0 / 1 | 1 | a mods mappák beolvasása (a szkriptekhez kell) |
| `LuaScripts` | 0 / 1 | 1 | a modok Lua szkriptjei futnak |
| `LuaBudget` | 10000 .. 100000000 | 1000000 | ennyi Lua utasítást futtathat egy eseményhívás |

A Modok képernyő (főmenü, „Modok”) kapcsolja be és ki a modokat. Az **Alkalmaz** azonnal újratölt minden
szkriptet: a régi állapotok bezárulnak, és az új modkészlet töltődik be.

A kontroller függvényei a saját kontrollerbeállításaidat is követik ugyanebben a szakaszban: `Rumble` (0 = nincs
rezgés), `LightBar` (`off` = a fénysáv soha nem változik) és `AdaptiveTriggers` (0 = nincs ravaszhatás). Egy
szkript nem kapcsolhatja be azt, amit te kikapcsoltál.

## 4. Események

Ezeket globális függvényként kell megadni. Mind elhagyható.

| Esemény | Mikor |
|---|---|
| `onLoad()` | a mod belépő szkriptjeinek betöltése után |
| `onMenu(name)` | a legfelső képernyő megváltozott: `main`, `options`, `quickrace`, `multiplayer`, `twoplayers`, `twosetup`, `players`, `newplayer`, `credits`, `ghost`, `garage`, `championship`, `champwin`, `mods`, `modsettings`, `pause`, `race`, `results`, `none`, `other` |
| `onRaceStart(info)` | a rajtnál (GO); az `info` az `rc.race()` táblája |
| `onFrame(dt)` | minden képkockában (a menükben is); `dt` = a képkocka ideje másodpercben |
| `onLap(car, lap, lapTime)` | egy autó befejezte a `lap` sorszámú kört `lapTime` másodperc alatt |
| `onCheckpoint(car, index)` | egy autó áthaladt az `index` ellenőrzőponton (1 = a rajt-cél vonal) |
| `onHit(car, strength)` | a játék ütést ítélt meg: 1 = „Hit!”, 2 = „Great hit!” |
| `onWater(car)` | egy autó vízbe ért |
| `onRespawn(car)` | egy autót visszatett a játék a pályára |
| `onRaceEnd(results)` | versenyenként egyszer, amikor a célszkript indul (minden játékos célba ért) |
| `onOptionChanged(key, value)` | a mod Beállítások oldalán megváltozott egy opció |
| `onBoost(car, on)` | (1.1) egy autó boostere bekapcsolt (`true`) vagy leállt (`false`) |
| `onJump(car)` | (1.1) egy versenyző autó 0,25 másodperce a levegőben van (a kis zökkenők nem számítanak) |
| `onLand(car, airTime)` | (1.1) az autó újra a földön van; `airTime` = a levegőben töltött másodpercek |
| `onOvertake(car, otherCar, newPlace)` | (1.1) a `car` elvette a `newPlace` helyet az `otherCar` autótól (verseny közben képkockánként egyszer vizsgálva) |
| `onCollision(car1, car2, strength, kind)` | (1.1) érintkezés: `kind` = `"car"` (két versenyző; `strength` = a közeledési sebesség km/h-ban) vagy `"roadcar"` (versenyző egy úton közlekedő autóval; a `car2` `nil`, a `strength` a versenyző sebessége km/h-ban). Páronként egy hívás, amíg az érintkezés tart (0,5 s érintkezés nélkül újra) |
| `onDogAttack(car)` | (1.1) egy kutya támadásba kezd a `car` ellen: megáll és ugat rá (a játék kutyái nem harapnak; egy kutya elütése „Great hit!”, lásd `onHit`) |
| `onPause(kind)` | (1.1) a verseny szünetel: `kind` = `"menu"` (a szünetmenü) vagy `"quick"` (a gyors szünet) |
| `onResume()` | (1.1) a verseny folytatódik a szünet után |
| `onChat(name, text)` | (1.1) hálózati chatsor érkezett (a saját soraid is); `name` = a küldő, szerver- és játéksoroknál `""`. Csak olvasható |

A `car` az autó sorszáma, 1 .. `rc.race().cars`. A `results` helyezési sorrendű lista; minden eleme: `car`,
`place`, `finished`, `time`, `bestLap` (hiányzik, ha nincs), `lap`, `name`.

## 5. API referencia (`rc` tábla)

### Olvasás

| Függvény | Visszaad |
|---|---|
| `rc.version` | az API verziója (`"1.1"`) |
| `rc.modName` | a mod neve |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = a HUD versenyórája másodpercben (a rajt előtt -1). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (az 1. játékos célba ért), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, raceTime, place, isPlayer, isAi, isGhost, player, finished, name}` vagy `nil`. `speed` km/h-ban; `player` = 1 / 2 egy játékos autójánál; `raceTime` = az autó ideje a rajt óta (megáll, amikor az autó célba ér) |
| `rc.player(n)` | az `n`. játékos autójának táblája (1 vagy 2, alapból 1), vagy `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: a renderelés mérete pixelben, az aktuális képernyő neve, VR be, osztott képernyő |
| `rc.formatTime(seconds, format)` | (1.1) egy idő úgy, ahogy a játék írja: `"m:ss.hh"`, mint a HUD órája (`0:15.89`), vagy `format = "short"` esetén `"m:ss"` |

A köridők úgy működnek, mint a játékban: a `lap` 0, amíg az autó először át nem halad a rajt-cél vonalon, és
minden köridő (az 1. köré is) a vonalon való áthaladástól számít. Az 1. kör alatt ezért a `lapTime` annyival
kisebb az `rc.race().time` értékénél, amennyi idő alatt az autó a rajthelyéről a vonalig ért. A játék kör-felirata,
eredménytáblája és az `onLap` ugyanezeket a köridőket használja.

### HUD (csak ebben a képkockában rajzolódik: minden képkockában hívd az `onFrame`-ből)

A koordináták egy virtuális 800 x 600-as képernyőé, amely az egész képre nyúlik (osztott képernyőn mindkét nézetre,
VR-ben a HUD rétegre). A színek `0xAARRGGBB` alakúak.

| Függvény | Jelentés |
|---|---|
| `rc.hudText(x, y, text, color, size, align)` | szöveg a játék betűtípusával; `size` 1 = a HUD szövegmérete (követi a UI-skálát és a `HudScale`-t); `align` = `"left"` (alap), `"center"`, `"right"` (az x a bal szél, a közép vagy a jobb szél) |
| `rc.hudRect(x, y, w, h, color)` | kitöltött téglalap (alapszín `0x80000000`) |
| `rc.hudImage(x, y, w, h, texture, color, u0, v0, u1, v1)` | kép; a `texture` a mod saját fájlja (a név útvonalként, `.png` / `.dds` / `.csi` kiterjesztéssel is, a `textures\` mappában is), különben a játék ilyen nevű textúrája; az uv alapból 0, 0, 1, 1 |

Képkockánként legfeljebb 512 HUD elem, modonként legfeljebb 64 kép.

### Hang és napló

| Függvény | Jelentés |
|---|---|
| `rc.playSound(name, volume)` | egyszer lejátssza: a mod saját fájlját (a név útvonalként, `.wav` / `.ogg` / `.mp3` / `.au` kiterjesztéssel is, a `sounds\` vagy `sound\` mappában is), különben a játék ilyen nevű hangját; `volume` 0 .. 1 (alapból 1, szorozva a játék effekthangerejével). `true`, ha szól |
| `rc.log(...)` / `print(...)` | egy sor a `game_dbg.log` fájlba (és a -dev konzolra) |
| `rc.warn(...)` / `warn(...)` | figyelmeztető sor (sárga a -dev konzolon) |

### Kamera (1.1)

| Függvény | Jelentés |
|---|---|
| `rc.camera{pos =, offset =, target =, car =, fov =, blend =}` | az 1. játékos versenykamerája lecserélődik az `rc.camera(nil)` hívásig. `pos = {x, y, z}`: a kamera helye a világban; vagy `offset = {x, y, z}` a `car` mellett: a hely az autóhoz képest, annak saját tengelyeiben (x jobbra, y fel, z előre); egyik nélkül sem a játék kamerájának helye marad. `target = {x, y, z}` vagy `car = i`: amire néz (egyik nélkül sem a játék iránya marad). `fov` = függőleges látószög fokban, 10 .. 150 (a játék egyetlen nézete kb. 64). `blend` = ennyi másodperc alatt siklik át a játék kamerájából (0: azonnal) |
| `rc.camera(nil)` | vissza a játék kamerájához (ugyanannyi `blend` idő alatt siklik vissza) |
| `rc.cameraInfo()` | az 1. játékos versenykamerája most: `{pos = {x, y, z}, dir = {x, y, z}, fov, override, blend}`, versenyen kívül `nil`. A `pos` / `dir` mezői `.x .y .z` néven is elérhetők; `override` = szkriptkamera van bekapcsolva, `blend` 0 .. 1 |

A kamera felülírása csak versenyben és csak az 1. játékos nézetén hat: osztott képernyőn a 2. játékos nézete
megtartja a játék kameráját, VR-ben pedig a headset mozgatja a kamerát, ezért ott a felülírás figyelmen kívül marad
(egy figyelmeztetés a naplóban). A menük kamerái soha nem változnak. A verseny elhagyása és a modok újratöltése
kikapcsolja a felülírást.

### Időjárás és hangulat (1.1)

Ezek csak azt változtatják meg, amit a saját géped rajzol. Mindegyiket kikapcsolja a saját reset függvénye, a
`nil` átadása, automatikusan a verseny vége (közvetlenül az `onRaceEnd` előtt, így egy szkript ott új hangulatot
állíthat be), a verseny elhagyása és a modok újratöltése. Ha több mod állítja ugyanazt a hatást, az utolsó hívás nyer.

| Függvény | Jelentés |
|---|---|
| `rc.fog{color =, near =, far =, density =}` | a pálya ködje: `color` = `0xRRGGBB`; `density` méterenként 0 .. 1 (a játék ködje exponenciális, a pályái 0,006 .. 0,026 értéket használnak); `near` / `far` méterben: ezekkel és `density` nélkül a köd lineáris a `near` és a `far` között. A hiányzó mezők a pálya értékét tartják meg. A köd csak akkor látszik, ha a játék ködje be van kapcsolva (Videó beállítások) |
| `rc.resetFog()` | ismét a pálya ködje (mint az `rc.fog(nil)`) |
| `rc.sun{dir = {x, y, z}}` vagy `rc.sun{elevation =, azimuth =}` | a nap iránya (a nap felé; a szögek fokban, az azimut a +z felől a +x felé fordul): a valós idejű árnyékok (`Shadows=realtime`) és az autók fénye |
| `rc.resetSun()` | ismét a pálya napja |
| `rc.lights{intensity =, color =}` | a pályák lámpái (csak `PointLights=1` mellett): `intensity` 0 .. 8-szoros erősség, `color` = `0xRRGGBB` a saját színük helyett. `true`, ha a pontfények be vannak kapcsolva |
| `rc.resetLights()` | ismét a lámpák saját fénye |
| `rc.water{color =, alpha =}` | a tenger: `color` = `0xRRGGBB` színezés, `alpha` 0 .. 1-szeres átlátszóság (`WaterFx=1` mellett a színezés a sekély vizet is színezi) |
| `rc.resetWater()` | ismét a tenger saját kinézete |

### Kontroller-visszajelzés (1.1)

A `player` 1 vagy 2 (alapból 1). A függvények `true` értéket adnak, ha egy kontroller most meg tudja jeleníteni a
hatást.

| Függvény | Jelentés |
|---|---|
| `rc.rumble(strength, seconds, player)` | rezgésimpulzus: `strength` 0 .. 1 (szorozva a `Rumble` beállításoddal), legfeljebb 3 másodperc. Csak akkor érezhető, amikor a játékos autója versenyez, mint a játék saját rezgése |
| `rc.lightBar(r, g, b, player)` | a DualSense / DualShock 4 fénysávja ebben a színben (mindegyik 0 .. 255) az `rc.lightBar(nil, player)` hívásig. Erősebb a játék színénél; `LightBar=off` mellett semmi sem változik |
| `rc.triggers{right =, left =, player =}` | DualSense adaptív ravaszok, amíg a játékos autója versenyez: mindkét ravasz `"off"` vagy `{mode = "resistance", start = 0 .. 1, force = 0 .. 1}` (folyamatos ellenállás a lenyomás `start` részétől). Az `rc.triggers(nil, player)` hívásig; `AdaptiveTriggers=0` mellett nem hat |
| `rc.padSound(name, player, volume)` | a hang (a mod saját fájlja vagy a játéké, mint az `rc.playSound`-nál) a kontroller saját hangszóróján: `PadSpeaker=1` és USB-kábel kell (Bluetooth-on a kontrollereknek nincs Windows hangeszközük); soha nem a PC hangszóróin. `volume` 0 .. 1, szorozva az effekthangerővel és a `PadSpeakerVolume`-mal. A DualShock 4 USB hangeszköze a headset-kimenete |
| `rc.padHaptics(name, player, volume)` | a hang (a mod saját fájlja vagy a játéké) a DualSense hangtekercses haptikáján, Bluetooth-on és USB-n: `PadHaptics=1` és 0-nál nagyobb `Rumble` kell; nem hat, ha a játék a háttérben van vagy a verseny szünetel. `volume` 0 .. 1, szorozva a `PadHapticsVolume`-mal. A DualShock 4-ben nincs hangtekercs |

A modok újratöltése megszünteti a szkript fénysávját és ravaszhatásait.

### A saját mod fájljai

| Függvény | Jelentés |
|---|---|
| `rc.readFile(path)` | a fájl bájtjai szövegként, vagy `nil, üzenet`. Csak a szkript saját modja olvasható |
| `rc.include(path)` | a saját mod egy `.lua` fájlját egyszer lefuttatja és visszaadja az eredményét (a későbbi hívások ugyanazt adják), mint a `require` |

### Beállítások

Tárolás: `Saves\Mods\<mod>.ini` a `RcCarsRe.exe` mellett (zip modnál `<mod>.zip.ini`), `[Settings]` szakasz.

| Függvény | Jelentés |
|---|---|
| `rc.setting(key, default)` | a tárolt érték a `default` típusára alakítva (logikai, szám, szöveg); tárolt érték nélkül a `default`, vagy az opció alapértéke |
| `rc.setSetting(key, value)` | logikai értéket, számot vagy szöveget tárol (`nil` törli); azonnal fájlba ír, ezért ne hívd minden képkockában |
| `rc.options{ ... }` | a mod Beállítások oldalának opciói (lent) |

Kulcsok: betűk, számjegyek, `_`, `.`, `-`, legfeljebb 63 karakter. Értékek: legfeljebb 1000 bájt, sortörés nélkül.

### Statisztikák (1.1)

Modonként a `Saves\Mods\<mod>.stats.ini` fájlban a `RcCarsRe.exe` mellett (zip modnál `<mod>.zip.stats.ini`), a
beállításoktól külön, és soha nem egy játékos mentésében. Az értékek számok vagy szövegek (legfeljebb 1000 bájt),
modonként legfeljebb 1000 kulcs, a kulcsok a beállításokéhoz hasonlóak. A változások a memóriában maradnak, és
egyszerre íródnak ki a verseny végén, a verseny elhagyásakor, a modok újratöltésekor és a játékból való kilépéskor,
így a függvények bármilyen gyakran hívhatók.

| Függvény | Jelentés |
|---|---|
| `rc.stats.get(key, default)` | a tárolt érték, vagy a `default` (vagy `nil`) |
| `rc.stats.set(key, value)` | számot vagy szöveget tárol; a `nil` törli a kulcsot |
| `rc.stats.add(key, n)` | `n`-t (alapból 1) ad egy számhoz (a hiányzó kulcs 0-nak számít), és visszaadja az új értéket |

### Beállítások oldal

```lua
rc.options{
  {key = "showLap", type = "bool", label = "Show lap time", default = true},
  {key = "size", type = "slider", min = 0, max = 10, step = 1, default = 5, label = "Size"},
  {key = "mode", type = "enum", values = {"small", "big"}, default = "small", label = "Mode",
   labels = {"Small", "Big"}},
}
```

- A `label` (és a `labels` minden eleme) szöveg vagy nyelvenkénti tábla: `{en = "...", hu = "...", ru = "...", pl = "..."}`.
- Egy betöltött, opciókkal rendelkező modnál aktív a Modok képernyő **Beállítások** gombja. Az oldala a játék saját
  menüelemeit használja (kapcsolók, csúszkák, gombok); a változások azonnal tárolódnak, és lefut az
  `onOptionChanged(key, value)`.
- Az `rc.setting(key)` az opció értékét adja; az oldal **Alapértékek** gombja visszaállítja az alapértékeket.

## 6. A homokozó korlátai

- Elérhető: a Lua alapfüggvényei, a `table`, `string`, `math`, `utf8`, `coroutine`, valamint az `os.clock`,
  `os.time`, `os.date`.
- Nem elérhető: `io`, az `os` többi része, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- A `load` csak szöveges darabot fogad (szöveget; bináris darabot nem).
- A `collectgarbage` csak a `"count"` paramétert fogadja.
- Memória: modonként 64 MB.
- Idő: eseményhívásonként `LuaBudget` Lua utasítás. Az egy könyvtári híváson belüli hosszú munkát (például egy
  hatalmas `string.rep` vagy egy bonyolult minta) az utasításszámlálás nem méri; maradjanak egyszerűek a szkriptek.
- A szkriptek soha nem írnak játékfájlt, modfájlt vagy játékosmentést; csak a mod beállítás- és statisztikafájlja íródik.

## 7. Hibakezelés

- Egy betöltési hiba, futási hiba vagy túllépett keret csak azt a hívást szakítja meg. A játék megy tovább.
- Minden hiba bekerül a `game_dbg.log` fájlba `Lua [mod] mi: fájl:sor: üzenet` alakban (veremkiírással).
- 5 hiba után a mod szkriptjei kikapcsolnak („mod scripts disabled after repeated errors”). Javítsd a szkriptet,
  majd nyomd meg az Alkalmaz gombot a Modok képernyőn (vagy fejlesztői módban mentsd a fájlt, lásd lent).
- Ha egy hívás a keret több mint 80 %-át használta, egyszer figyelmeztetés jön.

## 8. Fejlesztői mód (`RcCarsRe.exe -dev`)

- A hibák és figyelmeztetések a konzolablakban látszanak: a hibasorok pirosak, a figyelmeztetések sárgák (Lua és a
  játék egyaránt); a hibák a játékon belüli piros sávban is megjelennek.
- A `lua` konzolparancs felsorolja a szkriptes modokat; a `lua <kód>` az utoljára betöltött mod állapotában futtat,
  a `lua <mod> <kód>` az adott modéban, és kiírja az eredményeket (kifejezés is működik, például
  `lua rc.race().state`).
- Gyors újratöltés: a mappás modok `.lua` fájljait a játék másodpercenként ellenőrzi; ha egy megváltozik, az adott
  mod szkriptjei újratöltődnek (zip modoknál: Alkalmaz). Az újratöltés minden kamera-, időjárás- és
  fénysáv-felülírást is megszüntet.

## 9. Példák

A `docs/modding/examples/` három teljes modot tartalmaz. Másolj egy mappát a `RcCarsRe.exe` melletti `mods\` mappába:

- `laptime_hud`: az 1. játékos versenyideje (ugyanaz, mint a HUD órája), aktuális, előző és legjobb köride egy
  dobozban, a játék időformátumában; opciók: legjobb kör, méret, sarok.
- `checkpoint_sound`: az 1. játékos minden ellenőrzőpontjánál lejátssza a mod saját `sounds\ding.wav` hangját, és
  felvillantja a sorszámát.
- `drift_air`: amikor az 1. játékos autója egy ugrás után landol, kiírja a levegőben töltött időt, röviden rezeg és
  felvillantja a fénysávot, valamint `rc.stats`-szal megőrzi pályánként a legjobb repülési időt és az ugrások számát.

Egy minimális szkript:

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

## 10. Hibaelhárítás

| Probléma | Ellenőrizd |
|---|---|
| Semmi sem történik | `LuaScripts=1` és `Mods=1` a `RcCarsRe.ini` fájlban; a mod be van kapcsolva a Modok képernyőn; a fájl a mod gyökerében vagy a `scripts\` mappában van; a `game_dbg.log` tartalmazza: `Lua [mod]: ... loaded` |
| „mod scripts disabled after repeated errors” | olvasd el az első `Lua [mod]` hibasorokat a `game_dbg.log` fájlban, javítsd a szkriptet, nyomd meg az Alkalmaz gombot |
| „instruction budget exceeded” | az esemény egyszerre túl sokat dolgozott; oszd el több képkockára, vagy emeld a `LuaBudget` értékét |
| Nem látszik a HUD elem | a HUD hívások csak egy képkockáig élnek: az `onFrame`-ből hívd őket; nézd meg a szín alfa bájtját (`0xFF......` átlátszatlan) |
| „texture ... not found” / „sound ... not found” (sárga) | a fájl neve és mappája a modban; PNG, DDS vagy CSI kép; WAV, OGG, MP3 vagy AU hang |
| A szövegben `?` jelenik meg | UTF-8 kódolással írd a szkriptet; a játék betűtípusa csak a nyelve kódlapjának karaktereit ismeri |
| Az 1. kör ideje kisebb a HUD órájánál | mint a játékban, a köridők a rajt-cél vonaltól számítanak; a versenyidő az `rc.race().time` |
| Nem változik a kamera | csak versenyben, csak az 1. játékos nézetén, VR-ben nem |
| Nincs rezgés / fénysáv | csatlakoztatott kontroller kell; `Rumble`, `LightBar`, `AdaptiveTriggers` a `RcCarsRe.ini` fájlban; a rezgés és a ravaszok csak versenyzés közben hatnak |
| Hibák a -dev konzolon | a hibasorok pirosak, a figyelmeztetések sárgák; ugyanezek a sorok a `game_dbg.log` fájlban is ott vannak |
