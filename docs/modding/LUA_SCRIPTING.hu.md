# Lua szkriptek a modokban

[English](LUA_SCRIPTING.en.md) | **Magyar** | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

Az RcCarsRe futtatni tudja a modokhoz mellékelt kis Lua szkripteket. Egy szkript olvashatja a versenyt (pálya,
körök, autók, helyezések, köridők), reagálhat eseményekre (kör, ellenőrzőpont, ütközés, ugrás, előzés, szünet, a
verseny vége ...), és helyi dolgokat tehet: szöveget, képet és téglalapot rajzol a HUD-ra, hangot játszik le,
mozgatja a kamerát, megváltoztatja a ködöt, a napot és a fényeket, rezegteti a kontrollert, a naplóba ír, és
megőrzi a saját beállításait és statisztikáit. A szkriptek nem változtathatják meg a versenyt, az autókat és a
játék fájljait, egy kivétellel: egy játékmód szkriptje (6. fejezet, API 1.4) vezeti a saját versenyei
szabályait (egyelőre egyjátékos módban).

A nyelv a [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT-licenc, lásd
[LUA_LICENSE.txt](LUA_LICENSE.txt)). Ez a leírás az API **1.10**-es verziójáé.

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
| `onObjectHit(car, name)` | (1.9) egy autó fellökte a pálya egy laza tárgyát (doboz, labda, palack ...); a `name` a tárgy neve a pályán. Lökésenként egyszer |
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
| `onCountdown(n)` | (1.1) a verseny visszaszámlálása, a számokkal és a sípszóval egy pillanatban: `n` = 3, 2, 1, és 0 a GO-nál |

A `car` az autó sorszáma, 1 .. `rc.race().cars`. A `results` helyezési sorrendű lista; minden eleme: `car`,
`place`, `finished`, `time`, `bestLap` (hiányzik, ha nincs), `lap`, `name`.

## 5. API referencia (`rc` tábla)

### Olvasás

| Függvény | Visszaad |
|---|---|
| `rc.version` | az API verziója (`"1.10"`) |
| `rc.modName` | a mod neve |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = a HUD versenyórája másodpercben (a rajt előtt -1). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (az 1. játékos célba ért), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, raceTime, place, isPlayer, isAi, isGhost, player, finished, name}` vagy `nil`. `speed` km/h-ban; `player` = 1 / 2 egy játékos autójánál; `raceTime` = az autó ideje a rajt óta (megáll, amikor az autó célba ér); (1.8) `airTime` = másodpercek azóta, hogy az autó valamelyik kereke utoljára földet ért (a földön 0), `vy` = a függőleges sebessége m/s-ban (esés közben negatív); az ellenfeleknél mindkettő 0; (1.9) `dir` és `up` = az autó előre és felfelé mutató tengelye `{x, y, z}` alakban, `spin` = a szögsebessége rad/s-ban a világ tengelyei körül (az ellenfeleknél 0) |
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
| `rc.padHaptics(name, player, volume)` | a hang (a mod saját fájlja vagy a játéké) a DualSense hangtekercses haptikáján, Bluetooth-on és USB-n: `PadHaptics=1` és 0-nál nagyobb `Rumble` kell; nem hat, ha a játék a háttérben van vagy a verseny szünetel. `volume` 0 .. 1, szorozva a `PadHapticsVolume`-mal. A DualShock 4-ben nincs hangtekercs |

A modok újratöltése megszünteti a szkript fénysávját és ravaszhatásait.

### A saját mod fájljai

| Függvény | Jelentés |
|---|---|
| `rc.readFile(path)` | a fájl bájtjai szövegként, vagy `nil, üzenet`. Csak a szkript saját modja olvasható |
| `rc.readUserFile(suffix)` | (1.2) a játékos saját fájlja, `Saves\Mods\<mod>.<suffix>` a `RcCarsRe.exe` mellett (például `"controls.ini"`: a mod frissítéseit túlélő beállítások), vagy `nil, üzenet`. Csak ez a mappa és a mod saját neve; `suffix`: betűk, számjegyek, `_ . -` |
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

### Bemenet, szünet, HUD és képernyőkép (1.2)

Ezek egy fotómód, egy visszajátszó kamera és hasonló eszközök építőkövei. Mind csak a saját gépeden hatnak.

| Függvény | Jelentés |
|---|---|
| `rc.input.key(name)` | `true`, amíg a billentyű le van nyomva. Nevek: betűk `"A"` .. `"Z"`, számjegyek, `"F1"` .. `"F24"`, `"Space"`, `"Enter"`, `"Esc"`, `"Tab"`, `"Backspace"`, `"Shift"`, `"Ctrl"`, `"Alt"`, `"Up"`, `"Down"`, `"Left"`, `"Right"`, `"PageUp"`, `"PageDown"`, `"Home"`, `"End"`, `"Insert"`, `"Delete"`, `"Plus"`, `"Minus"`, `"Comma"`, `"Period"`, `"MouseLeft"`, `"MouseRight"`, `"MouseMiddle"` |
| `rc.input.pressed(name)` | `true` abban a képkockában, amikor a billentyűt lenyomták |
| `rc.input.mouse()` | `{dx, dy, wheel, left, right, middle}`: az egér mozgása és a görgő kattanásai ebben a képkockában, a gombjai |
| `rc.input.pad(player)` | `{lx, ly, rx, ry, lt, rt, kind, buttons = {..}, pressed = {..}}`, kontroller nélkül `nil`. A karok -1 .. 1 (fel pozitív), a ravaszok 0 .. 1, `kind` = `"xinput"`, `"ds4"`, `"dualsense"`. Gombnevek (mindegyik a `pressed`-ben is, a lenyomás képkockájában igaz): `a` / `cross`, `b` / `circle`, `x` / `square`, `y` / `triangle`, `lb` / `l1`, `rb` / `r1`, `back` / `view` / `share` / `create` / `select`, `start` / `menu` / `options`, `ls` / `l3`, `rs` / `r3`, `guide` / `ps`, `touchpad`, `mute`; a `buttons`-ban a D-pad is ott van: `up`, `down`, `left`, `right` |
| `rc.input.capture(on)` | amíg be van kapcsolva, az autó irányítása és a szünetmenü Esc / Start gombja nem kapja meg a billentyűket és gombokat: a szkript használja őket (például a karokat egy szabad kamerához) |
| `rc.pause(on)` | megállítja a versenyt, mint a szünetmenü (versenyóra, fizika, MI, víz, részecskék, animációk, hangok), menü nélkül. Hálózati versenyben `false` |
| `rc.timeScale(s)` | lassítás, `s` 0,05 .. 1 (1 = normál). Hálózati versenyben `false`. Teljes megállításhoz az `rc.pause` való |
| `rc.hud(show)` | `false` elrejti a játék saját HUD-ját (műszerfal, mérők, nyíl, térkép, versenyzőlista, üzenetek, chatsorok, ShowFps); a szkript `rc.hudText` / `rc.hudImage` / `rc.hudRect` elemei továbbra is rajzolódnak |
| `rc.screenshot{hideScriptHud =, scale =}` | a következő képkockát PNG-ként menti a `RcCarsRe.exe` melletti `Screenshots` mappába, és visszaadja a fájl nevét. A `hideScriptHud` (alapból `true`) kihagyja abból a képkockából a szkript saját HUD-elemeit. Csak `scale = 1` (a kép, ahogy látszik) készül |
| `rc.graphics{shadows =, reflections =}` | (1.3) a `Shadows` / `Reflections` átkapcsolása erre a játékmenetre: mindkettő `"original"`, `"realtime"` vagy `"off"` (a hiányzó mező marad). Az `rc.graphics()` a mostani `{shadows, reflections}` értéket adja. Az ini nem íródik: a játék visszaáll az értékeire a verseny végén, a verseny elhagyásakor, a modok újratöltésekor és szkripthiba esetén. Az első valós idejűre kapcsolás elkészíti az árnyéktérképeket / tükröződő kockákat (rövid akadás, néhány száz MB videomemória); a későbbi kapcsolások ezeket használják. Hálózati versenyben is szabad (csak a saját képed változik) |

- Az `rc.camera{...}` a `roll = fok` mezőt is elfogadja (pozitív: az óramutató járásával egyezően), és a verseny
  szünetelése alatt is működik.
- A bemenet csak akkor olvasható, ha a játék ablaka van elöl, és senki nem gépel szövegmezőbe (egy menü
  szövegmezője, a hálózati chatsor). Csak billentyűzettel és csak kontrollerrel is működik.
- Nem érhető el (a rendererben nincs olcsó út hozzá): mélységélesség, `scale = 2` képernyőkép, expozíció /
  telítettség. A hangulathoz az `rc.fog`, `rc.sun`, `rc.lights` és `rc.water` való.
- Biztonság: a szünetet, az elrejtett HUD-ot, a bemenet lefoglalását, a lassítást és a kamerát a játék visszaadja a
  verseny végén, a verseny elhagyásakor, a modok újratöltésekor, és ha egy szkript hibázik vagy kikapcsol, így egy
  hibás szkript soha nem hagyhatja a játékot megállítva vagy HUD nélkül.

### Fotómód építése

A `photo_mode` példamod (a `docs/modding/examples/` mappában) egy teljes fotómód egyetlen szkriptben. A magja:

```lua
local on, pos, yaw, pitch = false, nil, 0, 0

