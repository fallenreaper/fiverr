from dotenv import load_dotenv
import discord
import os
import asyncio
from datetime import datetime
from datetime import timezone
import json

# START-UP DECLARATIONS & FUNCTIONS ================================

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Start-up Discord Client
client = discord.Client()

guilds = {}
users = {}

properties_file = open('properties.json', 'r')
properties = json.loads(properties_file.read())
properties_file.close()
leaderboard_timers ={}


# START-UP END =====================================================


class Timer:
    def __init__(self, timeout, callback, args=None):
        self._timeout = timeout
        self._callback = callback
        self._args = args
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)

        if self._args == None:
            await self._callback()
        else:
            await self._callback(*self._args)

    def cancel(self):
        self._task.cancel()


class ScheduledFunc:
    def __init__(self, target_time, callback, args=None):
        # Time Specified in UTC
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        target = datetime.utcfromtimestamp(int(target_time)).replace(tzinfo=timezone.utc)

        time_diff = (target - now).total_seconds()

        self._timer = Timer(time_diff, callback, args)


# LOAD AND SAVE FUNCS ============================================


def save_guilds():
    with open("src/guilds.json", 'w') as f:
        json.dump(guilds, f)


def load_guilds():
    global guilds
    guilds_file = open('src/guilds.json', 'r')
    guilds = json.loads(guilds_file.read())
    guilds_file.close()


load_guilds()
