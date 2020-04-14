import vars
from tabulate import tabulate
import math
import json
import datetime
import asyncio


async def level(_message):
    user = str(_message.author.id)
    await is_new_discord_id(user)

    user_obj = vars.guilds[str(_message.guild.id)]['users'][str(user)]

    lvl = math.floor(user_obj['exp'] / vars.properties['xp_per_level'])

    await _message.channel.send(f'You are level {lvl} and have {user_obj["exp"]} total EXP.')


async def balance(_message):
    user = str(_message.author.id)
    await is_new_discord_id(user)

    user_obj = vars.guilds[str(_message.guild.id)]['users'][str(user)]

    await _message.channel.send(f'You have {user_obj[user]["money"]} {vars.properties["money_symbol"]}.')


async def is_new_discord_id(discord_id, server_id):
    if str(discord_id) not in vars.guilds[str(server_id)]['users']:
        vars.guilds[str(server_id)]['users'][str(discord_id)] = {
            'money': 0,
            'exp': 0
        }


async def add_value(discord_id, _type, value, server_id):
    await is_new_discord_id(discord_id, server_id)

    print(f'Adding value to {discord_id} ({value} {_type})')

    user = vars.guilds[str(server_id)]['users'][str(discord_id)]

    last_level = math.floor(user['exp'] / vars.properties['xp_per_level'])
    user[_type] += float(value)
    new_level = math.floor(user['exp'] / vars.properties['xp_per_level'])

    formatted_value = round(float(value), 1)
    name = "<@{0}>".format(discord_id)
    level_up = False

    if _type == 'exp':
        _message = "Player {0} earned {1} EXP.".format(name, formatted_value)
        level_up = new_level > last_level

    else:
        _message = "Player {0} earned {1} {2}.".format(name, formatted_value, vars.properties['money_symbol'])

    channel = vars.client.get_channel(int(vars.guilds[str(server_id)]['channel_ids']['rewards']))

    await channel.send(_message)

    if level_up:
        level_up_message = "Player {0} has leveled up to level {1}!".format(name, new_level)
        await channel.send(level_up_message)

    vars.save_guilds()


async def reward(discord_id, _type, value, server_id):
    await add_value(discord_id, _type, value, server_id)


async def achievement(discord_id, _achievement, server_id):
    achievement_obj = json.loads(_achievement)
    print(f'{discord_id} won Achievement: {achievement_obj["name"]}')

    name = "<@{0}>".format(discord_id)
    start = 'Player {0} unlocked the achievement {1}!'.format(name, achievement_obj['name'])
    end = '\n*{0}*'.format(achievement_obj['description'])

    _message = start + end

    channel = vars.client.get_channel(int(vars.guilds[str(server_id)]['channel_ids']['achievements']))

    await channel.send(_message)


async def action(target, _message, link):
    user = vars.client.get_user(int(target))
    print(f'Sent action to {target}')

    to_send = _message + '\n\n' + link

    await user.send(to_send)


async def message(target, _message, target_type, link):
    print(f'Sent message to {target} / {target_type}')
    to_send = _message
    if link != None:
        to_send += '\n\n' + link

    if target_type == 'dm_all':

        send_to = set()

        for guild_id in vars.guilds:
            for discord_id in vars.guilds[guild_id]['users']:
                send_to.add(str(discord_id))

        for discord_id in send_to:
            user = vars.client.get_user(int(discord_id))
            await user.send(to_send)

    elif target_type == 'dm_single':
        user = vars.client.get_user(int(target))
        await user.send(to_send)

    elif target_type == 'server_single':
        guild = vars.client.get_guild(int(target))
        if str(guild.id) in vars.guilds:
            default_channel = vars.client.get_channel(int(vars.guilds[str(guild.id)]['channel_ids']['bot-general']))

            await default_channel.send(to_send)

    elif target_type == 'server_all':
        for guild_id in vars.guilds:
            default_channel = vars.client.get_channel(int(vars.guilds[guild_id]['channel_ids']['bot-general']))

            await default_channel.send(to_send)


