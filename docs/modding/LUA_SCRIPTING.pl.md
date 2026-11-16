# Skrypty Lua w modach

[English](LUA_SCRIPTING.en.md) | [Magyar](LUA_SCRIPTING.hu.md) | [Русский](LUA_SCRIPTING.ru.md) | **Polski**

RcCarsRe potrafi uruchamiać małe skrypty Lua dołączone do moda. Skrypt może odczytywać wyścig (trasa, okrążenia,
samochody, pozycje, czasy okrążeń), reagować na zdarzenia (okrążenie, punkt kontrolny, uderzenie, skok,
wyprzedzenie, pauza, koniec wyścigu ...) i robić rzeczy lokalne: rysować teksty, obrazy i prostokąty na HUD,
odtwarzać dźwięki, poruszać kamerą, zmieniać mgłę, słońce i oświetlenie, włączać wibracje pada, pisać do dziennika
oraz przechowywać własne ustawienia i statystyki. Skrypty nie mogą zmieniać wyścigu, samochodów ani plików gry.

Językiem jest [Lua 5.4](https://www.lua.org/manual/5.4/) (Lua 5.4.9, licencja MIT, zob.
[LUA_LICENSE.txt](LUA_LICENSE.txt)). Ta strona opisuje wersję API **1.2**.

## 1. Przegląd

- Każdy włączony mod (folder lub zip w folderze `mods`, zob. [MODDING.pl.md](../MODDING.pl.md)) może zawierać pliki `.lua`.
- Każdy mod dostaje własny stan Lua. Mody nie widzą nawzajem swoich zmiennych globalnych.
- Mody są ładowane w kolejności ekranu Mody od dołu do góry: najpierw mod o najniższym priorytecie, na końcu górny.
- Gra wywołuje globalne funkcje zdarzeń skryptu (`onFrame`, `onLap`, ...), jeśli istnieją.
- Wszystko, co robi skrypt, zostaje na twoim komputerze: HUD, dźwięk, kamera, mgła, światła, pad, dziennik, jego
  własne pliki. Skrypty nigdy niczego nie wysyłają przez sieć i nie wpływają na innych graczy w wyścigu sieciowym.

## 2. Układ plików

```
mods\
  my_mod\                 (lub my_mod.zip z tą samą zawartością)
    main.lua              skrypt wejściowy (dowolny *.lua w katalogu głównym moda)
    scripts\
      hud.lua             skrypt wejściowy (dowolny *.lua bezpośrednio w scripts\)
      lib\util.lua        nie ładuje się sam: załaduj go przez rc.include("scripts/lib/util.lua")
    sounds\ding.wav       własny dźwięk moda dla rc.playSound("ding")
    textures\icon.png     własny obraz moda dla rc.hudImage(..., "icon", ...)
```

