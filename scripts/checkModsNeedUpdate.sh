#!/bin/bash

# Function to check if mods need an update and return true if they do, otherwise false
function checkModsNeedUpdate() {
  # Execute the checkModsNeedUpdate command in the Zomboid screen session
  screen -S zomboid -X stuff "checkModsNeedUpdate\n"
  sleep 2

  # Check the Zomboid server's debug log for the 'updated' message
  if tail ~/Zomboid/Logs/*DebugLog-server.txt -n 1 | grep -q updated; then
    echo 'false'  # Mods are up to date
  else
    echo 'true'   # Mods need an update
  fi
}

# Check if mods need an update
if checkModsNeedUpdate; then
  # Run the startModsUpdate.sh script in the background
  ~/zomboid-scripts/startModsUpdate.sh > /dev/null 2>&1 &

  # Return true, indicating that mods are being updated
  echo 'true'
else
  echo 'false' # Mods are up to date
fi
