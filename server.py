from datetime import datetime
from discord.ext import commands
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

    # Function to run the shell script
    async def runScript(self, scriptPath):
        try:
            process = await asyncio.create_subprocess_shell(
                f"bash {scriptPath}",
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
        """Check server mods status, update automatically if needed"""
        stdout_output, stderr_output = await self.runScript(self.scriptPath)

        self.bot.log.error(f"stderr_output: {stderr_output}")
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
