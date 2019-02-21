from Utils import Utils
from Embed import Embed
from Command import Command


class Info(Command):
    """
        Cookie command.

        Manages server internal reputation system - cookie system.
        """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['info', 'i']
        self.permits = {
            'execute': 'everyone',
            'help': 'everyone',
            'channels': 'allowed_user',
            'roles': 'allowed_user'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'channels': [
                "Lists all channels and their id's.",
                "``{{p}}{} channels``\n".format(self.aliases[0]),
                ['c', 'chan']
            ],
            'roles': [
                "Lists all roles and their id's.",
                "``{{p}}{} roles``\n".format(self.aliases[0]),
                ['r']
            ]
        }

    async def channels(self, msg):

        fields = [{'header': channel.name, 'text': 'ID: {}'.format(channel.id)} for channel in msg.server.channels]

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Loaded channels:', 'fields': fields}),
            -1
        )

    async def roles(self, msg):

        fields = [{'header': role.name, 'text': 'ID: {}'.format(role.id)} for role in msg.server.roles]

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Loaded roles:', 'fields': fields}),
            -1
        )

    async def command_recognizer(self, msg, args):
        """
        Default command recognizing loop.

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
                else:
                    commands.append((await eval('self.{}(msg)'.format(arg))))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
