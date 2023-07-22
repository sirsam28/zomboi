from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
from pathlib import Path
import glob
import os
import subprocess

DISCORD_MAX_CHAR = 2000

pathsToTry = [
    "Zomboid/scripts",
    "zomboi/scripts"
]


class ServerHandler(commands.Cog):
    def __init__(self, bot, logPath):
        self.bot = bot
        self.logPath = logPath
        self.scriptPath = os.getenv("SCRIPT_PATH")
        self.lastUpdateTimestamp = datetime.now()
        if self.scriptPath is None or len(self.scriptPath) == 0:
            for path in pathsToTry:
                tryPath = Path.home().joinpath(path)
                if tryPath.exists():
                    self.scriptPath = str(tryPath)
                    break
        if self.scriptPath is None or len(self.scriptPath) == 0 or not Path(self.scriptPath).is_dir():
            self.bot.log.error(
                f"script path {self.scriptPath} not found and/or no suitable default")
        else:
            self.bot.log.info(f"script path: {self.scriptPath}")
        self.update.start()
        self.webhook = None

    def splitLine(self, line: str):
        """Split a log line into a timestamp and the remaining message"""
        timestampStr, message = line.strip()[1:].split("]", 1)
        timestamp = datetime.strptime(timestampStr, "%d-%m-%y %H:%M:%S.%f")
        return timestamp, message

    @tasks.loop(minutes=30)
    async def update(self):
        """Update the handler

        This will check the latest log file and update our data based on any
        new entries
        """
        files = glob.glob(self.logPath + "/*server.txt")
        if len(files) > 0:
            with FileReadBackwards(files[0], encoding="utf-8") as f:
                newTimestamp = self.lastUpdateTimestamp
                for line in f:
                    timestamp, message = self.splitLine(line)
                    if timestamp > newTimestamp:
                        newTimestamp = timestamp
                    if timestamp > self.lastUpdateTimestamp:
                        await self.handleLog(timestamp, message)
                    else:
                        break
                self.lastUpdateTimestamp = newTimestamp

    # Function to run the shell script
    def runScript(self, scriptPath):
        try:
            # Run the shell script using the bash shell and capture the output
            result = subprocess.run(
                ["bash", scriptPath],
                check=True,
                capture_output=True,
                text=True
            )
            # Get the output of stdout and stderr
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            # Handle any errors that might occur
            # Get the stderr in case of an error
            return f"Error occurred: {e}", e.stderr.strip()
        except Exception as e:
            return f"An unexpected error occurred: {e}", ""

    @commands.command()
    async def checkserver(self, ctx):
        """Check server mods status, will trigger an update if needed in 60 seconds after execution"""
        stdout_output, stderr_output = self.runScript(self.scriptPath)

        if stdout_output:
            await ctx.send(f"Script Output (stdout):\n{stdout_output}")
            self.bot.log.info(f"Script Output: {stdout_output}")

        else:
            await ctx.send("The script ran successfully but didn't produce any output.")

        if stderr_output:
            await ctx.send(f"Script Error (stderr):\n{stderr_output}")
            self.bot.log.info(f"Script Error: {stderr_output}")