- Skrypty wejściowe: każdy `*.lua` w katalogu głównym moda i bezpośrednio w `scripts\`, w kolejności nazw.
- Pliki z głębszych folderów ładuje tylko `rc.include`.
- Skrypty i teksty są w UTF-8. Teksty są zamieniane na stronę kodową czcionki gry dla bieżącego języka.

## 3. Włączanie

W `RcCarsRe.ini` (obok `RcCarsRe.exe`), sekcja `[Modern]`:

| Klucz | Wartości | Domyślnie | Znaczenie |
|---|---|---|---|
| `Mods` | 0 / 1 | 1 | foldery mods są odczytywane (potrzebne dla skryptów) |
| `LuaScripts` | 0 / 1 | 1 | skrypty Lua modów działają |
| `LuaBudget` | 10000 .. 100000000 | 1000000 | ile instrukcji Lua może wykonać jedno wywołanie zdarzenia |

Ekran Mody (menu główne, „Mody”) włącza i wyłącza mody. **Zastosuj** od razu przeładowuje wszystkie skrypty: stare
stany są zamykane, a nowy zestaw modów jest ładowany.

Funkcje pada respektują też twoje własne ustawienia pada w tej samej sekcji: `Rumble` (0 = bez wibracji),
`LightBar` (`off` = pasek świetlny nigdy się nie zmienia) i `AdaptiveTriggers` (0 = bez efektów spustów). Skrypt
nie może włączyć tego, co wyłączyłeś.

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
| `onBoost(car, on)` | (1.1) dopalacz samochodu zaczął (`true`) lub przestał (`false`) działać |
| `onJump(car)` | (1.1) samochód w wyścigu jest od 0,25 s w powietrzu (małe wyboje się nie liczą) |
| `onLand(car, airTime)` | (1.1) ten samochód znów jest na ziemi; `airTime` = sekundy w powietrzu |
| `onOvertake(car, otherCar, newPlace)` | (1.1) `car` zajął miejsce `newPlace`, wyprzedzając `otherCar` (sprawdzane raz na klatkę w trakcie wyścigu) |
| `onCollision(car1, car2, strength, kind)` | (1.1) kontakt: `kind` = `"car"` (dwóch zawodników; `strength` = prędkość zbliżania w km/h) lub `"roadcar"` (zawodnik i samochód drogowy; `car2` to `nil`, `strength` = prędkość zawodnika w km/h). Jedno wywołanie na parę, dopóki kontakt trwa (ponownie po 0,5 s bez kontaktu) |
| `onDogAttack(car)` | (1.1) pies zaczyna atak na `car`: zatrzymuje się i szczeka na niego (psy w grze nie gryzą; potrącenie psa to „Great hit!”, zob. `onHit`) |
| `onPause(kind)` | (1.1) wyścig wstrzymano: `kind` = `"menu"` (menu pauzy) lub `"quick"` (szybka pauza) |
| `onResume()` | (1.1) wyścig toczy się dalej po pauzie |
| `onChat(name, text)` | (1.1) przyszedł wiersz czatu sieciowego (także twoje własne); `name` = nadawca, `""` dla wierszy serwera i gry. Tylko do odczytu |
| `onCountdown(n)` | (1.1) odliczanie wyścigu, w tej samej chwili co cyfry i sygnały: `n` = 3, 2, 1 oraz 0 przy GO |

`car` to numer samochodu, 1 .. `rc.race().cars`. `results` to lista w kolejności miejsc; każdy element ma `car`,
`place`, `finished`, `time`, `bestLap` (brak, jeśli nie było), `lap`, `name`.

## 5. Opis API (tabela `rc`)

### Odczyt

| Funkcja | Zwraca |
|---|---|
| `rc.version` | wersja API (`"1.2"`) |
| `rc.modName` | nazwa moda |
| `rc.race()` | `{track, trackIndex, laps, time, state, cars, mode, checkpoints}`. `time` = zegar wyścigu z HUD w sekundach (-1 przed startem). `state` = `menu`, `prestart`, `racing`, `paused`, `finished` (gracz 1 dojechał), `results` |
| `rc.car(i)` | `{index, x, y, z, speed, gear, lap, lapTime, bestLap, raceTime, place, isPlayer, isAi, isGhost, player, finished, name}` lub `nil`. `speed` w km/h; `player` = 1 / 2 dla samochodu gracza; `raceTime` = czas samochodu od startu (zatrzymuje się na mecie) |
| `rc.player(n)` | tabela samochodu gracza `n` (1 lub 2, domyślnie 1) lub `nil` |
| `rc.screen()` | `{w, h, menu, vr, split}`: rozmiar obrazu w pikselach, nazwa bieżącego ekranu, VR włączony, podzielony ekran |
| `rc.formatTime(seconds, format)` | (1.1) czas zapisany tak jak w grze: `"m:ss.hh"` jak zegar HUD (`0:15.89`), albo z `format = "short"` `"m:ss"` |

Czasy okrążeń działają jak w grze: `lap` wynosi 0, dopóki samochód po raz pierwszy nie przejedzie linii startu/mety,
a każdy czas okrążenia (także pierwszego) liczy się od przejazdu przez tę linię. Na pierwszym okrążeniu `lapTime`
jest więc mniejszy od `rc.race().time` o czas, w jakim samochód dojechał ze swojego miejsca startowego do linii.
Napis okrążenia, tabela wyników gry i `onLap` używają tych samych czasów.

### HUD (rysowany tylko w tej klatce: wywołuj go w każdej klatce z `onFrame`)

Współrzędne to wirtualny ekran 800 x 600 rozciągnięty na cały obraz (na podzielonym ekranie na oba widoki, w VR na
warstwę HUD). Kolory mają postać `0xAARRGGBB`.

| Funkcja | Znaczenie |
|---|---|
| `rc.hudText(x, y, text, color, size, align)` | tekst czcionką gry; `size` 1 = rozmiar tekstu HUD (podąża za skalą interfejsu i `HudScale`); `align` = `"left"` (domyślnie), `"center"`, `"right"` (x to lewa krawędź, środek lub prawa krawędź) |
| `rc.hudRect(x, y, w, h, color)` | wypełniony prostokąt (kolor domyślny `0x80000000`) |
| `rc.hudImage(x, y, w, h, texture, color, u0, v0, u1, v1)` | obraz; `texture` to własny plik moda (nazwa jako ścieżka, także z `.png` / `.dds` / `.csi` i w `textures\`), w przeciwnym razie tekstura gry o tej nazwie; uv domyślnie 0, 0, 1, 1 |

Najwyżej 512 elementów HUD na klatkę i 64 obrazy na mod.

### Dźwięk i dziennik

| Funkcja | Znaczenie |
|---|---|
| `rc.playSound(name, volume)` | odtwarza raz: własny plik moda (nazwa jako ścieżka, także z `.wav` / `.ogg` / `.mp3` / `.au` i w `sounds\` lub `sound\`), w przeciwnym razie dźwięk gry o tej nazwie; `volume` 0 .. 1 (domyślnie 1, razy głośność efektów gry). Zwraca `true`, gdy gra |
| `rc.log(...)` / `print(...)` | wiersz w `game_dbg.log` (i w konsoli -dev) |
| `rc.warn(...)` / `warn(...)` | wiersz ostrzeżenia (żółty w konsoli -dev) |

### Kamera (1.1)

| Funkcja | Znaczenie |
|---|---|
| `rc.camera{pos =, offset =, target =, car =, fov =, blend =}` | kamera wyścigowa gracza 1 zostaje zastąpiona do `rc.camera(nil)`. `pos = {x, y, z}`: położenie kamery w świecie; albo `offset = {x, y, z}` razem z `car`: położenie względem tego samochodu w jego własnych osiach (x w prawo, y w górę, z do przodu); bez obu zostaje położenie kamery gry. `target = {x, y, z}` lub `car = i`: na co patrzy (bez obu zostaje kierunek gry). `fov` = pionowy kąt widzenia w stopniach, 10 .. 150 (pojedynczy widok gry ma około 64). `blend` = w ile sekund płynnie przejść od kamery gry (0: od razu) |
| `rc.camera(nil)` | z powrotem do kamery gry (płynnie, w tym samym czasie `blend`) |
| `rc.cameraInfo()` | bieżąca kamera wyścigowa gracza 1: `{pos = {x, y, z}, dir = {x, y, z}, fov, override, blend}`, poza wyścigiem `nil`. `pos` / `dir` mają też pola `.x .y .z`; `override` = włączona kamera skryptu, `blend` 0 .. 1 |

Zastąpienie kamery działa tylko w wyścigu i tylko na widok gracza 1: na podzielonym ekranie widok gracza 2 zachowuje
kamerę gry, a w VR kamerą porusza gogle, więc tam zastąpienie jest pomijane (jedno ostrzeżenie w dzienniku).
Kamery menu nigdy się nie zmieniają. Wyjście z wyścigu i przeładowanie modów wyłączają zastąpienie.

### Pogoda i nastrój (1.1)

Zmieniają tylko to, co rysuje twój komputer. Każdy efekt wyłącza jego funkcja resetu, przekazanie `nil`,
automatycznie koniec wyścigu (tuż przed `onRaceEnd`, więc skrypt może tam ustawić nowy nastrój), wyjście z wyścigu
i przeładowanie modów. Gdy kilka modów ustawia ten sam efekt, wygrywa ostatnie wywołanie.

| Funkcja | Znaczenie |
|---|---|
| `rc.fog{color =, near =, far =, density =}` | mgła trasy: `color` = `0xRRGGBB`; `density` na metr 0 .. 1 (mgła gry jest wykładnicza, trasy używają 0,006 .. 0,026); `near` / `far` w metrach: z nimi i bez `density` mgła jest liniowa od `near` do `far`. Brakujące pola zachowują wartości trasy. Mgła jest widoczna tylko wtedy, gdy mgła gry jest włączona (opcje wideo) |
| `rc.resetFog()` | znów mgła trasy (jak `rc.fog(nil)`) |
| `rc.sun{dir = {x, y, z}}` lub `rc.sun{elevation =, azimuth =}` | kierunek słońca (w stronę słońca; kąty w stopniach, azymut obraca się od +z do +x): cienie w czasie rzeczywistym (`Shadows=realtime`) i oświetlenie samochodów |
| `rc.resetSun()` | znów słońce trasy |
| `rc.lights{intensity =, color =}` | latarnie tras (tylko przy `PointLights=1`): `intensity` = mnożnik ich siły 0 .. 8, `color` = `0xRRGGBB` zamiast ich własnego koloru. Zwraca `true`, gdy światła punktowe są włączone |
| `rc.resetLights()` | znów własne światło latarni |
| `rc.water{color =, alpha =}` | morze: `color` = odcień `0xRRGGBB`, `alpha` = mnożnik przezroczystości 0 .. 1 (przy `WaterFx=1` odcień barwi też płyciznę) |
| `rc.resetWater()` | znów własny wygląd morza |

### Odczucia pada (1.1)

`player` to 1 lub 2 (domyślnie 1). Funkcje zwracają `true`, gdy pad może teraz pokazać efekt.

| Funkcja | Znaczenie |
|---|---|
| `rc.rumble(strength, seconds, player)` | impuls wibracji: `strength` 0 .. 1 (razy twoje ustawienie `Rumble`), najwyżej 3 sekundy. Odczuwalny tylko podczas jazdy samochodu gracza w wyścigu, jak własna wibracja gry |
| `rc.lightBar(r, g, b, player)` | pasek świetlny DualSense / DualShock 4 w tym kolorze (każdy 0 .. 255) do `rc.lightBar(nil, player)`. Ma pierwszeństwo przed kolorem gry; przy `LightBar=off` nic się nie zmienia |
| `rc.triggers{right =, left =, player =}` | adaptacyjne spusty DualSense podczas jazdy samochodu gracza w wyścigu: każdy spust `"off"` lub `{mode = "resistance", start = 0 .. 1, force = 0 .. 1}` (stały opór od części `start` skoku). Do `rc.triggers(nil, player)`; przy `AdaptiveTriggers=0` nie działa |
| `rc.padHaptics(name, player, volume)` | dźwięk (własny plik moda lub dźwięk gry) na haptyce cewkowej DualSense, przez Bluetooth i USB: wymaga `PadHaptics=1` i `Rumble` powyżej 0; nie działa, gdy gra jest w tle lub wyścig jest wstrzymany. `volume` 0 .. 1, razy `PadHapticsVolume`. DualShock 4 nie ma cewek |

Przeładowanie modów kończy pasek świetlny i efekty spustów skryptu.

### Pliki własnego moda

| Funkcja | Znaczenie |
|---|---|
| `rc.readFile(path)` | bajty pliku jako ciąg albo `nil, komunikat`. Odczytywany jest tylko własny mod skryptu |
| `rc.include(path)` | uruchamia raz plik `.lua` własnego moda i zwraca jego wynik (kolejne wywołania zwracają ten sam wynik), jak `require` |

### Ustawienia

Zapisywane w `Saves\Mods\<mod>.ini` obok `RcCarsRe.exe` (`<mod>.zip.ini` dla moda zip), sekcja `[Settings]`.

| Funkcja | Znaczenie |
|---|---|
| `rc.setting(key, default)` | zapisana wartość zamieniona na typ `default` (logiczna, liczba, ciąg); bez zapisanej wartości `default` albo wartość domyślna opcji |
| `rc.setSetting(key, value)` | zapisuje wartość logiczną, liczbę lub ciąg (`nil` usuwa); zapisuje plik od razu, więc nie wywołuj tego w każdej klatce |
| `rc.options{ ... }` | deklaruje opcje strony Ustawienia moda (niżej) |

Klucze: litery, cyfry, `_`, `.`, `-`, najwyżej 63 znaki. Wartości: najwyżej 1000 bajtów, bez znaków nowego wiersza.

### Statystyki (1.1)

Przechowywane osobno dla każdego moda w `Saves\Mods\<mod>.stats.ini` obok `RcCarsRe.exe` (`<mod>.zip.stats.ini`
dla moda zip), oddzielnie od ustawień i nigdy w zapisie gracza. Wartości to liczby lub ciągi (najwyżej 1000 bajtów),
najwyżej 1000 kluczy na mod, klucze jak w ustawieniach. Zmiany są trzymane w pamięci i zapisywane naraz na końcu
wyścigu, przy wyjściu z wyścigu, przy przeładowaniu modów i przy wyjściu z gry, więc funkcje można wywoływać
dowolnie często.

| Funkcja | Znaczenie |
|---|---|
| `rc.stats.get(key, default)` | zapisana wartość albo `default` (lub `nil`) |
| `rc.stats.set(key, value)` | zapisuje liczbę lub ciąg; `nil` usuwa klucz |
| `rc.stats.add(key, n)` | dodaje `n` (domyślnie 1) do liczby (brakujący klucz liczy się jako 0) i zwraca nową wartość |

### Strona ustawień

```lua
rc.options{
  {key = "showLap", type = "bool", label = "Show lap time", default = true},
  {key = "size", type = "slider", min = 0, max = 10, step = 1, default = 5, label = "Size"},
  {key = "mode", type = "enum", values = {"small", "big"}, default = "small", label = "Mode",
   labels = {"Small", "Big"}},
}
```

- `label` (i każdy element `labels`) to ciąg albo tabela według języka: `{en = "...", hu = "...", ru = "...", pl = "..."}`.
- Załadowany mod z opcjami ma aktywny przycisk **Ustawienia** na ekranie Mody. Jego strona używa własnych elementów
  menu gry (przełączniki, suwaki, przyciski); zmiany są zapisywane od razu i uruchamia się
  `onOptionChanged(key, value)`.
- `rc.setting(key)` zwraca wartość opcji; przycisk **Wartości domyślne** na stronie przywraca wartości domyślne.

### Wejście, pauza, HUD i zrzuty ekranu (1.2)

To elementy do budowy trybu fotograficznego, kamery powtórek i podobnych narzędzi. Wszystkie działają tylko na
twoim komputerze.

| Funkcja | Znaczenie |
|---|---|
| `rc.input.key(name)` | `true`, dopóki klawisz jest wciśnięty. Nazwy: litery `"A"` .. `"Z"`, cyfry, `"F1"` .. `"F24"`, `"Space"`, `"Enter"`, `"Esc"`, `"Tab"`, `"Backspace"`, `"Shift"`, `"Ctrl"`, `"Alt"`, `"Up"`, `"Down"`, `"Left"`, `"Right"`, `"PageUp"`, `"PageDown"`, `"Home"`, `"End"`, `"Insert"`, `"Delete"`, `"Plus"`, `"Minus"`, `"Comma"`, `"Period"`, `"MouseLeft"`, `"MouseRight"`, `"MouseMiddle"` |
| `rc.input.pressed(name)` | `true` w klatce, w której klawisz wciśnięto |
| `rc.input.mouse()` | `{dx, dy, wheel, left, right, middle}`: ruch myszy i ząbki kółka w tej klatce, jej przyciski |
| `rc.input.pad(player)` | `{lx, ly, rx, ry, lt, rt, kind, buttons = {..}, pressed = {..}}` lub `nil` bez pada. Gałki -1 .. 1 (w górę dodatnio), spusty 0 .. 1, `kind` = `"xinput"`, `"ds4"`, `"dualsense"`. Nazwy przycisków (każdy także w `pressed`, true w klatce wciśnięcia): `a` / `cross`, `b` / `circle`, `x` / `square`, `y` / `triangle`, `lb` / `l1`, `rb` / `r1`, `back` / `view` / `share` / `create` / `select`, `start` / `menu` / `options`, `ls` / `l3`, `rs` / `r3`, `guide` / `ps`, `touchpad`, `mute`; w `buttons` jest też krzyżak: `up`, `down`, `left`, `right` |
| `rc.input.capture(on)` | gdy włączone, sterowanie samochodem i Esc / Start menu pauzy nie dostają klawiszy ani przycisków: używa ich skrypt (np. gałek do swobodnej kamery) |
| `rc.pause(on)` | zatrzymuje wyścig jak menu pauzy (zegar wyścigu, fizyka, SI, woda, cząsteczki, animacje, dźwięki), bez menu. W wyścigu sieciowym zwraca `false` |
| `rc.timeScale(s)` | spowolnienie, `s` 0,05 .. 1 (1 = normalnie). W wyścigu sieciowym `false`. Do pełnego zatrzymania służy `rc.pause` |
| `rc.hud(show)` | `false` ukrywa własny HUD gry (kokpit, wskaźniki, strzałkę, mapę, listę zawodników, komunikaty, wiersze czatu, ShowFps); `rc.hudText` / `rc.hudImage` / `rc.hudRect` skryptu nadal się rysują |
| `rc.screenshot{hideScriptHud =, scale =}` | zapisuje następną klatkę jako PNG w folderze `Screenshots` obok `RcCarsRe.exe` i zwraca nazwę pliku. `hideScriptHud` (domyślnie `true`) pomija w tej klatce elementy HUD skryptu. Powstaje tylko `scale = 1` (klatka tak, jak widać) |

- `rc.camera{...}` przyjmuje też `roll = stopnie` (dodatnio zgodnie z ruchem wskazówek zegara) i działa także
  podczas pauzy wyścigu.
- Wejście jest odczytywane tylko wtedy, gdy okno gry jest na pierwszym planie i nikt nie pisze w polu tekstowym
  (pole menu, wiersz czatu sieciowego). Działa zarówno tylko z klawiaturą, jak i tylko z padem.
- Niedostępne (renderer nie ma taniej drogi): głębia ostrości, zrzuty `scale = 2`, ekspozycja / nasycenie. Do
  nastroju służą `rc.fog`, `rc.sun`, `rc.lights` i `rc.water`.
- Bezpieczeństwo: pauzę, ukryty HUD, przechwycenie wejścia, spowolnienie i kamerę gra zwalnia na końcu wyścigu, przy
  wyjściu z wyścigu, przy przeładowaniu modów oraz gdy skrypt ma błędy lub zostaje wyłączony, więc wadliwy skrypt
  nigdy nie zostawi gry zatrzymanej ani bez HUD.

### Budowa trybu fotograficznego

Przykładowy mod `photo_mode` (w `docs/modding/examples/`) to pełny tryb fotograficzny w jednym skrypcie. Jego rdzeń:

```lua
local on, pos, yaw, pitch = false, nil, 0, 0

