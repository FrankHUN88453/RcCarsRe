# Gra sieciowa w RcCarsRe

[English](MULTIPLAYER.md) | [Magyar](MULTIPLAYER.hu.md) | [Русский](MULTIPLAYER.ru.md) | **Polski**

RcCarsRe (przebudowany exe RC Cars) gra w grę sieciową oryginału (Menu główne > Multiplayer > Create game /
Join game) własnym protokołem UDP. Nie gra z oryginalnym RCCARS.exe i nie potrzebuje DirectPlay. Ściga się do 6
graczy; host prowadzi grę (trasa, okrążenia, start, tabela wyścigu).

## Zakładanie gry w sieci lokalnej

1. Menu główne > Multiplayer > **Create game**. Na stronie Network options podaj nazwę gry, maks. opóźnienie,
   szybkość połączenia (od niej zależy, jak często wysyłane są stany aut) i liczbę graczy. Pole "Port" może zostać
   puste (domyślnie `NetPort`, 2302).
2. **Create**. Jesteś w poczekalni ("Wait players"). Na stronie Race summary wybierz trasę i okrążenia.
3. Gdy wszyscy pozostali są **Ready**, naciśnij **Race**.

Przy pierwszej grze w sieci lokalnej Windows może zapytać, czy RcCarsRe może używać sieci: zezwól dla sieci
prywatnych. Z `NetBind=loopback` wszystko zostaje na tym komputerze i Windows nie pyta.

## Dołączanie

- Menu główne > Multiplayer > **Join game**. Lista od razu i co sekundę szuka gier w sieci lokalnej (i kopii na tym
  komputerze); trwający wyścig lub gra z opóźnieniem ponad jej maksimum nie są pokazywane. **Sort** zmienia kolejność.
- **Bezpośredni IP:** wpisz adres hosta w "Server name" (np. `192.168.1.20` lub `192.168.1.20:2302`), port w "Port",
  jeśli nie jest domyślny, i naciśnij **Search**.
- Wybierz wiersz, **Connect**, potem **Ready** w poczekalni.

## Twoje auto (poczekalnia: Car setup, Car restrictions)

- **Car setup**: twoje auto, booster, silnik i opony (obracające się auto je pokazuje) oraz **Next skin**. Twój wybór
  wszyscy widzą w tabeli Race summary i w wyścigu.
- **Car restrictions**: host zezwala na każde auto lub je wyłącza i ustala jego najwyższe ulepszenie (Default,
  Level 1 .. 3). Pozostali widzą zasady, ale nie mogą ich zmienić. Wybór poza zasadami wraca do najbliższego
  dozwolonego; dopóki twoje auto łamie zasady, **Ready** nie jest przyjmowane.
- W oryginalnej grze na stronie Car setup można zmienić tylko malowanie (auto wraca do Road Rage). `NetCarChoice=0`
  przywraca to zachowanie.

## Gra przez Internet

Nasz serwer nie jest potrzebny: jeden gracz zakłada grę, pozostali łączą się z jego adresem internetowym.

1. **UPnP (automatycznie).** Gdy zakładasz grę z `NetBind=any`, RcCarsRe prosi router o otwarcie portu UDP gry
   (`NetUPnP=1`). Po kilku sekundach w poczekalni pojawia się złota linia: `Internet: 1.2.3.4:2302 (UPnP)` - ten adres
   podaj znajomym. Jeśli widzisz `UPnP not available: forward UDP 2302 by hand`, router ma wyłączone UPnP (albo
   jesteś za drugim routerem / NAT-em dostawcy).
2. **Przekierowanie portu (ręcznie).** W routerze przekieruj port **UDP** 2302 (lub twój `NetPort`) na lokalny adres
   tego komputera. Twój adres internetowy pokaże router lub dowolna strona "mój IP".
3. **Dołączanie:** Join game > adres internetowy hosta w "Server name" (`1.2.3.4` lub `1.2.3.4:2302`) > **Search** >
   **Connect**.
