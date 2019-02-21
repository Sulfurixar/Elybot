from Utils import Utils
from Embed import Embed
from Command import Command


class Update(Command):
    """
    Update command.

    Updates various dynamic libraries in the bot.
    This command outputs a string on every argument instance.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['update', 'u']
        self.permits = {
            'execute': 'bot_owner',
            'help': 'bot_owner',
            'events': 'bot_owner',
            'commands': 'bot_owner',
            'full_reload': 'bot_owner',
            'servers': 'bot_owner'
        }
        self.command_descriptions = {
            'commands': [
                "Reloads the bot's commands. ",  # description
                "``{{p}}{} commands``".format(self.aliases[0]),  # usage
                ['c', 'cmds']  # aliases
            ],
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'events': [
                "Reloads the bot's events. ",
                "``{{p}}{} events``".format(self.aliases[0]),
                ['e']
            ],
            'full_reload': [
                "Reloads bot's events, commands and servers. ",
                "``{{p}}{} full_reload".format(self.aliases[0]),
                ['fr', 'reload', 'full']
            ],
            'servers': [
                "Reloads the bot's servers. ",
                "``{{p}}{} servers``".format(self.aliases[0]),
                ['s']
            ]
        }

    async def servers(self):
        """
        Load all servers.

        :return: string - all loaded servers
        """
        self.data.loaded = False
        loads = '\n'.join(self.data.load_servers()) + '\n\n'
        self.data.loaded = True
        return loads

    async def events(self):
        """
        Load all commands.

        :return: string - all loaded events
        """
        self.data.loaded = False
        loads = '\n'.join(self.data.load(_reload=True)) + '\n\n'
        self.data.loaded = True
        return loads

    async def commands(self):
        """
        Load all commands.

        :return: string - all loaded commands
        """
        self.data.loaded = False
        loads = '\n'.join(self.data.load(mode=1, _reload=True)) + '\n\n'
        self.data.loaded = True
        return loads

    async def full_reload(self):
        """
        Reload all events, commands and servers for this bot.

        :return: string - all loaded components
        """
        loads = ''
        loads += await self.events()
        loads += await self.commands()
        loads += await self.servers()
        return loads

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
                else:
                    loads = await eval('self.{}()'.format(arg))
                    embed = Embed(self.data, msg, js={'title': 'Loaded Data:', 'description': loads})
                    commands.append((msg.channel, '', embed, -1))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