async def notification(target, _message, link, timestamp):
    print(f'Sent notification to {target}')
    notification = vars.ScheduledFunc(
        target_time=timestamp,
        callback=message,
        args=[target, _message, 'dm_single', link]
    )


def get_player_list(guild):
    return list(vars.guilds[str(guild.id)]['users'].keys())


async def send_local_leaderboard(_message, force_channel=False, target_channel=None):
    # print('Sending Local Leaderboard...')
    size = vars.properties['leaderboard_size']
    players = None
    guild_id = None

    if not force_channel:
        players = get_player_list(_message.guild)
        guild_id = str(_message.guild.id)
    else:
        players = get_player_list(target_channel.guild)
        guild_id = str(target_channel.guild.id)

    def get_exp(p):
        return vars.guilds[str(guild_id)]['users'][str(p)]['exp']

    sorted_players = sorted(players, key=get_exp, reverse=True)[:size]
    top_player_list = []

    for player in sorted_players:
        xp = get_exp(player)
        top_player_list.append(
            [vars.client.get_user(int(player)).name,
             math.floor(xp / vars.properties['xp_per_level']),
             xp])

    start = ''
    if force_channel:
        start = '```scss\n[ Weekly Local Leaderboard ]\n'
    else:
        start = '```scss\n[ Local Leaderboard ]\n'

    body = tabulate(top_player_list, headers=['Player', 'Level', 'EXP'])
    end = '\n```'

    to_send = start + body + end

    if force_channel:
        await target_channel.send(to_send)
    else:
        await _message.channel.send(to_send)


async def set_default_weekday(_message):
    data = {
        'MONDAY': 0,
        'TUESDAY': 1,
        'WEDNESDAY': 2,
        'THURSDAY': 3,
        'FRIDAY': 4,
        'SATURDAY': 5,
        'SUNDAY': 6,
    }

    try:
        weekday = _message.content.split(' ')[4]
    except Exception:
        await _message.channel.send('Either an invalid format was given or no weekday was given!')
    else:
        if str(_message.guild.id) in vars.guilds:
            if weekday.upper() not in data:
                await _message.channel.send("That's not a proper weekday! Ex. SET DEFAULT LEADERBOARD WEEKDAY SUNDAY")
            else:
                vars.guilds[str(_message.guild.id)]['default_time']['weekday'] = data[weekday.upper()]
                vars.save_guilds()
                timeout = next_time_for_weekly_leaderboard(str(_message.guild.id), False)

                del vars.leaderboard_timers[str(_message.guild.id)]
                vars.leaderboard_timers[str(_message.guild.id)] = vars.Timer(
                    timeout=timeout, callback=weekly_leaderboard, args=[str(_message.guild.id)])

                await _message.channel.send('Default weekday successfully set.')
        else:
            await _message.channel.send('This server has not been generated on server-end yet.'
                                  f'\nAsk an admin to {vars.properties["prompt"]}FORCE RESTART')


async def set_default_time(_message):

    try:
        time = _message.content.split(' ')[5]
        time_split = time.split(':')

    except Exception:
        await _message.channel.send('Either an invalid format was given or no time was given!\n'
                              f'EX. {vars.properties["prompt"]}SET DEFAULT LEADERBOARD TIME UTC 13:24')
    else:
        hour = int(time_split[0])
        _min = int(time_split[1])

        size_req = len(time_split[0]) == 2 and len(time_split[1]) == 2
        val_req = 0 <= hour <= 24 and 0 <= _min <= 59

        if size_req and val_req:
            if str(_message.guild.id) in vars.guilds:
                vars.guilds[str(_message.guild.id)]['default_time']['time'] = [hour, _min]
                vars.save_guilds()

                timeout = next_time_for_weekly_leaderboard(str(_message.guild.id), False)

                del vars.leaderboard_timers[str(_message.guild.id)]
                vars.leaderboard_timers[str(_message.guild.id)] = vars.Timer(
                    timeout=timeout, callback=weekly_leaderboard, args=[str(_message.guild.id)])

                await _message.channel.send('Default time successfully set.')
            else:
                await _message.channel.send('This server has not been generated on server-end yet.'
                                      f'\nAsk an admin to {vars.properties["prompt"]}FORCE RESTART')
        else:
            await _message.channel.send('Either an invalid format was given or no time was given!\n'
                                  f'EX. {vars.properties["prompt"]}SET DEFAULT LEADERBOARD TIME UTC 13:24')


