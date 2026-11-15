# Skrypty Lua w modach

[English](LUA_SCRIPTING.en.md) | [Magyar](LUA_SCRIPTING.hu.md) | [Русский](LUA_SCRIPTING.ru.md) | **Polski**

RcCarsRe potrafi uruchamiać małe skrypty Lua dołączone do moda. Skrypt może odczytywać wyścig (trasa, okrążenia,
samochody, pozycje, czasy okrążeń), reagować na zdarzenia (okrążenie, punkt kontrolny, uderzenie, woda, powrót na
trasę, koniec wyścigu) i robić rzeczy lokalne: rysować teksty, obrazy i prostokąty na HUD, odtwarzać dźwięki, pisać do
dziennika i przechowywać własne ustawienia. Skrypty nie mogą zmieniać wyścigu, samochodów ani plików gry.

Językiem jest [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, licencja MIT, zob.
[LUA_LICENSE.txt](LUA_LICENSE.txt)).

## 1. Przegląd

- Każdy włączony mod (folder lub zip w folderze `mods`, zob. [MODDING.pl.md](../MODDING.pl.md)) może zawierać pliki `.lua`.
- Każdy mod dostaje własny stan Lua. Mody nie widzą nawzajem swoich zmiennych globalnych.
- Mody są ładowane w kolejności ekranu Mody od dołu do góry: najpierw mod o najniższym priorytecie, na końcu górny.
- Gra wywołuje globalne funkcje zdarzeń skryptu (`onFrame`, `onLap`, ...), jeśli istnieją.
- Wszystko, co robi skrypt, zostaje na Twoim komputerze: HUD, dźwięk, dziennik, jego plik ustawień. Skrypty nigdy nic
  nie wysyłają przez sieć i nie wpływają na innych graczy w wyścigu sieciowym.

## 2. Układ plików

```
mods\
  my_mod\                 (lub my_mod.zip o tej samej zawartości)
    main.lua              skrypt wejściowy (dowolny *.lua w katalogu głównym moda)
    scripts\
      hud.lua             skrypt wejściowy (dowolny *.lua bezpośrednio w scripts\)
      lib\util.lua        nie ładuje się sam: załaduj go przez rc.include("scripts/lib/util.lua")
    sounds\ding.wav       własny dźwięk moda dla rc.playSound("ding")
    textures\icon.png     własny obraz moda dla rc.hudImage(..., "icon", ...)
```

