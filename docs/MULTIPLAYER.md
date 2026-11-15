# Network games with RcCarsRe

**English** | [Magyar](MULTIPLAYER.hu.md) | [Русский](MULTIPLAYER.ru.md) | [Polski](MULTIPLAYER.pl.md)

RcCarsRe (the rebuilt RC Cars exe) plays the original's network game (Main menu > Multiplayer > Create game /
Join game) over its own UDP protocol. It does not play with the original RCCARS.exe, and it needs no DirectPlay.
Up to 6 players race; the host runs the session (track, laps, the start, the race table).

## Hosting on the LAN

1. Main menu > Multiplayer > **Create game**. On the Network options page choose the session's name, the max lag,
   the connection speed (it sets how often the cars' states are sent) and the players. Leave "Port" empty for the
   default (`NetPort`, 2302) or type another one.
2. **Create**. You are in the lobby ("Wait players"). Choose the track and the laps on the Race summary page.
3. When every other player is **Ready**, press **Race**.

The first time a game is hosted on the LAN, Windows may ask whether RcCarsRe may use the network: allow it for
private networks. With `NetBind=loopback` everything stays on this PC and Windows does not ask.

## Joining

- Main menu > Multiplayer > **Join game**. The list searches the LAN (and the instances on this PC) at once and
  every second; a game that is racing or whose lag is above its max lag is not listed. **Sort** changes the order.
- **Direct IP:** type the host's address into "Server name" (for example `192.168.1.20`, or `192.168.1.20:2302`),
  the port into "Port" if it is not the default, and press **Search**.
- Choose the row and press **Connect**, then **Ready** in the lobby.

## Your car (lobby: Car setup, Car restrictions)

- **Car setup**: your car, booster, engine and tires (the turning car shows them) and **Next skin**. Everybody sees
  your choice in the Race summary table and in the race.
- **Car restrictions**: the host allows or disables each car and sets its highest upgrade (Default, Level 1 .. 3).
  Other players see the rules but cannot change them. A choice outside the rules is taken back to the nearest
  allowed one; **Ready** is refused while your car breaks the rules.
- In the original game only the skin can be changed on Car setup (the car goes back to Road Rage). `NetCarChoice=0`
  gives that back.

## Playing over the Internet

No server of ours is needed: one player hosts, the others connect to the host's Internet address.

1. **UPnP (automatic).** When you host with `NetBind=any`, RcCarsRe asks your router to open the UDP game port
   (`NetUPnP=1`). After a few seconds the lobby shows a gold line: `Internet: 1.2.3.4:2302 (UPnP)` - give that address
   to your friends. If it says `UPnP not available: forward UDP 2302 by hand`, the router has UPnP off (or you are
   behind a second router / your provider's NAT).
2. **Port forwarding (by hand).** In your router forward **UDP** port 2302 (or your `NetPort`) to this PC's LAN
   address. Your Internet address is shown by the router or any "what is my IP" page.
3. **Joining:** Join game > type the host's Internet address into "Server name" (`1.2.3.4` or `1.2.3.4:2302`) >
   **Search** > **Connect**.
4. **Discord invite.** With `Discord=1` and `NetDiscordJoin=1` your Discord profile shows the game while you host or
   play in a session, with **Join** / **Ask to join** for your friends (who also run RcCarsRe with Discord). Joining
   from Discord opens Multiplayer > Join game with the address and connects. If RcCarsRe is not running, Discord
   starts it (RcCarsRe registers its start command for this under
   `HKCU\Software\Classes\discord-<DiscordAppId>`). An "Ask to join" is accepted at once (`NetDiscordAutoAccept=1`);
   with `0` you get a Yes / No box in the lobby.

The join secret Discord passes to your friends holds your Internet (or LAN) address and port - only friends you let
join see it. Windows may ask once whether RcCarsRe may use the network: allow it for the networks you play on.

## Two instances on one PC (testing)

    cd /d D:\Games\RcCars
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 1
    start "" D:\Games\RcCars\_re\rebuild\out\RcCarsRe.exe -novid -instance 2

`-instance N` lets several copies run: each gets the port NetPort + N - 1, the log `game_dbg_N.log`, its own
window settings in `RcCarsRe.instN.ini` (a 960 x 540 window; Display / Width / Height / WindowX / WindowY /
PlayerName) and a scratch copy of the saves in `Saves\Instance<N>\` (your real saves are only read). Instance 2 and
up show "<profile> N" as their name unless PlayerName is set. Instance 1 hosts, instance 2 joins `127.0.0.1`.

## Names

- `[Modern] PlayerName=` - the name shown for you in races, results, tables and network games (at most 10
  letters; empty = your profile's name). `PlayerName2=` is the split screen's player 2. These are display names
  only: they are never written into a profile, RCCars.crs or a ghost file.
- `[Modern] NetSessionName=` - the name of a game you host (empty = the Create game page's name).

## Chat

- Lobby: the chat line of the Race summary page and the **Chat** page.
- Race: **Z** (`ChatKey`) opens a line under the race chat (the hint "Press Z to chat..." shows where), **Enter** sends it, **Esc** cancels. While you type the
  keyboard does not drive (the race goes on). **Y** shows the last lines again. (The original has no input line in
  the race; this is new.)

## Commands

Type them into the chat with `/`. The host can also type them into the -dev console without the `/`.

| Command | Who | |
|---|---|---|
| `/help`, `/players` | everybody | the commands; every player's number (#n), ping and short ids |
| `/kick <name or #n> [reason]` | host | removes the player (the reason is shown to them) |
| `/ban <name or #n> [reason]` | host | removes the player and refuses their joins |
| `/unban <name, line or id>` | host | a name, a line of `/bans`, or 8+ hex digits of an id; with several matches `/unban <x> all` |
| `/bans` | host | the bans |
| `/say <text>` | host | a "[SERVER] " line to everybody (also from the host's -dev console: `say ...`) |
| `/map <track>`, `/laps <n>` | host | the next race's track (beach_1 .., the menu name or 1 .. 10) and laps |
| `/votekick <name or #n> [reason]`, `/votemap <track>`, `/voterestart` | everybody | start a vote (a votekick needs `NetVoteKickMin` players, the host included; its target cannot vote) |
| `/yes`, `/no` (or **F1** / **F2** in a race) | everybody | answer the vote |
| `/cancelvote` | host | ends the vote |

A vote passes with more than half of the players (its starter counts as yes); it ends after `NetVoteTime`
seconds; a player can start a vote every `NetVoteCooldown` seconds; one vote at a time. A passed map vote sets the
next race's track; a restart vote restarts the race as the original's "Race again".

The host's name shows as "[HOST] <name>" in the lobby, the race list, the results, its chat lines and /players.
A kick's / ban's reason (up to 64 characters, else "no reason given") is shown to the player, to everybody in the
server line, and is kept in bans.txt and the chat log.

## Bans and what is sent

Every client sends, when it joins: its name, a random id of the install (`NetClientId.txt`) and two **hashed
hardware fingerprints** (SHA-256 of the physical network adapters' MAC addresses with the system volume's serial
number and the Windows machine GUID, and of the MAC addresses alone). Raw MAC addresses or serial numbers never
leave the PC and are never stored; the hashes are used only for bans. A join without valid ids is refused.

The host keeps its bans in `bans.txt` next to the exe (`bans_inst<N>.txt` for `-instance N`): one ban per line,
TAB separated (time, name, client id, hwid, macid, address, reason), `#` comments; you may edit it while no game is
hosted. A join is refused when its client id, hwid, macid or address matches a ban.

## Chat log (host)

With `NetChatLog=1` (default) the host writes every chat line, command, vote, join / leave / kick / ban and the
session's start / end with its time to `Logs\chat_<date>.log` (`chat_<date>_inst<N>.log`). It holds player names and
short ids, never addresses. Clients write no chat log.

## RcCarsRe.ini keys ([Modern])

| Key | Default | |
|---|---|---|
| `PlayerName`, `PlayerName2` | empty | display names |
| `NetSessionName` | empty | the hosted game's name |
| `NetPort` | 2302 | the host's UDP port |
| `NetDiscoveryPort` | 2301 | the LAN list's port |
| `NetBind` | any | `any`, `loopback` (this PC only) or a local address |
| `NetChatLog` | 1 | the host's chat log |
| `NetVotes`, `NetVoteKick`, `NetVoteMap` | 1 | votes on / off |
| `NetVoteTime`, `NetVoteCooldown` | 30, 60 | seconds |
| `NetVoteKickMin` | 4 | players a votekick needs |
| `ChatKey` | Z | the race's chat key (a letter, a digit, F1 .. F12, Enter, Tab) |
| `NetCarChoice` | 1 | Car setup lets you choose the car and parts (0 = the original: only the skin) |
| `NetUPnP` | 1 | the host opens its port on the router by UPnP |
| `NetDiscordJoin` | 1 | Join / Ask to join through Discord (needs `Discord=1`) |
| `NetDiscordAutoAccept` | 1 | "Ask to join" accepted at once (0 = a Yes / No box) |

Not yet: an Internet server list, the Player info / Server info pages of the original (your name and chat colour
come from the profile / `PlayerName`).
