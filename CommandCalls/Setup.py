from types import MethodType  # actually used in auto_generate_commands
from Utils import Utils
from Embed import Embed
from Command import Command
import datetime
import time
import copy


class Setup(Command):
    """
    Setup command.

    Used to set up various command related things on a server.
    All argument outputs are embeds.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['setup', 's']
        self.permits = {
            'execute': 'allowed_user',
            'help': 'allowed_user',
            'set_message_edit_channel': 'allowed_user',
            'get_message_edit_channel': 'allowed_user',
            'toggle_message_edit_logging': 'allowed_user',
            'set_message_delete_channel': 'allowed_user',
            'get_message_delete_channel': 'allowed_user',
            'toggle_message_delete_logging': 'allowed_user',
            'set_member_join_channel': 'allowed_user',
            'get_member_join_channel': 'allowed_user',
            'toggle_member_join_logging': 'allowed_user',
            'set_member_leave_channel': 'allowed_user',
            'get_member_leave_channel': 'allowed_user',
            'toggle_member_leave_logging': 'allowed_user',
            'set_command_use_channel': 'allowed_user',
            'get_command_use_channel': 'allowed_user',
            'toggle_command_use_logging': 'allowed_user',
            'get_custom_permissions': 'allowed_user',
            'add_custom_permission': 'allowed_user',
            'remove_custom_permission': 'allowed_user',
            'get_custom_permission': 'allowed_user',
            'set_bot_prefix': 'bot_owner',
            'add_join_role': 'allowed_user',
            'remove_join_role': 'allowed_user'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'add_custom_permission': [
                'Adds custom permissions for this server.'
                'Note that not all commands have ``allowed_user`` permission.',
                "``{{p}}{} add_custom_permission <role, user> [command, command:sub_command]``\n"
                    .format(self.aliases[0]) +
                "Example: ``{{p}}{} add_custom_permission @everyone setup setup:help setup:set_message_delete_channel``"
                    .format(self.aliases[0]),
                ['acp', 'ap']
            ],
            'remove_custom_permission': [
                'Removes custom permissions for this server.'
                'Note that not all commands have ``allowed_user`` permission.',
                "``{{p}}{} remove_custom_permission <role, user> [command, command:sub_command]``\n"
                    .format(self.aliases[0]) +
                "Example: ``{{p}}{} remove_custom_permission @everyone setup setup:help "
                "setup:set_message_delete_channel``"
                    .format(self.aliases[0]),
                ['rcp', 'rp']
            ],
            'get_custom_permission': [
                'Gets custom permissions for this server.',
                "``{{p}}{} get_custom_permission <role, user>``\n"
                    .format(self.aliases[0]) +
                "Example: ``{{p}}{} get_custom_permission @everyone``"
                    .format(self.aliases[0]),
                ['gcp', 'gp']
            ],
            'set_bot_prefix': [
                "Sets the prefix for this bot on this server.",
                "``{{p}}{} set_bot_prefix <prefix>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} set_bot_prefix s!``".format(self.aliases[0]),
                ['sbp', 'sp']
            ],
            'add_join_role': [
                "Adds the role given to users when they join the server.",
                "``{{p}}{} add_join_role <role>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} add_join_role @Member``".format(self.aliases[0]),
                ['ajr', 'ar']
            ],
            'remove_join_role': [
                "Removes the role given to users when they join the server.",
                "``{{p}}{} remove_join_role <role>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} remove_join_role @Member``".format(self.aliases[0]),
                ['rjr', 'rr']
            ]
        }
        self.auto_generate_commands()

    def auto_generate_commands(self):
        """
        Generate commands for this command automatically given a specified template.

        :return:
        """
        cmds = [
            'set_message_edit_channel',
            'set_message_delete_channel',
            'set_member_join_channel',
            'set_member_leave_channel',
            'set_command_use_channel'
        ]

        for cmd in cmds:
            initials = []
            for word in cmd.split('_'):
                initials.append(word[0])
            self.command_descriptions.update({
                cmd: [
                    "{} the {}. When a user {}s, it will be reported there.".format(
                        cmd.split('_')[0].capitalize(), ' '.join(cmd.split('_')[1:]), cmd.split('_')[2]
                    ),
                    "``{{p}}{} {} <channel>``\n".format(self.aliases[0], cmd) +
                    "Example1: ``{{p}}{} {} #general``\n".format(self.aliases[0], cmd) +
                    "Example2: ``{{p}}{} {} general``\n".format(self.aliases[0], cmd) +
                    "Example3: ``{{p}}{} {} 403243509324447755``".format(self.aliases[0], cmd),
                    [''.join(initials), ''.join([initials[0]] + initials[-2:])]
                ]
            })

            exec(
                "async def {}(self, msg, arg):\n\t".format(cmd) +
                "key = '{}_logging'\n\t".format('_'.join(cmd.split('_')[1:-1])) +
                "if arg.startswith('<#'):\n\t\t"
                "arg = arg[2:-1]\n\t"
                "channel = (await Utils(self.data).finder(msg.server, arg, channel=True))[1]\n\t"
                "if channel is None:\n\t\t"
                "return Utils(self.data).error_embed(msg, 'Could not find specified channel: ({})'.format(arg))\n\t"
                "if key not in self.data.servers[msg.server.id].config:\n\t\t"
                "self.data.servers[msg.server.id].config[key] = {"
                "'enabled': False,"
                "'channel': [channel.id, channel.name]"
                "}\n\t"
                "else:\n\t\t"
                "self.data.servers[msg.server.id].config[key].update("
                "{'channel': [channel.id, channel.name]}"
                ")\n\t\t"
                "self.data.servers[msg.server.id].write_config()\n\t"
                "return Embed(self.data, msg, js={" +
                "'title': '{}:',".format(' '.join(cmd.split('_')).capitalize()) +
                "'description': str(self.data.servers[msg.server.id].config[key])"
                "})\n" +
                "self.{} = MethodType({}, self)".format(cmd, cmd)
            )

        cmds = [
            'toggle_member_leave_logging',
            'toggle_member_join_logging',
            'toggle_message_delete_logging',
            'toggle_message_edit_logging',
            'toggle_command_use_logging'
        ]

        for cmd in cmds:
            initials = []
            for word in cmd.split('_'):
                initials.append(word[0])
            self.command_descriptions.update({
                cmd: [
                    "{} the {}.".format(
                        cmd.split('_')[0].capitalize(), ' '.join(cmd.split('_')[1:])
                    ),
                    "``{{p}}{} {} <,1,0,True,False,true,false>``\n".format(self.aliases[0], cmd) +
                    "Example1: ``{{p}}{} {}``\n".format(self.aliases[0], cmd) +
                    "Example2: ``{{p}}{} {} True``\n".format(self.aliases[0], cmd),
                    [''.join(initials), ''.join([initials[0]] + initials[-2:])]
                ]
            })

            exec(
                "async def {}(self, msg, arg=None):\n\t".format(cmd) +
                "key = '{}_logging'\n\t".format('_'.join(cmd.split('_')[1:-1])) +
                "if key not in self.data.servers[msg.server.id].config:\n\t\t"
                "self.data.servers[msg.server.id].config[key] = {"
                "'enabled': False,"
                "'channel': None"
                "}\n\t"
                "if arg is None:\n\t\t"
                "if self.data.servers[msg.server.id].config[key]['enabled']:\n\t\t\t"
                "arg = False\n\t\t"
                "else:\n\t\t\t"
                "arg = True\n\t"
                "else:\n\t\t"
                "if arg.lower() in [0, 'false']:\n\t\t\t"
                "arg = False\n\t\t"
                "elif arg.lower() in [1, 'true']:\n\t\t\t"
                "arg = True\n\t\t"
                "else:\n\t\t\t"
                "return Utils(self.data).error_embed(msg,"
                "'**{}**\\nInvalid argument: ({})'.format(msg.content, arg))\n\t"
                "self.data.servers[msg.server.id].config[key]['enabled'] = arg\n\t"
                "self.data.servers[msg.server.id].write_config()\n\t"
                "return Embed(self.data, msg, js={" +
                "'title': '{}:',".format(' '.join(cmd.split('_')).capitalize()) +
                "'description': str(self.data.servers[msg.server.id].config[key])"
                "})\n" +
                "self.{} = MethodType({}, self)".format(cmd, cmd)
            )

        cmds = [
            'get_member_leave_channel',
            'get_member_join_channel',
            'get_message_delete_channel',
            'get_message_edit_channel',
            'get_command_use_channel'
        ]

        for cmd in cmds:
            initials = []
            for word in cmd.split('_'):
                initials.append(word[0])
            self.command_descriptions.update({
                cmd: [
                    "{} the {}.".format(
                        cmd.split('_')[0].capitalize(), ' '.join(cmd.split('_')[1:])
                    ),
                    "``{{p}}{} {}``\n".format(self.aliases[0], cmd),
                    [''.join(initials), ''.join([initials[0]] + initials[-2:])]
                ]
            })

            exec(
                "async def {}(self, msg):\n\t".format(cmd) +
                "key = '{}_logging'\n\t".format('_'.join(cmd.split('_')[1:-1])) +
                "if key not in self.data.servers[msg.server.id].config:\n\t\t"
                "self.data.servers[msg.server.id].config[key] = {}\n\t"
                "return Embed(self.data, msg, js={" +
                "'title': '{}:',".format(' '.join(cmd.split('_')).capitalize()) +
                "'description': '__   __',"
                "'fields': Utils.convert_json_to_fields(self.data.servers[msg.server.id].config[key])"
                "})\n" +
                "self.{} = MethodType({}, self)".format(cmd, cmd)
            )

    def check_logging(self, key, member):
        """
        Check if we're supposed to log this.

        :param key: string - type of logging
        :param member: discord.Member - user who sent the message
        :return:
        """
        if member == self.data.client.user:
            return False, None

        if key not in self.data.servers[member.server.id].config:
            self.data.servers[member.server.id].config[key] = {
                'enabled': False,
                'channel': None
            }
        if not self.data.servers[member.server.id].config[key]['enabled']:
            return False, None
        if self.data.servers[member.server.id].config[key]['channel'] is None:
            return False, None
        channel = Utils(self.data).get_channel(key, member)
        return True, channel

    async def send_message_data(self, msg, attachments, channel):
        """
        Send all the data acquired from a discord.Message to a specified channel.

        :param msg: discord.Message
        :param attachments: list - list of dictionaries
        :param channel: discord.Channel
        :return:
        """
        # send message
        if msg.content is not None and msg.content != '':
            await self.data.client.send_message(channel, msg.content)

        # send attachment
        if len(attachments) > 0:
            for attachment in attachments:
                await self.data.client.send_file(channel, attachment)

        # send embeds
        if len(msg.embeds) > 0:
            for embed in msg.embeds:
                if embed['type'] != 'image' or embed['type'] != 'video':
                    pass
                else:
                    await self.data.client.send_message(channel, '', embed=embed)

    async def message(self, msg):
        """
        Discord.Client.on_message().

        :param msg: discord.Message
        :return:
        """
        msg, = msg

        # command logging

        if not msg.content.startswith(self.data.servers[msg.server.id].config['prefix']):
            return

        key = 'command_use_logging'

        go, channel = self.check_logging(key, msg.author)
        if channel is None or not go:
            return
        self.data.servers[msg.server.id].config[key]['channel'] = [channel.id, channel.name]

        embed = Embed(self.data, msg, js={
            'title': 'Detected command use by: {}:<@{}>.'.format(msg.author.id, msg.author.id),
            'description': 'user: {}:<@{}>\nchannel: {}:<#{}>\ndate: {}; {}\n\nCommand: {}'.format(
                msg.author.id, msg.author.id,
                msg.channel.id, msg.channel.id,
                Utils.get_full_time_string(datetime.datetime.now()), time.tzname[time.daylight],
                '``{}``'.format(msg.content)
            )
        })

        # send alert embed
        await self.data.client.send_message(channel, '', embed=embed.embed)
        #

    async def message_edit(self, tup):
        """
        Discord.Client.on_message_edit().

        :param tup: (discord.Message, discord.Message)
        :return:
        """
        before, after = tup

        if before.content == after.content and before.attachments == after.attachments and \
                before.embeds == after.embeds:
            return

        if before.content.startswith(self.data.servers[before.server.id].config['prefix']):
            return

        key = 'message_edit_logging'
        go, channel = self.check_logging(key, before.author)
        if channel is None or not go:
            return
        self.data.servers[before.server.id].config[key]['channel'] = [channel.id, channel.name]
        self.data.servers[before.server.id].write_config()

        # prepare first embed
        embed = Embed(self.data, before, js={
            'title': 'Detected message edit by: {}:<@{}>.'.format(before.author.id, before.author.id),
            'description': 'user: {}:<@{}>\nchannel: {}:<#{}>\ndate: {}; {}'.format(
                before.author.id, before.author.id,
                before.channel.id, before.channel.id,
                Utils.get_full_time_string(datetime.datetime.now()), time.tzname[time.daylight]
            )
        })
        #

        # download attachments before alerting
        before_attachments = []
        if len(before.attachments) > 0:
            for attachment in before.attachments:
                attachment = Utils.download_file(attachment)
                before_attachments.append(attachment)
        after_attachments = []
        if len(after.attachments) > 0:
            for attachment in after.attachments:
                attachment = Utils.download_file(attachment)
                after_attachments.append(attachment)

        #

        # send alert embed
        await self.data.client.send_message(channel, '', embed=embed.embed)
        #

        await self.send_message_data(before, before_attachments, channel)

        # send pause
        await self.data.client.send_message(channel, '----====----')

        await self.send_message_data(after, after_attachments, channel)

    async def message_delete(self, msg):
        """
        Discord.Client.on_message_delete().

        :param msg: discord.Message
        :return:
        """
        msg, = msg

        if msg.content.startswith(self.data.servers[msg.server.id].config['prefix']):
            return

        key = 'message_delete_logging'
        go, channel = self.check_logging(key, msg.author)
        if channel is None or not go:
            return

        self.data.servers[msg.server.id].config[key]['channel'] = [channel.id, channel.name]
        self.data.servers[msg.server.id].write_config()

        embed = Embed(self.data, msg, js={
            'title': 'Detected message deletion:',
            'description': 'user: {}:<@{}>\nchannel: {}:<#{}>\ndate: {}; {}'.format(
                msg.author.id, msg.author.id,
                msg.channel.id, msg.channel.id,
                Utils.get_full_time_string(datetime.datetime.now()), time.tzname[time.daylight]
            )
        })
        attachments = []
        if len(msg.attachments) > 0:
            for attachment in msg.attachments:
                attachment = Utils.download_file(attachment)
                attachments.append(attachment)

        await self.data.client.send_message(channel, '', embed=embed.embed)

        await self.send_message_data(msg, attachments, channel)

    async def member_join(self, member):
        """
        Discord.Client.on_member_join().

        :param member: discord.Member
        :return:
        """
        member, = member
        print("member join detected")

        key = 'member_join_logging'
        go, channel = self.check_logging(key, member)

        if 'join_roles' not in self.data.servers[member.server.id].config:
            print('no join roles')
            self.data.servers[member.server.id].config['join_roles'] = []
            self.data.servers[member.server.id].write_config()
        roles = []
        for role in self.data.servers[member.server.id].config['join_roles']:
            # [{'name': role.name, 'id': role.id}]
            role = (await Utils(self.data).finder(member.server, role["id"], role=True))[2]
            if role is None:
                continue
            roles.append(role)
        if len(roles) > 0:
            await self.data.client.add_roles(member, *(tuple(roles)))

        if channel is None or not go:
            return

        self.data.servers[member.server.id].config[key]['channel'] = [channel.id, channel.name]
        self.data.servers[member.server.id].write_config()

        embed = Embed(self.data, member, js={
            'title': 'Detected member join:',
            'description': 'user: {}:<@{}>\ndate: {}; {}'.format(
                member.id, member.id,
                Utils.get_full_time_string(datetime.datetime.now()), time.tzname[time.daylight]
            )
        })

        await self.data.client.send_message(channel, '', embed=embed.embed)

    async def member_remove(self, member):
        """
        Discord.Client.on_member_remove().

        :param member: discord.Member
        :return:
        """
        member, = member

        key = 'member_leave_logging'
        go, channel = self.check_logging(key, member)
        if channel is None or not go:
            return

        self.data.servers[member.server.id].config[key]['channel'] = [channel.id, channel.name]
        self.data.servers[member.server.id].write_config()

        embed = Embed(self.data, member, js={
            'title': 'Detected member leave:',
            'description': 'user: {}:<@{}>\ndate: {}; {}'.format(
                member.id, member.id,
                Utils.get_full_time_string(datetime.datetime.now()), time.tzname[time.daylight]
            )
        })
        await self.data.client.send_message(channel, '', embed=embed.embed)

    def check_args(self, args, msg):
        """
        Check that specified permissions exist.

        :param args: list - list of strings
        :param msg: discord.Message
        :return:
        """
        checked_args = []
        for arg in args:
            if ':' in arg:
                arg = arg.split(':')
                found, arg[0] = Utils.find_command(self, arg[0])
                if not found:
                    return self.arg_not_found(msg, arg[0]), checked_args
                cmd = None
                for cmd in self.data.command_calls:
                    if cmd.lower() == arg[0]:
                        break
                command = self.data.command_calls[cmd](self.data)
                command.user = self.user
                found, arg[1] = Utils.find_subcommand(command, arg[1])
                if not found:
                    return self.arg_not_found(msg, arg[1]), checked_args
                arg = ':'.join(arg)
            else:
                found, arg = Utils.find_command(self, arg)
                if not found:
                    return self.arg_not_found(msg, arg[0]), checked_args
                arg = arg + ':execute'

            checked_args.append(arg)
        return None, checked_args

    async def get_custom_permission(self, msg, arg):
        """
        Get current custom permissions for a server.

        :param msg: discord.Message
        :param arg: string - user or role
        :return:
        """
        user, channel, role = await Utils(self.data).finder(msg.server, arg, role=True, member=True)
        if role is None and user is None:
            return Utils(self.data).error_embed(msg, 'Could not find specified user or role: ({})'.format(arg))

        if role is not None:
            who = role
            if 'custom_permissions' not in self.data.servers[msg.server.id].config:
                self.data.servers[msg.server.id].config['custom_permissions'] = {}
            if role.id not in self.data.servers[msg.server.id].config['custom_permissions']:
                self.data.servers[msg.server.id].config['custom_permissions'][role.id] = []
            current_permissions = self.data.servers[msg.server.id].config['custom_permissions'][role.id]
        else:
            who = user
            user_class = self.data.servers[msg.server.id].load_user(user)
            if 'custom_permissions' not in user_class.config:
                user_class.config['custom_permissions'] = []
            current_permissions = user_class.config['custom_permissions']

        return Embed(self.data, msg, js={
            'title': 'Get custom permission:',
            'description': '**From:** {}:{} - {}\n\n'.format(who.name, who.id, who.mention) +
                           '**Current permissions:** {}'.format(', '.join(current_permissions))
        })

    async def add_custom_permission(self, msg, args):
        """
        Add custom permissions for user or role.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        self.user = msg.author

        full_id = args[0]
        args = args[1:]

        user, channel, role = await Utils(self.data).finder(msg.server, full_id, role=True, member=True)

        if role is None and user is None:
            return Utils(self.data).error_embed(msg, 'Could not find specified user or role: ({})'.format(full_id))

        # SUCCESS! we found the channel/user

        # check that all given commands are legal

        error, checked_args = self.check_args(args, msg)

        if error is not None:
            return error

        if role is not None:
            who = role
            if 'custom_permissions' not in self.data.servers[msg.server.id].config:
                self.data.servers[msg.server.id].config['custom_permissions'] = {}
            if role.id not in self.data.servers[msg.server.id].config['custom_permissions']:
                self.data.servers[msg.server.id].config['custom_permissions'][role.id] = []
            args_to_add = []
            current_permissions = self.data.servers[msg.server.id].config['custom_permissions'][role.id]
            old_perms = copy.deepcopy(current_permissions)
            for arg in checked_args:
                if arg not in current_permissions:
                    args_to_add.append(arg)
            current_permissions = current_permissions + args_to_add
            self.data.servers[msg.server.id].config['custom_permissions'][role.id] = current_permissions
        else:
            who = user
            user_class = self.data.servers[msg.server.id].load_user(user)
            if 'custom_permissions' not in user_class.config:
                user_class.config['custom_permissions'] = []
            args_to_add = []
            current_permissions = user_class.config['custom_permissions']
            old_perms = copy.deepcopy(current_permissions)
            for arg in checked_args:
                if arg not in current_permissions:
                    args_to_add.append(arg)
            current_permissions = current_permissions + args_to_add
            user_class.config['custom_permissions'] = current_permissions
            user_class.write_config()

        self.data.servers[msg.server.id].write_config()

        return Embed(self.data, msg, js={
            'title': 'Add custom permission:',
            'description': '**To:** {}:{} - {}\n\n'.format(who.name, who.id, who.mention) +
                           '**Old permissions:** {}\n\n'.format(', '.join(old_perms)) +
                           '**Permissions to add:** {}\n\n'.format(', '.join(args_to_add)) +
                           '**New permissions:** {}'.format(', '.join(current_permissions))
        })

    async def remove_custom_permission(self, msg, args):
        """
        Remove custom permission from user or role.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        full_id = args[0]
        args = args[1:]

        user, channel, role = await Utils(self.data).finder(msg.server, full_id, role=True, member=True)

        if role is None and user is None:
            return Utils(self.data).error_embed(msg, 'Could not find specified user or role: ({})'.format(full_id))

        # SUCCESS! we found the channel/user

        # check that all given commands are legal

        error, checked_args = self.check_args(args, msg)

        if error is not None:
            return error

        if role is not None:
            who = role
            if 'custom_permissions' not in self.data.servers[msg.server.id].config:
                self.data.servers[msg.server.id].config['custom_permissions'] = {}
            if role.id not in self.data.servers[msg.server.id].config['custom_permissions']:
                self.data.servers[msg.server.id].config['custom_permissions'][role.id] = []
            args_to_rem = []
            current_permissions = self.data.servers[msg.server.id].config['custom_permissions'][role.id]
            old_perms = copy.deepcopy(current_permissions)
            for arg in checked_args:
                if arg in current_permissions:
                    args_to_rem.append(arg)
                    current_permissions.remove(arg)
            self.data.servers[msg.server.id].config['custom_permissions'][role.id] = current_permissions
        else:
            who = user
            user_class = self.data.servers[msg.server.id].load_user(user)
            if 'custom_permissions' not in user_class.config:
                user_class.config['custom_permissions'] = []
            args_to_rem = []
            current_permissions = user_class.config['custom_permissions']
            old_perms = copy.deepcopy(current_permissions)
            for arg in checked_args:
                if arg in current_permissions:
                    args_to_rem.append(arg)
                    current_permissions.remove(arg)
            user_class.config['custom_permissions'] = current_permissions
            user_class.write_config()

        self.data.servers[msg.server.id].write_config()

        return Embed(self.data, msg, js={
            'title': 'Remove custom permission:',
            'description': '**From:** {}:{} - {}\n\n'.format(who.name, who.id, who.mention) +
                           '**Old permissions:** {}\n\n'.format(', '.join(old_perms)) +
                           '**Permissions to remove:** {}\n\n'.format(', '.join(args_to_rem)) +
                           '**New permissions:** {}'.format(', '.join(current_permissions))
        })

    async def set_bot_prefix(self, msg, arg):
        """
        Set a new prefix for the bot on a server.

        :param msg: discord.Message
        :param arg: string - new prefix
        :return:
        """
        self.data.servers[msg.server.id].config['prefix'] = arg
        self.data.servers[msg.server.id].write_config()
        self.data.load(mode=1, _reload=True)
        self.data.loaded = True
        return Embed(
            self.data, msg,
            js={
                'title': 'Set bot prefix:',
                'description': 'Set bot prefix to: ``{}``'.format(
                    self.data.servers[msg.server.id].config['prefix']
                )
            }
        )

    async def add_join_role(self, msg, arg):
        """
        Set a role that is given for every user when they join a server.

        :param msg:
        :param arg: role id or name
        :return:
        """

        role = (await Utils(self.data).finder(msg.server, arg, role=True))[2]
        if role is None:
            return Utils(self.data).error_embed(msg, 'Could not find specified role: ({})'.format(arg))

        if 'join_roles' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['join_roles'] = []

        f = list(filter(lambda r: r['id'] == role.id, self.data.servers[msg.server.id].config['join_roles']))
        if len(f) == 0:
            self.data.servers[msg.server.id].config['join_roles'].append({'name': role.name, 'id': role.id})
            self.data.servers[msg.server.id].write_config()

        return Embed(
            self.data, msg,
            js={
                'title': 'Set bot join role:',
                'description': 'Set bot join role to: ``{}``'.format(
                    self.data.servers[msg.server.id].config['join_roles']
                )
            }
        )

    async def remove_join_role(self, msg, arg):
        """
        Set a role that is given for every user when they join a server.

        :param msg:
        :param arg: role id or name
        :return:
        """

        role = (await Utils(self.data).finder(msg.server, arg, role=True))[2]
        if role is None:
            return Utils(self.data).error_embed(msg, 'Could not find specified role: ({})'.format(arg))

        if 'join_roles' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['join_roles'] = []

        f = list(filter(lambda r: r['id'] == role.id, self.data.servers[msg.server.id].config['join_roles']))
        if len(f) > 0:
            self.data.servers[msg.server.id].config['join_roles'].remove(f[0])
            self.data.servers[msg.server.id].write_config()

        return Embed(
            self.data, msg,
            js={
                'title': 'Set bot join role:',
                'description': 'Set bot join role to: ``{}``'.format(
                    self.data.servers[msg.server.id].config['join_roles']
                )
            }
        )

    async def command_recognizer(self, msg, args):
        """
        Command recognizing loop.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        commands = []
        skip = 0
        for i, arg in enumerate(args):
            if skip:
                skip -= 1
                continue

            found, arg = Utils.find_subcommand(self, arg)

            if found:

                if arg == 'help':
                    if len(args) > i + 1:
                        commands.append((
                            msg.channel, '', (await Utils(self.data).default_help(self, msg, arg=args[i + 1])), -1
                        ))
                        skip += 1
                    else:
                        commands.append((msg.channel, '', (await Utils(self.data).default_help(self, msg)), -1))
                elif arg == 'toggle_message_edit_logging' or arg == 'toggle_message_delete_logging' or \
                        arg == 'toggle_member_join_logging' or arg == 'toggle_member_leave_logging' or \
                        arg == 'toggle_command_use_logging':
                    if len(args) > i + 1:
                        commands.append((
                            msg.channel, '', (await eval('self.{}(msg, args[i+1])'.format(arg))), -1
                        ))
                        skip += 1
                    else:
                        commands.append((
                            msg.channel, '', (await eval('self.{}(msg)'.format(arg))), -1
                        ))
                elif arg == 'set_message_edit_channel' or arg == 'set_message_delete_channel' or \
                        arg == 'set_member_join_channel' or arg == 'set_member_leave_channel' or \
                        arg == 'set_command_use_channel' or arg == 'get_custom_permission' or arg == 'set_bot_prefix' \
                        or arg == 'add_join_role' or arg == 'remove_join_role':
                    if len(args) > i + 1:
                        commands.append((
                            msg.channel, '', (await eval('self.{}(msg, args[i+1])'.format(arg))), -1
                        ))
                        skip += 1
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'add_custom_permission' or arg == 'remove_custom_permission':
                    if len(args) > i + 1:
                        commands.append((
                            msg.channel, '', (await eval('self.{}(msg, args[i+1:])'.format(arg))), -1
                        ))
                        break
                    else:
                        commands.append(self.insufficient_args(msg))
                else:
                    commands.append((msg.channel, '', (await eval('self.{}(msg)'.format(arg))), -1))

            else:  # Command not found or not available for use
                commands.append(self.arg_not_found(msg, arg))
        return commands
