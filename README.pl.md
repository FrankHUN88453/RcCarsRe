# RcCarsRe

[English](README.md) | [Magyar](README.hu.md) | [Русский](README.ru.md) | **Polski**

RcCarsRe to fanowski projekt, w którym plik wykonywalny gry **RC Cars** (Creat Studio, 2003, PC) jest budowany
od nowa z odtworzonego kodu źródłowego w C, aby gra działała na dzisiejszych systemach i dało się ją modyfikować.

![RcCarsRe: szybki wyścig na pierwszej trasie plażowej](docs/preview.webp)

*Szybki wyścig w odbudowanym pliku wykonywalnym w rozdzielczości 2560 x 1440, z włączonymi cieniami i odbiciami
w czasie rzeczywistym.*

> To repozytorium zawiera na razie tylko ten opis i obrazek podglądu. Kod źródłowy nie został jeszcze
> opublikowany, a żadna część oryginalnej gry nigdy nie zostanie tu opublikowana.

## Czym jest ten projekt

- Nowy `RcCarsRe.exe`, napisany w C na podstawie udokumentowanego zachowania oryginalnej gry.
- Korzysta z plików danych zainstalowanej, legalnie posiadanej kopii gry (wydanie DVD lub wydanie Steam).
  Bez niej nie działa.
- Celem jest zachowanie wierne oryginałowi. Podstawowe procedury są porównywane bit po bicie z funkcjami
  oryginału w środowisku testowym.
- Nowoczesne zmiany są opcjonalne i można je przełączać w pliku `RcCarsRe.ini`; na początku pliku wymienione są
  wszystkie opcje i ich możliwe wartości.

## Nowoczesne opcje

- Renderer Direct3D 11 emulujący wywołania Direct3D 8 oryginału
- Natywna rozdzielczość, okno bez ramki, szerokoekranowe pole widzenia, skalowanie interfejsu i HUD
- Wygładzanie krawędzi (MSAA / FXAA), filtrowanie anizotropowe, najlepsza jakość tekstur
- Cienie w czasie rzeczywistym (kaskadowe mapy cieni) zamiast oryginalnych plam cienia
- Odbicia w czasie rzeczywistym na samochodach i ładniejsze morze (odbicie lustrzane, efekt Fresnela,
  przejrzyste płycizny)
- Ustawienia limitu klatek i VSync (bez ograniczenia do 64 kl./s), licznik FPS
- Czcionka menu w jakości HD, poprawki HUD dla szerokich ekranów
- Okluzja otoczenia w przestrzeni ekranu (SSAO), punktowe światła w czasie rzeczywistym przy lampach i latarniach
- 1280 x 800 (Steam Deck) i każda inna rozdzielczość; menu i HUD skalują się z oknem
- Kontrolery Xbox, PlayStation 4 i DualSense: wibracje, adaptacyjne spusty DualSense, pasek świetlny podążający
  za strzałką GPS w wyścigu (żółty w menu), strzały odczuwalne przez haptykę DualSense;
  przy wyjściu pad wraca do ustawień domyślnych
- Podzielony ekran dla dwóch graczy (klawiatura i mysz albo dwa pady), kamera sterowana myszą
- VR przez OpenXR (SteamVR i inne), status w Discordzie w czterech językach

## Tryb wieloosobowy

Do sześciu graczy przez LAN, bezpośredni adres IP albo zaproszenie na Discordzie, na własnym kodzie sieciowym UDP
(bez DirectPlay, bez wspólnej gry z oryginalnym exe). Host otwiera port przez UPnP, jeśli router na to pozwala. W
lobby i w wyścigu jest czat, host ma polecenia serwera (kick, ban, say, trasa i liczba okrążeń), są też głosowania.
Do testów na jednym PC można uruchomić dwie kopie. Jak to działa:
[English](docs/MULTIPLAYER.md) | [Magyar](docs/MULTIPLAYER.hu.md) | [Русский](docs/MULTIPLAYER.ru.md) | [Polski](docs/MULTIPLAYER.pl.md).

## Mody

Pliki gry można zastępować z folderu `mods` obok exe: foldery lub archiwa zip, tekstury w CSI, PNG lub DDS, dźwięki i
muzyka w AU, WAV, MP3 lub OGG, bez limitów rozmiaru. Menu Mody ustawia ich kolejność, włącza je i stosuje zmiany bez
restartu. Jak to działa:
[English](docs/MODDING.md) | [Magyar](docs/MODDING.hu.md) | [Русский](docs/MODDING.ru.md) | [Polski](docs/MODDING.pl.md).