local function enter()
  local c = rc.cameraInfo()
  if not c or not rc.pause(true) then return end      -- nincs versenykamera, vagy hálózati verseny
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

A teljes példa szabadon repül: W / S a nézés irányában (fel-le is), A / D oldalra (vízszintesen, a döntés nem
fordítja el), Shift / Ctrl egyenesen fel / le, Q / E döntés, Space gyorsabb, az egér néz, a görgő zoomol, F12 a
fotó, P / Esc kilép; kontrolleren a karok, a ravaszok (le / fel), a vállgombok (döntés), a D-pad (zoom), az A (fotó)
és a Back / View / Share / Create (ki-be). Bemenet nélkül a kamera áll: a karok és a ravaszok holtsávon mennek át
(0,2 / 0,1), tehetetlenség nincs.

A gombkiosztása a mod egy sima szövegfájljában van, `photo_mode\controls.ini`, soronként egy `művelet=gomb`,
megjegyzéssel (`[Keyboard]` és `[Pad]` szakasz, a holtsávok `deadzone=` / `triggerDeadzone=`). A szkript az
`rc.readFile`-lal olvassa betöltéskor (így az Alkalmaznál és a -dev gyors újratöltésnél is: egy mappás mod
megváltozott `.ini` / `.txt` fájlja újratölti a szkriptjeit), és minden bekapcsoláskor; ismeretlen név sárga
figyelmeztetést ad, és az adott műveletnél az alapérték marad. Gombnevek: `A` .. `Z`, `0` .. `9`, `F1` .. `F12`,
`Ctrl`, `Shift`, `Alt`, `Space`, `Tab`, `Enter`, `Esc`, `Up`, `Down`, `Left`, `Right`, `MouseLeft`, `MouseRight`,
`MouseMiddle`, `WheelUp`, `WheelDown`, `None`; a kontroller nevei az `rc.input.pad` szerint. A játékos saját
példánya a `RcCarsRe.exe` melletti `Saves\Mods\photo_mode.controls.ini` fájlban (az
`rc.readUserFile("controls.ini")` olvassa) erősebb nála, és túléli a mod frissítéseit.

Fotómódban az R (kontrolleren Y / Triangle) ki-be kapcsolja a valós idejű árnyékot és tükröződést (`realtimeGfx=` a controls.ini-ben); kilépéskor az ini értékei térnek vissza.

## 6. Játékmódok (1.4)

