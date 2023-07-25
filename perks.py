from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
import glob
import os
import re


class DayHourMinute:
    def __init__(self, day, hour, minute):
        self.day = day
        self.hour = hour
        self.minute = minute


class PerkHandler(commands.Cog):
    """Class which handles the Perk log files"""

    def __init__(self, bot, logPath):
        self.bot = bot
        self.logPath = logPath
        self.lastUpdateTimestamp = datetime.now()
        self.loadHistory()
        self.update.start()
        self.notifyJoin = os.getenv("JOINS", "True") == "True"
        self.notifyDeath = os.getenv("DEATHS", "True") == "True"
        self.notifyPerk = os.getenv("PERKS", "True") == "True"
        self.notifyCreateChar = os.getenv("CREATECHAR", "True") == "True"

    def splitLine(self, line: str):
        """Split a log line into a timestamp and the remaining message"""
        timestampStr, message = line.strip()[1:].split("]", 1)
        timestamp = datetime.strptime(timestampStr, "%d-%m-%y %H:%M:%S.%f")
        return timestamp, message

    @tasks.loop(seconds=2)
    async def update(self):
        files = glob.glob(self.logPath + "/*PerkLog.txt")
        if len(files) > 0:
            with FileReadBackwards(files[0]) as f:
                newTimestamp = self.lastUpdateTimestamp
                for line in f:
                    timestamp, message = self.splitLine(line)
                    if timestamp > newTimestamp:
                        newTimestamp = timestamp
                    if timestamp > self.lastUpdateTimestamp:
                        message = self.handleLog(
                            timestamp, message, fromUpdate=True)
                        if message is not None and self.bot.channel is not None:
                            await self.bot.channel.send(message)
                    else:
                        break
                self.lastUpdateTimestamp = newTimestamp

    # Load the history from the files up until the last update time
    def loadHistory(self):
        self.bot.log.info("Loading Perk history...")

        # Go through each user file in the log folder and subfolders
        files = glob.glob(self.logPath + "/**/*PerkLog.txt", recursive=True)
        files.sort(key=os.path.getmtime)
        for file in files:
            with open(file) as f:
                for line in f:
                    self.handleLog(*self.splitLine(line))
        self.bot.log.info("Perk history loaded")

    # Parse a line in the user log file and take appropriate action

    def formatTime(self, hours):
        days = hours // 24
        remaining_hours = hours % 24
        minutes = remaining_hours * 60
        return DayHourMinute(day=days, hour=remaining_hours, minute=minutes)

    def handleLog(self, timestamp: datetime, message: str, fromUpdate=False):
        # Ignore the id at the start of the message, no idea what it's for
        message = message[message.find("[", 2) + 1:]

        # Next is the name which we use to get the user
        name, message = message.split("]", 1)
        userHandler = self.bot.get_cog("UserHandler")
        user = userHandler.getUser(name)
        char_name = userHandler.getCharName(
            name) if fromUpdate and user else None
        log_char_string = 'aka ' + char_name + ' ' if char_name else ''

        # Then position which we set if it's more recent
        x = message[1: message.find(",")]
        y = message[message.find(
            ",") + 1: message.find(",", message.find(",") + 1)]
        message = message[message.find("[", 2) + 1:]

        if timestamp > user.lastSeen:
            user.lastSeen = timestamp
            user.lastLocation = (x, y)

        # Then the message type, can be "Died", "Login", "Level Changed" or a list of perks
        type, message = message.split("]", 1)

        # All these logs should include hours survived
        hours = re.search(r"Hours Survived: (\d+)", message).group(1)
        user.hoursAlive = hours
        if int(hours) > int(user.recordHoursAlive):
            user.recordHoursAlive = hours

        if type == "Died":
            user.died.append(timestamp)
            if timestamp > self.lastUpdateTimestamp:
                self.bot.log.info(f"{user.name} died")
                if self.notifyDeath:
                    return os.getenv("NOTIFY_DEATH").format(user=user, log_char_string=log_char_string)
        elif type == "Login":
            if timestamp > self.lastUpdateTimestamp:
                user.online = True
                self.bot.log.info(f"{user.name} login")
                if self.notifyJoin:
                    formattedTime = self.formatTime(user.recordHoursAlive)
                    return os.getenv("NOTIFY_JOIN").format(user=user, log_char_string=log_char_string, formattedTime=formattedTime)
        elif "Created Player" in type:
            if timestamp > self.lastUpdateTimestamp:
                user.online = True
                self.bot.log.info(f"{user.name} new character")
                if self.notifyCreateChar:
                    return os.getenv("NOTIFY_CREATE").format(user=user, log_char_string=log_char_string, perk="some_perk", level="some_level")
        elif type == "Level Changed":
            match = re.search(r"\[(\w+)\]\[(\d+)\]", message)
            perk = match.group(1)
            level = match.group(2)
            user.perks[perk] = level
            if timestamp > self.lastUpdateTimestamp:
                self.bot.log.info(f"{user.name} {perk} changed to {level}")
                if self.notifyPerk:
                    return os.getenv("NOTIFY_PERK").format(user=user, log_char_string=log_char_string, perk=perk.lower(), level=level)
        else:
            # Must be a list of perks following a login/player creation
            for (name, value) in re.findall(r"(\w+)=(\d+)", type):
                user.perks[name] = value