4. **Zaproszenie przez Discord.** Przy `Discord=1` i `NetDiscordJoin=1` twój profil Discord pokazuje grę, gdy jesteś
   hostem lub w grze, z przyciskami **Join** / **Ask to join** dla znajomych (oni też potrzebują RcCarsRe i Discorda).
   Dołączenie z Discorda otwiera Multiplayer > Join game z adresem i łączy. Jeśli RcCarsRe nie działa, Discord ją
   uruchamia (w tym celu RcCarsRe zapisuje swoje polecenie startu w `HKCU\Software\Classes\discord-<DiscordAppId>`).
   "Ask to join" jest przyjmowane od razu (`NetDiscordAutoAccept=1`); przy `0` w poczekalni pojawia się pytanie
   Tak / Nie.

Klucz dołączenia, który Discord przekazuje znajomym, zawiera twój adres internetowy (lub lokalny) i port - widzą go
tylko ci, których wpuszczasz. Windows może raz zapytać, czy RcCarsRe może używać sieci: zezwól w sieciach, w których
grasz.

## Świat w wyścigu sieciowym

Życiem trasy kieruje host i wszyscy widzą to, co u hosta: ruch uliczny (ciężarówki, Hummer i BTR ruszają, gdy wysyła
je host, i jadą tą samą drogą na każdym komputerze; wieża BTR obraca się jak u hosta), ludzi, psy i strażników (gdzie
stoją i chodzą, ich animację i czy w ogóle są), kraby (gdzie i kiedy krab wychodzi z nory), puszki, piłki i inne
przedmioty (ich położenie i obrót) oraz serie strażników i wieży (strzały i trafienia w twoje auto). Przedmiot
popchnięty na twoim komputerze przesuwa się także u hosta. Kopie u pozostałych podążają za hostem z małym opóźnieniem
(ludzie ok. 0,3 s). Mew, pająków i sępów oryginał nie przesyła: każdy komputer ma własne. Przy najwolniejszym
ustawieniu połączenia (bpsLevel 0) oryginał nie przesyła ludzi, psów, strażników, przedmiotów ani wieży; przedmioty
wymagają bpsLevel 2 lub wyższego.

## Dwie kopie na jednym komputerze (do testów)

    cd /d D:\Games\RcCars
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 1
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 2

`-instance N` pozwala uruchomić kilka kopii: każda ma swój port (NetPort + N - 1), dziennik `game_dbg_N.log`,
ustawienia okna `RcCarsRe.instN.ini` (okno 960 x 540; Display / Width / Height / WindowX / WindowY / PlayerName) i
kopię zapisów `Saves\Instance<N>\` (prawdziwe zapisy są tylko czytane). Od kopii 2 nazwa to "<profil> N", jeśli
PlayerName nie jest ustawione. Kopia 1 jest hostem, kopia 2 łączy się z `127.0.0.1`.

## Nazwy

- `[Modern] PlayerName=` - twoja nazwa w wyścigach, wynikach, tabelach i grze sieciowej (najwyżej 10 liter; puste =
  nazwa profilu). `PlayerName2=` - drugi gracz podzielonego ekranu. To tylko nazwy wyświetlane: nigdy nie trafiają do
  profilu, RCCars.crs ani pliku ducha.
- `[Modern] NetSessionName=` - nazwa zakładanej gry (puste = nazwa ze strony Create game).

## Czat

- Poczekalnia: wiersz czatu strony Race summary i strona **Chat**.
- Wyścig: **Z** (`ChatKey`) otwiera wiersz pod czatem wyścigu (podpowiedź „Naciśnij Z, aby czatować...” pokazuje gdzie), **Enter** wysyła, **Esc** anuluje. Podczas pisania
  klawiatura nie steruje autem (wyścig trwa). **Y** pokazuje ponownie ostatnie wiersze. (Oryginał nie ma wpisywania w
  wyścigu; to nowość.)

## Polecenia

Wpisuj je w czat z `/`. Host może je też wpisać w konsolę -dev bez `/`.

| Polecenie | Kto | |
|---|---|---|
| `/help`, `/players` | wszyscy | polecenia; numer (#n), ping i krótkie id każdego gracza |
| `/kick <nazwa lub #n> [powód]` | host | usuwa gracza (widzi powód) |
| `/ban <nazwa lub #n> [powód]` | host | usuwa gracza i nie wpuszcza go ponownie |
| `/unban <nazwa, wiersz lub id>` | host | nazwa, wiersz `/bans` lub 8+ cyfr hex id; przy kilku trafieniach `/unban <x> all` |
| `/bans` | host | bany |
| `/say <tekst>` | host | wiersz "[SERVER] " do wszystkich (także z konsoli -dev hosta: `say ...`) |
| `/map <trasa>`, `/laps <n>` | host | trasa następnego wyścigu (beach_1 .., nazwa z menu lub 1 .. 10) i okrążenia |
| `/votekick <nazwa lub #n> [powód]`, `/votemap <trasa>`, `/voterestart` | wszyscy | rozpoczyna głosowanie (votekick wymaga `NetVoteKickMin` graczy razem z hostem; cel nie głosuje) |
| `/yes`, `/no` (w wyścigu **F1** / **F2**) | wszyscy | odpowiedź w głosowaniu |
| `/cancelvote` | host | kończy głosowanie |