Egy mod **játékmódot** adhat a játékhoz: saját szabályokat egy normál pályán, a játékos a gépi autók ellen. Az a mod,
amelyik az `onLoad`-ban meghívja az `rc.registerMode`-ot, megjelenik a Gyors verseny képernyő **Mód** sorában (a
verseny összefoglaló oldalán, az ellenfelek ügyessége alatt): *Verseny* (a normál verseny) és minden regisztrált mód,
a játék nyelvén írt nevével. A mód versenye a választott pályát tölti be a megszokott módon; a gépi ellenfelek száma
az ügyességtől függ (könnyű 3, normál 4, nehéz 5), legfeljebb a mód `maxCars` értéke.

### Szövegek négy nyelven

Az API minden szövege lehet egy sztring vagy egy nyelvi tábla `{en = "...", hu = "...", ru = "...", pl = "..."}`.
A játék aktuális nyelve választ (ugyanaz, mint a menüké, `[Modern] Language`); ha arra nincs szöveg, vagy más a
nyelv, az angol jön, ha az sincs, az első, ami van.

| Függvény | Jelentés |
|---|---|
| `rc.lang()` | a játék nyelve: `"en"`, `"hu"`, `"ru"`, `"pl"`, vagy a nyelvi mappa neve kisbetűvel |
| `rc.text(t)` | a `t` nyelvi tábla szövege az aktuális nyelven (egy sztring változatlanul jön vissza) |

### Mód regisztrálása

```lua
rc.registerMode{
  id = "zombies",                                   -- betűk, számjegyek, _ . - (egyedi)
  name = {en = "Zombies", hu = "Zombik", ru = "Зомби", pl = "Zombie"},
  description = {en = "...", hu = "...", ru = "...", pl = "..."},
  minCars = 2, maxCars = 6,                          -- 1 .. 6
  checkpoints = false,                               -- nincs ellenőrzőpont, GPS-nyíl, kör és célvonal
  laps = false,                                      -- nincs körszámláló (alapból: mint a checkpoints)
  ai = "script",                                     -- "script": a gépi autók az rc.ai-t követik; "race": versenyeznek
  respawn = false,                                   -- a játék nem tesz vissza autót (alapból true)
  hud = {racerList = false, place = false, lap = false, wrongWay = false},   -- a HUD részei, amelyeket a mód elrejt
}
```

`checkpoints = false` mellett a versenyben nincs ellenőrzőpont, GPS-nyíl, rossz irány jelzés, körszámlálás és
célvonal; a helyezés képe rejtve van. Csak a rajt (3, 2, 1, GO) a játéké; GO után a mód szkriptje vezeti a versenyt,
és az `rc.mode.finish` zárja. A vízbe vagy a pályáról leeső autót a játék a gépi autók vezetési vonalainak
legközelebbi pontjára teszi vissza (`respawn = false` mellett ehelyett a mód dönt).

### A mód eseményei (csak a mód saját modjának)

| Esemény | Mikor |
|---|---|
| `onModeLoad(info)` | a mód versenye megjelent (az első képkockától, a rajt visszaszámlálása előtt), és újra a *Verseny újra*-nál. Itt állítsd be a mód kinézetét (köd, hangulat) |
| `onModeStart(info)` | GO-nál. `info` = az `rc.race()` táblája, plusz `id`, `player` (a játékos autója), `minCars`, `maxCars` |
| `onModeFrame(dt)` | minden képkockában, amíg a verseny fut (szünetben és a cél után nem) |
| `onModeTimer()` | az `rc.mode.timer` időzítője lejárt |
| `onModeEnd()` | egyszer, az `rc.mode.finish` után |
| `onRespawnBlocked(car, reason)` | `respawn = false` mellett: a játék visszatette volna az autót. `reason` = `"water"` (2 s víz alatt), `"bounds"` (kiesett a pályáról), `"zone"` (leesés-zóna), `"key"` (a játékos Reset gombja), `"flip"` (a tetején fekvő autót nem lehetett talpra állítani), `"stuck"` (a fizika szerint beragadt), `"timed"`, `"aiemu"`. Autónként legfeljebb másodpercenként egyszer |

A normál események (`onRaceStart`, `onCollision`, `onFrame`, ...) továbbra is minden modhoz eljutnak.

### A mód vezérlése (csak a futó mód saját szkriptje hívhatja)

