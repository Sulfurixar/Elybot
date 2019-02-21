from Utils import Utils
import datetime
import discord
import json
import copy
import os


class User(object):

    def __init__(self, data, server, user):
        self.user_config_path = os.path.join(server.user_path, '{}.json'.format(user.id))
        self.user = user
        self.server = server
        self.data = data
        self.config_template = {
            'id': user.id,
            'bot': user.bot,
            'created_at': user.created_at.strftime('%d-%m-%Y_%H-%M-%S-%f'),
            'name': {
                'current': '',
                'previous': {}
            },
            'discriminator': {
                'current': '',
                'previous': {}
            },
            'display_name': {
                'current': '',
                'previous': {}
            },
            'roles': {
                'current': {},
                'previous': {}
            },
            'voice': {
                'current': {},
                'previous': {}
            },
            'joined_at': {
                'current': '',
                'previous': {}
            },
            'status': {
                'current': '',
                'previous': {}
            },
            'game': {
                'current': {},
                'previous': {}
            },
            'colour': {
                'current': '',
                'previous': {}
            },
            'bans': {
                'current': 'not banned',
                'previous': {}
            },
            'activity': {}
        }

        self.config = self.load_user()
        self.update()

    def load_user(self):
        if not os.path.exists(self.server.path):
            os.mkdir(self.server.path)
        if not os.path.exists(self.server.server_path):
            os.mkdir(self.server.server_path)
        if not os.path.exists(self.user_config_path):
            self.write_config(conf=self.config_template)
        try:
            with open(self.user_config_path, 'r') as f:
                js = json.load(f)
        except ValueError:
            js = copy.deepcopy(self.config_template)

        return js

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

    def update_activity(self, channel):
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
                            str(channel.id): 1
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
        else:
            config[str(channel.id)] = config[str(channel.id)] + 1

    def check_name(self):
        self.update_value('name', self.user.name)

    def check_display_name(self):
        self.update_value('display_name', self.user.display_name)

    def check_discriminator(self):
        self.update_value('discriminator', self.user.discriminator)

    def check_roles(self):
        roles = {}
        for role in self.user.roles:
            roles[role.id] = {
                'name': role.name, 'permissions': role.permissions.value, 'colour': role.colour.value,
                'position': role.position, 'created_at': role.created_at.strftime('%d-%m-%Y_%H-%M-%S-%f')
            }
        self.update_value('roles', roles)

    def check_voice(self):
        state = {
            'server_deaf': self.user.voice.deaf,
            'server_mute': self.user.voice.mute,
            'self_mute': self.user.voice.self_mute,
            'self_deaf': self.user.voice.self_deaf,
            'is_afk': self.user.voice.is_afk,
        }
        if self.user.voice.voice_channel is not None:
            state['channel'] = {
                'id': self.user.voice.voice_channel.id,
                'name': self.user.voice.voice_channel.name,
                'private': self.user.voice.voice_channel.is_private
            }
        else:
            state['channel'] = {
                'id': None,
                'name': None,
                'private': None
            }
        self.update_value('voice', state)

    def check_joined_at(self):
        self.update_value('joined_at', self.user.joined_at.strftime('%d-%m-%Y_%H-%M-%S-%f'))

    def check_status(self):
        self.update_value('status', str(self.user.status))

    def check_game(self):
        game = {
            'name': None,
            'url': None,
            'type': None
        }
        if self.user.game is not None:
            game = {
                'name': self.user.game.name,
                'url': self.user.game.url,
                'type': self.user.game.type
            }
        self.update_value('game', game)

    def check_colour(self):
        self.update_value('colour', self.user.colour.value)

    def check_config_values(self):
        self.check_name()
        self.check_discriminator()
        self.check_display_name()
        self.check_status()
        self.check_game()
        if str(type(self.user)) == str(discord.member.Member):
            self.check_roles()
            self.check_voice()
            self.check_joined_at()
            self.check_colour()

    def write_config(self, conf=None):
        if conf is None:
            conf = self.config
        with open(self.user_config_path, 'w+')as f:
            json.dump(conf, f, indent=4)
            f.close()

    def update(self):
        Utils(self.data).update(copy.deepcopy(self.config_template), self.config)
        self.check_config_values()
        self.write_config()