local function enter()
  local c = rc.cameraInfo()
  if not c or not rc.pause(true) then return end      -- brak kamery wyścigu albo wyścig sieciowy
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

Przykład dodaje sterowanie padem (lewa / prawa gałka, spusty w górę / w dół, bumpery przechył, krzyżak pole
widzenia, A zdjęcie, przycisk Back / View / Share / Create włącza - do ustawienia), ruch w bok, prędkość, przechył,
pole widzenia i własną stronę ustawień.

## 6. Ograniczenia piaskownicy

- Dostępne: podstawowe funkcje Lua, `table`, `string`, `math`, `utf8`, `coroutine` oraz `os.clock`, `os.time`,
  `os.date`.
- Niedostępne: `io`, reszta `os`, `require`, `dofile`, `loadfile`, `debug`, `package`, `string.dump`.
- `load` przyjmuje tylko fragmenty tekstowe (ciąg; bez fragmentów binarnych).
- `collectgarbage` przyjmuje tylko `"count"`.
- Pamięć: 64 MB na mod.
- Czas: `LuaBudget` instrukcji Lua na wywołanie zdarzenia. Długiej pracy wewnątrz jednego wywołania biblioteki (np.
  ogromne `string.rep` albo złożony wzorzec) licznik instrukcji nie mierzy; pisz proste skrypty.
