import vars
from tabulate import tabulate
from text_commands import commands
import funcs
import api
import asyncio


client = vars.client


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild_id in vars.guilds:
        timeout = funcs.next_time_for_weekly_leaderboard(guild_id, False)

        vars.leaderboard_timers[guild_id] = vars.Timer(
            timeout, funcs.weekly_leaderboard, [guild_id])
        # await funcs.weekly_leaderboard(guild_id)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    c = message.content.upper()[len(vars.properties['prompt']):]
    if message.content.startswith(vars.properties['prompt'].upper()):
        print('Parsing Message...')

        if c.startswith('HELP'):
            print('A client used the help function!')
            start = '```scss\n[ HELP ]\n' + vars.properties["bot_description"]

            # Reformat Commands Table
            data = []

            for key in commands:
                if key != 'help':
                    data.append([vars.properties['prompt'] + key, commands[key]['help']])

            body = '\n\nSample Commands:\n' + tabulate(data)
            end = '```'

            to_send = start + body + end
            await message.channel.send(to_send)

        else:

            passed = False

            for comm in commands:
                if c.startswith(comm):
                    await commands[comm]['action'](message)
                    passed = True
                    break

            if not passed:
                await message.channel.send(
                    'That command does not exist... Try {0}help'.format(vars.properties['prompt']))


@client.event
async def on_guild_join(guild):

    print('Joined Guild ' + str(guild.id))

    channel_ids = {
        'bot-general': None,
        'rewards': None,
        'achievements': None
    }

    unfilled_channels = list(channel_ids.keys())

    for channel in guild.text_channels:
        if channel.name in channel_ids:
            channel_ids[channel.name] = channel.id
            unfilled_channels.remove(channel.name)

    for channel in unfilled_channels:
        new_channel = await guild.create_text_channel(channel)
        new_channel_id = new_channel.id

        channel_ids[channel] = new_channel_id

    vars.guilds[str(guild.id)] = {
        'channel_ids': channel_ids,
        'default_time': {
            'weekday': 'default',
            'time': 'default'
        },
        'users': {}
    }

    new_category = None
    category_exists = False

    for category in guild.categories:
        if category.name == vars.properties['text_channel_category_name']:
            new_category = category
            category_exists = True
            break

    if not category_exists:
        new_category = await guild.create_category(vars.properties['text_channel_category_name'])

    for channel_name in channel_ids:
        channel_id = channel_ids[channel_name]
        channel = vars.client.get_channel(channel_id)

        if channel.category == None or channel.category.id != new_category.id:
            await channel.edit(category=new_category)

    vars.save_guilds()
    await client.get_channel(channel_ids['bot-general']).send(vars.properties['first_joined_message'])

    timeout = funcs.next_time_for_weekly_leaderboard(str(guild.id), False)
    vars.leaderboard_timers[str(guild.id)] = vars.Timer(
        timeout, funcs.weekly_leaderboard, [str(guild.id)])

if __name__ == '__main__':
    client.run(vars.token)
