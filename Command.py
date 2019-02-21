from Utils import Utils
from Embed import Embed
import datetime


class Command(object):
    """
    Command base.

    Template for any commands that are created.
    """

    def __init__(self, data):
        self.data = data
        self.aliases = ['command']
        self.permits = {
            'execute': 'bot_owner',
            'help': 'bot_owner'
        }
        self.user = None
        self.prefix = None

    def arg_not_found(self, msg, arg):
        """
        Create embed for when an argument was not found.

        :param msg: discord.Message
        :param arg: argument that was not found
        :return:
        """
        return (
            msg.channel,
            "",
            Utils(self.data).error_embed(
                msg, "**{}**\nArgument was not found or you can't access it: ({}).".format(msg.content, arg)
            ),
            Utils.add_seconds(datetime.datetime.now(), 60)
        )

    def insufficient_args(self, msg):
        """
        Create embed for when there weren't enough arguments.

        :param msg: discord.Message
        :return:
        """
        return (
                    msg.channel, '',
                    Utils(self.data).error_embed(
                        msg, '**{}**\nInsufficient arguments.'.format(msg.content)
                    ),
                    Utils.add_seconds(datetime.datetime.now(), 60)
                )

    def empty_embed(self, msg):
        """
        Create an empty embed.

        :param msg: discord.Message
        :return:
        """
        return (
            msg.channel, '', Embed(self.data, msg), Utils.add_seconds(datetime.datetime.now(), 60)
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
                    loads = await eval('self.{}()'.format(arg))
                    embed = Embed(self.data, msg, js={'title': 'Loaded Data:', 'description': loads})
                    commands.append((msg.channel, '', embed, -1))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands

    async def execute(self, msg, args=None):
        """
        Execute this command.

        :param msg:
        :param args:
        :return: channel, message, embed, time
        """
        if args is None:
            args = []
        self.user = msg.author
        self.prefix = self.data.servers[msg.server.id].config['prefix']
        if not Utils(self.data).permissions(self.user, self.permits['execute'], self.aliases[0], 'execute'):
            embed = Utils(self.data).error_embed(msg, 'Command was not found.')
            return [(msg.channel, "", embed, Utils.add_seconds(datetime.datetime.now(), 60))]
        if len(args) == 0:
            if not Utils(self.data).permissions(self.user, self.permits['help'], self.aliases[0], 'help'):
                embed = Utils(self.data).error_embed(
                        msg, "**{}**\nArgument was not found or you can't access it: (help).".format(msg.content)
                    )
                return [(msg.channel, "", embed, Utils.add_seconds(datetime.datetime.now(), 60))]
            return [(msg.channel, '', (await Utils(self.data).default_help(self, msg)), -1)]
        else:
            return await self.command_recognizer(msg, args)