| Függvény | Jelentés |
|---|---|
| `rc.mode.countdown(seconds, text)` | nagy visszaszámlálás a képernyő közepén (a műszerfal számbetűivel), utána a `text` 1,5 másodpercig |
| `rc.mode.message(text, seconds, color)` | üzenet a képernyő közepe alatt (alapból 3 s, fehér; `0xRRGGBB`) |
| `rc.mode.timer(seconds)` | a HUD felső órája a hátralévő időt mutatja (az utolsó 10 s-ban pirosan); `nil` / 0 kikapcsolja |
| `rc.mode.timeLeft()` | a hátralévő másodpercek, időzítő nélkül `nil` |
| `rc.mode.clock()` | másodpercek a mód kezdete (GO) óta, a szünetek nélkül |
| `rc.mode.active()` | a futó mód azonosítója, normál versenyben `nil` (bármelyik mod hívhatja) |
| `rc.mode.freeze(car, on)` | megállít egy autót (nincs gáz, fékez), pl. előnyhöz |
| `rc.mode.listText(car, text, color)` | a HUD versenyzőlistája a különbség helyett ezt a szöveget mutatja (`nil`: újra a különbséget) |
| `rc.mode.finish(results, title)` | lezárja a versenyt: minden autó befut, utána jön a játék célba érése és az eredménylap ezekkel a sorokkal. `results` = `{{car =, place =, text =}, ...}`; a `title` (alapból a mód neve) a szövegoszlop fejléce |
| `rc.mode.holdEnd{seconds =, skippable =}` | az `rc.mode.finish` után: a játék eredménylapja `seconds` (alapból 20, legfeljebb 60) másodperccel később jön, egy zárójelenethez. `skippable = false` (alapból): a játékos gombjai addig semmit sem tesznek, a szünetmenü sem nyílik meg (az ablak bezárása továbbra is kilép). Szkripthiba vagy újratöltés azonnal feloldja |
| `rc.mode.showResults()` | a visszatartott eredménylap most |
| `rc.mode.respawn(on)` | a játék autó-visszahelyezései be / ki erre a versenyre (a kezdőérték a `registerMode` `respawn`-ja). Kikapcsolva az oldalán vagy tetején fekvő autót 2 s után a helyén talpra állítja (a játékosét is), de máshová nem viszi |
| `rc.mode.respawnCar(car)` | a mód visszateszi az autót a gépi vezetési vonalak legközelebbi pontjára (`respawn = false` mellett is) |
| `rc.setCarTeam(car, n)` | az autó csapata (bármilyen szám; `rc.car(i).team`) |
| `rc.setCar(car, {model =, paint =, physics =})` | az autó a játék egy másik RC autójává válik: `model` = `"Overkill"`, `"Buggy"` vagy `"Warhammer"`, `paint` = 1 .. 4 (a garázs festései), `physics` = `true` (alapból: annak az autónak a fizikájával is megy) vagy `false` (csak a kinézet). `rc.setCar(car, nil)`: újra a saját autója. Az autó megtartja a fejlesztéseit, a hangjait és a mozgását |
| `rc.carName(car)` | a versenyző neve |
| `rc.distance(car1, car2)` | két autó távolsága méterben |

Az `rc.car(i)` táblában (1.4) van még `team`, `model` (`""` a sajátja), `paint` (0 a sajátja), `frozen` és
`contacts`: az autók, amelyekhez ebben a képkockában hozzáért (`{2, 4}`).

### Parancsok a gépi autóknak (`ai = "script"`)

Az `rc.ai(car, order)` egy gépi autót vezet (játékos autóját soha; akkor `false`-t ad vissza). A gépi autó a pálya
gépi vezetési vonalaiból épített úthálón megy (a víz és a szakadékok melletti pontok jelölve: ott lassít és távol
marad attól az oldaltól), a legrövidebb utakat keresi, beragadáskor kitér, és ha a mód engedi a visszahelyezést,
a sokszor beragadt autót visszateszi.

| Parancs | Jelentés |
|---|---|
| `{mode = "chase", target = car}` | nekimegy annak az autónak: amíg messze van, az úton, 8 m-en belül egyenesen (a sebessége szerint kicsit elé célozva) |
| `{mode = "chase", targets = {cars}}` | ugyanez az autók közül az úton legközelebbire; csak akkor vált célt, ha egy másik egyértelműen közelebb van (alapból: minden más csapatbeli autó) |
| `{mode = "flee", from = {cars}, caution = m}` | menekül ezektől az autóktól (alapból: minden más csapatbeli): az úton 30 m-en belüli, tőlük legtávolabbi helyre (a legközelebbi számít legjobban), amelynek az útja `caution` métert (alapból 6) tart tőlük; sarokba szorítva a legtöbb helyet adó úton, az üldöző mellett elmenve; a közvetlenül előtte lévő üldözőt kikerüli |
| `{mode = "stop"}` | fékezve áll |
| `{mode = "path"}` | újra a normál versenyvonal |

Minden parancs elfogad `speed` = 0,1 .. 1 gázt (alapból 1). A beragadt autó (kb. 2 s haladás nélkül) előre balra
és jobbra tapogat (a pálya falai, a víz és a szakadékok akadálynak számítanak), az akadálytól elfordított orral
hátrál, a szabadabb oldalon egy kerülőponton megkerüli, és folytatja; 4 s-ig azon az oldalon marad, hogy ne próbálja
újra ugyanazt a vonalat. Engedélyezett visszahelyezés mellett a 12 s alatt háromszor beragadt autót visszateszi.

### Hangok és a pálya háttérhangjai (1.4)

