from Utils import Utils
from User import User
import datetime
import copy
import json
import os


class Server(object):

    def __init__(self, data, server):
        try:
            path = data.config['directories']['server_data']
        except KeyError:
            path = os.path.join(data.folder, 'ServerData')
        print("Servers path:", path)
        self.data = data
        if path != '':
            self.path = os.path.join(path)
        else:
            self.path = os.path.join(data.folder, 'ServerData')
        self.server_path = os.path.join(self.path, str(server.id))
        self.config_path = os.path.join(self.server_path, 'config.json')
        self.user_path = os.path.join(self.server_path, 'UserData')
        print("Config path:", self.config_path)
        self.config_template = {
            'id': str(server.id),
            'created_at': server.created_at.strftime('%d-%m-%Y_%H-%M-%S-%f'),
            'log_date': Utils.get_until_day_string(),
            'name': {
                'current': '',
                'previous': {}  # datetime:name
            },
            'roles': {
                'current': {},  # Role(id): {name:, permissions:value, colour:, position:, created_at:}
                'previous': {}  # datetime: Roles:{Role,Role,Role}
            },
            'region': {
                'current': '',
                'previous': {}
            },
            'embed_colours': {
                'default': 0,
                'developer': 0,
                'error': 0,
                'help': 0
            },
            'owner': {
                'current': '',
                'previous': {}
            },
            'availability': {
                'current': '',
                'previous': {}
            },
            'member_count': {
                'current': '',
                'previous': {}
            },
            'activity': {},
            'sent_messages': {},  # user_id: [[channel.id, msg.id, post_time, delete_time], [...], [...]]
            'custom_permissions': {},  # role_id: [commands]
            'prefix': data.config['commands']['prefix']
        }
        self.server = server
        self.config = self.load_server()
        self.update()
        self.load_users()

    def update_value(self, value, new_value, time=None):
        if time is None:
            time = Utils.get_full_time_string()
        if value not in self.config:
            self.config[value] = copy.deepcopy(self.config_template[value])
        if 'current' not in self.config[value]:
            self.config[value]['current'] = new_value
            return

        compare = True
        if isinstance(new_value, dict) and isinstance(self.config[value]['current'], dict):
            compare = self.comparer(new_value, self.config[value]['current'])

        if str(self.config[value]['current']) != str(new_value) and compare:
            if str(self.config[value]['current']) != '' \
                    and self.config[value]['current'] != {}:
                if 'previous' in self.config[value]:
                    self.config[value]['previous'].update({time: self.config[value]['current']})
                else:
                    self.config[value]['previous'] = {time: self.config[value]['current']}
            self.config[value]['current'] = new_value

    def comparer(self, dict1, dict2):
        if len(dict1) != len(dict2):
            return True
        for key in dict1:
            if key not in dict2:
                return True
            if dict1[key] is dict and dict2[key] is dict:
                if self.comparer(dict1[key], dict2[key]):
                    return True
            elif dict1[key] is dict and dict2[key] is not dict:
                return True
            else:
                if dict1[key] != dict2[key]:
                    return True
        return False

    def update_activity(self, user, channel):
        time = datetime.datetime.now()
        hour = str(time.hour)
        day = str(time.day)
        month = str(time.month)
        year = str(time.year)

        template = {
            year: {
                month: {
                    day: {
                        hour: {
                            str(channel.id): {
                                'name': channel.name,
                                'users': {
                                    str(user.id): 1  # str(user.id): message_count
                                },
                                'total_messages': 1
                            }
                        }
                    }
                }
            }
        }

        if 'activity' not in self.config:
            self.config['activity'] = template
            return
        template = template[year]
        config = self.config['activity']
        if year not in config:
            config[year] = template
            return
        template = template[month]
        config = config[year]
        if month not in config:
            config[month] = template
            return
        template = template[day]
        config = config[month]
        if day not in config:
            config[day] = template
            return
        template = template[hour]
        config = config[day]
        if hour not in config:
            config[hour] = template
            return
        template = template[str(channel.id)]
        config = config[hour]
        if str(channel.id) not in config:
            config[str(channel.id)] = template
            return
        config = config[str(channel.id)]
        if 'name' not in config:
            config['name'] = channel.name
        if 'total_messages' not in config:
            config['total_messages'] = 1
        else:
            config['total_messages'] = config['total_messages'] + 1
        if 'users' not in config:
            config['users'] = template['users']
        else:
            if str(user.id) not in config['users']:
                config['users'][str(user.id)] = 1
            else:
                config['users'][str(user.id)] = config['users'][str(user.id)] + 1

    def check_name(self): self.update_value('name', self.server.name)

    def check_roles(self):
        roles = {}
        for role in self.server.roles:
            roles[role.id] = {
                'name': role.name, 'permissions': role.permissions.value, 'colour': role.colour.value,
                'position': role.position, 'created_at': role.created_at.strftime('%d-%m-%Y_%H-%M-%S-%f')
            }
        self.update_value('roles', roles, time=Utils.get_until_hour_string())

    def check_region(self): self.update_value('region', str(self.server.region))

    def check_owner(self): self.update_value('owner', self.server.owner.id)

    def check_availability(self): self.update_value('availability', not self.server.unavailable)

    def check_member_count(self):
        self.update_value('member_count', self.server.member_count, time=Utils.get_until_day_string())

    def check_config_values(self):
        self.check_availability()
        if str(self.config['availability']['current']) != 'False':
            self.check_name()
            self.check_roles()
            self.check_region()
            self.check_owner()
            self.check_member_count()

    def update(self):
        self.config = Utils(self.data).update(copy.deepcopy(self.config_template), self.config)
        self.check_config_values()
        self.write_config()

    def write_config(self, conf=None):
        if conf is None:
            conf = self.config
        with open(self.config_path, 'w+')as f:
            json.dump(conf, f, indent=4)
            f.close()

    def load_server(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.exists(self.server_path):
            os.mkdir(self.server_path)
        if not os.path.exists(self.config_path):
            self.write_config(conf=self.config_template)
        try:
            with open(self.config_path, 'r') as f:
                js = json.load(f)
        except ValueError:
            js = copy.deepcopy(self.config_template)

        return js

    def check_paths(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.exists(self.server_path):
            os.mkdir(self.server_path)
        if not os.path.exists(self.user_path):
            os.mkdir(self.user_path)

    def load_user(self, user):
        self.check_paths()
        return User(self.data, self, user)

    def load_users(self):
        if self.server.large:
            self.data.client.request_offline_members(self.server)
        for member in self.server.members:
            self.load_user(member)
