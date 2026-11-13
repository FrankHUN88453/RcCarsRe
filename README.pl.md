# RcCarsRe

[English](README.md) | [Magyar](README.hu.md) | [Русский](README.ru.md) | **Polski**

RcCarsRe to fanowski projekt, w którym plik wykonywalny gry **RC Cars** (Creat Studio, 2003, PC) jest budowany
od nowa z odtworzonego kodu źródłowego w C, aby gra działała na dzisiejszych systemach i dało się ją modyfikować.

> To repozytorium zawiera na razie tylko ten opis. Kod źródłowy nie został jeszcze opublikowany, a żadna część
> oryginalnej gry nigdy nie zostanie tu opublikowana.

## Czym jest ten projekt

- Nowy `RcCarsRe.exe`, napisany w C na podstawie udokumentowanego zachowania oryginalnej gry.
- Korzysta z plików danych zainstalowanej, legalnie posiadanej kopii gry (wydanie DVD lub wydanie Steam).
  Bez niej nie działa.
- Celem jest zachowanie wierne oryginałowi. Podstawowe procedury są porównywane bit po bicie z funkcjami
  oryginału w środowisku testowym.
- Nowoczesne zmiany są opcjonalne i można je przełączać w pliku `RcCarsRe.ini`.

## Nowoczesne opcje

- Renderer Direct3D 11 emulujący wywołania Direct3D 8 oryginału
- Natywna rozdzielczość, okno bez ramki, skalowanie interfejsu
- Wygładzanie krawędzi (MSAA / FXAA), najlepsza jakość tekstur
- Ustawienia limitu klatek i VSync (bez ograniczenia do 64 kl./s), licznik FPS
- Czcionka menu w jakości HD

## Stan prac

Prace trwają. Projekt nie jest jeszcze grywalny jako pełna gra.

| Obszar | Stan |
|---|---|
| Intro, menu główne, ekrany Options i Quick race | działa |
| Muzyka i dźwięki interfejsu | działa |
| Wczytywanie poziomu, rysowanie trasy, animowana woda | działa |
| Samochody SI jadące po nagranych trasach | działa (rozwiązanie tymczasowe) |
| Fizyka samochodu gracza: kolizje z poziomem, zawieszenie, opony, silnik, układ kierowniczy | działa, w trakcie dopracowywania |
| Widoczne zawieszenie i koła | pierwszy samochód gotowy, pozostałe w toku |
| Antena, kamera wyścigowa | w toku |
| Światła startowe, okrążenia, punkty kontrolne, HUD | nie rozpoczęto |
| Pozostałe tryby gry, garaż, tryb wieloosobowy | nie rozpoczęto |

## Czego to repozytorium nie będzie zawierać

- Pliku wykonywalnego, bibliotek, poziomów, modeli, tekstur, dźwięków ani żadnych innych zasobów oryginalnej gry
- Narzędzi do obchodzenia zabezpieczeń przed kopiowaniem ani cheatów

## Informacje prawne

RC Cars oraz wszystkie związane z nią nazwy i zasoby należą do ich właścicieli. To nieoficjalny, niekomercyjny
projekt, który nie jest z nimi powiązany ani przez nich wspierany. Do korzystania z niego potrzebna jest własna,
legalnie nabyta kopia gry.

## Języki

Ten opis jest dostępny po angielsku, węgiersku, rosyjsku i polsku. Wersją odniesienia jest wersja angielska.
