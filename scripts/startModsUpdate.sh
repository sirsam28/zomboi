#!/bin/bash

# Load environment variables from .env file
source .env

sendDiscordMessage() {
    local message="$1"
    local webhook_url="$2"
    local payload="{
        \"content\": \"$message\"
    }"

    echo "webhook url: $webhook_url"
    echo "message: $message"
    echo "sending discord message: $message to webhook"

    curl -H "Content-Type: application/json" -d "$payload" "$webhook_url"
}

# Notify users that the server will be shutting down in 60 seconds
echo "server will be shutting down in 60 seconds"
sendDiscordMessage "$NOTICE_MESSAGE" "$NOTICE_WEBHOOK"
screen -S zomboid -X stuff "servermsg \"60 Seconds Remaining\"\n"
sleep 60

# Notify users that the server is shutting down
echo "server is shutting down"
sendDiscordMessage "$QUIT_MESSAGE" "$QUIT_WEBHOOK"
screen -S zomboid -X stuff "quit\n"
ZPID=$(pidof ProjectZomboid64)
while [ -e /proc/$ZPID ]; do
    sleep 1
done

# Notify users that the server is updating
echo "server is updating"
sendDiscordMessage "$UPDATE_MESSAGE" "$UPDATE_WEBHOOK"
steamcmd +runscript $HOME/update_zomboid.txt

# Notify users that the server is starting up
echo "server is starting up"
sendDiscordMessage "$START_MESSAGE" "$START_WEBHOOK"
screen -dmS zomboid /opt/pzserver/start-server.sh
GREP_OPTS=(-e "RCON: listening on port 27015.")
while [ grep -q "${GREP_OPTS[@]}" ~/Zomboid/Logs/*DebugLog-server.txt && echo false || echo true ]; do
    sleep 1
done

# Notify users that the server is up and running
echo "server is up and running"
sendDiscordMessage "$READY_MESSAGE" "$READY_WEBHOOK"
