# Modok készítése az RcCarsRe-hez

[English](MODDING.md) | **Magyar** | [Русский](MODDING.ru.md) | [Polski](MODDING.pl.md)

Az RcCarsRe (az RC Cars újraépített exe-je) modokat tud betölteni. Ezek olyan fájlok, amelyek a játék saját fájljait
helyettesítik, a játék mappáinak érintése nélkül. Az eredeti játék nem támogat modokat; ez az újraépítés modern
funkciója, amit a `RcCarsRe.ini [Modern] Mods=1` kapcsol (ez az alapértelmezés). `Mods=0` esetén, vagy ha nincs `mods`
mappa, a játék pontosan azokat a fájlokat olvassa, amelyeket az eredeti.

## Hová kerülnek a modok

Az `RcCarsRe.exe` mellé, egy `mods` nevű mappába. A játék saját mappájában lévő `mods` mappát is beolvassa (például
a Steam-es példány `RCCars\mods` mappáját). Az exe egyikbe sem ír soha.

```
RcCarsRe.exe
RcCarsRe.ini
mods\
    BetterSkins.zip            mod zip archívumként
    LoudReset\                 mod sima mappaként
        Sound\cp_reset.wav
```

Egy mod vagy egy `mods\<név>\` mappa, vagy egy `mods\<név>.zip` archívum. Benne a fájlok a játék saját relatív
útvonalát viselik, ugyanúgy, mint a játék mappájában (DVD-s telepítés) vagy az `RCCars.pack` fájlban (Steam-es kiadás):

| Mi                             | Útvonal a modban (példák)                                    |
|--------------------------------|--------------------------------------------------------------|
| textúrák                       | `Textures.1\sand.csi`, `Textures.2\...`, `Textures.3\...`    |
| textúrák, minden minőségben    | `Textures\sand.png` (a Textures.1, .2 és .3 helyett)         |
| hangok                         | `Sound\cp_reset.au`, `Sound\snd.ini`                         |
| zene és intro                  | `Tracks\Dead_Track01.mp3`                                    |
| beállítások                    | `Settings\...`                                               |
| pályák és adatbázis            | `RCCarsDB\...`, `RCCars.sb`                                  |
| nyelv, betűtípusok             | `Language\Game\English.tbl`, `Language\English\...`         |
| autók, forgalom, emberek       | `CarProfiles\...`, `Profiles\...`                            |
| szkriptek, spline-ok, arcok    | `Scripts\...`, `Splines\...`, `FacesSys\...`, `Faces\...`   |
| indítási konfiguráció          | `Config.gm`, `Autoexec.gm`                                   |

Bármely fájl, amit a játék beolvas, lecserélhető. A játék által listázott mappákba új fájlok is felvehetők (például
új arcok vagy betűtípus-lapok); ezek a játék saját fájljai után jelennek meg. A nevekben a kis- és nagybetű nem
számít, a `/` és a `\` egyenértékű. Ha egy zip egyetlen, a moddal azonos nevű főmappát tartalmaz (`BetterSkins.zip`,
benne `BetterSkins\Sound\...`), azt úgy olvassa, mintha az a mappa ott sem lenne.

## Szkriptek

Egy mod Lua-szkripteket is tartalmazhat (`*.lua` a gyökerében vagy a `scripts\` mappában): HUD-szövegek és képek,
hangok, saját beállítóoldal a Mods képernyőn, valamint (API 1.1) kamera, köd, nap, fények, kontroller-rezgés /
fénysáv és saját statisztikák, mind csak a saját gépeden. Lásd: [modding/LUA_SCRIPTING.hu.md](modding/LUA_SCRIPTING.hu.md). Egy mod saját **játékmódot** is adhat (Lua API 1.4: szabályok, gépi parancsok, autócsere, zárójelenet): a Gyors verseny képernyő Mód sorában jelenik meg; a példa a `docs\modding\examples\zombies` (a játékhoz másold a `mods\` mappába). Egy mod **saját pályákat** is adhat: a pályát Blenderben készítsd el az RC Cars Track Editor addonnal, ami modként exportálja; az útmutató és egy minta pálya a `docs\modding\examples\custom_track` mappában van.

## Formátumok

A játék az eredeti fájlneveket kéri. Egy mod ugyanazt a fájlt ugyanazon a néven, de más kiterjesztéssel, más
formátumban is adhatja, és az exe átalakítja:

- **Textúrák** (a játék a `név.csi` fájlt kéri): `név.csi`, `név.png`, `név.dds`, vagy nagy dinamikatartományú
  `név.hdr` (Radiance) / `név.exr` (OpenEXR: ZIP, ZIPS, RLE vagy tömörítés nélkül; PIZ / DWA nem) - pl. HDRI égbolt;
  a fényerőt a játék magától hozza tartományba (automatikus expozíció).
  - Minőségi mappák: egy mod adhat `Textures.1\x.csi`, `Textures.2\x.csi` és `Textures.3\x.csi` fájlt (mindegyik az
    ugyanabban a mappában lévő fájlt cseréli; a játék a választott textúraminőség mappáit olvassa, a legjobbat
    először), és / vagy `Textures\x.csi` fájlt (mindhármat helyettesíti; a minőségi mappában lévő fájl erősebb nála).
    A mod textúrája a minőségi beállítástól függetlenül használatba kerül: ha a modban csak egy másik minőségi
    mappában van meg, mint amit a játék előnyben részesít, akkor is az kerül elő a játék sajátja helyett.
  - A nyelvi mappa képei (`Language\English\logoRC_Main.csi`, a menü logói és a verseny üzenetei) ugyanígy
    cserélhetők a nyelv mappájának nevével.
  - A mod saját `.csi` fájlját engedékenyen olvassa: bármilyen méret jó. Ha a fejléc több mip-szintet nevez meg,
    mint amennyi a fájlban van (egyes eszközök ilyet írnak egy kép nagyításakor: az eredeti fejléce 8 szinttel, a
    fájlban csak az első), a hiányzó szinteket elkészíti (ARGB8888 fájloknál), vagy a meglévő szintekkel olvassa
    (más formátumoknál). A 0 mip-szám 1-nek számít. Ha egy `.csi` még az első szintjét sem tartalmazza, elutasítja
    (és naplózza).
  - PNG a Windows Imaging Componenten keresztül (a Windows része): 8 / 16 bites, palettás, szürke, alfával vagy
    anélkül.
  - DDS: BC1 (DXT1), BC2 (DXT2/3), BC3 (DXT4/5), BC4 (ATI1), BC5 (ATI2), BC7 (DX10 fejléc), és tömörítetlen
    RGBA / RGB / BGRA / 565 / 1555 / 4444 / luminancia / alfa. A mip-szinteket úgy használja, ahogy a fájlban vannak;
    a hiányzókat elkészíti (2 x 2 átlag). A BC4 szürkén, a BC5 vörös / zöldként jelenik meg. Az sRGB formátumokat
    sima értékként veszi.
  - Kocka-textúrák (az autófényezés tükröződése, `cubemap_racer`): a játék a `cubemap_racer.csi` fájlt és hat lapját
    olvassa, `cubemap_racer.1.csi` .. `.6.csi` (+X, -X, +Y, -Y, +Z, -Z). Egyetlen, mind a hat lapot tartalmazó
    kocka-DDS (`cubemap_racer.dds`) mind a hét fájlt helyettesíti. Ha egyenként cseréled őket, minden lapnak a
    `cubemap_racer.csi` méretével kell egyeznie.
- **Hangok és zene** (a játék `.au` / `.wav` hangeffekteket és `.mp3` zenét kér): a `.au`, `.wav`, `.mp3`, `.ogg`
  bármelyike bármelyik helyett állhat.
  - WAV: PCM 8 / 16 / 24 / 32 bit, float 32 / 64 bit, WAVE_FORMAT_EXTENSIBLE, más WAV-kodekek a Media Foundationön
    keresztül; `.au`: a játék saját formátuma (RIFF WAVE .au névvel) vagy Sun / NeXT .au (mu-law, A-law, PCM, float);
    MP3 (és más, a Windows által dekódolt formátumok) a Media Foundationön keresztül; OGG Vorbis az stb_vorbis
    segítségével.
  - Bármilyen hossz, mintavételi frekvencia és csatornaszám. A hangeffekteket 16 bites PCM-re alakítja (a 8 / 16
    bites mono vagy sztereó PCM pontosan változatlan marad); kettőnél több csatornát sztereóra kever le; a 100 ..
    200000 Hz-en kívüli frekvenciát 48000 Hz-re mintavételezi újra. Az olyan zenét, amit a DirectShow magától nem
    játszik le (.ogg, .au), vagy ami zipben van, egy ideiglenes .wav fájlba / másolatba írja a
    `%TEMP%\RcCarsRe_mods_<folyamatazonosító>\` mappában; ezt a játék kilépéskor törli.

## Ha egy mod fájlja hibás

Ha egy mod fájlját nem lehet megnyitni, beolvasni, kicsomagolni vagy dekódolni (textúra, hang, zeneszám, beállítás-
vagy szövegfájl), a játék helyette a saját eredeti fájlját olvassa, és az okát egyszer naplózza (`Mods: <mod>: <file>
can't be decoded (...); the game's own file is used`). A fájlt addig nem kínálja fel újra, amíg a modokat újra nem
alkalmazzák. Egy textúra egy mod miatt soha nem marad hiányzó, és bekapcsolt modoknál egy hiányzó interfész-textúra
már nem akasztja meg az indítást a töltőképernyőn (naplózza, és a menük mennek tovább). Az olyan fájlokat, amelyek
tartalmát a játék maga nem tudja ellenőrizni (belül sérült pálya-`.sb`, hibás értékeket tartalmazó szkript), továbbra
is úgy olvassa, ahogy a mod adja.

## Méretek

A játéknak nincs saját méretkorlátja: egy 4096 x 4096-os textúra lecserélhet egy 256 x 256-osat, és a saját méretében
kerül használatba, minden textúraminőségben (`TexQual`, `Textures.1 / .2 / .3`: a mod textúrája minden minőségi
mappában nyer). A textúráknak nem kell négyzetesnek vagy kettő hatványának lenniük. A korlát a Direct3D 11-é: oldalanként
16384 texel. Egy textúra legfeljebb 10 mip-szintet kap (a .csi formátum korlátja), ami a méret 1 / 512-éig megy le: a
mintavételezéshez bőven elég. Memória: egy 4096 x 4096-os textúra betöltés közben kb. 85 MB-ot foglal, és 85 MB
videomemóriát.

Amik pixelben tartják a jelentésüket: a betűtípus-lapokat (`Language\...` Smash betűtípusok és a műszerfal
betűtípusa) a játék rögzített pixelméretű betűcellákra vágja, ezért egy betűtípus-lapnak meg kell tartania az eredeti
méretét és elrendezését. Néhány képet a játék kódja pixelenként olvas (a pályák fénytérképei, a versenyzők arcképei a
`Faces` / `FacesSys` mappákban): ezeknél más méreteket nem teszteltünk; a biztonság kedvéért tartsd meg az eredeti
méretet.

## Betöltési sorrend

A betöltési sorrend egy lista, amelynek **a teteje a legfontosabb mod**: ha két modban ugyanaz a fájl van (bármelyik
formátumában), a listában feljebb lévő mod fájlja kerül használatba. Egy modon belül a kért kiterjesztésű fájl nyer a
többi formátum felett.

1. `[Modern] ModOrder=A,B,C` (opcionális): ezek a modok kerülnek felülre, ebben a sorrendben: `A` nyer `B` felett,
   `B` a `C` felett. (Változás 2026-11-15: korábban a későbbi név nyert.)
2. A ModOrder-ben nem szereplő modok alájuk kerülnek, név szerint rendezve (kis- és nagybetű nem számít; közöttük a
   név szerinti első nyer). Azonos nevű mappa és zip: a mappa kerül előbbre.
3. `[Modern] ModsDisabled=A,B` (opcionális): ezek a modok nem töltődnek be. Az `A` az A nevű mappát és zipet is
   jelenti, az `A.zip` csak a zipet, az `A\` csak a mappát (ugyanezek a formák a ModOrder-ben is működnek).
4. Ha egy azonos nevű mod mindkét mods mappában (az exe mellett és a játék mappájában) megvan, csak egyszer veszi,
   az exe mellettit.

## A Mods képernyő

`[Modern] ModsMenu=1` esetén (ez az alapértelmezés) a főmenü „Demo play” pontja (a demóverseny még nincs
újraépítve) helyén a **Mods** áll (a játék nyelvén Modok / Моды / Mody). A képernyő minden talált modot listáz,
betöltöttet és nem betöltöttet is, betöltési sorrendben (a felső nyer), a fájljai számával, azzal, hogy a játék hány
fájlját cseréli, és egy piros `!` jellel, ha valamelyik fájlja nem dekódolható (a kiválasztott mod részletei a lista
alatt látszanak, az okok a `game_dbg.log`-ban). Az első sorban a **Mods** az egész modtámogatást kapcsolja
(`[Modern] Mods`).

- Fel / le (vagy az egér) választ modot, PgUp / PgDn egy oldalt görget; balra / jobbra, Enter vagy Szóköz (a
  kontroller A gombja) be- vagy kikapcsolja;
- **Move up** / **Move down** (a jobb oldali menügombok) mozgatja a kiválasztott modot a listában;
- **Refresh** újra listázza mindkét mods mappát: az azóta hozzáadott modok a lista aljára kerülnek, bekapcsolva; a
  törölt modok eltűnnek; minden mod számai újra elkészülnek. A még nem alkalmazott sorrend és kapcsolók megmaradnak.
  A Refresh semmit nem tölt be: az az Apply dolga;
- **Apply** beírja a `Mods`, `ModOrder` (minden mod, a felső először) és `ModsDisabled` kulcsot az `RcCarsRe.ini`-be
  (ha változtak), kiírja: „Applying mods...”, azonnal az új módon tölti be a modokat, kiírja: „Mods applied”, majd
  visszatér a főmenübe. Változás nélkül az Apply is újratölti a modok fájljait (használd egy mod fájljainak
  szerkesztése után);
- **Main menu** (vagy Esc / a kontroller B gombja) elveti a változtatásokat.

A képernyő csak az `RcCarsRe.ini`-t írja, soha nem a mods mappákat vagy a játék mappáit.

### Amit az Apply azonnal újratölt (újraindítás nélkül)

- minden textúrát, ami a textúramappákból és a nyelvi mappából jön (menük, logók, gombok, autók festése, a
  `cubemap_racer` lapjai, az interfész képei), a Smash betűtípusok lapjait és a versenyzők arcait (`FacesSys`, `Faces`);
- a hangeffekteket (`Sound\*`, a menük saját hangjait is) és a `snd.ini` / `chn.ini` táblákat;
- a zenét: minden zeneszám fájlját újra megkeresi (egy mod MP3 / OGG / WAV fájlja egy szám helyett), és a menük
  zenéje újraindul;
- a `Settings\*` csúszkafájlokat (a következő használatkor olvassa újra; a saját beállításaid az Options oldalakon az
  `RCCars.crs` fájlban vannak, és változatlanok maradnak);
- a `Language\Game\<nyelv>.tbl` nyelvi táblát (a főmenü szövegeit azonnal, a többi képernyőét megnyitáskor);
- a `Scripts\championship.ini` és `Scripts\AIlayouts.ini` fájlt.

Egy verseny minden része (pályák, autók, azok `.sb` fájljai, AI-útvonalak, `CarProfiles`, `Profiles`, `UPGRADES.ini`,
pályaszkriptek) a verseny betöltésekor olvasódik be, így a következő verseny már a modok fájljait használja.

### Amihez újraindítás kell

Azok a fájlok, amelyeket a játék csak az indításkor olvas: `Config.gm`, `Autoexec.gm` (és minden `*.gm`: a mappák, a
változók, a zene számlistája), a `RCCars.sb`, `Interface.sb` és `RaceTextures.sb` jelenet-adatbázisok (az
objektumaik, a főmenü autói, a beágyazott képeik, az interfész textúralistája és hangcsatornái) és a `Splines\`. Ha
egy mod ezek valamelyikét módosítja, az Apply ezt jelzi („Some files need a restart”), és a `game_dbg.log` megnevezi
a fájlokat. Az adatbázisba (`.sb`) ágyazott képek továbbra is az adatbázisból jönnek, mint indításkor. Az intróvideók
csak indításkor játszódnak le. A nyelv mappája (`Language\<név>\`, a tábla 2. szövegéből) az indításkori marad.

## Ami nem modolható

- A játékosmentések (`Players\`, minden `*.scp`), a szellem-rekordok (`GhostRecords\`) és a beállítástár `RCCars.crs`
  (`RCCars.crs.bak`): ezeket a játék írja, ezért egy mod példányát figyelmen kívül hagyja (és naplózza).
- A játék mappáján kívüli fájlok (abszolút útvonal a `Config.gm`-ben), az exe és a DLL-jei, az `RcCarsRe.ini`.
- Zip archívumok: csak „stored” és „deflate” bejegyzések, titkosítás nélkül, ZIP64 nélkül (4 GB / 65535 fájl fölötti
  archívumok).
- A pályafájlok beágyazott textúráit magából az `.sb` fájlból olvassa: cseréld le az egész `.sb`-t, vagy a pályák
  által megnevezett textúrákat, amelyeket a `Textures.*` mappákban keres, mint minden más textúrát.

## A napló

Az exe melletti `game_dbg.log` az indításkor felsorolja: minden talált modot (zip vagy mappa, a fájljai száma), minden
fájlt és hogy mit cserél (`Mods: BetterSkins: Textures\car_askin11.png replaces textures.1\car_askin11.csi`), az új
fájlokat, egy későbbi mod által elrejtett fájlokat, a figyelmen kívül hagyott fájlokat és a nem dekódolható fájlokat
(az okkal; ezeknél a játék saját fájlja kerül használatba), majd egy összegzést. Az átalakításokat akkor naplózza,
amikor a játék betölti a fájlt (`decoded (PNG 2048x2048)`, `converted to a ...-byte WAVE`).

A `mods` mappába vagy a játék mappáiba soha semmi nem íródik.

## Köszönet és licencek

- `third_party\stb\stb_vorbis.c` v1.24: Ogg Vorbis dekóder, Sean Barrett és közreműködők, közkincs (vagy választás
  szerint MIT). Változatlanul, saját egységként fordul (`src\sound\oggdec.c`).
- `third_party\openxr` 1.1.65: a Khronos OpenXR loader (`openxr_loader.dll` / `.lib`) és fejlécek, Copyright The
  Khronos Group Inc., Apache-2.0 OR MIT (az OpenXR.Loader NuGet csomag). Változatlanul használva az opcionális VR
  módhoz (`src\modern\vr.c`), késleltetett betöltéssel; a DLL az exe mellett van.
- `third_party\lua` 5.4.9: Lua.org, PUC-Rio, MIT (lásd [modding/LUA_LICENSE.txt](modding/LUA_LICENSE.txt)).
  Változatlanul fordul a modszkriptekhez.
- DualSense haptika Bluetooth-on (`PadHaptics`): a protokoll ismerete a SAxense-ből származik, szerzője egormanga /
  Sdore (MPL-2.0, https://github.com/egormanga/SAxense, https://apps.sdore.me/SAxense), ez az első nyilvános leírása;
  a riport felépítése saját megvalósítás (SAxense-kód nincs a forrásban). Az USB-csatornák kiosztása a streetpea /
  chiaki-ng által mutatott tényeket követi; a padok riportjaihoz a controllers.fandom.com és a psdevwiki volt a forrás.
- A modtámogatás minden más része (zip kicsomagolás, DDS / BC7 dekóderek, az átalakítók) az újraépítés saját kódja; a
  PNG-dekódolás (WIC) és az MP3-dekódolás (Media Foundation) a Windows saját komponensei.
