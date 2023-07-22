from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
from pathlib import Path
import glob
import os
import asyncio


class ServerHandler(commands.Cog):
    def __init__(self, bot, logPath):
        self.bot = bot
        self.logPath = logPath
        self.scriptPath = os.getenv("SCRIPT_PATH")
        self.lastUpdateTimestamp = datetime.now()
        if self.scriptPath is None or len(self.scriptPath) == 0:
            self.bot.log.error(
                f"script path {self.scriptPath} not found")
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
    async def runScript(self, scriptPath):
        try:
            script_abs_path = os.path.join(self.base_script_dir, scriptPath)
            process = await asyncio.create_subprocess_shell(
                f"bash {script_abs_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Get the output of stdout and stderr
            return stdout.decode().strip(), stderr.decode().strip()
        except Exception as e:
            return f"An unexpected error occurred: {e}", ""

    @commands.command()
    async def checkserver(self, ctx):
        """Check server mods status, will trigger an update if needed in 60 seconds after execution"""
        stdout_output, stderr_output = await self.runScript(self.scriptPath)

        if stderr_output:
            self.bot.log.error(f"stderr_output: {stderr_output}")
        else:
            self.bot.log.info(f"stdout_output: {stdout_output}")

        # Interpret the output of the shell script
        if stdout_output == 'true':
            await ctx.send("Updating in progress. Mods will be updated shortly.")
        elif stdout_output == 'false':
            await ctx.send("Mods are up to date.")
        else:
            await ctx.send("An error occurred while checking/modifying the mods.")

        if stderr_output:
            await ctx.send(f"Script Error (stderr):\n{stderr_output}")
            self.bot.log.info(f"Script Error: {stderr_output}")