- Skrypty nigdy nie zapisują plików gry, plików modów ani zapisów graczy; zapisywane są tylko pliki ustawień i
  statystyk moda.

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
  moda są ładowane ponownie (mody zip: Zastosuj). Przeładowanie kończy też wszystkie zastąpienia kamery, pogody i
  paska świetlnego.

## 9. Przykłady

`docs/modding/examples/` zawiera cztery kompletne mody. Skopiuj folder do `mods\` obok `RcCarsRe.exe`:

- `laptime_hud`: czas wyścigu gracza 1 (ten sam co zegar HUD), bieżące, ostatnie i najlepsze okrążenie w ramce, w
  formacie czasu gry; opcje: najlepsze okrążenie, rozmiar, róg.
- `checkpoint_sound`: przy każdym punkcie kontrolnym gracza 1 odtwarza własny `sounds\ding.wav` moda i wyświetla
  jego numer.
- `drift_air`: gdy samochód gracza 1 ląduje po skoku, pokazuje czas w powietrzu, daje krótką wibrację i błysk paska
  świetlnego oraz zapamiętuje przez `rc.stats` najlepszy czas w powietrzu dla każdej trasy i liczbę skoków.
- `photo_mode`: tryb fotograficzny (P lub przycisk Back / Share / Create pada): wyścig wstrzymany, HUD ukryty, swobodna kamera, F12 / A zdjęcie, rc.stats je liczy (API 1.2).

Minimalny skrypt:

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

## 10. Rozwiązywanie problemów

| Problem | Sprawdź |
|---|---|
| Nic się nie dzieje | `LuaScripts=1` i `Mods=1` w `RcCarsRe.ini`; mod jest włączony na ekranie Mody; plik leży w katalogu głównym moda lub w `scripts\`; `game_dbg.log` zawiera `Lua [mod]: ... loaded` |
| „mod scripts disabled after repeated errors” | przeczytaj pierwsze wiersze błędów `Lua [mod]` w `game_dbg.log`, popraw skrypt, naciśnij Zastosuj |
| „instruction budget exceeded” | zdarzenie wykonało naraz za dużo pracy; rozłóż ją na klatki albo zwiększ `LuaBudget` |
| Element HUD niewidoczny | wywołania HUD działają tylko przez jedną klatkę: wywołuj je z `onFrame`; sprawdź bajt alfa koloru (`0xFF......` jest nieprzezroczysty) |
| „texture ... not found” / „sound ... not found” (żółte) | nazwa i folder pliku w modzie; obrazy PNG, DDS lub CSI; dźwięki WAV, OGG, MP3 lub AU |
| W tekście pojawia się `?` | zapisz skrypt w UTF-8; czcionka gry ma tylko znaki strony kodowej swojego języka |
| Czas 1. okrążenia jest mniejszy niż zegar HUD | jak w grze, czasy okrążeń liczą się od linii startu/mety; czas wyścigu to `rc.race().time` |
| Kamera się nie zmienia | tylko w wyścigu, tylko widok gracza 1, nie w VR |
| Brak wibracji / paska świetlnego | pad musi być podłączony; `Rumble`, `LightBar`, `AdaptiveTriggers` w `RcCarsRe.ini`; wibracja i spusty działają tylko podczas jazdy w wyścigu |
| Błędy w konsoli -dev | wiersze błędów są czerwone, ostrzeżeń żółte; te same wiersze są w `game_dbg.log` |
