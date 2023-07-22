#!/bin/bash
# Load environment variables from .env file
source .env

send_discord_message() {
    local message="$1"
    local webhook_url="$2"
    local payload="{
        \"content\": \"$message\"
    }"
    curl -H "Content-Type: application/json" -d "$payload" "$webhook_url"
}

# Notify users that the server  will be shutting down in 60 seconds
send_discord_message "Alert! Off to secret mission in 60 seconds" "$NOTICE_WEBHOOK"
screen -S zomboid -X stuff "servermsg \"Alert! Spiffo need to do stuffs in 60 seconds\"\n"
sleep 60

# Notify users that the server is shutting down
send_discord_message "Going dark" "$QUIT_WEBHOOK"
screen -S zomboid -X stuff "quit\n"
sleep 15

# Notify users that the server is updating
send_discord_message "Doing secret mission" "$UPDATE_WEBHOOK"
steamcmd +runscript $HOME/update_zomboid.txt

# Notify users that the server is starting up
send_discord_message "Calling for extraction" "$START_WEBHOOK"
screen -dmS zomboid /opt/pzserver/start-server.sh
sleep 15

# Notify users that the server is up and running
send_discord_message "Reached the apocalypse" "$READY_WEBHOOK"
