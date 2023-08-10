#!/bin/bash
screen -S zomboid -X stuff "checkModsNeedUpdate\n"

tail -f ~/Zomboid/Logs/*DebugLog-server.txt -n 0 | while read line; do
  if echo $line | grep -q "Mods updated"; then
    echo "false" && break
  fi

  if echo $line | grep -q "Mods need update"; then
    echo "true" && break
  fi
done
