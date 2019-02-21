"""
Data storage class.

Stores, loads and saves various data that the server will be using.
"""
from importlib import import_module, reload
from Server import Server
from Utils import Utils
import zipfile
import inspect
import json
import copy
import sys
import os


class Data(object):
    """Data class that stores all the data required to moderate the server."""

    def __init__(self, client):
        self.client = client
        self.folder = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.folder, 'config.json')
        self.config_template = {
            'login': {
                'user': {
                    'username': '',
                    'password': ''
                },
                'bot': {
                    'token': ''
                },
                'method': 'bot'
            },
            'directories': {
                'events': os.path.join(self.folder, 'EventCalls'),
                'commands': os.path.join(self.folder, 'CommandCalls'),
                'server_data': os.path.join(self.folder, 'ServerData'),
                'backup_data': os.path.join(self.folder, 'BackupData')
            },
            'commands': {
                'use_ai': False,
                'prefix': 'e!'
            }
        }
        self.config = self.get_config()
        print(self.config)

        self.ticker_calls = {}

        if 'commands' in self.config and 'owner' in self.config['commands']:
            self.owner = self.config['commands']['owner']
        else:
            self.owner = 0

        self.event_calls = {
            'message': {},
            'socket_raw_receive': {},
            'socket_raw_send': {},
            'message_delete': {},
            'message_edit': {},
            'reaction_add': {},
            'reaction_remove': {},
            'reaction_clear': {},
            'channel_delete': {},
            'channel_create': {},
            'channel_update': {},
            'member_join': {},
            'member_remove': {},
            'member_update': {},
            'server_join': {},
            'server_remove': {},
            'server_update': {},
            'server_role_create': {},
            'server_role_delete': {},
            'server_role_update': {},
            'server_emojis_update': {},
            'server_available': {},
            'server_unavailable': {},
            'voice_state_update': {},
            'member_ban': {},
            'member_unban': {},
            'typing': {},
            'group_join': {},
            'group_remove': {}
        }

        self.load()  # load events
        self.command_calls = {}
        self.load(mode=1)  # load commands
        self.loaded = False

        self.servers = {}

    def get_config(self):
        """
        Acquire config for for this client.

        :return: json dictionary
        """
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w+') as f:
                json.dump(self.config_template, f, indent=4)
                return copy.deepcopy(self.config_template)
        try:
            with open(self.config_path, 'r+') as f:
                return Utils(self).update(self.config_template, json.load(f))
        except ValueError:
            with open(self.config_path, 'w+') as f:
                json.dump(self.config_template, f, indent=4)
                return copy.deepcopy(self.config_template)

    def load(self, mode=0, _reload=False):
        """
        Load commands or events dynamically.

        :param mode: 0 or 1; 0 - events, 1 - commands
        :param _reload: True or False; whether they're being reloaded or not
        :return: list - list of strings of all the loaded components
        """
        modes = ['event', 'command']
        mode = modes[mode]

        if _reload:
            self.loaded = False

        conf = self.config
        path = ''
        if 'directories' in conf and 'events' in conf['directories']:
            if mode == 'event':
                path = conf['directories']['events']
            else:
                path = conf['directories']['commands']
        else:
            if mode == 'event':
                path = os.path.join(os.getcwd(), 'EventCalls')
            elif mode == 'command':
                path = os.path.join(os.getcwd(), 'CommandCalls')

        if not os.path.exists(path):
            os.mkdir(path)
        init = os.path.join(path, '__init__.py')
        if not os.path.exists(init):
            with open(init, 'w+') as f:
                f.close()

        # make sure that we can load the packages
        folder = os.path.dirname(path)
        sys.path.append(folder)
        package = os.path.basename(path)

        loaded = []
        for file in os.listdir(path):
            if not file.endswith('.py') or file == '__init__.py':
                continue
            name = str(file.split('.')[0])
            package_name = package + '.' + name
            if _reload and package_name in sys.modules:
                del sys.modules[package_name]
                m = __import__(package_name)
                m = reload(m)
                m = getattr(m, name)
            else:
                m = import_module(package_name)
            executor = getattr(m, name)
            exe = executor(self)
            methods = inspect.getmembers(exe, predicate=inspect.ismethod)
            files = []
            for method_name, method in methods:
                if method_name in self.event_calls:
                    self.event_calls[method_name].update({name: exe})
                    files.append('on_' + method_name)
                if mode == 'command':
                    if method_name == 'execute':
                        self.command_calls.update({name: executor})
                if method_name == 'ticker':
                    self.ticker_calls.update({name: exe})
                    files.append(method_name)

            arg = ''
            if mode == 'event':
                arg = 'EventCall'
            elif mode == 'command':
                arg = 'CommandCall'
            loaded.append('Loaded {}: {}; contained events: {}'.format(arg, name, files))
            print('Loaded {}: {}; contained events: {}'.format(arg, name, files))

        return loaded

    def load_server(self, server):
        """
        Load server.

        :param server: discord.server
        :return: Server
        """
        new_server = Server(self, server)
        self.servers[server.id] = new_server
        return new_server

    def load_servers(self):
        """
        Load all servers this client is connected to.

        :return: list - list of strings of connected servers
        """
        servers = []
        self.servers = {}
        for server in self.client.servers:
            self.load_server(server)
            try:
                string = 'Connected to {}:{}'.format(server.name, server.id)
            except AttributeError:
                string = 'Connected to ' + server.id
            servers.append(string)
        return servers

    def backup(self):
        """
        Create backup of servers' data.

        :return: None
        """
        conf = self.config
        dirs = ['backup_data', 'server_data']
        for i, p in enumerate(dirs):
            if 'directories' in conf and p in conf['directories']:
                path = conf['directories'][p]
            else:
                path = os.path.join(os.getcwd(), ''.join(map(str.capitalize, p.split('_'))))

            if not os.path.exists(path):
                os.mkdir(path)
            dirs[i] = path

        c_path = os.path.join(dirs[0], 'ServerData-{}.zip'.format(Utils.get_until_day_string()))
        zip_file = zipfile.ZipFile(c_path, 'w', zipfile.ZIP_DEFLATED)

        def zipper(dir_path, path_name=''):
            """
            Zip function to save files as zip.

            :param dir_path:
            :param path_name:
            :return:
            """
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                write_path = path_name + os.sep + file
                if os.path.isdir(file_path):
                    zipper(file_path, path_name=path_name+os.sep+file)
                else:
                    zip_file.write(file_path, write_path)

        zipper(dirs[1])
        zip_file.close()
