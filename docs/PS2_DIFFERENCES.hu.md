# RC Cars (PC) és Smash Cars (PS2): miben térnek el

*Más nyelveken: [English](PS2_DIFFERENCES.md), [Русский](PS2_DIFFERENCES.ru.md), [Polski](PS2_DIFFERENCES.pl.md)*

A PlayStation 2-es **Smash Cars** (2003) a PC-s **RC Cars** konzolos változata. Ez az oldal azokat az eltéréseket
sorolja fel, amelyek akkor kerültek elő, amikor a PS2-es játék autói modként bekerültek az újraépített PC-s
játékba.

**Hogyan készült.** A PC-s játék fájljait az európai PS2-es lemez (SLES-51800) fájljaival vetettük össze:
modellek, textúrák, hangbankok, beállításrekordok, valamint a program egyes részei, amelyben megmaradtak a
függvénynevek. Magát a PS2-es játékot ehhez nem játszottuk végig, ezért ami csak játék közben látszik (menük,
játékmódok, szabályok, nehézség), az itt nem szerepel. Ahol valami értelmezés és nem bizonyosság, ott jelezzük.

## Áttekintés

| | PC (RC Cars) | PS2 (Smash Cars) |
|---|---|---|
| Autók | 3: Overkill, Buggy, Warhammer | 13: négy váz három-három karosszériával, plusz a sugárhajtású CCCP |
| Festések | autónként több | karosszériánként 3, a CCCP-n 8 |
| Pályák | 10 (beach 1-4, country 1-4, urban 1-2) | 13 pálya |
| Motorhangok | három készlet, autónként egy, 44,1 kHz | egy készlet minden autóra, 22 kHz, rövidebb felvételek |
| Zene | MP3 fájlok | 7 szám |
| Irányítás a levegőben | nincs | légi irányítás trükkpontokkal és lassított „Matrix móddal" |
| Sugárhajtás | nincs | a CCCP a levegőben hajtóművekkel kormányoz és tolja magát |
| Textúrák | nagyobb felbontás, teljes színmélység | 256 színű textúrák, 64-256 képpont |

## Autók

A PS2-es játék tizenkét autóját négy vázból és vázanként három karosszériából rakja össze; a tizenharmadiknak
saját váza van. A vázak közül három megegyezik a PC-s játék három autójával: ugyanaz a futómű, milliméteren
belüli egyezéssel.

| Váz | PC-s autó | PS2-es karosszériák |
|---|---|---|
| Over | Overkill | Road Rage, Redneck, Beatle |
| Buggy | Buggy | Tornado, HotShot, Razor |
| Hummer | Warhammer | Warhammer, Skull Tank, Rockarolla |
| Half | a PC-s játékban nincs | Sting, Flashback, Blazer |
| Super | a PC-s játékban nincs | CCCP (három kerék, két hajtómű) |

A Half a Buggyhoz hasonló felépítésű (független kerekek), de kerekenként két rugója van, és nincs felső
lengőkarja. A Supernek egyetlen széles hátsó kereke van.

## Fizika

- A két játék ugyanazt a fizikát használja. Minden váznak egy beállításrekordja van, ugyanazokkal az értékekkel
  és ugyanabban a sorrendben, mint a PC-s játék autóbeállításai (sebességek, tapadás, rugók, kerékméretek,
  ütközési alak, fejlesztések).
- A három közös autó ütközési alakja a két játékban azonos. A hangolt értékeik (végsebesség, tapadás, a
  fejlesztések szorzói) nem: a PS2-es játék ezeket másképp állította be.
- A Half és a Super az Overkill ütközési alakját használja.
- A PS2-es rekordban van néhány többletérték, ami a PC-s játékban nincs; ezeket csak a Super használja (a
  hajtóműveihez).

## A CCCP hajtóművei

A PS2-es programból kiolvasva:

- A hajtóművek **csak a levegőben** működnek. A földön a CCCP a kerekeivel megy, mint bármelyik másik autó.
- A levegőben az autó arra repül, amerre néz: az oldalirányú sodródása azonnal megszűnik.
- A gáz előre tolja a vízszintes haladási iránya mentén; a hátramenet fele akkora erővel tol hátra.
- A kormány az egyik oldali hajtóművet járatja, ez fordítja az autót.
- Repülés közben az autó vízszintbe fordul, így a kerekeire érkezik.
- A gravitációja a sebességgel gyengül: álló helyzetben a szokásos nagyjából fele, végsebességnél szinte nulla, ezért magasra és messzire ugrik. (Hogy a gravitáció a sebességet követi, az a programban van; hogy a játék melyik görbéjét használja hozzá, azt az értékei alapján választottuk ki, nem követtük végig.)

## Légi trükkök és „Matrix mód"

A PS2-es programban van egy minden autóra érvényes légi irányítási rendszer, ami a PC-s játékban nincs: az autó
a levegőben forgatható, a fordulatok és a magasság pontot érnek.

A „Matrix mód" lassítás ugrás közben. A PS2-es programból kiolvasva akkor kapcsol be, ha ezek mind teljesülnek:

- be van kapcsolva a beállítások menüben (a játékos kétállású beállítása);
- verseny zajlik, és az nem a két kizárt versenytípus egyike (hogy melyik kettő, azt nem azonosítottuk);
- a játékos autójának több mint 0,02 másodperce nincs sem kerék-, sem tetőérintkezése;
- az autó 0,1 másodperce esik, vagyis épp túl van az ugrás tetőpontján.

