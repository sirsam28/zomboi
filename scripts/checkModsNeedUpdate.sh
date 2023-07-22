#!/bin/bash
screen -S zomboid -X stuff "checkModsNeedUpdate\n"
sleep 2
if tail ~/Zomboid/Logs/*DebugLog-server.txt -n 1 | grep -q updated; then
  echo 'false' # Mods are up to date
else
  echo 'true'
  ~/zomboid-scripts/startModsUpdate.sh > /dev/null 2>&1 &
fi