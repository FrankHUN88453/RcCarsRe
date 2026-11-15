# Lua szkriptek a modokban

[English](LUA_SCRIPTING.en.md) | **Magyar** | [Русский](LUA_SCRIPTING.ru.md) | [Polski](LUA_SCRIPTING.pl.md)

Az RcCarsRe futtatni tudja a modokhoz mellékelt kis Lua szkripteket. Egy szkript olvashatja a versenyt (pálya,
körök, autók, helyezések, köridők), reagálhat eseményekre (kör, ellenőrzőpont, ütközés, víz, visszahelyezés, a
verseny vége), és helyi dolgokat tehet: szöveget, képet és téglalapot rajzol a HUD-ra, hangot játszik le, a naplóba
ír, és megőrzi a saját beállításait. A szkriptek nem változtathatják meg a versenyt, az autókat és a játék fájljait.

A nyelv a [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, MIT-licenc, lásd
[LUA_LICENSE.txt](LUA_LICENSE.txt)).

## 1. Áttekintés

- Minden bekapcsolt mod (mappa vagy zip egy `mods` mappában, lásd [MODDING.hu.md](../MODDING.hu.md)) tartalmazhat `.lua` fájlokat.
- Minden mod saját Lua állapotot kap. A modok nem látják egymás globális változóit.
- A modok a Modok képernyő sorrendjében töltődnek be alulról felfelé: először a legkisebb prioritású, utoljára a
  lista teteje.
- A játék meghívja a szkript globális eseményfüggvényeit (`onFrame`, `onLap`, ...), ha léteznek.
- Minden, amit egy szkript tesz, a saját gépeden marad: HUD, hang, napló, a beállításfájlja. A szkriptek soha nem
  küldenek semmit a hálózaton, és nem hatnak a többi játékosra egy hálózati versenyben.

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

A `car` az autó sorszáma, 1 .. `rc.race().cars`. A `results` helyezési sorrendű lista; minden eleme: `car`,
`place`, `finished`, `time`, `bestLap` (hiányzik, ha nincs), `lap`, `name`.

## 5. API referencia (`rc` tábla)

### Olvasás

| Függvény | Visszaad |
|---|---|
| `rc.version` | az API verziója (`"1.0"`) |
| `rc.modName` | a mod neve |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = másodpercek a rajt óta (előtte -1). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (az 1. játékos célba ért), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, place, isPlayer, isAi, isGhost, player, finished, name}` vagy `nil`. `speed` km/h-ban; `player` = 1 / 2 egy játékos autójánál |
| `rc.player(n)` | az `n`. játékos autójának táblája (1 vagy 2, alapból 1), vagy `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: a renderelés mérete pixelben, az aktuális képernyő neve, VR be, osztott képernyő |

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

### A saját mod fájljai

| Függvény | Jelentés |
|---|---|
| `rc.readFile(path)` | a fájl bájtjai szövegként, vagy `nil, üzenet`. Csak a szkript saját modja olvasható |
| `rc.include(path)` | a saját mod egy `.lua` fájlját egyszer lefuttatja és visszaadja az eredményét (a későbbi hívások ugyanazt adják), mint a `require` |

### Beállítások

Tárolás: `Saves\Mods\<mod>.ini` a `RcCarsRe.exe` mellett (zip modnál `<mod>.zip.ini`), `[Settings]` szakasz.
Más fájl nem íródik.

| Függvény | Jelentés |
|---|---|
| `rc.setting(key, default)` | a tárolt érték a `default` típusára alakítva (logikai, szám, szöveg); tárolt érték nélkül a `default`, vagy az opció alapértéke |
| `rc.setSetting(key, value)` | logikai értéket, számot vagy szöveget tárol (`nil` törli); azonnal fájlba ír, ezért ne hívd minden képkockában |
| `rc.options{ ... }` | a mod Beállítások oldalának opciói (lent) |

Kulcsok: betűk, számjegyek, `_`, `.`, `-`, legfeljebb 63 karakter. Értékek: legfeljebb 1000 bájt, sortörés nélkül.

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
- A szkriptek soha nem írnak játékfájlt, modfájlt vagy játékosmentést; az egyetlen írt fájl a mod beállításfájlja.

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
  mod szkriptjei újratöltődnek (zip modoknál: Alkalmaz).

## 9. Példák

A `docs/modding/examples/` két teljes modot tartalmaz. Másolj egy mappát a `RcCarsRe.exe` melletti `mods\` mappába:

- `laptime_hud`: az 1. játékos aktuális, előző és legjobb köride egy dobozban; opciók: legjobb kör, méret, sarok.
- `checkpoint_sound`: az 1. játékos minden ellenőrzőpontjánál lejátssza a mod saját `sounds\ding.wav` hangját, és
  felvillantja a sorszámát.

Egy minimális szkript:

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

## 10. Hibaelhárítás

| Probléma | Ellenőrizd |
|---|---|
| Semmi sem történik | `LuaScripts=1` és `Mods=1` a `RcCarsRe.ini` fájlban; a mod be van kapcsolva a Modok képernyőn; a fájl a mod gyökerében vagy a `scripts\` mappában van; a `game_dbg.log` tartalmazza: `Lua [mod]: ... loaded` |
| „mod scripts disabled after repeated errors” | olvasd el az első `Lua [mod]` hibasorokat a `game_dbg.log` fájlban, javítsd a szkriptet, nyomd meg az Alkalmaz gombot |
| „instruction budget exceeded” | az esemény egyszerre túl sokat dolgozott; oszd el több képkockára, vagy emeld a `LuaBudget` értékét |
| Nem látszik a HUD elem | a HUD hívások csak egy képkockáig élnek: az `onFrame`-ből hívd őket; nézd meg a szín alfa bájtját (`0xFF......` átlátszatlan) |
| „texture ... not found” / „sound ... not found” (sárga) | a fájl neve és mappája a modban; PNG, DDS vagy CSI kép; WAV, OGG, MP3 vagy AU hang |
| A szövegben `?` jelenik meg | UTF-8 kódolással írd a szkriptet; a játék betűtípusa csak a nyelve kódlapjának karaktereit ismeri |
| Hibák a -dev konzolon | a hibasorok pirosak, a figyelmeztetések sárgák; ugyanezek a sorok a `game_dbg.log` fájlban is ott vannak |
