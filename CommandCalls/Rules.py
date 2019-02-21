from Utils import Utils
from Embed import Embed
from Command import Command


class Rules(Command):
    """
    Rules command.

    Manages server-side rules.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['rules', 'r']
        self.permits = {
            'execute': 'allowed_user',
            'help': 'allowed_user',
            'set_rules': 'allowed_user',
            'add_rules': 'allowed_user',
            'get_rules': 'allowed_user'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'set_rules': [
                'Sets the rules for this server.',
                '``{{p}}{} set_rules <json>``\n'.format(self.aliases[0]) +
                "Example: ``{{p}}{} set_rules ".format(self.aliases[0]) +
                "{'text': 'Server rules', 'embed': {'title': 'Rules:', " + " 'description': 'The following are the " +
                "rules of this place', 'fields': [{'header': 'Rule 1:', 'text': 'This is the first rule.'}]}}``",
                ['sr', 's']
            ],
            'add_rules': [
                'Adds the rules to this server.',
                '``{{p}}{} add_rules <json>``\n'.format(self.aliases[0]) +
                "Example: ``{{p}}{} add_rules ".format(self.aliases[0]) +
                "{'text': 'Server rules', 'embed': {'title': 'Rules:', " + " 'description': 'The following are the " +
                "rules of this place', 'fields': [{'header': 'Rule 1:', 'text': 'This is the first rule.'}]}}``",
                ['ar', 'a']
            ],
            'get_rules': [
                'Gets the rules of this server.',
                '``{{p}}{} get_rules <,permanent,perm,p>``\n'.format(self.aliases[0]) +
                "Example: ``{{p}}{} get_rules permanent`` - gets rules that stay permanently"
                .format(self.aliases[0]),
                ['gr', 'g']
            ]
        }

    async def set_rules(self, msg, arg):
        """
        Set rules for server.

        :param msg: discord.Message
        :param arg:
        :return:
        """
        key = 'rules'

        config = self.data.servers[msg.server.id].config
        if key not in config or config[key] is None:
            self.data.servers[msg.server.id].config[key] = []

        js = Utils.js_decoder(arg)

        if not isinstance(js, list):
            js = [js]

        self.data.servers[msg.server.id].config[key] = js
        self.data.servers[msg.server.id].write_config()
        full_embeds = [Embed(self.data, msg, js={
            'title': 'Set server rules:',
            'description': 'The following are the rules.'
        })]
        full_embeds = full_embeds + [Embed(self.data, msg, js=embed) for embed in js]
        return full_embeds

    async def add_rules(self, msg, arg):
        """
        Add rules to server.

        :param msg: discord.Message
        :param arg: string - json
        :return:
        """
        key = 'rules'

        config = self.data.servers[msg.server.id].config
        if key not in config or config[key] is None:
            self.data.servers[msg.server.id].config[key] = []
            config = self.data.servers[msg.server.id].config

        js = Utils.js_decoder(arg)

        if not isinstance(js, list):
            js = [js]

        full_embeds = [Embed(self.data, msg, js={
            'title': 'Added server rules:',
            'description': 'The following are the rules.'
        })]
        data = config[key]
        n_data = [embed for embed in js]
        self.data.servers[msg.server.id].config[key] = data + n_data
        full_embeds = full_embeds + n_data

        self.data.servers[msg.server.id].write_config()

        return full_embeds

    async def get_rules(self, msg, arg=None):
        """
        Get rules of a server.

        :param msg: discord.Message
        :param arg: string
        :return:
        """
        key = 'rules'
        full_embeds = [Embed(self.data, msg, js={
            'title': 'Got server rules:',
            'description': 'The following are the rules.'
        })]
        config = self.data.servers[msg.server.id].config
        if key in config and config[key] is not None:
            full_embeds = full_embeds + [Embed(self.data, msg, js=rule) for rule in config[key]]

        if arg is not None:
            if arg.lower() in ['p', 'perm', 'permanent']:
                for embed in full_embeds[1:]:
                    await self.data.client.send_message(msg.channel, '', embed=embed.embed)
                return [Embed(self.data, msg, js={'title': 'Got server rules:'})]

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
                elif arg == 'set_rules' or arg == 'add_rules':
                    if len(args) > i + 1:
                        skip += 1
                        embeds = await eval('self.{}(msg, args[i+1])'.format(arg))
                        for embed in embeds:
                            commands.append((
                                msg.channel, '', embed, -1
                            ))
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'get_rules':
                    if len(args) > i + 1:
                        skip += 1
                        embeds = await eval('self.{}(msg, arg=args[i+1])'.format(arg))
                        for embed in embeds:
                            commands.append((
                                msg.channel, '', embed, -1
                            ))
                    else:
                        executable = eval('self.{}(msg)'.format(arg))
                        embeds = await executable
                        for embed in embeds:
                            commands.append((
                                msg.channel, '', embed, -1
                            ))
                else:
                    loads = await eval('self.{}()'.format(arg))
                    embed = Embed(self.data, msg, js={'title': 'Loaded Data:', 'description': loads})
                    commands.append((msg.channel, '', embed, -1))

            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