- Skrypty wejściowe: wszystkie `*.lua` w katalogu głównym moda i bezpośrednio w `scripts\`, w kolejności nazw.
- Pliki z głębszych folderów są ładowane tylko przez `rc.include`.
- Skrypty i teksty są w UTF-8. Teksty są zamieniane na stronę kodową czcionki gry dla bieżącego języka.

## 3. Włączanie

W `RcCarsRe.ini` (obok `RcCarsRe.exe`), sekcja `[Modern]`:

| Klucz | Wartości | Domyślnie | Znaczenie |
|---|---|---|---|
| `Mods` | 0 / 1 | 1 | foldery mods są czytane (potrzebne dla skryptów) |
| `LuaScripts` | 0 / 1 | 1 | skrypty Lua modów działają |
| `LuaBudget` | 10000 .. 100000000 | 1000000 | ile instrukcji Lua może wykonać jedno wywołanie zdarzenia |

Ekran Mody (menu główne, „Mody”) włącza i wyłącza mody. **Zastosuj** od razu przeładowuje wszystkie skrypty: stare
stany są zamykane, a nowy zestaw modów jest ładowany.

## 4. Zdarzenia

Zdefiniuj je jako funkcje globalne. Wszystkie są opcjonalne.

| Zdarzenie | Kiedy |
|---|---|
| `onLoad()` | po załadowaniu skryptów wejściowych moda |
| `onMenu(name)` | zmienił się górny ekran: `main`, `options`, `quickrace`, `multiplayer`, `twoplayers`, `twosetup`, `players`, `newplayer`, `credits`, `ghost`, `garage`, `championship`, `champwin`, `mods`, `modsettings`, `pause`, `race`, `results`, `none`, `other` |
| `onRaceStart(info)` | na starcie (GO); `info` to tabela `rc.race()` |
| `onFrame(dt)` | w każdej klatce (także w menu); `dt` = czas klatki w sekundach |
| `onLap(car, lap, lapTime)` | samochód ukończył okrążenie numer `lap` w `lapTime` sekund |
| `onCheckpoint(car, index)` | samochód minął punkt kontrolny `index` (1 = linia startu/mety) |
| `onHit(car, strength)` | gra przyznała uderzenie: 1 = „Hit!”, 2 = „Great hit!” |
| `onWater(car)` | samochód wjechał do wody |
| `onRespawn(car)` | samochód został odstawiony na trasę |
| `onRaceEnd(results)` | raz na wyścig, gdy startuje skrypt mety (wszyscy gracze dojechali) |
| `onOptionChanged(key, value)` | na stronie Ustawienia moda zmieniono opcję |

`car` to numer samochodu, 1 .. `rc.race().cars`. `results` to lista w kolejności miejsc; każdy element ma `car`,
`place`, `finished`, `time`, `bestLap` (brak, jeśli nie było), `lap`, `name`.

## 5. Opis API (tabela `rc`)

### Odczyt

| Funkcja | Zwraca |
|---|---|
| `rc.version` | wersja API (`"1.0"`) |
| `rc.modName` | nazwa moda |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = sekundy od startu (przed nim -1). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (gracz 1 dojechał), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, place, isPlayer, isAi, isGhost, player, finished, name}` lub `nil`. `speed` w km/h; `player` = 1 / 2 dla samochodu gracza |
| `rc.player(n)` | tabela samochodu gracza `n` (1 lub 2, domyślnie 1) lub `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: rozmiar renderowania w pikselach, nazwa bieżącego ekranu, VR włączone, podzielony ekran |

### HUD (rysowany tylko w tej klatce: wywołuj co klatkę z `onFrame`)

Współrzędne to wirtualny ekran 800 x 600 rozciągnięty na cały obraz (na podzielonym ekranie na oba widoki, w VR na
warstwę HUD). Kolory w postaci `0xAARRGGBB`.

| Funkcja | Znaczenie |
|---|---|
| `rc.hudText(x, y, text, color, size, align)` | tekst czcionką gry; `size` 1 = rozmiar tekstu HUD (podąża za skalą UI i `HudScale`); `align` = `"left"` (domyślnie), `"center"`, `"right"` (x to lewa krawędź, środek lub prawa krawędź) |
| `rc.hudRect(x, y, w, h, color)` | wypełniony prostokąt (domyślny kolor `0x80000000`) |
| `rc.hudImage(x, y, w, h, texture, color, u0, v0, u1, v1)` | obraz; `texture` to własny plik moda (nazwa jako ścieżka, także z `.png` / `.dds` / `.csi` i w `textures\`), a w przeciwnym razie tekstura gry o tej nazwie; uv domyślnie 0, 0, 1, 1 |

Najwyżej 512 elementów HUD na klatkę i 64 obrazy na mod.

### Dźwięk i dziennik

| Funkcja | Znaczenie |
|---|---|
| `rc.playSound(name, volume)` | odtwarza raz: własny plik moda (nazwa jako ścieżka, także z `.wav` / `.ogg` / `.mp3` / `.au` i w `sounds\` lub `sound\`), a w przeciwnym razie dźwięk gry o tej nazwie; `volume` 0 .. 1 (domyślnie 1, razy głośność efektów gry). Zwraca `true`, gdy gra |
| `rc.log(...)` / `print(...)` | wiersz w `game_dbg.log` (i w konsoli -dev) |
| `rc.warn(...)` / `warn(...)` | wiersz ostrzeżenia (żółty w konsoli -dev) |

### Pliki własnego moda

| Funkcja | Znaczenie |
|---|---|
| `rc.readFile(path)` | bajty pliku jako ciąg lub `nil, komunikat`. Czytany jest tylko własny mod skryptu |
| `rc.include(path)` | raz uruchamia plik `.lua` własnego moda i zwraca jego wynik (kolejne wywołania zwracają ten sam), jak `require` |

### Ustawienia

Zapisywane w `Saves\Mods\<mod>.ini` obok `RcCarsRe.exe` (`<mod>.zip.ini` dla moda zip), sekcja `[Settings]`.
Nic innego nie jest zapisywane.

| Funkcja | Znaczenie |
|---|---|
| `rc.setting(key, default)` | zapisana wartość zamieniona na typ `default` (logiczna, liczba, ciąg); bez zapisanej wartości `default` lub wartość domyślna opcji |
| `rc.setSetting(key, value)` | zapisuje wartość logiczną, liczbę lub ciąg (`nil` usuwa); plik jest zapisywany od razu, więc nie wywołuj tego co klatkę |
| `rc.options{ ... }` | deklaruje opcje strony Ustawienia moda (poniżej) |

Klucze: litery, cyfry, `_`, `.`, `-`, najwyżej 63 znaki. Wartości: najwyżej 1000 bajtów, bez znaków nowego wiersza.

### Strona Ustawienia

```lua
rc.options{
  {key = "showLap", type = "bool", label = "Show lap time", default = true},
  {key = "size", type = "slider", min = 0, max = 10, step = 1, default = 5, label = "Size"},
  {key = "mode", type = "enum", values = {"small", "big"}, default = "small", label = "Mode",
   labels = {"Small", "Big"}},
}
```

- `label` (i każdy element `labels`) to ciąg lub tabela według języków: `{en = "...", hu = "...", ru = "...", pl = "..."}`.
- Załadowany mod z opcjami ma aktywny przycisk **Ustawienia** na ekranie Mody. Jego strona używa własnych elementów
  menu gry (przełączniki, suwaki, przyciski); zmiany są zapisywane od razu i uruchamia się
  `onOptionChanged(key, value)`.
- `rc.setting(key)` zwraca wartość opcji; przycisk **Wartości domyślne** na stronie przywraca wartości domyślne.

## 6. Ograniczenia piaskownicy

- Dostępne: podstawowe funkcje Lua, `table`, `string`, `math`, `utf8`, `coroutine` oraz `os.clock`, `os.time`,
  `os.date`.
- Niedostępne: `io`, reszta `os`, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- `load` przyjmuje tylko fragmenty tekstowe (ciąg; bez fragmentów binarnych).
- `collectgarbage` przyjmuje tylko `"count"`.
- Pamięć: 64 MB na mod.
- Czas: `LuaBudget` instrukcji Lua na wywołanie zdarzenia. Długiej pracy wewnątrz jednego wywołania biblioteki (np.
  ogromne `string.rep` albo złożony wzorzec) licznik instrukcji nie mierzy; pisz proste skrypty.
- Skrypty nigdy nie zapisują plików gry, plików modów ani zapisów graczy; jedynym zapisywanym plikiem jest plik
  ustawień moda.

## 7. Obsługa błędów

- Błąd ładowania, błąd wykonania lub przekroczony budżet przerywa tylko to wywołanie. Gra działa dalej.
- Każdy błąd trafia do `game_dbg.log` jako `Lua [mod] co: plik:wiersz: komunikat` (ze śladem stosu).
- Po 5 błędach skrypty moda są wyłączane („mod scripts disabled after repeated errors”). Popraw skrypt i naciśnij
  Zastosuj na ekranie Mody (albo zapisz plik w trybie dewelopera, zob. niżej).
- Gdy wywołanie zużyło ponad 80 % budżetu, pojawia się jedno ostrzeżenie.

## 8. Tryb dewelopera (`RcCarsRe.exe -dev`)

- Błędy i ostrzeżenia widać w oknie konsoli: wiersze błędów są czerwone, ostrzeżeń żółte (zarówno Lua, jak i gry);
  błędy pojawiają się też na czerwonym pasku w grze.
- Polecenie konsoli `lua` wypisuje mody ze skryptami; `lua <kod>` uruchamia kod w stanie ostatnio załadowanego moda,
  `lua <mod> <kod>` w stanie tego moda, i wypisuje wyniki (działa też wyrażenie, np. `lua rc.race().state`).
- Szybkie przeładowanie: pliki `.lua` modów-folderów są sprawdzane co sekundę; gdy któryś się zmieni, skrypty tego
  moda są ładowane ponownie (mody zip: Zastosuj).

## 9. Przykłady

`docs/modding/examples/` zawiera dwa kompletne mody. Skopiuj folder do `mods\` obok `RcCarsRe.exe`:

- `laptime_hud`: bieżący, poprzedni i najlepszy czas okrążenia gracza 1 w ramce; opcje dla najlepszego okrążenia,
  rozmiaru i narożnika.
- `checkpoint_sound`: przy każdym punkcie kontrolnym gracza 1 odtwarza własny `sounds\ding.wav` moda i pokazuje jego
  numer.

Minimalny skrypt:

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

## 10. Rozwiązywanie problemów

| Problem | Sprawdź |
|---|---|
| Nic się nie dzieje | `LuaScripts=1` i `Mods=1` w `RcCarsRe.ini`; mod jest włączony na ekranie Mody; plik jest w katalogu głównym moda lub w `scripts\`; w `game_dbg.log` jest `Lua [mod]: ... loaded` |
| „mod scripts disabled after repeated errors” | przeczytaj pierwsze wiersze błędów `Lua [mod]` w `game_dbg.log`, popraw skrypt, naciśnij Zastosuj |
| „instruction budget exceeded” | zdarzenie wykonało naraz zbyt dużo pracy; rozłóż ją na klatki lub zwiększ `LuaBudget` |
| Element HUD jest niewidoczny | wywołania HUD działają tylko przez jedną klatkę: wywołuj je z `onFrame`; sprawdź bajt alfa koloru (`0xFF......` jest nieprzezroczysty) |
| „texture ... not found” / „sound ... not found” (żółte) | nazwa i folder pliku w modzie; obrazy PNG, DDS lub CSI; dźwięki WAV, OGG, MP3 lub AU |
| W tekście widać `?` | zapisz skrypt w UTF-8; czcionka gry ma tylko znaki strony kodowej swojego języka |
| Błędy w konsoli -dev | wiersze błędów są czerwone, ostrzeżeń żółte; te same wiersze są w `game_dbg.log` |
