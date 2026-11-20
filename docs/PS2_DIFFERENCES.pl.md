# RC Cars (PC) i Smash Cars (PS2): czym się różnią

*Inne języki: [English](PS2_DIFFERENCES.md), [Magyar](PS2_DIFFERENCES.hu.md), [Русский](PS2_DIFFERENCES.ru.md)*

Gra **Smash Cars** (2003) na PlayStation 2 to konsolowa wersja gry **RC Cars** na PC. Ta strona wymienia różnice
znalezione podczas przenoszenia samochodów z gry na PS2 do odtworzonej gry na PC jako moda.

**Jak to ustalono.** Pliki gry na PC porównano z plikami europejskiej płyty PS2 (SLES-51800): modele, tekstury,
banki dźwięków, rekordy ustawień oraz części programu, w którym zachowały się nazwy funkcji. W samą grę na PS2
przy tym nie grano, więc to, co widać dopiero podczas gry (menu, tryby, zasady, poziom trudności), nie jest tu
opisane. Tam, gdzie coś jest odczytaniem, a nie pewnością, jest to zaznaczone.

## W skrócie

| | PC (RC Cars) | PS2 (Smash Cars) |
|---|---|---|
| Samochody | 3: Overkill, Buggy, Warhammer | 13: cztery podwozia po trzy karoserie oraz odrzutowy CCCP |
| Malowania | kilka na samochód | 3 na karoserię, 8 dla CCCP |
| Trasy | 10 (beach 1-4, country 1-4, urban 1-2) | 13 poziomów |
| Dźwięki silnika | trzy zestawy, po jednym na samochód, 44,1 kHz | jeden zestaw dla wszystkich, 22 kHz, krótsze nagrania |
| Muzyka | pliki MP3 | 7 utworów |
| Sterowanie w powietrzu | brak | sterowanie w powietrzu z punktami za triki i zwolnionym „trybem Matrix" |
| Silniki odrzutowe | brak | CCCP w powietrzu skręca i pcha się silnikami |
| Tekstury | wyższa rozdzielczość, pełny kolor | tekstury 256-kolorowe, od 64 do 256 pikseli |

## Samochody

Dwanaście samochodów gry na PS2 składa się z czterech podwozi i trzech karoserii na każde; trzynasty ma własne.
Trzy podwozia to trzy samochody gry na PC: to samo zawieszenie, zgodne co do milimetra.

| Podwozie | Samochód PC | Karoserie PS2 |
|---|---|---|
| Over | Overkill | Road Rage, Redneck, Beatle |
| Buggy | Buggy | Tornado, HotShot, Razor |
| Hummer | Warhammer | Warhammer, Skull Tank, Rockarolla |
| Half | nie ma w grze na PC | Sting, Flashback, Blazer |
| Super | nie ma w grze na PC | CCCP (trzy koła, dwa silniki) |

Half jest zbudowany jak Buggy (niezależne koła), ale ma dwie sprężyny na koło i nie ma górnych wahaczy.
Super ma jedno szerokie tylne koło.

## Fizyka

- Obie gry używają tej samej fizyki. Każde podwozie ma jeden rekord ustawień z tymi samymi wartościami w tej
  samej kolejności co ustawienia samochodów gry na PC (prędkości, przyczepność, sprężyny, rozmiary kół, kształt
  kolizji, ulepszenia).
- Kształty kolizji trzech wspólnych samochodów są w obu grach identyczne. Ich dostrojone wartości (prędkość
  maksymalna, przyczepność, mnożniki ulepszeń) nie: gra na PS2 ustawia je inaczej.
- Half i Super używają kształtu kolizji Overkilla.
- Rekord PS2 ma kilka dodatkowych wartości, których nie ma w grze na PC; używa ich tylko Super (do silników).

## Silniki CCCP

Odczytane z programu PS2:

- Silniki działają **tylko w powietrzu**. Na ziemi CCCP jedzie na kołach jak każdy inny samochód.
- W powietrzu samochód leci tam, gdzie jest skierowany: boczny znos znika od razu.
- Gaz pcha go do przodu wzdłuż poziomego kursu; wsteczny pcha do tyłu z połową siły.
- Skręt uruchamia silnik jednej strony, który obraca samochód.
- W locie samochód jest obracany do poziomu, więc ląduje na kołach.
- Jego grawitacja słabnie wraz z prędkością: w miejscu około połowy zwykłej, przy prędkości maksymalnej prawie żadna, więc skacze wysoko i daleko. (To, że grawitacja zależy od prędkości, jest w programie; której z krzywych gry używa, wybrano po jej wartościach, nie prześledzono.)

## Triki w powietrzu i „tryb Matrix"

Program PS2 ma system sterowania w powietrzu dla wszystkich samochodów, którego nie ma w grze na PC: samochód
można obracać w powietrzu, obroty i wysokość są punktowane.

„Tryb Matrix" to zwolnienie czasu podczas skoku. Według programu PS2 włącza się, gdy spełnione jest wszystko:

- jest włączony w menu opcji (dwupozycyjne ustawienie gracza);
- trwa wyścig i nie jest to jeden z dwóch typów wyścigu (których, nie ustalono);
- samochód gracza od ponad 0,02 sekundy nie dotyka niczego kołami ani dachem;
- samochód spada od 0,1 sekundy, czyli właśnie minął szczyt skoku.

