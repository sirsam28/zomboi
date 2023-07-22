#!/bin/bash
screen -S zomboid -X stuff "checkModsNeedUpdate\n"
sleep 2
if tail ~/Zomboid/Logs/*DebugLog-server.txt -n 1 | grep -q updated; then
  echo 'zomboid mods are up to date'
else
  echo 'running startModsUpdate'
  ~/zomboid-scripts/startModsUpdate.sh
fi