def next_time_for_weekly_leaderboard(guild_id, force_next=True):
    # guild_id as str
    _def_time = vars.guilds[guild_id]['default_time']

    weekday = None
    hour = None
    _min = None

    if _def_time['weekday'] == 'default':
        weekday = int(vars.properties['default_weekly_leaderboard_weekday'])
    else:
        weekday = int(_def_time['weekday'])

    if _def_time['time'] == 'default':
        time_split = vars.properties['default_weekly_leaderboard_hour_min_utc'].split(':')

        hour = int(time_split[0])
        _min = int(time_split[1])

    else:
        hour = int(_def_time['time'][0])
        _min = int(_def_time['time'][1])

    d = datetime.datetime.utcnow().date()

    if force_next:
        d += datetime.timedelta(1)

    while d.weekday() != weekday:
        d += datetime.timedelta(1)

    target = datetime.datetime(
        year=d.year, month=d.month, day=d.day, minute=_min, second=0, hour=hour, tzinfo=datetime.timezone.utc)

    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    time_diff = (target - now).total_seconds()

    if time_diff < 0:
        return next_time_for_weekly_leaderboard(guild_id, True)
    else:
        return time_diff


async def weekly_leaderboard(guild_id):
    channel_id = vars.guilds[guild_id]['bot-general']

    channel = vars.client.get_channel(int(channel_id))

    await send_local_leaderboard(None, True, channel)
    timeout = next_time_for_weekly_leaderboard(guild_id, False)

    vars.leaderboard_timers[guild_id] = vars.Timer(
        timeout=timeout, callback=weekly_leaderboard, args=[guild_id])

    # timer = vars.Timer(timeout, channel.send, args=['Test Message'])


async def force_restart(_message):
    author = _message.author

    admin = False

    if author.guild_permissions.administrator:
        admin = True

    if admin:
        guild = _message.guild
        print('Restarting Guild ' + str(guild.id))

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
        await vars.client.get_channel(channel_ids['bot-general']).send(vars.properties['first_joined_message'])

        timeout = next_time_for_weekly_leaderboard(str(guild.id), False)

        try:
            del vars.leaderboard_timers[str(guild.id)]
        except Exception:
            pass

        vars.leaderboard_timers[str(guild.id)] = vars.Timer(
            timeout, weekly_leaderboard, [str(guild.id)])


async def force_refresh(_message):
    author = _message.author

    admin = False

    if author.guild_permissions.administrator:
        admin = True

    if admin:
        guild = _message.guild
        print('Restarting Guild ' + str(guild.id))

        channel_ids = {
            'bot-general': None,
            'rewards': None,
            'achievements': None
        }

        unfilled_channels = list(channel_ids.keys())

        for channel in guild.text_channels:
            if channel.name in channel_ids:
                channel_ids[channel.name] = str(channel.id)
                unfilled_channels.remove(channel.name)

        for channel in unfilled_channels:
            new_channel = await guild.create_text_channel(channel)
            new_channel_id = str(new_channel.id)

            channel_ids[channel] = new_channel_id

        vars.guilds[str(guild.id)]['channel_ids'] = channel_ids

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
        await vars.client.get_channel(channel_ids['bot-general']).send(vars.properties['first_joined_message'])

        timeout = next_time_for_weekly_leaderboard(str(guild.id), False)

        try:
            del vars.leaderboard_timers[str(guild.id)]
        except Exception:
            pass

        vars.leaderboard_timers[str(guild.id)] = vars.Timer(
            timeout, weekly_leaderboard, [str(guild.id)])

