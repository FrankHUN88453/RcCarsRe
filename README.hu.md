# RcCarsRe

[English](README.md) | **Magyar** | [Русский](README.ru.md) | [Polski](README.pl.md)

Az RcCarsRe egy rajongói projekt, amely a 2003-as **RC Cars** (Creat Studio) PC-s játék futtatható állományát
építi újra visszafejtett C forrásból, hogy a játék a mai rendszereken is fusson és módosítható legyen.

![RcCarsRe: gyors verseny az első tengerparti pályán](docs/preview.webp)

*Gyors verseny az újraépített exében 2560 x 1440-ben, bekapcsolt valós idejű árnyékkal és tükröződéssel.*

> Ez a tároló egyelőre csak ezt a leírást és az előnézeti képet tartalmazza. Forráskód még nincs közzétéve, és
> az eredeti játék semmilyen része nem kerül ide soha.

## Mi ez

- Egy új `RcCarsRe.exe`, amely C nyelven készül az eredeti játék dokumentált viselkedése alapján.
- A játék egy telepített, jogtisztán birtokolt példányának adatfájljait használja (a DVD-s vagy a Steames
  kiadásét). Enélkül nem működik.
- A cél az eredetihez hű viselkedés. Az alapvető rutinokat egy tesztkörnyezet bitre pontosan összeveti az eredeti
  függvényeivel.
- A modern változtatások nem kötelezők, az `RcCarsRe.ini` fájlban kapcsolhatók; a fájl elején minden opció és
  annak lehetséges értékei fel vannak sorolva.

## Modern beállítások

- Direct3D 11 megjelenítő, amely az eredeti Direct3D 8 hívásait emulálja
- Natív felbontás, keret nélküli ablak, szélesvásznú látószög, a kezelőfelület és a HUD méretezése
- Élsimítás (MSAA / FXAA), anizotróp szűrés, legjobb textúraminőség
- Valós idejű árnyék (kaszkádos árnyéktérképek) az eredeti folt-árnyékok helyett
- Valós idejű tükröződés az autókon és szebb tenger (tükörkép, nézőszögtől függő átlátszóság, átlátszó sekély víz)
- Képkockasebesség-korlát és VSync beállítások (nincs 64 fps-es plafon), FPS-számláló
- HD menübetűtípus, HUD-javítások szélesvásznú képernyőre

## Modok

A játék fájljai lecserélhetők az exe melletti `mods` mappából: mappák vagy zip archívumok, textúrák CSI, PNG vagy DDS,
hangok és zene AU, WAV, MP3 vagy OGG formátumban, méretkorlát nélkül. A Modok menüben sorba rendezhetők, ki- és
bekapcsolhatók, és a változás újraindítás nélkül érvényesül. Hogyan működik:
[English](docs/MODDING.md) | [Magyar](docs/MODDING.hu.md) | [Русский](docs/MODDING.ru.md) | [Polski](docs/MODDING.pl.md).

## Lua szkriptek a modokban

A modok kis, homokozóban futó Lua szkripteket hozhatnak: HUD szövegek és képek, hangok, kör- és
ellenőrzőpont-események, és egy beállítási oldal a Modok menüben. A szkriptek csak helyben hatnak (HUD, hang,
napló); a versenyt és a játék fájljait nem változtathatják meg. Dokumentáció a teljes API-val és két példamoddal:
[English](docs/modding/LUA_SCRIPTING.en.md) | [Magyar](docs/modding/LUA_SCRIPTING.hu.md) |
[Русский](docs/modding/LUA_SCRIPTING.ru.md) | [Polski](docs/modding/LUA_SCRIPTING.pl.md).
A Lua 5.4 az MIT-licenc alapján szerepel ([LUA_LICENSE.txt](docs/modding/LUA_LICENSE.txt)).

## Állapot

A munka folyamatban van. A gyors verseny és a bajnokság elejétől a végéig lejátszható; a garázsban vásárlás és a
hálózati többjátékos mód még nem kész.

| Terület | Állapot |
|---|---|
| Intró, főmenü, Options, Quick race képernyők | működik |
| Zene, a kezelőfelület és a verseny hangjai | működik |
| Pályabetöltés és -megjelenítés, tenger, parti hab, patakok, vízesések | működik |
| A játékos autójának fizikája: ütközés, felfüggesztés, gumik, motor, kormányzás, antenna | működik |
| Gépi ellenfelek | működik (az eredeti útvonalválasztásuk folyamatban) |
| Verseny: visszaszámlálás, körök, ellenőrzőpontok, helyezések, HUD, térkép, versenyzőlista, eredménytábla | működik |
| Tárgyak fizikával, emberek, sirályok, rákok, kutyák, forgalom, őrök, pókok, keselyűk | működik, finomítás alatt |
| Autóeffektek: keréknyom, por, kipufogófüst, koszolódás, vízfröccsenés | működik |
| Köd, szünetmenü | működik |
| Az őrök és a páncélautó lövése | folyamatban |
| Bajnokság pénzdíjakkal, játékosprofilok, mentés az eredeti formátumban | működik |
| Garázs | a képernyők működnek, a vásárlás folyamatban |
| Osztott képernyő két játékosnak; Xbox, PlayStation 4 és DualSense kontrollerek rezgéssel | működik |
| VR (OpenXR), Discord-állapot | működik |
| Hálózati többjátékos mód (saját UDP-átvitel, először LAN) | folyamatban |
| Modtámogatás (`mods` mappa, Modok menü, Lua szkriptek) | működik |

## Amit ez a tároló nem fog tartalmazni

- Az eredeti játék futtatható állományát, könyvtárait, pályáit, modelljeit, textúráit, hangjait vagy bármely más
  tartalmát
- Másolásvédelem megkerülésére szolgáló eszközöket vagy csalásokat

## Jogi tudnivalók

Az RC Cars, valamint a hozzá tartozó nevek és tartalmak a jogtulajdonosaik tulajdonát képezik. Ez egy nem
hivatalos, nem kereskedelmi projekt, amely nem áll kapcsolatban velük, és amelyet nem ők támogatnak. A
használatához saját, jogszerűen megszerzett játékpéldány szükséges. Az előnézeti kép az újraépített exét mutatja
az eredeti játék adataival futás közben.

## Nyelvek

Ez a leírás angolul, magyarul, oroszul és lengyelül érhető el. Az angol változat a mérvadó.