## Skrypty Lua w modach

Mody mogą zawierać małe skrypty Lua działające w piaskownicy: teksty i obrazy na HUD, dźwięki, zdarzenia okrążeń i
punktów kontrolnych oraz stronę ustawień w menu Mody. Skrypty działają tylko lokalnie (HUD, dźwięk, dziennik); nie
mogą zmieniać wyścigu ani plików gry. Dokumentacja z pełnym API i przykładowymi modami (zdarzenia, kamera, mgła, słońce i woda, wibracje i pasek świetlny, własne statystyki, tryb
zdjęć oraz **Zombie** — cały nowy tryb gry zbudowany tylko z API: nowe tryby pojawiają się w wierszu Mode w Quick race):
[English](docs/modding/LUA_SCRIPTING.en.md) | [Magyar](docs/modding/LUA_SCRIPTING.hu.md) |
[Русский](docs/modding/LUA_SCRIPTING.ru.md) | [Polski](docs/modding/LUA_SCRIPTING.pl.md).
Lua 5.4 jest używane na licencji MIT ([LUA_LICENSE.txt](docs/modding/LUA_LICENSE.txt)).

## Stan prac

Prace trwają. Szybki wyścig i mistrzostwa można rozegrać od początku do końca, wyścig sieciowy działa w sieci
lokalnej, przez bezpośredni IP i przez Internet (UPnP lub przekierowany port, zaproszenia na Discordzie), świat
hosta widzą wszyscy; zakupy w garażu nie są jeszcze gotowe.

| Obszar | Stan |
|---|---|
| Intro, menu główne, ekrany Options i Quick race | działa |
| Muzyka, dźwięki interfejsu i wyścigu | działa |
| Wczytywanie i rysowanie poziomów, morze, piana przy brzegu, strumienie, wodospady | działa |
| Fizyka samochodu gracza: kolizje, zawieszenie, opony, silnik, układ kierowniczy, antena | działa |
| Przeciwnicy SI | działa (ich oryginalny wybór trasy w toku) |
| Wyścig: odliczanie, okrążenia, punkty kontrolne, pozycje, HUD, mapa, lista zawodników, tabela wyników | działa |
| Przedmioty z fizyką, ludzie, mewy, kraby, psy, ruch uliczny, strażnicy, pająki, sępy | działa, w trakcie dopracowywania |
| Efekty samochodów: ślady opon, kurz, dym z wydechu, brud, rozbryzgi wody | działa |
| Mgła, menu pauzy | działa |
| Strzały strażników i transportera opancerzonego | w toku |
| Mistrzostwa z nagrodami pieniężnymi, profile graczy, zapisy w oryginalnym formacie | działa |
| Garaż | ekrany działają, zakupy w toku |
| Podzielony ekran dla dwóch graczy; kontrolery Xbox, PlayStation 4 i DualSense z wibracjami | działa |
| VR (OpenXR), status w Discordzie | działa |
| Tryb wieloosobowy: LAN, bezpośredni IP, zaproszenie na Discordzie, UPnP, czat, polecenia serwera i głosowania | działa (ruch uliczny, ludzie, psy, strażnicy, kraby, przedmioty i strzały hosta są synchronizowane) |
| Obsługa modów (folder `mods`, menu Mody, skrypty Lua) | działa |

## Czego to repozytorium nie będzie zawierać

- Pliku wykonywalnego, bibliotek, poziomów, modeli, tekstur, dźwięków ani żadnych innych zasobów oryginalnej gry
- Narzędzi do obchodzenia zabezpieczeń przed kopiowaniem ani cheatów

## Informacje prawne

RC Cars oraz wszystkie związane z nią nazwy i zasoby należą do ich właścicieli. To nieoficjalny, niekomercyjny
projekt, który nie jest z nimi powiązany ani przez nich wspierany. Do korzystania z niego potrzebna jest własna,
legalnie nabyta kopia gry. Obrazek podglądu pokazuje odbudowany plik wykonywalny działający z danymi oryginalnej
gry.

## Języki

Ten opis jest dostępny po angielsku, węgiersku, rosyjsku i polsku. Wersją odniesienia jest wersja angielska.
