# Zombies (example game mode)

A tag / infection game mode made only with the Lua API (1.5): see the "Game modes" chapter of
[LUA_SCRIPTING.en.md](../../LUA_SCRIPTING.en.md). Copy this folder to `mods\zombies\` next to the exe and pick
**Zombies** in the Quick race's Mode row. In a network game the host types `/mode zombies` in the lobby's chat
(every player needs the mod); the host's script decides, see "Network races" in the scripting guide.

The script expects some files of your own, which are not part of this repository. Without them the mode still
works: a missing file is logged as a warning and skipped.

| File in the mod | Used for |
|---|---|
| `sounds\zombie_ambient.mp3` | the looping ambience that replaces the level's own during a round |
| `sounds\thunder01.wav` | heard by everyone from the place where someone becomes a zombie |
| `sounds\zombie_attack*.wav` | one picked at random, at both cars when a zombie catches a survivor |
| `sounds\heart_beat.wav` | survivors hear it from the nearest zombie's direction, faster as it gets closer |
| `sounds\zombie_outro.mp3` | the end scene when the zombies win |
| `sounds\humans_win.wav` | the end scene when the survivors win |
| `skins\man_1new.png`, `skins\man_2new.png`, `skins\woman_1new.png`, `skins\woman_2new.png`, `skins\seagullsitting.png` | zombie skins for the pedestrians and the seagulls, swapped in only while the mode runs (`rc.replaceTexture`) |

The skins must keep the layout (UV map) of the game's own textures of the same names; any size works.