Głosowanie przechodzi, gdy „za” jest ponad połowa graczy (rozpoczynający liczy się jako „za”); kończy się po
`NetVoteTime` sekundach; gracz może rozpocząć głosowanie co `NetVoteCooldown` sekund; naraz trwa jedno. Przyjęte
głosowanie na trasę ustawia trasę następnego wyścigu; restart to "Race again" oryginału.

Nazwa hosta jest pokazywana jako „[HOST] <nazwa>” w poczekalni, liście wyścigu, wynikach, jego wierszach czatu i w
/players. Powód kicka / bana (do 64 znaków, inaczej „no reason given”) widzi gracz, wszyscy w wierszu serwera; jest
zapisany w bans.txt i dzienniku czatu.

## Bany i co jest wysyłane

Przy dołączaniu każdy klient wysyła: nazwę, losowy identyfikator instalacji (`NetClientId.txt`) i dwa **zahaszowane
odciski sprzętu** (SHA-256 z adresów MAC fizycznych kart sieciowych razem z numerem seryjnym woluminu systemowego i
GUID maszyny Windows oraz z samych adresów MAC). Surowe adresy MAC ani numery seryjne nigdy nie opuszczają komputera
i nigdzie nie są zapisywane; hasze służą tylko do banów. Dołączenie bez poprawnych id jest odrzucane.

Host trzyma bany w `bans.txt` obok exe (`bans_inst<N>.txt` dla `-instance N`): jeden w wierszu, rozdzielone TAB
(czas, nazwa, id klienta, hwid, macid, adres, powód), komentarze `#`; można go edytować ręcznie, gdy gra nie jest
założona. Dołączenie jest odrzucane, gdy pasuje id klienta, hwid, macid lub adres.

## Dziennik czatu (host)

Z `NetChatLog=1` (domyślnie) host zapisuje każdy wiersz czatu, polecenie, głosowanie, wejście / wyjście / kick / ban
i początek / koniec gry z czasem do `Logs\chat_<data>.log` (`chat_<data>_inst<N>.log`). Zawiera nazwy i krótkie id,
nigdy adresy. Klienci nie piszą dziennika.

## Klucze RcCarsRe.ini ([Modern])

| Klucz | Domyślnie | |
|---|---|---|
| `PlayerName`, `PlayerName2` | puste | nazwy wyświetlane |
| `NetSessionName` | puste | nazwa zakładanej gry |
| `NetPort` | 2302 | port UDP hosta |
| `NetDiscoveryPort` | 2301 | port listy w sieci lokalnej |
| `NetBind` | any | `any`, `loopback` (tylko ten komputer) lub adres lokalny |
| `NetChatLog` | 1 | dziennik czatu hosta |
| `NetVotes`, `NetVoteKick`, `NetVoteMap` | 1 | głosowania wł. / wył. |
| `NetVoteTime`, `NetVoteCooldown` | 30, 60 | sekundy |
| `NetVoteKickMin` | 4 | graczy do votekicka |
| `ChatKey` | Z | klawisz czatu w wyścigu (litera, cyfra, F1 .. F12, Enter, Tab) |
| `NetCarChoice` | 1 | na stronie Car setup wybiera się auto i części (0 = jak w oryginale: tylko malowanie) |
| `NetUPnP` | 1 | host otwiera swój port na routerze przez UPnP |
| `NetDiscordJoin` | 1 | Join / Ask to join przez Discord (wymaga `Discord=1`) |
| `NetDiscordAutoAccept` | 1 | "Ask to join" przyjmowane od razu (0 = pytanie Tak / Nie) |

Jeszcze nie ma: internetowej listy serwerów, stron oryginału Player info / Server info (nazwa i kolor czatu pochodzą
z profilu / `PlayerName`).
