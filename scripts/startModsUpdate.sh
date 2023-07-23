#!/bin/bash
# Load environment variables from .env file
source .env

send_discord_message() {
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
send_discord_message ":loudspeaker:  Alert, 60 seconds till mission start" $NOTICE_WEBHOOK
screen -S zomboid -X stuff "servermsg \"Alert! Spiffo need to do stuffs in 60 seconds\"\n"
sleep 60

# Notify users that the server is shutting down
echo "server is shutting down"
send_discord_message ":detective:  Going dark right now" $QUIT_WEBHOOK
screen -S zomboid -X stuff "quit\n"
sleep 15

# Notify users that the server is updating
echo "server is updating"
send_discord_message ":mag:   Doing secret mission" $UPDATE_WEBHOOK
steamcmd +runscript $HOME/update_zomboid.txt

# Notify users that the server is starting up
echo "server is starting up"
send_discord_message :helicopter:  Calling for extraction $START_WEBHOOK
screen -dmS zomboid /opt/pzserver/start-server.sh
sleep 15

# Notify users that the server is up and running
echo "server is up and running"
send_discord_message ":crossed_swords:  Reached the apocalypse" $READY_WEBHOOK