Ekkor az idő 0,2 másodperc alatt az ötödére lassul. Amikor az autó földet ér, az idő fél másodperc alatt
visszaáll. A beállítások között van hozzá minimális trükkpontszám is, de az 0-ra van állítva.

## Hangok

- A PC-s játékban három motorhang-készlet van (autónként egy). A PS2-es játékban egy van, minden autó ezt
  használja, a PC-s Overkill-készlet neveivel; a felvételek rövidebbek és gyengébb minőségűek.
- Egyik PS2-es autónak sincs saját hangja, a CCCP-nek sem.
- A PS2-es játékban van néhány autóhang, ami a PC-sből hiányzik: csúszás aszfalton és földön, fűnek ütközés,
  valamint a `motor_flying_matrix`, a lassított repülés motorhangja.
- Minden PS2-es pályának saját hangbankja van; benne vannak a pálya állatai és tárgyai is.

## Modellek és textúrák

- A PS2 minden felület mindkét oldalát kirajzolja, a PC csak az elülsőt. A tükrözött PS2-es alkatrészek (az autó
  jobb oldala) kifordítva vannak tárolva, ezért a PC-hez meg kell fordítani őket.
- A PS2-es textúrák 256 színűek: a karosszériafestések 256 x 256, a váz 128 x 128, a gumik 64 x 64 képpontosak.
  A közös autók PC-s textúrái nagyobbak, és nem ugyanazok a képek.
- A PS2-es autóknak külön, egyszerű árnyékmodelljük van.

## Pályák

A PS2-es oktatópályából kiolvasva (egy bekerített udvar, ami a PC-s játékban nincs meg):

- **Fény.** A PC-s pályákat fénytérkép világítja meg, ami egy második textúraréteg. A PS2-es pályákon a fény a
  geometria minden sarkának színébe van beleszámolva.
- **Textúrák.** A PS2-es pályatextúrák többsége 256 színű; az átlátszó részűek (kerítésháló, fák, a földre festett
  jelek) 16 vagy 32 bites képek.
- **Fű.** A PS2-es játékban van fűrendszer, a PC-sben nincs: több ezer kis növény (az oktatóudvaron kb. 2600),
  nyolc fajta egyetlen képből kivágva. Lengenek, és az autók alatt elhajlanak.
- **Tárgyak.** A lökhető tárgyak a két játékban ugyanazok a fajták: dobozok, labdák, vödrök, bóják. A PS2-es pálya
  mindegyiknek a helyét és az ütközési alakját tárolja; van benne egy sisak is, amihez a PC-s játékban nincs modell.
- **Ellenőrzőpontok.** A PS2-es pályán egyszerű pontlista van, a PC-sen jelölő objektumok.
- **Szereplők.** Az oktatóudvaron egy triciklis fiú van (animált modell, saját hanggal) és két gokart sofőrrel, amelyek a rögzített körüket járják (Kart.StartProfile).

## Fájlok

| | PC | PS2 |
|---|---|---|
| Pályák és autók | `.sb` adatbázisok | `.S_A` ... modellfájlok, pályánként egy `.SBF` jegyzék |
| Hangok | hangonként egy fájl | pályánként egy `.MSB` hangbank |
| Zene | MP3 | `TRACK1` - `TRACK7` |
| Videók | `Intro.dat` | három videófájl |

## Az újraépített PC-s játékban

Az `extension` mod hozzáadja a PS2-es játékot az újraépített játékhoz: a PS2-es oktatóudvart pályaként (a főmenüben a "Tutorial" gomb az intróval és a három feladattal, a mod config.ini-jében kikapcsolható) és a PS2-es autókat: a Sting és a CCCP új autóként, saját
fizikai értékekkel jelenik meg, a többi nyolc karosszéria a három PC-s autó és a Sting további karosszériájaként.
A Lua-függvényeit a [modding/LUA_SCRIPTING.hu.md](modding/LUA_SCRIPTING.hu.md) 6a. fejezete írja le. Az
átalakított autók a felhasználó saját PS2-es lemezéből készülnek, és nem kerülnek terjesztésre.

A modnak saját `config.ini` fájlja van: a `[SlowMotion]` `SlowMotion=1` bekapcsolja a Matrix mód lassítását ugráskor
(egyjátékos módban), a `Tutorial=1` megjeleníti a főmenüben a PS2-es oktatás "Tutorial" gombját.

Az oktatópálya PC-s pályává van alakítva: a geometria, a textúrák, a beleszámolt fény, az ellenőrzőpontok, a fű
(leng és letaposható), a tárgyak (a PS2-es dobozok, labdák, vödör, bója és sisak modellként), az ellenfelek, a
triciklis fiú és a két gokart a PS2-es útvonalán, valamint az oktatás három feladata a PS2-es időkorlátokkal és
trükkpontozással. Az udvarban most már ott vannak a bogarak is (járkálnak és elmenekülnek, mint a PC-s játék
pókjai; a PS2-eshez képest nem repülnek el), a földön heverő szemét, a fiú és a gokartok saját hangjai (pedálozás,
csengő, a gokartok motorja) és a feladatok tippjei egy gombra (H vagy a kontroller Back gombja). Mint minden más,
ezek is a felhasználó saját PS2-es lemezéből készülnek, és nem kerülnek terjesztésre.

Nem került át: a többi PS2-es pálya, a légi trükkök pontozása az oktatáson kívül, a PS2-es hangok az oktatóudvaréin
kívül, az oktatás intrójának rövid bemutató versenye és a jutalmai.
