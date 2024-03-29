# minecraft-control

## Deprecated
DEPRECATED: I have had much more success managing minecraft servers with kubernetes. See https://github.com/gilesknap/k3s-minecraft

## Intro
Some scripts for managing multiple Minecraft servers on a single machine

Inspired by https://github.com/agowa338/MinecraftSystemdUnit/ configuration for running minecraft as a systemd service.
Also note a similar project at https://github.com/docent-net/mc-server-manager.

Adds python scripts to easily see the state of any number of servers, plus configure and control them.

Current functions

- List the set of minecraft servers installed with info on status and worlds
- start / stop / restart
- enable / disable (i.e. control auto start)
- attach to console
- switch configured world for a server
- backup a world

Future functions

- create new server
- add new world to server
- upgrade minecraft
- improved CLI via click
- consider client server split (maybe - or stick to ssh)
- replace screen with an RCON client (maybe using https://pypi.org/project/mcipc/)

Example interaction

```
/home/minecraft/minecraft-control$ pipenv run python mc-control.py

Minecraft Servers' State
No Name                State      SubSt   Auto Sta GameMode  World          Wlds
0  MinecraftSurvival   active     running enabled  adventure NoahSurvival09 1
1  DadNoahSurvival     inactive   dead    disabled adventure GilesWorld     2
2  DevilsDeep          inactive   dead    disabled adventure Deep           2

Choose a Server (a=all)
2

Choose an action: s=start k=stop e=enable d=disable r=restart c=console w=set_world b=backup_world
e

Minecraft Servers' State
No Name                State      SubSt   Auto Sta GameMode  World          Wlds
0  MinecraftSurvival   active     running enabled  adventure NoahSurvival09 1
1  DadNoahSurvival     inactive   dead    disabled adventure GilesWorld     2
2  DevilsDeep          inactive   dead    enabled  adventure Deep           2

Choose an action: s=start k=stop e=enable d=disable r=restart c=console w=set_world b=backup_world
```

The project is in a working state but not yet fully documented. See
instructions.txt for hints on setup.
