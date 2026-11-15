# Hálózati játék az RcCarsRe-vel

[English](MULTIPLAYER.md) | **Magyar** | [Русский](MULTIPLAYER.ru.md) | [Polski](MULTIPLAYER.pl.md)

Az RcCarsRe (az RC Cars újraépített exe-je) az eredeti hálózati játékát (Főmenü > Multiplayer > Create game /
Join game) saját UDP-protokollon játssza. Az eredeti RCCARS.exe-vel nem tud együtt játszani, és nem kell hozzá
DirectPlay. Legfeljebb 6 játékos versenyez; a host vezeti a játékot (pálya, körök, rajt, a verseny táblázata).

## Játék indítása (host) a helyi hálózaton

1. Főmenü > Multiplayer > **Create game**. A Network options oldalon add meg a játék nevét, a max. késést, a
   kapcsolat sebességét (ez szabja meg, milyen sűrűn mennek az autók állapotai) és a játékosok számát. A "Port"
   maradhat üresen (alapértelmezett: `NetPort`, 2302).
2. **Create**. A váróteremben ("Wait players") vagy. A Race summary oldalon válaszd ki a pályát és a köröket.
3. Ha mindenki más **Ready**, nyomd meg a **Race** gombot.

Az első helyi hálózati játéknál a Windows megkérdezheti, használhatja-e az RcCarsRe a hálózatot: magánhálózatra
engedélyezd. `NetBind=loopback` mellett minden ezen a gépen marad, és a Windows nem kérdez.

## Csatlakozás

- Főmenü > Multiplayer > **Join game**. A lista azonnal és másodpercenként keres a helyi hálózaton (és az ezen a
  gépen futó példányoknál); a már versenyző vagy a max. késésénél lassabb játék nem jelenik meg. A **Sort** a
  sorrendet váltja.
- **Közvetlen IP:** írd a host címét a "Server name" mezőbe (pl. `192.168.1.20` vagy `192.168.1.20:2302`), a portot
  a "Port" mezőbe, ha nem az alapértelmezett, és nyomd meg a **Search** gombot.
- Válaszd ki a sort, **Connect**, majd a váróteremben **Ready**.

## Az autód (váróterem: Car setup, Car restrictions)

- **Car setup**: az autód, a booster, a motor és a gumik (a forgó autó mutatja őket), valamint a **Next skin**.
  A választásodat mindenki látja a Race summary táblázatában és a versenyben.
- **Car restrictions**: a host engedélyezi vagy letiltja az egyes autókat, és megadja a legmagasabb fejlesztésüket
  (Default, Level 1 .. 3). A többiek látják a szabályokat, de nem módosíthatják. A szabályon kívüli választást a
  játék a legközelebbi engedélyezettre állítja vissza; amíg az autód megszegi a szabályt, a **Ready** nem fogadható el.
- Az eredeti játékban a Car setup oldalon csak a skin változtatható (az autó visszaáll Road Rage-re). A
  `NetCarChoice=0` ezt adja vissza.

## Játék az interneten át

Nem kell hozzá saját szerverünk: egy játékos hostol, a többiek a host internetes címéhez csatlakoznak.

1. **UPnP (automatikus).** Ha `NetBind=any` mellett hostolsz, az RcCarsRe megkéri a routert, hogy nyissa meg az UDP
   játékportot (`NetUPnP=1`). Néhány másodperc múlva a váróteremben arany sor jelenik meg: `Internet: 1.2.3.4:2302
   (UPnP)` - ezt a címet add meg a barátaidnak. Ha ezt írja: `UPnP not available: forward UDP 2302 by hand`, akkor a
   routeren ki van kapcsolva az UPnP (vagy egy második router / a szolgáltató NAT-ja mögött vagy).
2. **Porttovábbítás (kézzel).** A routerben továbbítsd az **UDP** 2302-es portot (vagy a `NetPort`-odat) erre a gépre
   (a helyi hálózati címére). Az internetes címedet a router vagy bármelyik "mi az IP-címem" oldal megmutatja.
3. **Csatlakozás:** Join game > a host internetes címe a "Server name" mezőbe (`1.2.3.4` vagy `1.2.3.4:2302`) >
   **Search** > **Connect**.