| Függvény | Jelentés |
|---|---|
| `rc.playSound(name, {volume =, loop =, car =, pos =, minDist =, maxDist =, pan =, panTo =})` | a hang azonosítóval (`false`, ha nem szól). `loop = true`: az `rc.stopSound`-ig. `car = i` / `pos = {x, y, z}`: a világban elhelyezve, DirectSound 3D-vel, mint a játék saját hangjai: `minDist` (5) méteren belül teljes hangerő a kamerától, `maxDist`-ig (60) halkul -20 dB-ig, ennél halkabb nem lesz, az irányából szól (egy autó hangja követi az autót; osztott képernyőn irány nélkül). `pan` = -1 .. 1, vagy `panTo = {x, y, z}`: abból az irányból, ahogy a kamera látja. Modonként egyszerre legfeljebb 16; a verseny elhagyásakor mind elhallgat |
| `rc.stopSound(handle)` | leállítja |
| `rc.soundPlaying(handle)` | `true`, amíg szól |
| `rc.listModFiles(folder, pattern)` | a mod saját fájljai abban a mappában, amelyek neve illeszkedik (`*`, `?`), pl. `rc.listModFiles("sounds", "hit*.wav")`; az üres fájlok kimaradnak (figyelmeztetéssel) |
| `rc.levelAmbient(on, music)` | `false` elnémítja a pálya ismétlődő háttérhangjait (a háttérzajokat, a tengert, a patakokat és a vízesést; az egyszeri hangok, pl. egy tárgy vagy kő ütközése és a hangok, beszéd maradnak, ahogy az autók, az effektek és a szkriptek hangjai is); `music` = a verseny zenéjének dB-je (0 ahogy be van állítva, -100 néma; a menük zenéje marad). A verseny elhagyásakor, újratöltéskor és a mod szkriptjeinek leállásakor visszaáll |
| `rc.fog{...}` | (1.4) `true`-t ad vissza, ha a játék köde látszik (Beállítások / Videó köd be) |
| `rc.hudParts{racerList =, place =, lap =, gps =, map =, timer =, speedo =, boost =, wrongWay =}` | `false` elrejti a játék HUD-jának azt a részét (versenyzőlista, helyezés, körszámláló, GPS-nyíl, minitérkép, óra, sebességmérő, gyorsító, a rossz irány jelzése és hangja), `true` újra megmutatja; argumentum nélkül annak táblája, ami látszik. A verseny elhagyásakor, a *Verseny újra*-nál, újratöltéskor és a szkriptek leállásakor visszaáll |
| `rc.textWidth(text, size)` | egy `rc.hudText` szöveg szélessége a 800 x 600-as egységekben, abban a méretben (a felületméretezéssel és a HudScale-lel együtt), a szövegek középre vagy egymás alá igazításához; az `rc.hudText` utolsó argumentuma lehet `{align = "center"}` (vagy `"right"`) is |
| `rc.replaceTexture(gameTexture, modFile)` | a játék ilyen nevű (már betöltött, pl. egy gyalogos vagy egy sirály) textúrája a mod képét mutatja (`.png` / `.dds` / `.csi`, a `textures\` vagy `skins\` alatt is) az `rc.restoreTexture(name)` / `rc.restoreTextures()` hívásig; textúra-újratöltés után is megmarad; a verseny elhagyásakor, a *Verseny újra*-nál, újratöltéskor és a szkriptek leállásakor magától visszaáll. A mod `Textures\` mappájában lévő fájllal szemben csak addig hat, amíg a szkript akarja |

### Kamerautak (1.4)

| Függvény | Jelentés |
|---|---|
| `rc.cameraPath{points = {{pos =, target =, fov =, roll =}, ...}, duration =, ease =, blend =}` | az 1. játékos versenykamerája végigrepül a pontokon: sima görbe a helyeken és egy a célpontokon, a `fov` / `roll` közöttük, `duration` másodperc alatt (alapból 10), `ease` = `"inout"` (alapból), `"in"`, `"out"`, `"linear"`, a játék kamerájától `blend` másodperc alatt átúszva. Utána az utolsó ponton marad. Legfeljebb 16 pont; az `rc.camera(...)` vagy az `rc.cameraPath(nil)` befejezi; a versennyel véget ér |

A mód köde, napja, fényei, vize és kamerája a zárólapján megmarad (a normál verseny a célnál visszaállítja); a
verseny elhagyásakor, a *Verseny újra*-nál és újratöltéskor áll vissza. A *Verseny újra* (az eredménylapon, a
szünetmenü újraindítása, a hálózati újra) mindent felold, mint a verseny elhagyása: a kamerát és az útját, a vég
visszatartását, a szünetet és a lassítást, a rejtett HUD-ot és részeit, a bemenet elfogását, a kinézetet, a hangokat
és a háttérhangot, az `rc.setCar` cseréket (minden autó újra a saját modelljével, festésével és fizikájával), a
csapatokat, a listaszövegeket, a gépi parancsokat, a visszahelyezés tiltását, az időzítőket és az üzeneteket; utána a
mód elölről indul (`onModeLoad`, `onModeStart`). Amíg egy mód
némán tartja a verseny zenéjét (`rc.levelAmbient(false, -100)`), az eredménylap zenéje is néma marad, így a mód saját
zárózenéje hallatszik; a zene a verseny elhagyásakor tér vissza. Hangfájlok: `.wav` (PCM vagy Microsoft ADPCM),
`.ogg`, `.mp3`, `.au`.

### Hálózati versenyek (1.5)

A módok hálózati versenyben is futnak. A gazdagép a lobbiban a `/mode <id>` csevegőparanccsal választ (`/mode`
felsorolja a módokat, `/mode race` újra a sima verseny); a mód modja minden játékosnál kell. A versenyben **minden
gép futtatja a mód szkriptjét, de csak a gazdagépé dönt**:

| Hívás / esemény | Mit csinál |
|---|---|
| `rc.mode.host()` | `true` azon a gépen, amelyiknek a szkriptje dönt: egyjátékos módban mindig, hálózatban csak a gazdagépen |
| `rc.mode.send(name, ...)` | a döntő szkript közli, mit döntött: az `onModeEvent(name, ...)` itt azonnal lefut, a klienseken pedig amikor az üzenet megérkezik. Értékek: `nil`, logikai, szám, szöveg (legfeljebb 32, 1000 bájt). Kliensen nem csinál semmit, `false` az eredménye |
| `onModeEvent(name, ...)` | itt változtasd a kört (`rc.setCar`, `rc.setCarTeam`, `rc.mode.freeze` / `listText` / `message` / `timer` / `finish` ...), így minden gép ugyanazokat a hívásokat teszi |
| `onModeLoad(info)` / `onModeStart(info)` | `info.network` (hálózati verseny) és `info.host` (ez a gép dönt) |

- Csak ott dönts, ahol `rc.mode.host()` igaz (`onCollision`, `onModeTimer`, az `onModeFrame` ellenőrzései), és az időt
  vagy a véletlen választást küldd el, ne vedd újra minden gépen.
- A gazdagép `onCollision` eseménye megkapja azokat az érintéseket is, amelyeket a kliensek a saját autójukról
  jelentenek; az `onRespawnBlocked` csak a gazdagépen fut (a kliens szól a saját autójáról); a gazdagépen az
  `rc.mode.respawnCar(car)` egy másik játékos autóját annak a játékosnak a gépén teszi vissza.
- `rc.options`: a `perPlayer = true` beállítás (kép, hang) minden játékosé marad; a többinek a verseny alatt minden
  gépen a gazdagép értéke él (`rc.setting`).
- Hálózati versenyben nincs gépi autó (`rc.ai` eredménye `false`), az `rc.setCar` csak a gép saját autójának a
  fizikáját cseréli, és a visszatett autó a rajthelyére kerül (az útpontok a gépi autók útvonalaiból vannak).

### A Zombik példa

A `docs\modding\examples\zombies` egy fogócska: 10 másodperc előny után ("Fuss!") egy véletlen autó (a tiéd vagy egy
gépié) lesz a zombi: egy Warhammer zöld terepszínű festéssel, és úgy is megy. A túlélőhöz (a beállított erősségű
autó-autó érintéssel) hozzáérő zombi megfertőzi. A zombik nyernek, ha mindenki fertőzött; a túlélők, ha lejár az idő
(alapból 5:00). Az eredmények mutatják, ki élte túl és ki mikor fertőződött. A gépi zombik az úton elérhető
legközelebbi túlélőt üldözik, a gépi túlélők menekülnek. Szürkészöld köd üli meg a kört, egyre sűrűbb, ahogy fogynak a
túlélők; fertőzéskor a kontroller fénysávja zöld lesz és rezeg; az `rc.stats` számolja a köröket és a győzelmeket
zombiként / túlélőként. A versenyzőlista helyén saját állapotsort mutat (túlélők / zombik, hátralévő idő, a
szereped). Beállítások oldala: időkorlát (1 .. 10 perc), előny, fertőzés erőssége, köd be / sűrűség, a
zombi MI agresszivitása, a túlélő MI óvatossága, háttérhang be / hangerő, szívverés be / hatótáv, mi lesz a kieső
túlélővel (zombi lesz / kiesik), mennyi idő múlva kerül vissza az útra a kiesett zombi, zárókamera be / ki. Minden
szöveg négy nyelven. Ebben a módban a játék nem tesz vissza autót (`respawn = false`): a tetején fekvő autót a helyén
talpra állítja. A kör végén zárójelenet (VR-ben nem): a zombik győzelménél az utolsó áldozat fölül emelkedik a kamera
a zombik fölé, a túlélőknél körbejárja őket; becsúszik egy eredménytábla (túlélési idők, ki kit kapott el, az utolsó
túlélő, az összesítés, a legjobb túlélési időd az `rc.stats`-ból); nem lehet átugrani, a jelenet vagy a zárózene
hosszáig tart (legfeljebb 30 s), utána jön az eredménylap. A játékhoz másold a `zombies` mappát a játék `mods`
mappájába.

A hangjai a mod szerzőjének saját fájljai, és **nem** részei a nyilvános példának; tedd a sajátjaidat a mod `sounds\`
mappájába (a hiányzókat figyelmeztetéssel kihagyja): `zombie_ambient.mp3` (a kör háttérhangja a pályáé helyett),
`thunder01.wav` (új zombi, az egész pályán hallható onnan, ahol történt), `zombie_attack*.wav` (a fertőző érintés,
mindkét autónál), `heart_beat.wav` (a szívverésed a legközelebbi zombi irányából, gyorsabban, ahogy közeledik),
`zombie_outro.mp3` (a zombik nyernek), `humans_win.wav` (a túlélők nyernek).

## 6a. Hozzáadott autók, karosszériák és festések (1.6)

Egy mod úgy is adhat autót, karosszériát és festést a játékhoz, hogy a játék sajátjait nem cseréli le. A szkript
betöltésekor hívd ezeket:

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

- **`rc.registerCar`**: saját vázú autó. A `base` autó helyét használja a játékos profiljában (akkor lehet vele
  versenyezni, ha az alapautó a játékosé), annak a hangját és fejlesztéseit; semmi újat nem ment. `physics` /
  `physicsScale` nélkül pontosan úgy megy, mint az alapautó.
- **`rc.registerBody`**: másik karosszéria egy meglévő vázra: a `car` a játék egyik autója vagy egy hozzáadott autó
  `id`-je. Úgy megy, mint az az autó.
- **`rc.registerSkin`**: egy további festés. Csak `car`: az autó saját karosszériájához; `body`: egy hozzáadott
  karosszériához. A `texture2` a játék Buggy és Warhammer autójának második (B) textúrája, ezek kettőt használnak.
- A Gyors verseny autóválasztója a játék autóit sorolja fel, mindegyik után a hozzá adott karosszériákkal, majd a
  hozzáadott autókat az övéikkel. Az előnézet alatti **Skin** (Festés) sor választja a festést (a „-" a profil
  festése). A választásokat nem menti. A hálózati játék, az osztott képernyő, a garázs és a bajnokság a játék
  autóit használja.
- A `file` a mod egy jelenet-adatbázisa (`.sb`) a `<model>`, `<model>LOD1` .. `<model>LOD3` modellekkel: a teljes
  autó (váz és karosszéria), karosszériánál is. A modell objektumai az alapautóét követik (`WHEEL_FRONT_LEFT`, a
  tengelyek, a `booster_N` / `compressor_N` fejlesztés-alkatrészek ...): a játék a kerekek helyét a modellből veszi.
- A modell textúráinak adj a modhoz tartozó saját nevet, így egy másik autó textúráját sem cseréled le. A `skin` a
  festések textúranevének eleje; a modellnek mindet fel kell sorolnia (`<skin>1` .. `<skin><paints>`).
- A `physics` a játék saját mértékegységeiben ad értéket, a `physicsScale` az alapautó értékét szorozza. Nevek:
  `speedBaseMax`, `speedBoostMax` (km/h), `boostSpeedUp`, `boostSpeedDown`, `boosters`, `resonators`, `resonatorsForce`, `tyreUpgrades` (4 each), `tyresFront`, `tyresRear`, `angleDriftOn`, `speedDriftOn`, `coeffDriftRear`, `coeffDeepSand`, `coeffWater`, `speedAngMaxRel`, `frictionBearings`, `airResistance`, `angleSteer`, `springLength`, `springLenMin`, `springLenMax`, `springKPos`, `springKSpeed`, `springDx`, `springTouchPoint`, `springDz`, `coeffMomentOX`, `coeffMomentOZ`, `lenAxe`, `angleUpMax`, `angleDownMax`, `wheelRad` (6), `bodyRad` (4), `bodyPos` (4 x {x, y, z}), `centreMass`.
- Sugárhajtás (hajtóműves autóhoz, mint a PS2-es játék CCCP-je): ha a `physics` megadja a `jetForceForward` értéket, az autó sugárhajtást kap. A PS2-es játék kódját követi, és **csak a levegőben** hat (amikor egy kerék sem ér földet); a földön az autó a kerekeivel megy, mint bármelyik másik. A levegőben: az autó arra repül, amerre néz (az oldalirányú sodródása `jetSideDecayTime` alatt megszűnik), a gáz a vízszintes haladási iránya mentén tolja `jetForceForward` erővel (hátramenet a felével), a kormány `jetForceRotate` erővel tolja az oldalsó hajtóműnél (`jetLeverLen` távolságra), amíg a fordulási perdület el nem éri a `jetMaxYawImpulse` értéket, és az autó vízszintbe fordul (az iránya megmarad) legfeljebb 160 fok/másodperccel, így a kerekeire érkezik. Az erők nincsenek megszorozva az autó tömegével. Elfogadott, de nem használt kulcsok (a kiolvasott PS2-es kód sem használja őket): `jetStabYawSpeed`, `jetStabRollSpeed`, `jetStabRollAngle`, `jetRotateMinSpeed`, `jetCoeffSand`, `jetCoeffGrass`; a `jetPitchDecayTime` a `jetSideDecayTime` régi neve. A `jetGravitySpeed = {..}` és a `jetGravity = {..}` (legfeljebb hat pont, növekvő sebességek km/h-ban) az autó gravitációját a sebességétől teszi függővé, ahogy a PS2-es autónál van (a játék gravitációja 10); az autó ettől magasabbra és messzebbre is ugrik.
- Hangok (1.7), az `rc.registerCar` és az `rc.registerBody` számára: a `sound = "Overkill" | "Buggy" | "Warhammer"` (vagy 1 .. 3) megadja, melyik gyári autó motorhang-készletével szóljon az autó (alapértelmezés: az alapautóé); a `sounds = {motor_accel1 = "mycar_accel", ...}` egyes hangokat a mod saját fájljából játszik le: a kulcs a játék hangneve (az Overkill nevei minden készletre működnek: `motor_accel1`, `motor_engine`, `motor_idle`, `motor_off`, `motor_reverse`, `motor_decel1` .. `3`, `motor_accel1_ws`, `motor_engine_ws`, `motor_decel1_ws`, `Motor_flying2`, `Motor_flying_end2`, `car_boost`, `car_boost_end`, `car_flying`, `car_landing`, `car_break`, `car_cdt_*`, `car_surf_*`, `car_hit_*`), az érték egy kiterjesztés nélküli fájlnév a mod `Sound` mappájában (`Sound/mycar_accel.wav`). A hiányzó fájl a naplóba kerül, és a játék saját hangja szól. A hangbeállítás nélküli karosszéria úgy szól, mint az autója. Csak a játékos autója használja (az ellenfelek a játék közös AI-hangjaival szólnak). A motorhangnak nincs hangmagasság-váltása: a játék a `motor_accel1` felvételbe a sebességsáv szerint 0 / 1,38 / 3,35 / 6,81 másodpercnél lép be, ezért a csere ugyanígy emelkedjen.
- Mindegyik hívás eredménye `true`; az azonos `id`-jű autót / karosszériát felülírja. Legfeljebb 16 autó,
  48 karosszéria, 96 festés.

## 6b. Főmenü-bejegyzések, verseny indítása, tárgyak fellökése (1.9)

```lua
rc.registerMenu{id = "tutorial", name = {en = "Tutorial", hu = "Oktató"}, onSelect = function()
  rc.startRace{track = "beach_1", car = "Buggy", laps = 3, mode = "my_mode"}
end}

function onObjectHit(car, name)            -- a car knocked a can, a ball, a bottle ...
  rc.log(rc.carName(car) .. " hit " .. name)
end
```

| Függvény | Leírás |
|---|---|
| `rc.registerMenu{id =, name =, onSelect =}` | gombot ad a főmenühöz, a Mods és a Credits közé. A `name` szöveg vagy nyelvi tábla; az `onSelect` a gomb megnyomásakor fut le. A menüben összesen két ilyen gombnak van hely (az összes modra együtt); a harmadik figyelmeztetéssel kimarad, a hívás `false` értéket ad. Ha van bejegyzés, a menü gombjai kicsit közelebb kerülnek egymáshoz |
| `rc.startRace{track =, car =, laps =, mode =}` | Gyors versenyt indít a menükből. `track`: a játék tíz pályájának egyike (`"beach_1"` .. `"country_4"`, a megjelenített név, vagy 1 .. 10); `car`: 1 .. 3, `"Overkill"` / `"Buggy"` / `"Warhammer"`, vagy egy hozzáadott autó, illetve karosszéria azonosítója (alapértelmezés: a játékos autója); `laps`: a körök száma; `mode`: egy `rc.registerMode` hívással regisztrált játékmód azonosítója (alapértelmezés: sima verseny). `true`, ha az indítás sorba került (egy másodpercen belül megtörténik), különben `false` és az ok (verseny fut, hálózati játék, nincs kiválasztott játékos) |
| `rc.addSpin(car, x, y, z)` | ennyivel változtatja az autó szögsebességét (rad/s a világ tengelyei körül), például hogy a játékos a levegőben forgathassa az autót. Csak saját fizikájú autóra (a játékosokéra), hálózati versenyben nem; `true`, ha megtörtént |

### Hozzáadott pályák (1.10)

```lua
rc.registerTrack{id = "tutorial", name = {en = "Tutorial", hu = "Oktatópálya"},
  description = {en = "Learn to drive.", hu = "Tanulj meg vezetni."},
  level = "tutorial",                    -- RCCarsDB/tutorial.sb of the mod
  picture = "tutorial_pic",              -- the selection picture on the Quick race page
  loading = "tutorial_load",             -- the loading screen's big picture
  shots = {"tutorial_s1", "tutorial_s2"},  -- up to four more small pictures of the loading screen
  ai = "tutorial_ai.ini"}                -- Scripts/tutorial_ai.ini of the mod: the opponents
```

Az `rc.registerTrack` a mod egy pályáját adja a Gyors verseny oldalához, a játék tíz pályája után (összesen legfeljebb 8 hozzáadott pálya). Minden, amit megnevez, a játék saját formátumában van, a mod mappáiban:

- `level`: a pálya adatbázisa, `RCCarsDB/<level>.sb`, úgy felépítve, mint a játék pályái (a `Checkpoints` mappa a `cp_1` .. `cp_8` jelölőkkel, a `Player` példány, és így tovább).
- `picture`: a pálya kiválasztásakor mutatott textúra (a mod `Textures` mappájában). `loading`: a betöltőképernyő nagy képe; `shots`: legfeljebb négy további kis kép a betöltőképernyőre. Ami kimarad, annak a helyén a `picture` áll; `picture` nélkül az első gyári pálya képei látszanak.
- `ai`: az ellenfelek leírása a mod `Scripts` mappájában, úgy megírva, mint a játék `Scripts/AIlayouts.ini` fájlja: az `AIPlayer<n>` szakaszok és egy `AIRace1` szakasz a `PlayerPath`, `AI<n>Path` (felvett menetek a `CarProfiles/` mappában), `AI<n>Car`, `AI<n>Ref`, `AI<n>Races` stb. kulcsokkal. `ai` nélkül a pályán nincs ellenfél, és a játékos a pálya `Player` példányánál indul.
- `name`, `description`: szöveg vagy nyelvi tábla.

Az `rc.startRace{track = "<id>"}` az azonosítójával indít el egy hozzáadott pályát. A hozzáadott pályák nincsenek benne a Bajnokságban, a Szellemversenyben és a többjátékos oldalakon, és nem készül róluk rekord vagy statisztika.

## 7. A homokozó korlátai

- Elérhető: a Lua alapfüggvényei, a `table`, `string`, `math`, `utf8`, `coroutine`, valamint az `os.clock`,
  `os.time`, `os.date`.
- Nem elérhető: `io`, az `os` többi része, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- A `load` csak szöveges darabot fogad (szöveget; bináris darabot nem).
- A `collectgarbage` csak a `"count"` paramétert fogadja.
- Memória: modonként 64 MB.
- Idő: eseményhívásonként `LuaBudget` Lua utasítás. Az egy könyvtári híváson belüli hosszú munkát (például egy
  hatalmas `string.rep` vagy egy bonyolult minta) az utasításszámlálás nem méri; maradjanak egyszerűek a szkriptek.
- A szkriptek soha nem írnak játékfájlt, modfájlt vagy játékosmentést; csak a mod beállítás- és statisztikafájlja íródik.

## 8. Hibakezelés

- Egy betöltési hiba, futási hiba vagy túllépett keret csak azt a hívást szakítja meg. A játék megy tovább.
- Minden hiba bekerül a `game_dbg.log` fájlba `Lua [mod] mi: fájl:sor: üzenet` alakban (veremkiírással).
- 5 hiba után a mod szkriptjei kikapcsolnak („mod scripts disabled after repeated errors”). Javítsd a szkriptet,
  majd nyomd meg az Alkalmaz gombot a Modok képernyőn (vagy fejlesztői módban mentsd a fájlt, lásd lent).
- Ha egy hívás a keret több mint 80 %-át használta, egyszer figyelmeztetés jön.

## 9. Fejlesztői mód (`RcCarsRe.exe -dev`)

- A hibák és figyelmeztetések a konzolablakban látszanak: a hibasorok pirosak, a figyelmeztetések sárgák (Lua és a
  játék egyaránt); a hibák a játékon belüli piros sávban is megjelennek.
- A `lua` konzolparancs felsorolja a szkriptes modokat; a `lua <kód>` az utoljára betöltött mod állapotában futtat,
  a `lua <mod> <kód>` az adott modéban, és kiírja az eredményeket (kifejezés is működik, például
  `lua rc.race().state`).
- Gyors újratöltés: a mappás modok `.lua` fájljait a játék másodpercenként ellenőrzi; ha egy megváltozik, az adott
  mod szkriptjei újratöltődnek (zip modoknál: Alkalmaz). Az újratöltés minden kamera-, időjárás- és
  fénysáv-felülírást is megszüntet.

## 10. Példák

A `docs/modding/examples/` négy teljes modot tartalmaz. Másolj egy mappát a `RcCarsRe.exe` melletti `mods\` mappába:

- `laptime_hud`: az 1. játékos versenyideje (ugyanaz, mint a HUD órája), aktuális, előző és legjobb köride egy
  dobozban, a játék időformátumában; opciók: legjobb kör, méret, sarok.
- `checkpoint_sound`: az 1. játékos minden ellenőrzőpontjánál lejátssza a mod saját `sounds\ding.wav` hangját, és
  felvillantja a sorszámát.
- `drift_air`: amikor az 1. játékos autója egy ugrás után landol, kiírja a levegőben töltött időt, röviden rezeg és
  felvillantja a fénysávot, valamint `rc.stats`-szal megőrzi pályánként a legjobb repülési időt és az ugrások számát.
- `photo_mode`: fotómód (P vagy a kontroller Back / Share / Create gombja): a verseny megáll, a HUD eltűnik, szabad kamera, F12 / A a fotó, az rc.stats számolja őket (API 1.2).
- `zombies`: játékmód (API 1.4): fogócska / fertőzés a gépi autók ellen, lásd "Játékmódok".

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

## 11. Hibaelhárítás

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
