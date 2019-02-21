from Embed import Embed
import progressbar
import traceback
import requests
import datetime
import discord
import shutil
import json
import copy
import sys
import re
import os


class Utils:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def loading_bar(max_val, current_val, pbar=None):

        if pbar is None:
            pbar = progressbar.ProgressBar(
                widgets=[
                    'Test: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='0', left='[', right=']'), ' ',
                    progressbar.ETA(), ' ', progressbar.FileTransferSpeed()
                ],
                maxval=max_val
            )
            pbar.start()
        pbar.update(current_val)
        if current_val == max_val:
            pbar.finish()
        else:
            current_val += 1
        return pbar, current_val

    async def finder(self, server, _id, member=False, channel=False, role=False):
        """
        Member, channel, role finder. Finds whichever you need.

        :param server: discord.Server - server from which we're searching from
        :param _id: string of the object id we're looking for
        :param member: True/False - whether we think it could be a member
        :param channel: True/False - whether we think it could be a channel
        :param role: True/False - whether it could be a role
        :return: member, channel, role - None, None, None if none of them were found, otherwise their respective objects
        """
        if _id.startswith('<@&') or _id.startswith('<@!'):
            _id = _id[3:-1]
        elif _id.startswith('<@') or _id.startswith('<#'):
            _id = _id[2:-1]
        lookup = [[member, None, server.members], [channel, None, server.channels], [role, None, server.roles]]

        for i, looker in enumerate(lookup):
            if looker[0]:
                if i == 0 and server.large:
                    await self.data.client.request_offline_members(server)
                lookup[i][1] = discord.utils.find(lambda m: m.name == _id or str(m.id) == str(_id), looker[2])
        return lookup[0][1], lookup[1][1], lookup[2][1]

    def update(self, template, config):
        assert type(template) == type(config)
        template, config = copy.deepcopy(template), copy.deepcopy(config)
        if isinstance(config, dict):
            for item, value in template.items():
                if item not in config:
                    config[item] = value
                elif isinstance(config[item], dict) or isinstance(config[item], list):
                    config[item] = self.update(template[item], config[item])
        return config

    def permissions(self, user, permission, command, sub_command):
        data = self.data
        if permission == 'bot_owner':
            if user.id == data.owner:
                return True
        if permission == 'server_owner':
            if user.id == data.owner:
                return True
            if user.id == user.server.owner.id:
                return True

        if permission == 'everyone':
            return True

        if permission == 'allowed_user':
            if user.id == data.owner:
                return True
            if user.id == user.server.owner.id:
                return True
            if user.server_permissions.administrator:
                return True
            for role in user.roles:
                if 'custom_permissions' in data.servers[user.server.id].config:
                    if role.id in data.servers[user.server.id].config['custom_permissions']:
                        if '{}:{}'.format(command, sub_command) in \
                                data.servers[user.server.id].config['custom_permissions'][role.id]:
                            return True
            user = data.servers[user.server.id].load_user(user)
            if 'custom_permissions' in user.config:
                if '{}:{}'.format(command, sub_command) in user.config['custom_permissions']:
                    return True

        return False

    @staticmethod
    async def default_help(self, msg, arg=None):
        """
        Provide help for this command.

        :param self: command where this was called (in place of self)
        :param msg: discord.message
        :param arg: string or None
        :return: Help embed
        """
        js = {
            'title': 'Help: ',
            'description': ''
        }

        if arg is None:

            js['title'] = js['title'] + '--{}--'.format(self.aliases[0])
            js['description'] = '**[Aliases]: {}**\n\n**Descriptions:**\n'.format(', '.join(sorted(self.aliases)))
            command_descriptions = []
            for command in sorted(self.command_descriptions):
                if Utils(self.data).permissions(self.user, self.permits[command], self.aliases[0], command):
                    command_descriptions.append({
                        'header': '**{}:**\n'.format(command),
                        'text': 'Permission: {}\n'.format(self.permits[command]) +
                                'Function: {}'.format(self.command_descriptions[command][0])
                    })
            if len(command_descriptions) == 0:
                command_descriptions = [{
                    'header': "This command doesn't take any arguments or you can not access them.",
                    'text': '__   __'
                }]

            js['fields'] = command_descriptions + [
                {
                    'header': 'Syntax:',
                    'text': '<arg> - non-optional argument\n'
                            '<,arg> - optional argument\n'
                            '[arg] - non-optional arguments\n'
                            '[,arg] - optional arguments'
                }
            ]

        else:  # arg is not None

            js['title'] = js['title'] + '--{}[{}]--'.format(self.aliases[0], arg)
            found = True
            if arg not in self.command_descriptions:
                found = False
                for cmd in self.command_descriptions:
                    if arg in self.command_descriptions[cmd][2]:
                        found = True
                        arg = cmd
            if found and not Utils(self.data).permissions(self.user, self.permits[arg], self.aliases[0], arg):
                found = False

            if not found:
                js['description'] = '**{}**\nArgument was not found: ({}).'.format(msg.content, arg)
            else:
                js['fields'] = [{
                    'header': '**{}:**'.format(arg),
                    'text':
                        '**[Aliases]:** {}\n\n'.format(', '.join(sorted(self.command_descriptions[arg][2]))) +
                        "**[Function]:** {}\n\n".format(self.command_descriptions[arg][0]) +
                        "**[Usage]:** {}".format(
                            self.command_descriptions[arg][1]
                            .format(p=self.data.servers[msg.server.id].config['prefix'])
                        )
                }]
        return Embed(self.data, msg, js=js, help=True)

    @staticmethod
    def convert_json_to_fields(js, func=str):
        return [{'header': '{}:'.format(key), 'text': func(value)} for key, value in js.items()]

    @staticmethod
    def find_command(self, command):
        found = True
        if command.lower() not in self.data.command_calls:
            found = False
            for cmd in self.data.command_calls:
                if command.lower() in self.data.command_calls[cmd](self.data).aliases:
                    found = True
                    command = cmd.lower()
        if found and not Utils(self.data).permissions(self.user, self.permits['execute'], self.aliases[0], command):
            found = False
        return found, command

    @staticmethod
    def find_subcommand(self, command):
        found = True
        if command not in self.command_descriptions:
            found = False
            for cmd in self.command_descriptions:
                if command in self.command_descriptions[cmd][2]:
                    found = True
                    command = cmd
        if found and not Utils(self.data).permissions(self.user, self.permits[command], self.aliases[0], command):
            found = False
        return found, command

    def get_channel(self, key, member):
        channel = discord.utils.find(
            lambda m:
            str(m.id) == self.data.servers[member.server.id].config[key]['channel'][0],
            member.server.channels
        )
        if channel is None:
            channel = discord.utils.find(
                lambda m:
                m.name == self.data.servers[member.server.id].config[key]['channel'][1],
                member.server.channels
            )
        return channel

    @staticmethod
    def download_file(js):
        path = os.path.join(os.getcwd(), 'temp_files')
        if not os.path.exists(path):
            os.mkdir(path)
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(js['proxy_url'], stream=True, headers=headers)
        if r.status_code == 200:
            with open(os.path.join(path, js['proxy_url'].split('/')[-1]), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return os.path.join(path, js['proxy_url'].split('/')[-1])

    @staticmethod
    def js_decoder(input_string):

        # convert to a suitable format
        convert_list = ["'"]
        input_list = list(input_string)
        for char in convert_list:
            for match in re.finditer(r"(?<=[{[:,]) *" + char, input_string):
                input_list[match.span()[1] - 1] = '"'
            for match in re.finditer(char + r" *(?=[}\]:,])", input_string):
                input_list[match.span()[0]] = '"'

        # Now let's try converting it to a dictionary!
        try:
            js = json.loads(''.join(input_list))
            return js
        except json.decoder.JSONDecodeError:
            exc_type, exc_value, tb = sys.exc_info()
            traceback.print_tb(tb, limit=20)
            point = int(re.findall(r'\d*(?=\))', str(exc_value))[-2])
            input_string = ''.join(input_list[:point]) + '__**' + ''.join(input_list[point:point + 1]) + '**__' + \
                           ''.join(input_list[point + 1:])
            js = {'title': 'Error!', 'description': input_string + '\n\n' + str(exc_value)}
            return js

    def error_embed(self, msg, error):
        return Embed(
            self.data,
            msg,
            js={'title': 'Error:', 'description': error},
            error=True
        )

    async def delete_messages(self, strength=0):
        for server in self.data.servers.values():
            if len(server.config['sent_messages']) == 0:
                continue
            users = []
            for user, messages in server.config['sent_messages'].items():
                pops = []
                if len(messages) == 0:
                    users.append(user)
                    continue
                for i, message in enumerate(messages):
                    channel, msg, post_time, delete_time = message[0], message[1], message[2], message[3]
                    strengths = [
                        delete_time != -1 and Utils.get_full_time(delete_time) < datetime.datetime.now(),
                        delete_time == -1 or Utils.get_full_time(delete_time) < datetime.datetime.now()
                        ]
                    if strengths[strength]:
                        try:
                            self.data.client.logs_from(
                                server.server.get_channel(channel),
                                around=Utils.get_full_time(post_time).utcnow()
                            )
                            try:
                                sent_message = await self.data.client.get_message(
                                    server.server.get_channel(channel),
                                    msg
                                )
                                await self.data.client.delete_message(sent_message)
                            except Exception as e:
                                if e is discord.HTTPException:
                                    self.data.error()
                        except Exception as e:
                            if e is discord.HTTPException:
                                self.data.error()
                        pops.append(i)
                pops.reverse()
                for _ in pops:
                    self.data.servers[server.server.id].config['sent_messages'][user].pop(-1)
                if len(self.data.servers[server.server.id].config['sent_messages'][user]) == 0:
                    users.append(user)
            for user in users:
                self.data.servers[server.server.id].config['sent_messages'].pop(user)

    @staticmethod
    def get_full_time_string(time=datetime.datetime.now()):
        return time.strftime('%d-%m-%Y_%H-%M-%S-%f')

    @staticmethod
    def get_full_time(string):
        return datetime.datetime.strptime(string, '%d-%m-%Y_%H-%M-%S-%f')

    @staticmethod
    def get_until_day_string(time=datetime.datetime.now()):
        return time.strftime('%d-%m-%Y')

    @staticmethod
    def get_until_day(string):
        return datetime.datetime.strptime(string, '%d-%m-%Y')

    @staticmethod
    def get_until_hour(string):
        return datetime.datetime.strptime(string, '%d-%m-%Y_%H')

    @staticmethod
    def get_until_hour_string(time=datetime.datetime.now()):
        return time.strftime('%d-%m-%Y_%H')

    @staticmethod
    def add_seconds(time, seconds):
        return time + datetime.timedelta(seconds=seconds)