4. **Discord-meghívás.** `Discord=1` és `NetDiscordJoin=1` mellett a Discord-profilod mutatja a játékot, amíg hostolsz
   vagy játékban vagy, a barátaidnak **Join** / **Ask to join** gombbal (nekik is RcCarsRe és Discord kell). A
   Discordból való csatlakozás megnyitja a Multiplayer > Join game oldalt a címmel, és csatlakozik. Ha az RcCarsRe nem
   fut, a Discord elindítja (ehhez az RcCarsRe bejegyzi az indítóparancsát a
   `HKCU\Software\Classes\discord-<DiscordAppId>` kulcsba). Az "Ask to join" kérést azonnal elfogadja
   (`NetDiscordAutoAccept=1`); `0` esetén Igen / Nem kérdést kapsz a váróteremben.

A Discord által a barátaidnak átadott csatlakozási kulcs tartalmazza az internetes (vagy helyi) címedet és portodat -
csak azok látják, akiket beengedsz. A Windows egyszer megkérdezheti, használhatja-e az RcCarsRe a hálózatot: engedd
meg azokon a hálózatokon, ahol játszol.

## A világ hálózati versenyben

A pálya életét a host futtatja, és mindenki a hostét látja: a forgalmat (a teherautók, a Hummer és a Btr akkor
indulnak, amikor a host indítja őket, és minden gépen ugyanazt az utat járják; a Btr tornya úgy fordul, mint a
hostnál), az embereket, kutyákat és őröket (hol állnak és járnak, az animációjukat, és hogy egyáltalán ott vannak-e),
a rákokat (hol és mikor bújnak elő), a dobozokat, labdákat és más tárgyakat (helyüket és forgásukat), valamint az őrök
és a torony sorozatait (a lövéseket és a találatot az autódon). Ha a saját gépeden lökök meg egy tárgyat, a hostnál is
elmozdul. A többiek példányai egy pillanattal a host mögött követik (az emberek kb. 0,3 s-mal). A sirályokat, pókokat
és keselyűket nem küldi (ahogy az eredeti sem): minden gép a sajátját futtatja. A leglassabb kapcsolat-beállításnál
(bpsLevel 0) az eredeti nem küld embert, kutyát, őrt, tárgyat és tornyot; a tárgyakhoz legalább bpsLevel 2 kell.

## Két példány egy gépen (teszteléshez)

    cd /d D:\Games\RcCars
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 1
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 2

