# Tworzenie modów do RcCarsRe

[English](MODDING.md) | [Magyar](MODDING.hu.md) | [Русский](MODDING.ru.md) | **Polski**

RcCarsRe (odbudowany plik exe RC Cars) potrafi wczytywać mody: pliki, które zastępują własne pliki gry bez
naruszania jej folderów. Oryginalna gra nie obsługuje modów; to nowoczesna funkcja odbudowy, włączana przez
`RcCarsRe.ini [Modern] Mods=1` (domyślnie). Przy `Mods=0` albo bez folderu `mods` gra czyta dokładnie te same pliki
co oryginał.

## Gdzie umieszczać mody

Obok `RcCarsRe.exe`, w folderze `mods`. Folder `mods` we własnym folderze gry (np. `RCCars\mods` w kopii ze Steam)
też jest czytany; exe nigdy nie zapisuje do żadnego z nich.

```
RcCarsRe.exe
RcCarsRe.ini
mods\
    BetterSkins.zip            mod jako archiwum zip
    LoudReset\                 mod jako zwykły folder
        Sound\cp_reset.wav
```

Mod to folder `mods\<nazwa>\` albo archiwum `mods\<nazwa>.zip`. W środku pliki mają własne ścieżki względne gry, tak
jak w folderze gry (instalacja z DVD) albo w `RCCars.pack` (wydanie Steam):

| Co                                | Ścieżka w modzie (przykłady)                                 |
|-----------------------------------|--------------------------------------------------------------|
| tekstury                          | `Textures.1\sand.csi`, `Textures.2\...`, `Textures.3\...`    |
| tekstury dla każdej jakości       | `Textures\sand.png` (zamiast Textures.1, .2 i .3)            |
| dźwięki                           | `Sound\cp_reset.au`, `Sound\snd.ini`                         |
| muzyka i intro                    | `Tracks\Dead_Track01.mp3`                                    |
| ustawienia                        | `Settings\...`                                               |
| trasy i baza danych               | `RCCarsDB\...`, `RCCars.sb`                                  |
| język, czcionki                   | `Language\Game\English.tbl`, `Language\English\...`         |
| samochody, ruch uliczny, ludzie   | `CarProfiles\...`, `Profiles\...`                            |
| skrypty, splajny, twarze          | `Scripts\...`, `Splines\...`, `FacesSys\...`, `Faces\...`   |
| konfiguracja startowa             | `Config.gm`, `Autoexec.gm`                                   |

Można zastąpić każdy plik, który gra czyta, a do folderów, które gra wylicza, można dodawać nowe pliki (np. nowe
twarze albo strony czcionek): pojawiają się po własnych plikach gry. Wielkość liter w nazwach nie ma znaczenia, `/` i
`\` są równoważne. Zip zawierający jeden główny folder o nazwie samego modu (`BetterSkins.zip` z
`BetterSkins\Sound\...` w środku) jest czytany tak, jakby tego folderu nie było.

## Skrypty

Mod może też zawierać skrypty Lua (`*.lua` w katalogu głównym albo w `scripts\`): teksty i obrazy HUD, dźwięki, własną
stronę ustawień na ekranie Mods, a także (API 1.1) kamerę, mgłę, słońce, światła, wibracje / pasek świetlny pada
i własne statystyki, wszystko tylko na twoim komputerze. Zob. [modding/LUA_SCRIPTING.pl.md](modding/LUA_SCRIPTING.pl.md). Mod może też dodać własny **tryb gry** (Lua API 1.4: zasady, rozkazy SI, zamiana samochodów, scena końcowa): pojawia się w wierszu Tryb ekranu Szybki wyścig; przykład to `docs\modding\examples\zombies` (aby zagrać, skopiuj go do `mods\`). Mod może też dodać **własne trasy**: zrób trasę w Blenderze dodatkiem RC Cars Track Editor, który eksportuje ją jako mod; poradnik i przykładowa trasa są w `docs\modding\examples\custom_track`.

## Formaty

Gra prosi o swoje oryginalne nazwy plików; mod może podać ten sam plik w innym formacie pod tą samą nazwą z innym
rozszerzeniem, a exe go przekształci:

- **Tekstury** (gra prosi o `nazwa.csi`): `nazwa.csi`, `nazwa.png`, `nazwa.dds` albo obraz HDR `nazwa.hdr`
  (Radiance) / `nazwa.exr` (OpenEXR: ZIP, ZIPS, RLE lub bez kompresji; nie PIZ / DWA) - np. niebo HDRI; gra sama
  dobiera jasność (automatyczna ekspozycja).
  - Foldery jakości: mod może zawierać `Textures.1\x.csi`, `Textures.2\x.csi` i `Textures.3\x.csi` (każdy zastępuje
    plik w tym samym folderze; gra czyta foldery wybranej jakości tekstur, najlepszy najpierw) i / lub
    `Textures\x.csi` (zastępuje wszystkie trzy; plik w samym folderze jakości ma pierwszeństwo). Tekstura modu jest
    używana przy każdym ustawieniu jakości: jeśli mod ma ją tylko w innym folderze jakości niż preferowany, bierze się
    ją zamiast pliku gry.
  - Obrazy folderu językowego (`Language\English\logoRC_Main.csi`, loga menu i komunikaty wyścigu) zastępuje się tak
    samo, pod nazwą folderu języka.
  - Własny `.csi` modu jest czytany pobłażliwie: dowolny rozmiar. Jeśli nagłówek podaje więcej poziomów mip, niż jest
    w pliku (niektóre narzędzia tak zapisują przy powiększaniu obrazu: nagłówek oryginału z 8 poziomami, w pliku
    tylko pierwszy), brakujące poziomy są tworzone (pliki ARGB8888) albo plik jest czytany z poziomami, które ma (inne
    formaty); liczba mip 0 liczy się jako 1. `.csi`, który nie zawiera nawet pierwszego poziomu, jest odrzucany (z
    wpisem w dzienniku).
  - PNG przez Windows Imaging Component (wbudowany w Windows): 8 / 16 bitów, paleta, skala szarości, z alfą lub bez.
  - DDS: BC1 (DXT1), BC2 (DXT2/3), BC3 (DXT4/5), BC4 (ATI1), BC5 (ATI2), BC7 (nagłówek DX10) oraz nieskompresowane
    RGBA / RGB / BGRA / 565 / 1555 / 4444 / luminancja / alfa. Poziomy mip są używane tak, jak są w pliku; brakujące
    są tworzone (średnia 2 x 2). BC4 jest pokazywany na szaro, BC5 jako czerwony / zielony. Formaty sRGB są brane jako
    zwykłe wartości.
  - Tekstury sześcienne (odbicie lakieru samochodów, `cubemap_racer`): gra czyta `cubemap_racer.csi` i jego sześć
    ścian `cubemap_racer.1.csi` .. `.6.csi` (+X, -X, +Y, -Y, +Z, -Z). Jeden sześcienny DDS `cubemap_racer.dds` ze
    wszystkimi sześcioma ścianami zastępuje wszystkie siedem plików. Jeśli zastępujesz je pojedynczo, każda ściana
    musi mieć rozmiar `cubemap_racer.csi`.
- **Dźwięki i muzyka** (gra prosi o efekty dźwiękowe `.au` / `.wav` i muzykę `.mp3`): każdy z `.au`, `.wav`, `.mp3`,
  `.ogg` może zastąpić każdy inny.
  - WAV: PCM 8 / 16 / 24 / 32 bity, float 32 / 64 bity, WAVE_FORMAT_EXTENSIBLE, inne kodeki WAV przez Media
    Foundation; `.au`: własny format gry (RIFF WAVE z nazwą .au) albo Sun / NeXT .au (mu-law, A-law, PCM, float);
    MP3 (i inne formaty dekodowane przez Windows) przez Media Foundation; OGG Vorbis przez stb_vorbis.
  - Dowolna długość, częstotliwość próbkowania i liczba kanałów. Efekty dźwiękowe są przekształcane do 16-bitowego PCM
    (8 / 16-bitowy PCM mono lub stereo zostaje dokładnie taki sam); więcej niż dwa kanały są miksowane do stereo;
    częstotliwość spoza 100 .. 200000 Hz jest przepróbkowana do 48000 Hz. Muzyka w formacie, którego DirectShow sam
    nie odtwarza (.ogg, .au), albo w zipie, jest zapisywana do tymczasowego .wav / kopii w
    `%TEMP%\RcCarsRe_mods_<id procesu>\`, usuwanej przy wyjściu z gry.

## Gdy plik modu nie działa

Jeśli pliku modu nie da się otworzyć, przeczytać, rozpakować ani zdekodować (tekstura, dźwięk, utwór muzyczny, plik
ustawień lub tekstu), gra czyta zamiast niego swój oryginalny plik i raz zapisuje przyczynę w dzienniku (`Mods: <mod>:
<file> can't be decoded (...); the game's own file is used`); plik nie jest już proponowany, dopóki mody nie zostaną
zastosowane ponownie. Tekstura nigdy nie zostaje brakująca z powodu modu, a przy włączonych modach brakująca
tekstura interfejsu nie zatrzymuje już startu na ekranie ładowania (jest to zapisywane w dzienniku, a menu działają
dalej). Pliki, których zawartości gra sama nie może sprawdzić (uszkodzony w środku `.sb` trasy, skrypt z błędnymi
wartościami), są nadal czytane tak, jak podaje je mod.

## Rozmiary

Gra nie ma własnych limitów rozmiaru: tekstura 4096 x 4096 może zastąpić teksturę 256 x 256 i jest używana w swoim
rozmiarze przy każdej jakości tekstur (`TexQual`, `Textures.1 / .2 / .3`: tekstura modu wygrywa w każdym folderze
jakości). Tekstury nie muszą być kwadratowe ani potęgą dwójki. Limit to limit Direct3D 11: 16384 teksele na bok.
Tekstura dostaje najwyżej 10 poziomów mip (limit formatu .csi), co schodzi do 1 / 512 rozmiaru: w zupełności
wystarcza do próbkowania. Pamięć: tekstura 4096 x 4096 zajmuje około 85 MB podczas wczytywania i 85 MB pamięci wideo.

Co zachowuje znaczenie w pikselach: strony czcionek (czcionki Smash w `Language\...` i czcionka deski rozdzielczej)
są cięte na komórki liter o stałym rozmiarze w pikselach, więc strona czcionki musi zachować rozmiar i układ
oryginału. Niektóre obrazy kod gry czyta piksel po pikselu (mapy oświetlenia tras, portrety kierowców w `Faces` /
`FacesSys`): dla nich inne rozmiary nie były testowane; dla bezpieczeństwa zachowaj oryginalny rozmiar.

## Kolejność wczytywania

Kolejność wczytywania to lista, której **góra to najważniejszy mod**: jeśli dwa mody mają ten sam plik (w dowolnym
jego formacie), używany jest plik modu wyżej na liście. W obrębie jednego modu plik z żądanym rozszerzeniem wygrywa z
jego innymi formatami.

1. `[Modern] ModOrder=A,B,C` (opcjonalnie): te mody są na górze w tej kolejności: `A` wygrywa z `B`, `B` z `C`.
   (Zmiana 2026-11-15: wcześniej wygrywała późniejsza nazwa.)
2. Mody, których ModOrder nie wymienia, są niżej, posortowane według nazwy (bez rozróżniania wielkości liter; wśród
   nich wygrywa pierwszy według nazwy). Folder i zip o tej samej nazwie: folder jest pierwszy.
3. `[Modern] ModsDisabled=A,B` (opcjonalnie): te mody nie są wczytywane. `A` oznacza folder i zip o nazwie A, `A.zip`
   tylko zip, `A\` tylko folder (te same formy działają w ModOrder).
4. Mod o tej samej nazwie w obu folderach mods (obok exe i w folderze gry) jest brany raz — ten obok exe.

## Ekran Mods

Przy `[Modern] ModsMenu=1` (domyślnie) zamiast pozycji menu głównego „Demo play” (wyścig demo nie jest jeszcze
odbudowany) jest **Mods** (Modok / Моды / Mody w języku gry). Ekran pokazuje wszystkie znalezione mody, wczytane i
nie, w kolejności wczytywania (górny wygrywa), z liczbą plików, liczbą zastępowanych plików gry i czerwonym `!`, gdy
któregoś pliku nie da się zdekodować (szczegóły wybranego modu są pod listą, przyczyny w `game_dbg.log`). W pierwszym
wierszu **Mods** włącza i wyłącza całą obsługę modów (`[Modern] Mods`).

- Góra / dół (albo mysz) wybierają mod, PgUp / PgDn przewijają stronę; lewo / prawo, Enter albo spacja (przycisk A
  pada) włączają lub wyłączają go;
- **Move up** / **Move down** (przyciski menu po prawej) przesuwają wybrany mod na liście;
- **Refresh** ponownie przegląda oba foldery mods: dodane mody pojawiają się na dole listy, włączone; usunięte
  znikają; wszystkie liczniki są liczone od nowa. Jeszcze niezastosowana kolejność i przełączniki zostają.
  Refresh niczego nie wczytuje: to zadanie Apply;
- **Apply** zapisuje `Mods`, `ModOrder` (wszystkie mody, górny pierwszy) i `ModsDisabled` do `RcCarsRe.ini` (jeśli
  się zmieniły), pokazuje „Applying mods...”, od razu wczytuje mody w nowy sposób, informuje „Mods applied” i wraca do
  menu głównego. Apply bez zmian też wczytuje ponownie pliki modów (użyj po edycji plików modu);
- **Main menu** (albo Esc / przycisk B pada) odrzuca zmiany.

Ekran zapisuje tylko `RcCarsRe.ini`, nigdy foldery mods ani foldery gry.

### Co Apply wczytuje od razu (bez restartu)

- wszystkie tekstury z folderów tekstur i folderu językowego (menu, loga, przyciski, malowania samochodów, ściany
  `cubemap_racer`, obrazy interfejsu), strony czcionek Smash i twarze kierowców (`FacesSys`, `Faces`);
- efekty dźwiękowe (`Sound\*`, także dźwięki menu) i tabele `snd.ini` / `chn.ini`;
- muzykę: plik każdego utworu jest wyszukiwany ponownie (MP3 / OGG / WAV modu zamiast utworu), a muzyka menu zaczyna
  się od nowa;
- pliki suwaków `Settings\*` (czytane ponownie przy następnym użyciu; twoje własne ustawienia ze stron Options są w
  `RCCars.crs` i zostają bez zmian);
- tabelę językową `Language\Game\<język>.tbl` (teksty menu głównego od razu, innych ekranów przy otwarciu);
- `Scripts\championship.ini` i `Scripts\AIlayouts.ini`.

Wszystko, co dotyczy wyścigu (trasy, samochody, ich `.sb`, ścieżki SI, `CarProfiles`, `Profiles`, `UPGRADES.ini`,
skrypty tras), jest czytane przy wczytywaniu wyścigu, więc następny wyścig już bierze pliki modów.

### Co wymaga restartu

Pliki, które gra czyta tylko przy starcie: `Config.gm`, `Autoexec.gm` (i każdy `*.gm`: foldery, zmienne, lista
utworów muzycznych), bazy scen `RCCars.sb`, `Interface.sb` i `RaceTextures.sb` (ich obiekty, samochody menu głównego,
osadzone obrazy, lista tekstur interfejsu i jego kanały dźwiękowe) oraz `Splines\`. Gdy mod zmienia któryś z nich,
Apply to zgłasza („Some files need a restart”), a `game_dbg.log` wymienia pliki. Obrazy osadzone w bazie danych
(`.sb`) nadal pochodzą z bazy, jak przy starcie. Filmy intro odtwarzają się tylko przy starcie. Folder języka
(`Language\<nazwa>\`, z tekstu 2 tabeli) pozostaje ten ze startu.

## Czego nie można modyfikować

- Zapisy graczy (`Players\`, każdy `*.scp`), zapisy duchów (`GhostRecords\`) i magazyn ustawień `RCCars.crs`
  (`RCCars.crs.bak`): zapisuje je gra, więc kopia z modu jest ignorowana (z wpisem w dzienniku).
- Pliki poza folderem gry (ścieżka bezwzględna w `Config.gm`), exe i jego DLL, `RcCarsRe.ini`.
- Archiwa zip: tylko wpisy „stored” i „deflate”, bez szyfrowania, bez ZIP64 (archiwa ponad 4 GB / 65535 plików).
- Osadzone tekstury plików tras są czytane z samego pliku `.sb`: zastąp cały `.sb` albo tekstury, które nazywają
  trasy — są one wyszukiwane w folderach `Textures.*`, jak każda inna tekstura.

## Dziennik

`game_dbg.log` obok exe wymienia przy starcie: każdy znaleziony mod (zip lub folder, liczba plików), każdy plik i co
zastępuje (`Mods: BetterSkins: Textures\car_askin11.png replaces textures.1\car_askin11.csi`), nowe pliki, pliki
ukryte przez późniejszy mod, pliki zignorowane i pliki, których nie da się zdekodować (z przyczyną; dla nich używany
jest plik gry), potem podsumowanie. Konwersje są zapisywane, gdy gra wczytuje plik (`decoded (PNG 2048x2048)`,
`converted to a ...-byte WAVE`).

Nic nigdy nie jest zapisywane do folderu `mods` ani folderów gry.

## Podziękowania i licencje

- `third_party\stb\stb_vorbis.c` v1.24: dekoder Ogg Vorbis, Sean Barrett i współtwórcy, domena publiczna (albo MIT,
  do wyboru). Budowany bez zmian jako osobny moduł (`src\sound\oggdec.c`).
- `third_party\openxr` 1.1.65: loader Khronos OpenXR (`openxr_loader.dll` / `.lib`) i nagłówki, Copyright The Khronos
  Group Inc., Apache-2.0 OR MIT (pakiet NuGet OpenXR.Loader). Używany bez zmian dla opcjonalnego trybu VR
  (`src\modern\vr.c`), ładowany z opóźnieniem; DLL jest dostarczany obok exe.
- `third_party\lua` 5.4.9: Lua.org, PUC-Rio, MIT (zob. [modding/LUA_LICENSE.txt](modding/LUA_LICENSE.txt)). Budowany
  bez zmian dla skryptów modów.
- Haptyka DualSense przez Bluetooth (`PadHaptics`): wiedza o protokole pochodzi z SAxense, autor egormanga / Sdore
  (MPL-2.0, https://github.com/egormanga/SAxense, https://apps.sdore.me/SAxense), jego pierwszego publicznego opisu;
  układ raportu to nasza własna implementacja (w źródłach nie ma kodu SAxense). Układ kanałów USB opiera się na
  faktach pokazanych przez streetpea / chiaki-ng; źródłami dla raportów padów były controllers.fandom.com i psdevwiki.
- Cała reszta obsługi modów (rozpakowywanie zip, dekodery DDS / BC7, konwertery) to własny kod odbudowy; dekodowanie
  PNG (WIC) i MP3 (Media Foundation) to własne komponenty Windows.
