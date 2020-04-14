import funcs
import vars


commands = {
    'LEADERBOARD': {
        'action': funcs.send_local_leaderboard,
        'help': 'Displays the local leaderboard for a Discord Server.',
        'help_after': '\nUsage: "{0}leaderboard"'.format(vars.properties['prompt'])
    },
    'SET LEADERBOARD WEEKDAY': {
        'action': funcs.set_default_weekday,
        'help': 'Sets the default weekday for the weekly leaderboard.',
        'help_after': '\nEx: "{0}set default leaderboard weekday Sunday"'.format(vars.properties['prompt'])
    },
    'SET LEADERBOARD TIME': {
        'action': funcs.set_default_time,
        'help': 'Sets the default UTC Time for the weekly leaderboard.',
        'help_after': '\nEx: "{0}set default leaderboard time utc 13:34"'.format(vars.properties['prompt'])
    },
    'FORCE RESTART':{
        'action': funcs.force_restart,
        'help': 'Resets server stored properties and BOT text-channels.',
        'help_after': 'This can be used to fix and restore servers.'
    },
    'FORCE REFRESH':{
        'action': funcs.force_refresh,
        'help': 'Refreshes server BOT text-channels.',
        'help_after': 'This can be used to fix and restore servers.'
    },
    'LEVEL': {
        'action': funcs.level,
        'help': 'Displays your current level and EXP,',
        'help_after': '\nex. "{0}level"'.format(vars.properties['prompt'])
    },
    'BALANCE': {
        'action': funcs.balance,
        'help': 'Displays your currrent amount of {0}'.format(vars.properties['money_symbol']),
        'help_after': '\nex. "{0}balance"'.format(vars.properties['prompt'])
    }
}