A `-instance N` több példányt enged: mindegyik saját portot (NetPort + N - 1), naplót (`game_dbg_N.log`),
ablakbeállítást (`RcCarsRe.instN.ini`: 960 x 540-es ablak; Display / Width / Height / WindowX / WindowY / PlayerName)
és mentés-másolatot kap (`Saves\Instance<N>\`; a valódi mentéseidet csak olvassa). A 2. példánytól a név
"<profil> N", ha nincs PlayerName. Az 1. példány a host, a 2. a `127.0.0.1`-hez csatlakozik.

## Nevek

- `[Modern] PlayerName=` - a neved a versenyekben, eredményekben, táblázatokban és hálózaton (legfeljebb 10 betű;
  üres = a profil neve). `PlayerName2=` az osztott képernyő 2. játékosáé. Csak megjelenített nevek: soha nem kerülnek
  profilba, RCCars.crs-be vagy szellemfájlba.
- `[Modern] NetSessionName=` - az általad hostolt játék neve (üres = a Create game oldal neve).

## Chat

- Váróterem: a Race summary oldal chat-sora és a **Chat** oldal.
- Verseny: a **Z** (`ChatKey`) nyit egy sort a verseny chat alatt (a „Nyomd meg a Z-t a csevegéshez...” felirat mutatja, hol), **Enter** elküldi, **Esc** bezárja. Gépelés
  közben a billentyűzet nem vezet (a verseny megy tovább). **Y** újra megmutatja az utolsó sorokat. (Az eredetiben
  versenyben nincs beírás; ez új.)

## Parancsok

A chatbe `/`-rel írd őket. A host a -dev konzolba `/` nélkül is írhatja.

| Parancs | Ki | |
|---|---|---|
| `/help`, `/players` | mindenki | a parancsok; a játékosok száma (#n), pingje és rövid azonosítói |
| `/kick <név vagy #n> [ok]` | host | eltávolítja a játékost (az okot látja) |
| `/ban <név vagy #n> [ok]` | host | eltávolítja és nem engedi vissza |
| `/unban <név, sor vagy azonosító>` | host | név, a `/bans` sora, vagy egy azonosító legalább 8 hex jegye; több találatnál `/unban <x> all` |
| `/bans` | host | a kitiltások |
| `/say <szöveg>` | host | "[SERVER] " előtagú sor mindenkinek (a host -dev konzoljából is: `say ...`) |
| `/map <pálya>`, `/laps <n>` | host | a következő verseny pályája (beach_1 .., a menü neve vagy 1 .. 10) és körei |
| `/votekick <név vagy #n> [ok]`, `/votemap <pálya>`, `/voterestart` | mindenki | szavazás indítása (a votekickhez `NetVoteKickMin` játékos kell, a hosttal együtt; a célpont nem szavazhat) |
| `/yes`, `/no` (versenyben **F1** / **F2**) | mindenki | válasz a szavazásra |
| `/cancelvote` | host | lezárja a szavazást |

A szavazás a játékosok több mint felével megy át (az indító igennek számít); `NetVoteTime` másodperc után lejár;
egy játékos `NetVoteCooldown` másodpercenként indíthat; egyszerre egy szavazás fut. Az elfogadott pályaszavazás a
következő verseny pályáját állítja; az újraindítás az eredeti "Race again"-je.

A host neve „[HOST] <név>” alakban látszik a váróteremben, a versenylistán, az eredményekben, a chat-soraiban és a
/players-ben. A kirúgás / kitiltás oka (legfeljebb 64 karakter, különben „no reason given”) a játékosnak, mindenkinek
a szerver-sorban, a bans.txt-ben és a chat-naplóban is megjelenik.

## Kitiltás és amit a játék küld

Csatlakozáskor minden kliens elküldi: a nevét, a telepítés véletlen azonosítóját (`NetClientId.txt`) és két
**hash-elt hardver-ujjlenyomatot** (a fizikai hálózati kártyák MAC-címeinek, a rendszerkötet sorozatszámának és a
Windows gépazonosítójának SHA-256-ja, illetve csak a MAC-címeké). Nyers MAC-cím vagy sorozatszám soha nem hagyja el a
gépet és sehol nincs tárolva; a hash-eket csak kitiltáshoz használja. Érvényes azonosítók nélkül a csatlakozást
elutasítja.

A host a kitiltásokat az exe melletti `bans.txt`-ben tartja (`-instance N`: `bans_inst<N>.txt`): soronként egy,
TAB-bal elválasztva (idő, név, kliens-azonosító, hwid, macid, cím, ok), `#` megjegyzés; kézzel szerkeszthető, amíg
nincs hostolt játék. Ha a kliens-azonosító, a hwid, a macid vagy a cím egyezik egy kitiltással, elutasítja.

## Chat-napló (host)

`NetChatLog=1` (alapértelmezett) mellett a host minden chat-sort, parancsot, szavazást, belépést / kilépést /
kirúgást / kitiltást és a játék kezdetét / végét időponttal a `Logs\chat_<dátum>.log`-ba írja
(`chat_<dátum>_inst<N>.log`). Neveket és rövid azonosítókat tartalmaz, címeket soha. A kliensek nem naplóznak.

## RcCarsRe.ini kulcsok ([Modern])

| Kulcs | Alapérték | |
|---|---|---|
| `PlayerName`, `PlayerName2` | üres | megjelenített nevek |
| `NetSessionName` | üres | a hostolt játék neve |
| `NetPort` | 2302 | a host UDP-portja |
| `NetDiscoveryPort` | 2301 | a helyi lista portja |
| `NetBind` | any | `any`, `loopback` (csak ez a gép) vagy egy helyi cím |
| `NetChatLog` | 1 | a host chat-naplója |
| `NetVotes`, `NetVoteKick`, `NetVoteMap` | 1 | szavazások be / ki |
| `NetVoteTime`, `NetVoteCooldown` | 30, 60 | másodperc |
| `NetVoteKickMin` | 4 | a votekickhez kellő játékosok |
| `ChatKey` | Z | a verseny chat-billentyűje (betű, szám, F1 .. F12, Enter, Tab) |
| `NetCarChoice` | 1 | a Car setup oldalon autó és alkatrészek választhatók (0 = az eredeti: csak a skin) |
| `NetUPnP` | 1 | a host UPnP-vel megnyitja a portját a routeren |
| `NetDiscordJoin` | 1 | Join / Ask to join a Discordon át (kell hozzá `Discord=1`) |
| `NetDiscordAutoAccept` | 1 | az "Ask to join" azonnali elfogadása (0 = Igen / Nem kérdés) |

Még nincs: internetes szerverlista, az eredeti Player info / Server info oldalai (a neved és a chat-színed a
profilból / a `PlayerName`-ből jön).
