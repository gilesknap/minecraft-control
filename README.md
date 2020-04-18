# minecraft-control
Some scripts for managing multiple Minecraft servers on a single machine

Inspired by https://github.com/agowa338/MinecraftSystemdUnit/ configuration for running minecraft as a systemd service.

Adds python scripts to easily see the state of any number of servers, plus configure and control them.

Current functions

- List the set of minecraft servers installed with info on status and worlds
- start / stop / restart
- enable / disable (i.e. control auto start)
- attach to console
- switch configured world for a server

Future functions

- backup a world
- create new server
- add new world to server
