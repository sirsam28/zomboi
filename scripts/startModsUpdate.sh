#!/bin/bash
echo 'broadcasting message: server will be restarting in 60 seconds'
screen -S zomboid -X stuff "servermsg \"server will be restarting in 60 seconds\"\n"
sleep 60
screen -S zomboid -X stuff "servermsg \"restarting Ssrver\"\n"
sleep 3

echo 'shutting down server'
screen -S zomboid -X stuff "quit\n"
sleep 15

echo 'updating server'
steamcmd +runscript $HOME/update_zomboid.txt

echo "starting zomboid server"
screen -dmS zomboid /opt/pzserver/start-server.sh
