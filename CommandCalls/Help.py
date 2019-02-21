from Command import Command
from Utils import Utils
from Embed import Embed


class Help(Command):
    """Help command."""

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['help', 'h', '?']
        self.permits = {
            'execute': 'everyone',
            'help': 'everyone',
            'commands': 'everyone'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'commands': [
                "Displays all the commands you can use.",
                "``{{p}}{} commands``\n".format(self.aliases[0]),
                ['c']
            ]
        }

    async def commands(self, msg):
        """
        Get commands that a member can use.

        :param msg: discord.Server
        :return:
        """
        commands = self.data.command_calls
        accessible_commands = []
        for command, executable in commands.items():
            permission = Utils(self.data).permissions(
                msg.author, executable(self.data).permits['execute'], command.lower(), 'execute'
            )
            if permission:
                accessible_commands.append(command.lower())
        return 'You can access [{}].\nUse ``{}<command>`` to see more details on the commands you can access.'.format(
            ', '.join(accessible_commands), self.data.servers[msg.server.id].config['prefix'])

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
            print(arg)

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
                    loads = await eval('self.{}(msg)'.format(arg))
                    embed = Embed(self.data, msg, js={'title': 'Loaded Data:', 'description': loads})
                    commands.append((msg.channel, '', embed, -1))
            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
