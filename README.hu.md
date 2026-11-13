# RcCarsRe

[English](README.md) | **Magyar** | [Русский](README.ru.md) | [Polski](README.pl.md)

Az RcCarsRe egy rajongói projekt, amely a 2003-as **RC Cars** (Creat Studio) PC-s játék futtatható állományát
építi újra visszafejtett C forrásból, hogy a játék a mai rendszereken is fusson és módosítható legyen.

> Ez a tároló egyelőre csak ezt a leírást tartalmazza. Forráskód még nincs közzétéve, és az eredeti játék
> semmilyen része nem kerül ide soha.

## Mi ez

- Egy új `RcCarsRe.exe`, amely C nyelven készül az eredeti játék dokumentált viselkedése alapján.
- A játék egy telepített, jogtisztán birtokolt példányának adatfájljait használja (a DVD-s vagy a Steames
  kiadásét). Enélkül nem működik.
- A cél az eredetihez hű viselkedés. Az alapvető rutinokat egy tesztkörnyezet bitre pontosan összeveti az eredeti
  függvényeivel.
- A modern változtatások nem kötelezők, az `RcCarsRe.ini` fájlban kapcsolhatók.

## Modern beállítások

- Direct3D 11 megjelenítő, amely az eredeti Direct3D 8 hívásait emulálja
- Natív felbontás, keret nélküli ablak, a kezelőfelület méretezése
- Élsimítás (MSAA / FXAA), legjobb textúraminőség
- Képkockasebesség-korlát és VSync beállítások (nincs 64 fps-es plafon), FPS-számláló
- HD menübetűtípus

## Állapot

A munka folyamatban van. Teljes játékként még nem játszható.

| Terület | Állapot |
|---|---|
| Intró, főmenü, Options, Quick race képernyők | működik |
| Zene és a kezelőfelület hangjai | működik |
| Pályabetöltés, a pálya kirajzolása, animált víz | működik |
| A rögzített útvonalukat követő gépi autók | működik (átmeneti) |
| A játékos autójának fizikája: pályaütközés, felfüggesztés, gumik, motor, kormányzás | működik, finomítás alatt |
| Látható felfüggesztés és kerekek | az első autó kész, a többi folyamatban |
| Antenna, versenykamera | folyamatban |
| Rajtlámpák, körök, ellenőrzőpontok, HUD | nincs elkezdve |
| Egyéb játékmódok, garázs, többjátékos mód | nincs elkezdve |

## Amit ez a tároló nem fog tartalmazni

- Az eredeti játék futtatható állományát, könyvtárait, pályáit, modelljeit, textúráit, hangjait vagy bármely más
  tartalmát
- Másolásvédelem megkerülésére szolgáló eszközöket vagy csalásokat

## Jogi tudnivalók

Az RC Cars, valamint a hozzá tartozó nevek és tartalmak a jogtulajdonosaik tulajdonát képezik. Ez egy nem
hivatalos, nem kereskedelmi projekt, amely nem áll kapcsolatban velük, és amelyet nem ők támogatnak. A
használatához saját, jogszerűen megszerzett játékpéldány szükséges.

## Nyelvek

Ez a leírás angolul, magyarul, oroszul és lengyelül érhető el. Az angol változat a mérvadó.
