from Utils import Utils
from Embed import Embed
from Command import Command
import datetime


class Misc(Command):
    """
    Misc commands.

    Commands that have yet to find themselves a grouping for.
    """

    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self.aliases = ['misc', 'm']
        self.permits = {
            'execute': 'everyone',
            'help': 'everyone',
            'remove_role_from_everyone': 'allowed_user',
            'add_role_to_everyone': 'allowed_user',
            'purge_messages': 'allowed_user'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'remove_role_from_everyone': [
                "Removes a role from all users on the server.",
                "``{{p}}{} remove_role_from_everyone <role>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} remove_role_from_everyone @Member``".format(self.aliases[0]),
                ['rrfe', 'rr']
            ],
            'add_role_to_everyone': [
                "Adds a role to all users on the server.",
                "``{{p}}{} add_role_to_everyone <role>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} add_role_to_everyone @Member``".format(self.aliases[0]),
                ['arte', 'ar']
            ],
            'purge_messages': [
                "Purges a given amount of messages (or all of them) from the channel.",
                "``{{p}}{} purge_messages [,user] <,amount>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} purge_messages 1000``".format(self.aliases[0]) +
                " - deletes 1000 messages from the channel.\n" +
                "Example: ``{{p}}{} purge_messages @Elisiya 1000``".format(self.aliases[0]) +
                " - deletes 1000 messages sent by @Elisiya from the channel.",
                ['p', 'pm', 'purge']
            ]
        }

    async def purge_messages(self, msg, args=None):

        total_deleted = 0
        last_timestamp = msg.timestamp

        amount = None
        members = []

        # check for members and amount
        if args is not None:
            if len(args) > 1:
                for arg in args[:-1]:
                    member = (await Utils(self.data).finder(msg.server, arg, member=True))[0]
                    if member is None:
                        return ((
                            msg.channel, '',
                            Utils(self.data).error_embed(msg, "Supplied user could not be found: ``{}``".format(arg)),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        ))
                    members.append(str(member.id))
            member = (await Utils(self.data).finder(msg.server, args[-1], member=True))[0]
            if member is None:
                try:
                    amount = int(args[-1])
                except ValueError:
                    return (
                        msg.channel, '',
                        Utils(self.data).error_embed(
                            msg,
                            '**{}**\nInvalid value supplied.: ``{}``. Was not a member nor amount.'
                            .format(msg.content, args[-1])
                        ),
                        Utils.add_seconds(datetime.datetime.now(), 60)
                    )
            else:
                members.append(str(member.id))

        #

        def user_check(message):
            if message is None or message['author']['id'] in members or message['id'] == str(msg.id):
                return False
            else:
                return True

        logs = (await self.data.client._logs_from(msg.channel))

        amsg = await self.data.client.send_message(msg.channel, embed=(
            Embed(self.data, msg, js={'title': 'Commencing deletion. Please be patient'})).embed)

        while len(logs) > 0:
            max_val = len(logs)
            current_val = 0
            pbar = None
            for i, m in enumerate(logs):
                if user_check(m):
                    for d, data in self.data.servers[msg.server.id].config['sent_messages'].items():
                        for dm in data:
                            if dm[1] == str(m['id']):
                                self.data.servers[msg.server.id].config['sent_messages'][d].remove(dm)
                    logs[i] = await self.data.client.get_message(msg.channel, m['id'])
                else:
                    logs[i] = None
                pbar, current_val = Utils.loading_bar(max_val, current_val, pbar=pbar)
            logs = list(filter(None, logs))
            for m in logs:
                try:
                    await self.data.client.delete_message(m)
                except Exception as e:
                    print(e)
                total_deleted += 1
                if amount is not None and total_deleted >= amount:
                    break
                if last_timestamp > m.timestamp:
                    last_timestamp = m.timestamp
            if amount is not None and total_deleted >= amount:
                break
            if len(logs) > 55 or amount is not None:
                logs = (await self.data.client._logs_from(msg.channel, before=last_timestamp))
            else:
                logs = []

        await self.data.client.delete_message(amsg)

        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={'title': 'Purged messages:', 'description': 'Purged {} messages.'.format(total_deleted)}
            ),
            -1
        )

    async def remove_role_from_everyone(self, msg, arg):

        role = (await Utils(self.data).finder(msg.server, arg, role=True))[2]
        if role is None:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(msg, 'Could not find specified role: ``{}``'.format(arg)),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        if msg.server.large:
            await self.data.client.request_offline_members()

        for member in msg.server.members:
            if role in member.roles:
                await self.data.client.remove_roles(member, role)

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Removed roles:', 'description': 'Removed <@{}>'.format(role.id)}),
            -1
        )

    async def add_role_to_everyone(self, msg, arg):

        role = (await Utils(self.data).finder(msg.server, arg, role=True))[2]
        if role is None:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(msg, 'Could not find specified role: ``{}``'.format(arg)),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        if msg.server.large:
            await self.data.client.request_offline_members()

        for member in msg.server.members:
            if role not in member.roles:
                await self.data.client.add_roles(member, role)

        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Added roles:', 'description': 'Added <@{}>'.format(role.id)}),
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
                elif arg == 'remove_role_from_everyone' or arg == 'add_role_to_everyone':
                    if len(args) > i + 1:
                        commands.append((
                            await eval("self.{}(msg, args[i + 1])".format(arg))
                        ))
                        skip += 1
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'purge_messages':
                    if len(args) > i + 1:
                        commands.append((
                            await eval("self.{}(msg, args=args[i + 1:])".format(arg))
                        ))
                        skip += len(args[i + 1])
                    else:
                        commands.append((
                            await eval("self.{}(msg)".format(arg))
                        ))
                else:
                    loads = await eval('self.{}()'.format(arg))
                    embed = Embed(self.data, msg, js={'title': 'Loaded Data:', 'description': loads})
                    commands.append((msg.channel, '', embed, -1))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
