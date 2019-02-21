from Utils import Utils
from Embed import Embed as Em
from Command import Command
import datetime


class Embed(Command):
    """
    Embed command.

    Allows users to create embeds using the json format.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['embed', 'e']
        self.permits = {
            'execute': 'allowed_user',
            'help': 'allowed_user',
            'create_embed': 'allowed_user'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'create_embed': [
                'Creates an embed based on entered json input.',
                '``{{p}}{} create_embed <json> <,p,perm,permanent>`` - creates an embed based on the entered json.\n'
                .format(self.aliases[0]) +
                "Example: ``{{p}}{} ".format(self.aliases[0]) +
                "create_embed {{'title': 'Embed Title', 'description': 'Embed description'}}``\n" +
                "Example: ``{{p}}{} ".format(self.aliases[0]) +
                "create_embed {{'title': 'Hello world!', 'description': 'Embed description'}} permanent`` - "
                "creates an embed that will stay indefinitely unless manually deleted.",
                ['ce', 'c']
            ]
        }

    async def create_embed(self, msg, arg, perm=''):
        """
        Create an embed.

        :param msg: discord.Message
        :param arg: string - json
        :param perm: string
        :return:
        """
        if perm != '':
            if perm.lower() in ['p', 'perm', 'permanent']:
                perm = True
            else:
                perm = False

        js = Utils.js_decoder(arg)

        embeds = []
        if not isinstance(js, list):
            embeds = [js]

        full_embeds = []
        errors = []
        if not perm:
            for embed in embeds:
                embed = Em(self.data, msg, js=embed)
                errors = errors + embed.unconfigured
                full_embeds.append((
                    msg.channel, '',
                    embed,
                    -1
                ))
        else:
            for embed in embeds:
                embed = Em(self.data, msg, js=embed)
                errors = errors + embed.unconfigured
                await self.data.client.send_message(msg.channel, '', embed=embed.embed)
        full_embeds = full_embeds + [
            (
                msg.channel, '',
                Utils(self.data).error_embed(msg, error),
                Utils.add_seconds(datetime.datetime.now(), 60)
            ) for error in errors
        ]
        return full_embeds

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
                elif arg == 'create_embed':
                    if len(args) > i + 2:
                        skip += 2
                        get_commands = (await eval('self.{}(msg, args[i+1], perm=args[i+2])'.format(arg)))
                        for embed in get_commands:
                            commands.append(embed)
                    if len(args) > i + 1:
                        skip += 1
                        get_commands = (await eval('self.{}(msg, args[i+1])'.format(arg)))
                        for embed in get_commands:
                            commands.append(embed)
                    else:
                        commands.append(self.insufficient_args(msg))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