Czas zwalnia wtedy do jednej piątej w ciągu 0,2 sekundy. Gdy samochód dotknie ziemi, czas wraca do normy w pół
sekundy. W ustawieniach jest też minimalny wynik za triki, ale ma wartość 0.

## Dźwięki

- Gra na PC ma trzy zestawy dźwięków silnika (po jednym na samochód). Gra na PS2 ma jeden zestaw dla
  wszystkich samochodów, z nazwami zestawu Overkilla z PC; nagrania są krótsze i gorszej jakości.
- Żaden samochód PS2 nie ma własnych dźwięków, CCCP też nie.
- Gra na PS2 ma kilka dźwięków samochodu, których brakuje na PC: poślizg na asfalcie i na ziemi, uderzenie w
  trawę oraz `motor_flying_matrix`, dźwięk silnika w zwolnionym locie.
- Każdy poziom PS2 ma własny bank dźwięków; są w nim też zwierzęta i przedmioty poziomu.

## Modele i tekstury

- PS2 rysuje obie strony każdej powierzchni, PC tylko przednią. Lustrzane części PS2 (prawa strona samochodu) są
  zapisane wywrócone na lewą stronę, więc dla PC trzeba je odwrócić.
- Tekstury PS2 mają 256 kolorów: malowania karoserii 256 x 256, podwozie 128 x 128, opony 64 x 64. Tekstury
  wspólnych samochodów na PC są większe i nie są tymi samymi obrazami.
- Samochody PS2 mają osobne, proste modele cienia.

## Poziomy

Odczytane z poziomu samouczka PS2 (ogrodzone podwórko, którego nie ma w grze na PC):

- **Światło.** Poziomy PC oświetlają mapy światła, czyli druga warstwa tekstur. W poziomach PS2 światło jest
  zapisane w kolorze każdego wierzchołka geometrii.
- **Tekstury.** Większość tekstur poziomów PS2 ma 256 kolorów; te z przezroczystymi częściami (siatka ogrodzenia,
  drzewa, znaki na ziemi) to obrazy 16- lub 32-bitowe.
- **Trawa.** Gra na PS2 ma system trawy, którego nie ma na PC: tysiące małych roślin (około 2600 na podwórku
  samouczka), osiem rodzajów wyciętych z jednego obrazu. Kołyszą się i uginają pod samochodami.
- **Przedmioty.** Przedmioty do przepychania są w obu grach tych samych rodzajów: puszki, piłki, wiadra, pachołki.
  Poziom PS2 przechowuje miejsce i kształt kolizji każdego; ma też kask, dla którego gra na PC nie ma modelu.
- **Punkty kontrolne.** W poziomie PS2 to zwykła lista punktów, w poziomie PC to obiekty-znaczniki.
- **Postacie.** Na podwórku samouczka jest chłopiec na trójkołowym rowerku (animowany model z własnym dźwiękiem)
  i dwa gokarty z kierowcą, które jeżdżą po nagranych pętlach (Kart.StartProfile).

## Pliki

| | PC | PS2 |
|---|---|---|
| Sceny i samochody | bazy `.sb` | pliki modeli `.S_A` ..., jeden indeks `.SBF` na poziom |
| Dźwięki | jeden plik na dźwięk | jeden bank `.MSB` na poziom |
| Muzyka | MP3 | `TRACK1` - `TRACK7` |
| Filmy | `Intro.dat` | trzy pliki wideo |

## W odtworzonej grze na PC

Mod `extension` dodaje grę PS2 do odtworzonej gry: plac samouczka PS2 jako trasę (w menu głównym przycisk "Tutorial" z intro i trzema zadaniami, do wyłączenia w config.ini modu) oraz samochody PS2: Sting i CCCP jako nowe samochody z własnymi wartościami
fizyki, pozostałe osiem karoserii jako dodatkowe karoserie trzech samochodów PC i Stinga. Jego funkcje Lua
opisuje [modding/LUA_SCRIPTING.pl.md](modding/LUA_SCRIPTING.pl.md), rozdział 6a. Przerobione samochody powstają
z własnej płyty PS2 użytkownika i nie są rozpowszechniane.

Mod ma własny `config.ini`: `[SlowMotion]` `SlowMotion=1` włącza zwolnienie czasu trybu Matrix podczas skoków (gra
jednoosobowa), `Tutorial=1` pokazuje w menu głównym przycisk "Tutorial" samouczka z PS2.

Poziom samouczka jest przerobiony na poziom PC: geometria, tekstury, zapisane światło, punkty kontrolne, trawa
(kołysze się i daje się zdeptać), przedmioty (puszki, piłki, wiadro, pachołek i kask z PS2 jako modele),
przeciwnicy, chłopiec na rowerku i dwa gokarty na swoich trasach z PS2 oraz trzy zadania samouczka z limitami czasu
i punktacją trików jak na PS2. Plac ma teraz także żuki (chodzą i uciekają jak pająki gry na PC; nie odlatują jak
na PS2), śmieci na ziemi, własne dźwięki chłopca i gokartów (pedałowanie, dzwonek, silniki gokartów) oraz
podpowiedzi zadań pod klawiszem (H albo Back na padzie). Jak wszystko inne powstają one z własnej płyty PS2
użytkownika i nie są rozpowszechniane.

Nie przeniesiono: pozostałych tras PS2, punktacji trików w powietrzu poza samouczkiem, dźwięków PS2 innych niż
dźwięki placu samouczka, krótkiego wyścigu pokazowego z intro samouczka ani jego nagród.
