from flask import Flask
from flask import request
import funcs
import json
import vars
from threading import Thread

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/api/v1.0/reward', methods=['POST'])
def reward():
    discord_id = request.form.get('discord_id')
    server_id = request.form.get('server_id')
    _type = request.form.get('type')
    value = request.form.get('value')

    # Error Catching
    if discord_id == None or _type == None or value == None or server_id == None:
        return "Unsuccessful; invalid parameters."
    elif _type != "exp" and _type != "money" and _type != 'both':
        return "Unsuccessful; Type given does not exist!"
    else:

        if _type == 'both':
            values = None

            try:
                values = json.loads(value)
            except Exception:
                return "Unsuccessful; Values given in an incorrect format!"
            else:
                vars.client.loop.create_task(funcs.reward(discord_id, 'money', values[1], server_id))
                vars.client.loop.create_task(funcs.reward(discord_id, 'exp', values[0], server_id))
        else:
            vars.client.loop.create_task(funcs.reward(discord_id, _type, value, server_id))

        return "Success!"


@app.route('/api/v1.0/achievement', methods=['POST'])
def achievement():
    # Achievement Structure:
    """
    {
        name: "achievement_name"
        description: "description"
    }
    """

    discord_id = request.form.get('discord_id')
    _achievement = request.form.get('achievement')
    server_id = request.form.get('server_id')
    _type = request.form.get('type')
    value = request.form.get('value')

    # Error Catching
    if discord_id == None or _type == None or value == None or achievement == None or server_id == None:
        return "Unsuccessful; invalid parameters."
    elif _type != "exp" and _type != "money" and _type != 'both':
        return "Unsuccessful; Type given does not exist!"
    else:
        vars.client.loop.create_task(funcs.achievement(discord_id, _achievement, server_id))

        if _type == 'both':
            values = None

            try:
                values = json.loads(value)
            except Exception:
                return "Unsuccessful; Values given in an incorrect format!"
            else:
                vars.client.loop.create_task(funcs.reward(discord_id, 'money', values[1], server_id))
                vars.client.loop.create_task(funcs.reward(discord_id, 'exp', values[0], server_id))

        else:
            vars.client.loop.create_task(funcs.reward(discord_id, _type, value, server_id))

        return "Success!"


@app.route('/api/v1.0/action', methods=['POST'])
def action():
    discord_id = request.form.get('discord_id')
    _message = request.form.get('message')
    link = request.form.get('link')

    # Error Catching
    if discord_id == None or _message == None or link == None:
        return "Unsuccessful; invalid parameters."
    else:
        vars.client.loop.create_task(funcs.action(discord_id, _message, link))
        return "Success!"


@app.route('/api/v1.0/notification', methods=['POST'])
def notification():
    discord_id = request.form.get('discord_id')
    _message = request.form.get('message')
    link = request.form.get('link')
    timestamp = request.form.get('timestamp')


    if link == None:
        link = ''

    # Error Catching
    if discord_id == None or _message == None or timestamp == None:
        return "Unsuccessful; invalid parameters."
    else:
        vars.client.loop.create_task(funcs.notification(discord_id, _message, link, timestamp))
        return "Success!"


@app.route('/api/v1.0/message', methods=['POST'])
def message():
    target = request.form.get('target')
    _message = request.form.get('message')
    target_type = request.form.get('target_type')
    link = request.form.get('link')

    if link == None:
        link = ''

    # Error Catching
    if _message == None or target_type == None:
        return "Unsuccessful; invalid parameters."
    elif target_type != 'dm_all' and target_type != 'dm_single' and target_type != 'server_single' and target_type != 'server_all':
        return "Unsuccessful' invalid target type!"
    else:
        vars.client.loop.create_task(funcs.message(target, _message, target_type, link))
        return "Success!"


def run():
    app.run(host=vars.properties['host'], port=vars.properties['port'])


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()
