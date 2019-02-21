from Utils import Utils
from Embed import Embed
from Command import Command
import datetime


class Access(Command):
    """
    Access command.

    Gives access to channels or roles.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['access', 'a']
        self.permits = {
            'execute': 'everyone',
            'help': 'everyone',
            'add_access': 'allowed_user',
            'remove_access': 'allowed_user',
            'show_access': 'allowed_user',
            'enable': 'everyone',
            'disable': 'everyone',
            'toggle': 'everyone'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'add_access': [
                "Adds a new access option for users.",
                "``{{p}}{} add_access [<channel or role>, <command_keyword>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} add_access #general general``".format(self.aliases[0]) +
                " - adds an option for users to get access to #general via enable command.",
                ['a', 'aa', 'add']
            ],
            'remove_access': [
                "Removes an access option from users.",
                "``{{p}}{} remove_access [<command_keyword>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} remove_access general``".format(self.aliases[0]) +
                " - removes the access channel or role given with general.",
                ['r', 'ra', 'rem', 'remove']
            ],
            'show_access': [
                "Shows current access data.",
                "``{{p}}{} show_access``".format(self.aliases[0]),
                ['s', 'sa', 'show']
            ],
            'enable': [
                "Enables a user the access to a specified role or channel.",
                "``{{p}}{} enable [<command_keyword>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} enable general``".format(self.aliases[0]) +
                " - gives access to general for the user.",
                ['e']
            ],
            'disable': [
                "Disables a user the access to a specified role or channel.",
                "``{{p}}{} disable [<command_keyword>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} disable general``".format(self.aliases[0]) +
                " - takes access to general for the user.",
                ['d']
            ],
            'toggle': [
                "Toggles a user the access to a specified role or channel.",
                "``{{p}}{} toggle [<command_keyword>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} toggle general``".format(self.aliases[0]) +
                " - toggle access to general for the user.",
                ['t']
            ]
        }

    async def enable(self, msg, args):

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['access'] = {}
            self.data.servers[msg.server.id].write_config()

        conf = self.data.servers[msg.server.id].config['access']
        done = []
        for arg in args:
            if arg in conf:
                print(conf[arg])
                member, channel, role = await Utils(self.data).finder(
                    msg.server, conf[arg]['id'], channel=True, role=True
                )
                if conf[arg]['type'] == 'channel':
                    if channel is None:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
                    overwrites = channel.overwrites_for(msg.author)
                    if not overwrites.read_messages:
                        overwrites.update(read_messages=True)
                        await self.data.client.edit_channel_permissions(channel, msg.author, overwrites)
                if conf[arg]['type'] == 'role':
                    if role is None:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
                    if role not in msg.author.roles:
                        await self.data.client.add_roles(msg.author, role)
            done.append(arg)

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Enabled access:', 'description': ', '.join(done)}),
            -1
        )

    async def disable(self, msg, args):

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['access'] = {}
            self.data.servers[msg.server.id].write_config()

        conf = self.data.servers[msg.server.id].config['access']
        done = []
        for arg in args:
            if arg in conf:
                member, channel, role = await Utils(self.data).finder(
                    msg.server, conf[arg]['id'], channel=True, role=True
                )
                if conf[arg]['type'] == 'channel':
                    if channel is None:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
                    overwrites = channel.overwrites_for(msg.author)
                    if overwrites.read_messages:
                        overwrites.update(read_messages=False)
                        await self.data.client.edit_channel_permissions(channel, msg.author, overwrites)
                if conf[arg]['type'] == 'role':
                    if role is None:
                        if channel is None:
                            return (
                                msg.channel, '',
                                Utils(self.data).error_embed(
                                    msg,
                                    '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                    .format(msg.content, arg)
                                ),
                                Utils.add_seconds(datetime.datetime.now(), 60)
                            )
                    if role in msg.author.roles:
                        await self.data.client.remove_roles(msg.author, role)
            done.append(arg)

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Disabled access:', 'description': ', '.join(done)}),
            -1
        )

    async def toggle(self, msg, args):

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['access'] = {}
            self.data.servers[msg.server.id].write_config()

        conf = self.data.servers[msg.server.id].config['access']
        done = []
        for arg in args:
            if arg in conf:
                member, channel, role = await Utils(self.data).finder(
                    msg.server, conf[arg]['id'], channel=True, role=True
                )
                if conf[arg]['type'] == 'channel':
                    if channel is None:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
                    overwrites = channel.overwrites_for(msg.author)
                    overwrites.update(read_messages=(not overwrites.read_messages))
                    await self.data.client.edit_channel_permissions(channel, msg.author, overwrites)
                if conf[arg]['type'] == 'role':
                    if role is None:
                        if channel is None:
                            return (
                                msg.channel, '',
                                Utils(self.data).error_embed(
                                    msg,
                                    '**{}**\nInvalid configuration for ``{}`` - could not recognize channel or role.'
                                    .format(msg.content, arg)
                                ),
                                Utils.add_seconds(datetime.datetime.now(), 60)
                            )
                    if role in msg.author.roles:
                        await self.data.client.remove_roles(msg.author, role)
                    else:
                        await self.data.client.add_roles(msg.author, role)
            done.append(arg)

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Toggled access:', 'description': ', '.join(done)}),
            -1
        )

    async def show_access(self, msg):

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['access'] = {}
            self.data.servers[msg.server.id].write_config()

        if len(self.data.servers[msg.server.id].config['access']) == 0:
            return (
                msg.channel, '',
                Embed(
                    self.data, msg, js={'title': 'Access data:', 'description': 'Currently there is no access data.'}
                ),
                -1
            )
        fields = Utils.convert_json_to_fields(self.data.servers[msg.server.id].config['access'])

        return (
                msg.channel, '',
                Embed(self.data, msg, js={'title': 'Access data:', 'fields': fields}),
                -1
            )

    async def remove_access(self, msg, args):

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.server[msg.server.id].config['access'] = {}

        values = {}
        for arg in args:
            if arg in self.data.servers[msg.server.id].config['access']:
                values.update({arg: str(self.data.servers[msg.server.id].config['access'][arg])})
                self.data.servers[msg.server.id].config['access'].pop(arg)

        fields = Utils.convert_json_to_fields(values)
        self.data.servers[msg.server.id].write_config()

        return (
            msg.channel, '',
            Embed(
                self.data, msg, js={'title': 'Removed access values:', 'fields': fields}
            ),
            -1
        )

    async def add_access(self, msg, args):
        """
                Add specified rewards.

                :param msg: discord.Message
                :param args: list - list of strings
                :return:
                """

        # Find
        pairs = []  # list of channels or roles
        skip = 0
        for i, arg in enumerate(args):
            if skip:
                skip -= 1
                continue
            user, channel, role = await Utils(self.data).finder(msg.server, arg, channel=True, role=True)
            if role is None and channel is None:
                return (
                    msg.channel, '',
                    Utils(self.data).error_embed(
                        msg,
                        '**{}**\nInvalid argument supplied ``{}`` - not recognized channel or role.'
                        .format(msg.content, arg)
                    ),
                    Utils.add_seconds(datetime.datetime.now(), 60)
                )
            if not len(args) > i + 1:
                return (
                    msg.channel, '',
                    Utils(self.data).error_embed(
                        msg,
                        '**{}**\nInvalid amount of arguments supplied missing amount for: ``{}``.'
                        .format(msg.content, arg)
                    ),
                    Utils.add_seconds(datetime.datetime.now(), 60)
                )
            skip += 1
            arg2 = args[i + 1]
            pairs.append(((role, channel), arg2))

        #

        if 'access' not in self.data.servers[msg.server.id].config:
            self.data.servers[msg.server.id].config['access'] = {}
        access = self.data.servers[msg.server.id].config['access']

        values = {}

        for obj, key in pairs:
            role, channel = obj
            if key not in access:
                if channel is not None:
                    access[key] = [{'id': channel.id, 'name': channel.name, 'type': 'channel'}]
                else:
                    access[key] = [{'id': role.id, 'name': role.name, 'type': 'role'}]
            else:
                if channel is not None:
                    access[key] = access[key] + [{'id': channel.id, 'name': channel.name, 'type': 'channel'}]
                else:
                    access[key] = access[key] + [{'id': role.id, 'name': role.name, 'type': 'role'}]
            values.update({key: str(access[key])})

        self.data.servers[msg.server.id].config['access'] = access

        fields = Utils.convert_json_to_fields(values)
        self.data.servers[msg.server.id].write_config()

        return (
            msg.channel, '',
            Embed(
                self.data, msg, js={'title': 'Added access values:', 'fields': fields}
            ),
            -1
        )

    async def command_recognizer(self, msg, args):
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
                elif arg == 'add_access':
                    if len(args) > i + 2:
                        commands.append((
                            await eval(
                                'self.{}(msg, args=args[i+1:])'.format(arg)
                            )
                        ))
                        skip += len(args[i+1])
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'remove_access' or arg == 'enable' or arg == 'disable' or arg == 'toggle':
                    if len(args) > i + 1:
                        commands.append((
                            await eval(
                                'self.{}(msg, args=args[i+1:])'.format(arg)
                            )
                        ))
                        skip += len(args[i+1])
                    else:
                        commands.append(self.insufficient_args(msg))
                else:  # show_access
                    commands.append((
                        await eval("self.{}(msg)".format(arg))
                    ))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
