"""
Elybot discord client.

For server administration and analytics.
Current version: 0.0.1.
Author @Elisiya.
"""
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import CancelledError
from Utils import Utils
from Data import Data
import traceback
import datetime
import inspect  # is actually required for use, but it's in string format in load_client_events()
import discord
import asyncio
import time
import sys


error_buffer = []
client = discord.Client()
data = Data(client)


def load_client_events():
    """
    Load client related events dynamically.

    :return:
    """
    for ev in data.event_calls:
        def create_func():
            """
            Create function that is to be stored inside client.
            :return:
            """
            exec(
                "async def on_{e}(*args):\n\t"
                "event = '{e}'\n\t"
                "if data.loaded:\n\t\t"
                "for ev in data.event_calls[event]:\n\t\t\t"
                "executor = data.event_calls[event][ev]\n\t\t\t"
                "s = inspect.getmembers(executor, predicate=inspect.ismethod)\n\t\t\t"
                "for name, method in s:\n\t\t\t\t"
                "if name == event:\n\t\t\t\t\t"
                "await method(args)".format(e=ev))
            return eval("on_{}".format(ev))

        setattr(data.client, 'on_{}'.format(ev), create_func())


def error():
    """
    Limit reoccurring errors to one. Print new errors.

    :return:
    """
    exc_type, exc_value, tb = sys.exc_info()
    if len(error_buffer) > 0:
        if error_buffer[-1] != exc_type:
            error_buffer.append(exc_type)
            traceback.print_tb(tb, limit=20)
            print(exc_value)
            print(type(exc_value).__name__)
    else:
        error_buffer.append(exc_type)
        traceback.print_tb(tb, limit=20)
        print(exc_value)
        print(type(exc_value).__name__)
    if len(error_buffer) > 10:
        error_buffer.pop(0)


def execute():
    """
    Execute coroutines for client.

    :return:
    """
    # executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    try:
        tasks = [asyncio.Task(login()), asyncio.Task(ticker())]
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as ex:
        print(ex)
        error()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.stop()

        loop.run_forever()  # run_forever() returns after calling loop.stop()
        tasks = asyncio.Task.all_tasks()
        for t in [t for t in tasks if not (t.done() or t.cancelled())]:
            loop.run_until_complete(t)
    finally:
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())
        global data
        data = Data(client)


@client.event
async def on_ready():
    data.error = error
    data.loaded = True
    data.load_client_events = load_client_events
    data.load_client_events()
    servers = data.load_servers()
    print('\n'.join(servers))


async def login():
    """
    Check config for required fields for bot to login and then connect to discord server.

    :return:
    """
    if 'login' not in data.config:
        print("Config missing 'login' section. Delete the config and configure it from the start.")
        return
    if 'method' not in data.config['login']:
        print("Config missing 'method' in 'login'. Delete the config and configure it from the start.")
        return
    method = data.config['login']['method']
    if method == '':
        print("'method' in 'login' is set to ''. Allowed values: bot | user")
        return
    if method not in data.config['login']:
        print("Config missing '{}' in 'login'. Delete the config and configure it from start.".format(method))
        return
    user = data.config['login'][method]
    if method == 'user':
        if 'username' not in user:
            print("Config missing 'username' in 'user' in 'login' in config.")
            return
        username = user['username']
        if username == '':
            print("'username' in 'user' in 'login' is set to ''.")
            return
        if 'password' not in user:
            print("Config missing 'password' in 'user' in 'login' in config.")
            return
        password = user['password']
        if password == '':
            print("'password' in 'user' in 'login' is set to ''.")
            return
        print('Connecting...')
        await client.login(username, password)
    elif method == 'bot':
        if 'token' not in user:
            print("Config missing 'token' in 'bot' in 'login' in config.")
            return
        token = user['token']
        if token == '':
            print("'token' in 'bot' in 'login' is set to ''.")
            return
        print('Connecting...')
        await client.login(token)
    else:
        print("Invalid value for 'method' in 'login'. Allowed values: bot | user")
        return
    await client.connect()


async def ticker():
    """
    Run events after some time has passed.

    :return:
    """
    t = 0
    last_day = datetime.datetime.now().day
    while run:
        if t == 0:
            try:
                if data.loaded:

                    # check if we need to do a backup of our server data
                    if datetime.datetime.now().day != last_day:
                        last_day = datetime.datetime.now().day
                        data.backup()

                    await Utils(data).delete_messages(strength=1)

                    for ticker_call in data.ticker_calls.values():
                        await ticker_call.ticker()

                    # await for the next hour
                    last = datetime.datetime.now()
                    t = 3600 - last.minute * 60 - last.second
            except Exception as ex:
                print(type(ex).__name__)
                error()
        else:
            await Utils(data).delete_messages()

            t -= 1
        await asyncio.sleep(1)

run = True
while run:
    try:
        execute()
    except KeyboardInterrupt:
        run = False
    except CancelledError:
        time.sleep(10)
    except Exception as e:
        print(e)
        error()
        time.sleep(10)
