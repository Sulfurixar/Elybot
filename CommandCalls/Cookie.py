from Utils import Utils
from Embed import Embed
from Command import Command
import datetime
import math
import copy


class Cookie(Command):
    """
    Cookie command.

    Manages server internal reputation system - cookie system.
    """

    def __init__(self, data):
        super().__init__(data)
        self.aliases = ['cookie', 'c']
        self.permits = {
            'execute': 'everyone',
            'help': 'everyone',
            'show_full': 'allowed_user',
            'show': 'everyone',
            'set_cookie_emoji': 'allowed_user',
            'set_jar_emoji': 'allowed_user',
            'give_cookies': 'everyone',
            'give_cookies_over_limit': 'allowed_user',
            'add_cookie_rewards': 'allowed_user',
            'remove_cookie_rewards': 'allowed_user',
            'show_cookie_rewards': 'allowed_user',
            'show_cookie_data': 'bot_owner',
            'jar_cookies': 'everyone',
            'unjar_cookies': 'everyone'
        }
        self.command_descriptions = {
            'help': [
                "Displays help for this command.",
                "``{{p}}{} help <,argument>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} help help`` - displays help about this command.".format(self.aliases[0]),
                ['h', '?']
            ],
            'show_full': [
                "Displays your cookie data.",
                "``{{p}}{} show_full``\n".format(self.aliases[0]),
                ['sf']
            ],
            'show': [
                "Displays your cookies.",
                "``{{p}}{} show``\n".format(self.aliases[0]),
                ['s']
            ],
            'set_cookie_emoji': [
                "Sets the emoji used to represent cookies.",
                "``{{p}}{} set_cookie_emoji <emoji>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} set_cookie_emoji :cookie:``".format(self.aliases[0]),
                ['sce', 'sc']
            ],
            'set_jar_emoji': [
                "Sets the emoji used to represent the cookie jar.",
                "``{{p}}{} set_jar_emoji <emoji>``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} set_jar_emoji :bank:``".format(self.aliases[0]),
                ['sje', 'sj']
            ],
            'give_cookies': [
                "Gives a user cookies.",
                "``{{p}}{} give_cookies <,user> <,amount> <,ol,over_limit>``\n".format(self.aliases[0]) +
                "Note that this command doesn't take user id as valid user input as it could be read as an amount of "
                "cookies."
                "Example: ``{{p}}{} give_cookies @Elisiya 200 over_limit``"
                "- gives Elisiya 200 cookies even if the limit is lower.\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} give_cookies @Elisiya`` - gives Elisiya 1 cookie.\n"
                .format(self.aliases[0]) +
                "Example: ``{{p}}{} give_cookies 10`` - gives you 10 cookies.".format(self.aliases[0]),
                ['g', 'gc']

            ],
            'add_cookie_rewards': [
                "Adds the values for rewards acquired through getting cookies.",
                "``{{p}}{} add_cookie_rewards [<channel, role>, <amount>, <,p, perm, permanent>]``\n"
                .format(self.aliases[0]) +
                "Example: ``{{p}}{} add_cookie_rewards #general 0.4, False``".format(self.aliases[0]) +
                " - rewards users who reach the 40th percentile with access to general and it will never go away.\n"
                "Example: ``{{p}}{} add_cookie_rewards @Member 0.6``".format(self.aliases[0]) +
                " - rewards users who reach the 60th percentile with Member role that will be removed when they reach "
                "a higher rank.",
                ['acr', 'ar']
            ],
            'remove_cookie_rewards': [
                "Removes the values or rewards for the values.",
                "``{{p}}{} remove_cookie_rewards [<value>, <,channel, role>]``\n".format(self.aliases[0]) +
                "Example: ``{{p}}{} remove_cookie_rewards 0.4``".format(self.aliases[0]) +
                " - removes all rewards from the value 0.4.\n"
                "Example: ``{{p}}{} remove_cookie_rewards 0.4 #general``".format(self.aliases[0]) +
                " - removes the #general channel reward from the value 0.4.",
                ['rcr', 'rr']
            ],
            'show_cookie_rewards': [
                "Shows the current configuration for cookies.",
                "``{{p}}{} show_cookie_rewards``\n".format(self.aliases[0]),
                ['scr', 'sr']
            ],
            'show_cookie_data': [
                "Shows the cookie data.",
                "``{{p}}{} show_cookie_data``\n".format(self.aliases[0]),
                ['scd', 'sd']
            ],
            "jar_cookies": [
                "Adds your cookies into the cookie jar.",
                '``{{p}}{} jar_cookies <amount>``\n'.format(self.aliases[0]) +
                "Example: ``{{p}}{} jar_cookies 10``".format(self.aliases[0]) +
                " - Puts 10 of your on-hand cookies in the jar.",
                ['jc', 'j']
            ],
            "unjar_cookies": [
                "Takes your cookies from the cookie jar.",
                '``{{p}}{} unjar_cookies <amount>``\n'.format(self.aliases[0]) +
                "Example: ``{{p}}{} unjar_cookies 10``".format(self.aliases[0]) +
                " - Takes 10 of your cookies from the jar.",
                ['ujc', 'uj']
            ]
        }
        self.user_config = {
            'total_cookies': 0,
            'current_cookies': 0,
            'cookies_in_jar': 0,    # if a user should want to withdraw some cookies from the jar or deposit them
                                    # can go to deficit to generate interest for the cookie jar in the form of a loan
                                    # works the other way around as well, to create more cookies for the user if it's
                                    # positive
                                    # if user has a cookie rank (given out based on some amount of cookies) then once
                                    # the deficit reaches amount of cookies required for that rank it will be annulled
                                    # and the user will be demoted to the previous rank
                                    # one can only earn negative interest while there are negative cookies in jar
                                    # one can only earn positive interest while there are positive cookies in jar 
            'cookie_interest': 0,   # if it gets to 1 or -1, then a cookie is given or taken from the user's jar
            'cookie_transfer_quota': 0,  # how many cookie transfers a user has done this epoch
            'get': {
                'total_cookies': 0,
                'average': 0
            },
            'give': {
                'total_cookies': 0,
                'average': 0
            },
            'active_this_epoch': False,  # True if user has been active this epoch, set to False during hourly ticker
            'active_epochs': 0,
            'measured_epochs': 0  # +1 during hourly ticker if user is online and has had activity
        }
        self.server_config = {
            'cookie_jar': 0,  # if there are cookies in jar, there is no need to make cookies when giving others cookies
            'total_cookies': 0,
            'cookie_value': 0,
            'cookie_transfer_limit': 0,
            'averages': {
                'cookies_per_person': 0,
                'cookies_in_cookie_jar': 0,
                'cookies_on_hand': 0,
                'user_give_average_average': 0,
                'user_get_average_average': 0,
                'server_give_average': 0,
                'server_give_average_average': 0,
                'server_get_average': 0,
                'server_get_average_average': 0
            },
            'cookie_distribution': {},
            'cookie_rewards': {},  # amount: [{'id': '1', 'type': 'channel/server', 'permanent': True/False}]
            'active_this_epoch': False,
            'active_epochs': 0,
            'measured_epochs': 0,
            'emojis': ['🍪', '🏦']
        }

    def transaction(self, user_giving, user_receiving, server, over_limit=False, amount=1):
        """
        Make a transaction between users.

        :param user_giving: discord.Member
        :param user_receiving: discord.Member
        :param server: discord.Server
        :param over_limit: True/False - disable transfer limit
        :param amount: int - how many cookies to transfer
        :return:
        """
        _server = self.check_server_config(server)

        _server.config['cookies']['cookie_transfer_limit'] = \
            self.calculate_cookie_transfer(server)

        if user_giving.config['cookies']['cookie_transfer_quota'] + amount > \
                self.data.servers[server.id].config['cookies']['cookie_transfer_limit'] or \
                user_receiving.config['cookies']['cookie_transfer_quota'] + amount > \
                self.data.servers[server.id].config['cookies']['cookie_transfer_limit']:
            if not over_limit:
                return False

        # SET TRANSFER ACTIVE
        self.data.servers[server.id].config['cookies']['active_this_epoch'] = True
        if not over_limit:
            user_giving.config['cookies']['active_this_epoch'] = True
        user_receiving.config['cookies']['active_this_epoch'] = True
        #

        # UPDATE user QUOTAS
        if not over_limit:
            user_giving.config['cookies']['cookie_transfer_quota'] = \
                user_giving.config['cookies']['cookie_transfer_quota'] + amount
        user_receiving.config['cookies']['cookie_transfer_quota'] = \
            user_receiving.config['cookies']['cookie_transfer_quota'] + amount
        #

        # check if we need to make a new cookie or there's cookies in the bank, and if need be create a new cookie
        if not self.data.servers[server.id].config['cookies']['cookie_jar']:
            self.data.servers[server.id].config['cookies']['total_cookies'] = \
                self.data.servers[server.id].config['cookies']['total_cookies'] + amount
        elif self.data.servers[server.id].config['cookies']['cookie_jar'] >= amount:
            self.data.servers[server.id].config['cookies']['cookie_jar'] = \
                self.data.servers[server.id].config['cookies']['cookie_jar'] - amount
        else:
            n_amount = amount - self.data.servers[server.id].config['cookies']['cookie_jar']
            self.data.servers[server.id].config['cookies']['cookie_jar'] = 0
            self.data.servers[server.id].config['cookies']['total_cookies'] = \
                self.data.servers[server.id].config['cookies']['total_cookies'] + n_amount

        if not over_limit:
            user_giving.config['cookies']['give']['total_cookies'] = \
                user_giving.config['cookies']['total_cookies'] + amount

        user_receiving.config['cookies']['total_cookies'] = user_receiving.config['cookies']['total_cookies'] + amount
        user_receiving.config['cookies']['get']['total_cookies'] = \
            user_receiving.config['cookies']['get']['total_cookies'] + amount
        user_receiving.config['cookies']['current_cookies'] = \
            user_receiving.config['cookies']['current_cookies'] + amount
        #

        # SAVE USERS
        user_giving.write_config()
        user_receiving.write_config()
        #

        # UPDATE SERVER DATA
        self.data.servers[server.id].config['cookies']['cookie_value'] = self.calculate_value(server)
        self.data.servers[server.id].write_config()
        #

        return True

    def update_cookie_data(self):
        """
        Update all cookie config data.

        :return:
        """
        # reload servers to make sure we got the latest data
        self.data.loaded = False
        self.data.load_servers()
        self.data.loaded = True
        #

        for server_id, server in self.data.servers.items():

            server = self.check_server_config(server.server)

            # update server epochs
            server.config['cookies']['measured_epochs'] = server.config['cookies']['measured_epochs'] + 1
            if not server.config['cookies']['active_this_epoch']:
                server.write_config()
                continue
            else:
                server.config['cookies']['active_this_epoch'] = False
                server.config['cookies']['active_epochs'] = server.config['cookies']['active_epochs'] + 1
            #

            if server.server.large:
                self.data.client.request_offline_members(server.server)

            cookies_per_person = 0
            cookies_in_cookie_jar = 0
            cookies_on_hand = 0
            user_gives = 0
            user_gets = 0
            user_give_average_average = 0
            user_get_average_average = 0
            distribution = {}
            for member in server.server.members:
                member = self.check_user_config(member)

                # update user epochs
                if member.config['cookies']['active_this_epoch']:
                    member.config['cookies']['active_this_epoch'] = False
                    member.config['cookies']['active_epochs'] = member.config['cookies']['active_epochs'] + 1
                member.config['cookies']['measured_epochs'] = member.config['cookies']['measured_epochs'] + 1
                #

                # calculate user interest and give cookies accordingly
                if member.config['cookies']['cookies_in_jar']:
                    # update user cookie interest
                    member.config['cookies']['cookie_interest'] = member.config['cookies']['cookie_interest'] + \
                                                                  member.config['cookies']['cookies_in_jar'] * \
                                                                  server.config['cookies']['cookie_value']
                    #

                    # add cookies to user's jar
                    if int(member.config['cookies']['cookie_interest']) > 0:
                        cookie_amount = int(member.config['cookies']['cookie_interest'])
                        member.config['cookies']['cookie_interest'] = member.config['cookies']['cookie_interest'] - \
                            cookie_amount
                        server.config['cookies']['cookie_jar'] = server.config['cookies']['cookie_jar'] + cookie_amount
                        server.config['cookies']['total_cookies'] = server.config['cookies']['total_cookies'] + \
                            cookie_amount
                        member.config['cookies']['cookies_in_jar'] = server.config['cookies']['cookie_jar'] + \
                            cookie_amount
                        member.config['cookies']['total_cookies'] = server.config['cookies']['total_cookies'] + \
                            cookie_amount
                    #
                    if int(member.config['cookies']['cookie_interest']) < 0:
                        cookie_amount = int(member.config['cookies']['cookie_interest'])
                        member.config['cookies']['cookie_interest'] = member.config['cookies']['cookie_interest'] - \
                            abs(cookie_amount)
                        server.config['cookies']['cookie_jar'] = server.config['cookies']['cookie_jar'] + cookie_amount
                        server.config['cookies']['total_cookies'] = server.config['cookies']['total_cookies'] + \
                            cookie_amount
                        member.config['cookies']['cookies_in_jar'] = server.config['cookies']['cookies_in_jar'] + \
                            cookie_amount
                        member.config['cookies']['total_cookies'] = server.config['cookies']['total_cookies'] + \
                            cookie_amount
                #

                # calculate user averages
                member.config['cookies']['give']['average'] = member.config['cookies']['give']['total_cookies'] / \
                    member.config['cookies']['measured_epochs']
                member.config['cookies']['get']['average'] = member.config['cookies']['get']['total_cookies'] / \
                    member.config['cookies']['measured_epochs']
                #

                # null limit
                member.config['cookies']['cookie_transfer_quota'] = 0
                #

                # add averages that are user specific
                cookies_per_person += member.config['cookies']['total_cookies']
                cookies_in_cookie_jar += member.config['cookies']['cookies_in_jar']
                cookies_on_hand += member.config['cookies']['current_cookies']
                user_give_average_average += member.config['cookies']['give']['average']
                user_get_average_average += member.config['cookies']['give']['average']
                user_gives += member.config['cookies']['give']['total_cookies']
                user_gets += member.config['cookies']['get']['total_cookies']
                if member.config['cookies']['total_cookies'] not in distribution:
                    distribution.update({member.config['cookies']['total_cookies']: 0})
                distribution[member.config['cookies']['total_cookies']] = \
                    distribution[member.config['cookies']['total_cookies']] + 1
                #

                member.write_config()

            # calculate server averages
            server.config['cookies']['averages']['cookies_per_person'] = cookies_per_person / server.server.member_count
            server.config['cookies']['averages']['cookies_in_cookie_jar'] = \
                cookies_in_cookie_jar / server.server.member_count
            server.config['cookies']['averages']['cookies_on_hand'] = cookies_on_hand / server.server.member_count
            server.config['cookies']['averages']['user_give_average_average'] = \
                user_give_average_average / server.server.member_count
            server.config['cookies']['averages']['user_get_average_average'] = \
                user_get_average_average / server.server.member_count
            server.config['cookies']['averages']['server_give_average'] = user_gives / server.server.member_count
            server.config['cookies']['averages']['server_get_average'] = user_gets / server.server.member_count
            server.config['cookies']['averages']['server_give_average_average'] = \
                user_give_average_average / server.server.member_count
            server.config['cookies']['averages']['server_get_average_average'] = \
                user_get_average_average / server.server.member_count
            server.config['cookies']['cookie_distribution'] = distribution
            #

            # calculate transfer limit
            server.config['cookies']['cookie_transfer_limit'] = self.calculate_cookie_transfer(server.server)
            #

            # calculate cookie value
            server.config['cookies']['cookie_value'] = self.calculate_value(server.server)
            #

            server.write_config()

    def calculate_cookie_reward(self, server):
        """
        Calculate cookie rewards.

        :param server: Server
        :return:
        """
        distribution = copy.deepcopy(server.config['cookies']['cookie_distribution'])
        total_cookies = server.config['cookies']['total_cookies']
        total_users = server.server.member_count
        cookie_value = self.calculate_value(server.server)
        if "0" in distribution:
            distribution.pop("0")
        arithmetic_average_of_people_per_value = 0
        value_count = 0
        for value, people in distribution.items():
            arithmetic_average_of_people_per_value += people
            value_count += 1
        if value_count != 0:
            arithmetic_average_of_people_per_value = arithmetic_average_of_people_per_value / value_count
            maximum_cookie_count = total_cookies / value_count
        else:
            arithmetic_average_of_people_per_value = 0
            maximum_cookie_count = 0
        hundred = maximum_cookie_count * cookie_value
        ignore_values = []
        for value in distribution:
            if float(value) < arithmetic_average_of_people_per_value:
                ignore_values.append(value)
        for value in ignore_values:
            distribution.pop(value)
        if len(distribution) > 0:
            zero = distribution[sorted(distribution, key=lambda v: int(v), reverse=True)[0]]
        else:
            zero = 0

        diff = hundred - zero

        embeds = []
        try:
            embeds.append({
                'title': 'Cookie Distribution:',
                'fields': [
                    eval("{{'header': 'Cookies: {}:', 'value': 'Users: {}'}}".format(cookies, users))
                    for cookies, users in server.config['cookies']['cookie_distribution'].items()
                ]
            })
        except:
            pass
        try:
            embeds.append({
                'title': 'Filtered Distribution:',
                'fields': [
                    eval("{{'header': 'Cookies: {}:', 'value': 'Users: {}'}}".format(cookies, users))
                    for cookies, users in distribution.items()
                ]
            })
        except:
            pass
        try:
            embeds.append({
                'title': 'Cookie Reward Data:',
                'fields': [
                    {'header': 'Total Cookies:', 'value': str(total_cookies)},
                    {'header': 'Total Users:', 'value': str(total_users)},
                    {'header': 'Cookie Value:', 'value': str(cookie_value)},
                    {'header': 'Arithmetic Average Per People:', 'value': str(arithmetic_average_of_people_per_value)},
                    {'header': 'Filtered Cookie Groups Amount:', 'value': str(value_count)},
                    {'header': 'Maximum Cookie Value:', 'value': str(maximum_cookie_count)},
                    {'header': 'Hundred Percent (100%):', 'value': str(hundred)},
                    {'header': 'Zero Percent (0%):', 'value': str(zero)},
                    {'header': 'Difference:', 'value': str(diff)},
                    {'header': 'One Percent (1%):', 'value': str(diff/100)}
                ]
            })
        except:
            pass
        try:
            embeds.append({
                'title': 'Cookie Reward Levels:',
                'fields': [
                    eval("{{'header': 'Cookie Amount: {}', "
                         "'value': '\\n'.join(['{{}}'.format(reward) for reward in {}])}}"
                         .format(float(percentage) * diff, rewards))
                    for percentage, rewards in server.config['cookies']['cookie_rewards'].items()
                ]
            })
        except Exception as e:
            print(e)
            pass

        return (hundred, zero, diff), embeds

    async def reward_users(self):
        """
        Reward all users from all servers.

        :return:
        """
        async def get_object(r, server):
            """
            Get channel or role from a reward.

            :param r: dict - reward
            :param server:
            :return:
            """
            _m, _c, _r = await Utils(self.data).finder(server, r['id'], channel=True, role=True)
            if _c is not None:
                obj = _c
            else:
                obj = _r
            if obj is not None:
                i = \
                    self.data.servers[server_id].config['cookies']['cookie_rewards'][str(value)] \
                        .index(r)
                self.data.servers[server_id] \
                    .config['cookies']['cookie_rewards'][str(value)][i] = {
                    'type': r['type'], 'id': obj.id, 'name': obj.name,
                    'permanent': r['permanent']
                }
                self.data.servers[server_id].write_config()
            return obj

        for server_id, Server in self.data.servers.items():

            distribution = Server.config['cookies']['cookie_distribution']
            if len(distribution) == 0:
                continue

            reward_data, embeds = self.calculate_cookie_reward(Server)
            hundred, zero, diff = reward_data

            if Server.server.large:
                await self.data.client.request_offline_members(Server.server)

            for member in Server.server.members:

                user = self.check_user_config(member)

                highest = 0
                for value in Server.config['cookies']['cookie_rewards']:

                    value = float(value)
                    if value*diff/100 > user.config['cookies']['total_cookies']:
                        continue

                    if value*diff/100 < user.config['cookies']['total_cookies']:
                        if value > highest:
                            highest = value

                for value, rewards in Server.config['cookies']['cookie_rewards'].items():

                    value = float(value)

                    if value > highest:
                        continue

                    # When user has grown out of the reward
                    if value < highest:

                        for reward in rewards:

                            if reward['permanent']:
                                continue
                            if reward['type'] == 'role':
                                role = await get_object(reward, Server.server)
                                if role is None:
                                    continue
                                if role in user.user.roles:
                                    await self.data.client.remove_roles(user.user, role)

                            if reward['type'] == 'channel':
                                channel = await get_object(reward, Server.server)
                                if channel is None:
                                    continue
                                overwrites = channel.overwrites_for(user.user)
                                overwrites.update(read_messages=False)
                                await self.data.client.edit_channel_permissions(channel, user.user, overwrites)
                    #
                    if value == highest:

                        for reward in rewards:

                            if reward['type'] == 'role':
                                role = await get_object(reward, Server.server)
                                if role is None:
                                    continue
                                if role not in user.user.roles:
                                    await self.data.client.add_roles(user.user, role)

                            if reward['type'] == 'channel':
                                channel = await get_object(reward, Server.server)
                                if channel is None:
                                    continue
                                overwrites = channel.overwrites_for(user.user)
                                if not overwrites.read_messages:
                                    overwrites.update(read_messages=True)
                                    await self.data.client.edit_channel_permissions(channel, user.user, overwrites)

    async def ticker(self):
        """
        Run events after some time has passed.

        :return:
        """
        # updates server cookie data and user cookie data
        self.update_cookie_data()
        #

        # Cookie rewards
        await self.reward_users()
        #

    async def reaction_add(self, tup):
        """
        Discord.Client.on_reaction_add().

        :param tup: (discord.Reaction, discord.Member)
        :return:
        """
        reaction, user_giving = tup

        sent_emoji = reaction.emoji
        cookie_emoji = self.data.servers[reaction.message.server.id].config['cookies']['emojis'][0]
        if str(sent_emoji) != cookie_emoji:
            return

        user_receiving = reaction.message.author

        # No giving cookies to yourself
        if user_giving == user_receiving:
            return
        #

        user_giving = self.check_user_config(user_giving)
        user_receiving = self.check_user_config(user_receiving)

        self.transaction(user_giving, user_receiving, reaction.message.server)

    def check_user_config(self, user):
        """
        Check and update user config.

        :param user: discord.Member
        :return:
        """
        user = self.data.servers[user.server.id].load_user(user)
        if 'cookies' not in user.config:
            user.config['cookies'] = self.user_config

        user.config['cookies'] = Utils(self.data).update(self.user_config, user.config['cookies'])
        user.write_config()
        return user

    def check_server_config(self, server):
        """
        Check and update server config.

        :param server: discord.Server
        :return:
        """
        if 'cookies' not in self.data.servers[server.id].config:
            self.data.servers[server.id].config['cookies'] = self.server_config

        self.data.servers[server.id].config['cookies'] = Utils(self.data).update(
            self.server_config, self.data.servers[server.id].config['cookies']
        )
        self.data.servers[server.id].write_config()
        return self.data.servers[server.id]

    @staticmethod
    def calculate_cookie_transfer(server):
        """
        Calculate the amount of cookies that can be transferred per epoch.

        :param server: discord.Server
        :return:
        """
        return int(round(math.log(server.member_count + 1, math.e) * 2 + 5)) * 2

    def calculate_value(self, server):
        """
        Calculate a cookie's value.

        :param server: discord.Server
        :return:
        """
        user_count = server.member_count
        cookie_count = self.data.servers[server.id].config['cookies']['total_cookies']

        # def sigmoid_function(x, v):
        #     return 2*v / (1 + math.e ** (-x/v))

        def full_sigmoid(cookie, user):
            d = user/cookie
            return d * (1 + math.e**-d)/(1 + math.e**-(d**-1))

        if cookie_count == 0:
            return math.inf
        else:
            return full_sigmoid(cookie_count, user_count)

    async def show_full(self, msg):
        """
        Show entire cookie data for a member.

        :param msg: discord.Message
        :return:
        """
        user = self.check_user_config(msg.author)
        data = '\n'.join(['{}: {}'.format(key, value) for (key, value) in user.config['cookies'].items()])
        return {
            'title': 'Cookies for {}:'.format(msg.author.mention),
            'description': '{}\n\n{}'.format(msg.author.mention, data)
        }

    async def show(self, msg):
        """
        Show a member's cookies.

        :param msg: discord.Message
        :return:
        """
        user = self.check_user_config(msg.author)
        self.check_server_config(msg.server)
        return {
            'title': 'Cookies for {}:'.format(msg.author.mention),
            'description': '{}\n\nCookies on hand: {} {}\nCookies in jar: {} {}'.format(
                msg.author.mention, user.config['cookies']['current_cookies'],
                self.data.servers[msg.server.id].config['cookies']['emojis'][0],
                user.config['cookies']['cookies_in_jar'],
                self.data.servers[msg.server.id].config['cookies']['emojis'][1]
            )
        }

    async def set_cookie_emoji(self, msg, arg):
        """
        Set emoji for cookie.

        :param msg: discord.Message
        :param arg: string
        :return:
        """
        self.check_server_config(msg.server)
        emojis = self.data.servers[msg.server.id].config['cookies']['emojis']
        emojis[0] = arg
        self.data.servers[msg.server.id].config['cookies'][emojis] = emojis
        self.data.servers[msg.server.id].write_config()
        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={'title': 'Set server cookie emoji:', 'description': 'Set server cookie to {}'.format(arg)}
            ),
            -1
        )

    async def set_jar_emoji(self, msg, arg):
        """
        Set emoji for cookie jar.

        :param msg: discord.Message
        :param arg: string
        :return:
        """
        self.check_server_config(msg.server)
        emojis = self.data.servers[msg.server.id].config['cookies']['emojis']
        emojis[1] = arg
        self.data.servers[msg.server.id].config['cookies'][emojis] = emojis
        self.data.servers[msg.server.id].write_config()
        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={'title': 'Set server cookie jar emoji:', 'description': 'Set server cookie jar to {}'.format(arg)}
            ),
            -1
        )

    async def give_cookies(self, msg, args=None):
        """
        Give a member cookies.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        if args is None:
            args = []
        values = [None, 1, False]  # receiving_user, amount, over_limit
        argpos = 0
        for i, arg in enumerate(args):
            if argpos == 2:
                break
            if i == 0 and len(args) == 3:
                values[0] = (await Utils(self.data).finder(msg.server, arg, member=True))[0]
                if values[0] is None:
                    return (
                        msg.channel, '',
                        Utils(self.data).error_embed(msg, 'Could not find specified user: ({})'.format(arg)),
                        Utils.add_seconds(datetime.datetime.now(), 60)
                    )
                continue
            if i == 0:
                if argpos == 0:
                    user = (await Utils(self.data).finder(msg.server, arg, member=True))[0]
                    if user is not None:
                        values[0] = user
                        continue
                if arg.isdigit():
                    argpos = 1
                    values[1] = int(arg)
                    continue
                if arg.lower() in ['ol', 'over_limit']:
                    argpos = 2
                    values[2] = True
                    continue
            if i == 1 and len(args) == 3:
                if not arg.isdigit():
                    return (
                        msg.channel, '',
                        Utils(self.data).error_embed(
                            msg, 'Argument in incorrect format. Only digits allowed for amount: ({})'.format(arg)
                        ),
                        Utils.add_seconds(datetime.datetime.now(), 60)
                    )
                values[1] = int(arg)
                continue
            if i == 1:
                if argpos == 0:
                    if arg.isdigit():
                        argpos = 1
                        values[1] = int(arg)
                        continue
                elif argpos == 1:
                    if arg.lower() in ['ol', 'over_limit']:
                        argpos = 2
                        values[2] = True
                        continue
                    else:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg, 'Argument in incorrect format or unrecognized: ({})'.format(arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
            if i == 2:
                if arg.lower() in ['ol', 'over_limit']:
                    argpos = 2
                    values[2] = True
                    continue
                else:
                    return self.arg_not_found(msg, arg)

        if values[0] is None:
            values[0] = msg.author

        # checking if we can use over_limit, if it's enabled
        if values[2]:
            permission = Utils(self.data).permissions(
                msg.author, self.permits['give_cookies_over_limit'], 'cookies', 'give_cookies_over_limit'
            )
            if not permission:
                return self.arg_not_found(msg, values[2])
        # making sure user isn't trying to give themselves cookies without over_limit
        elif values[0].id == msg.author.id:
            return (
                        msg.channel, '',
                        Utils(self.data).error_embed(
                            msg, '**{}**\nTried to give self cookies without over_limit.'.format(msg.content)
                        ),
                        Utils.add_seconds(datetime.datetime.now(), 60)
                    )
        #

        user_giving = self.check_user_config(msg.author)
        user_receiving = self.check_user_config(values[0])

        success = self.transaction(user_giving, user_receiving, msg.server, over_limit=values[2], amount=values[1])
        if not success:
            return (
                        msg.channel, '',
                        Utils(self.data).error_embed(
                            msg, '**{}**\nTried to give cookies over the limit without over_limit.'.format(msg.content)
                        ),
                        Utils.add_seconds(datetime.datetime.now(), 60)
                    )

        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={
                    'title': 'Gave user cookies:', 'description': 'Gave {}:{} {} cookies.'.format(
                        user_receiving.user.id, user_receiving.user.mention, values[1]
                    )
                }
            ),
            Utils.add_seconds(datetime.datetime.now(), 60)
        )

    async def add_cookie_rewards(self, msg, args):
        """
        Add specified rewards.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        pairs = []
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
            try:
                arg2 = float(args[i + 1])
                if arg2 > 1 or arg2 < 0:
                    return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid value supplied for "amount": ``{}``. Amount must be between 0 and 1.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
            except ValueError:
                return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid argument supplied for "amount":``{}``.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
            if len(args) > i + 2 and args[i + 2].lower() in ['p', 'perm', 'permanent']:
                skip += 1
                pairs.append(((role, channel), arg2, True))
            else:
                pairs.append(((role, channel), arg2, False))

        cookie_rewards = self.check_server_config(msg.server).config['cookies']['cookie_rewards']

        values = []

        for pair in pairs:

            role, channel = pair[0]
            value = pair[1]
            permanent = pair[2]

            if value not in values:
                values.append(value)

            if value not in cookie_rewards:
                cookie_rewards.update({value: []})
            if channel is not None:
                cookie_rewards[value].append({
                    'id': channel.id, 'name': channel.name, 'permanent': permanent, 'type': 'channel'
                })
            else:
                cookie_rewards[value].append({
                    'id': role.id, 'name': role.name, 'permanent': permanent, 'type': 'role'
                })

        self.data.servers[msg.server.id].config['cookies']['cookie_rewards'] = cookie_rewards

        fields = []
        for value in values:
            s = ''
            for item in self.data.servers[msg.server.id].config['cookies']['cookie_rewards'][value]:
                s += '{}\n'.format(item)
            fields.append({'header': '{}:'.format(value), 'text': s})

        self.data.servers[msg.server.id].write_config()

        return (
            msg.channel, '',
            Embed(
                self.data, msg, js={'title': 'Added rewards for cookie values:', 'fields': fields}
            ),
            -1
        )

    async def remove_cookie_rewards(self, msg, args):
        """
        Remove specified cookie rewards.

        :param msg: discord.Message
        :param args: list - list of strings
        :return:
        """
        skip = 0
        pairs = []
        server = self.check_server_config(msg.server)
        for i, arg in enumerate(args):
            if skip:
                skip -= 1
                continue

            try:
                arg1 = float(arg)
                if arg1 > 1 or arg1 < 0:
                    return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid value supplied for "amount": ``{}``. Amount must be between 0 and 1.'
                                .format(msg.content, arg)
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
            except ValueError:
                return (
                    msg.channel, '',
                    Utils(self.data).error_embed(
                        msg,
                        '**{}**\nInvalid argument supplied for "amount" for ``{}``.'
                        .format(msg.content, arg)
                    ),
                    Utils.add_seconds(datetime.datetime.now(), 60)
                )

            if str(arg1) not in server.config['cookies']['cookie_rewards']:
                return self.arg_not_found(msg, arg)

            role, channel = None, None

            if len(args) > i + 1:

                member, channel, role = await Utils(self.data).finder(msg.server, args[i + 1], channel=True, role=True)

                if role is None and channel is None:
                    try:
                        float(args[i+1])
                    except ValueError:
                        return (
                            msg.channel, '',
                            Utils(self.data).error_embed(
                                msg,
                                '**{}**\nInvalid argument supplied ``{}`` - not recognized channel or role.'
                                .format(msg.content, args[i + 1])
                            ),
                            Utils.add_seconds(datetime.datetime.now(), 60)
                        )
                else:
                    skip += 1
            pairs.append((str(arg1), (role, channel)))

        for pair in pairs:

            role, channel = pair[1]
            value = pair[0]

            if role is not None or channel is not None:
                rewards = []
                for reward in server.config['cookies']['cookie_rewards'][value]:
                    if (role is not None and reward['type'] == 'role' and reward['id'] == role.id) or \
                            (channel is not None and reward['type'] == 'channel' and reward['id'] == channel.id):
                        rewards.append(reward)
                for reward in rewards:
                    self.data.servers[msg.server.id].config['cookies']['cookie_rewards'][value].remove(reward)
            else:
                self.data.servers[msg.server.id].config['cookies']['cookie_rewards'].pop(value)

        self.data.servers[msg.server.id].write_config()
        return (
            msg.channel, '',
            Embed(self.data, msg, js={'title': 'Removed rewards.'}),
            -1
        )

    async def show_cookie_rewards(self, msg):
        """
        Show cookie rewards.

        :param msg: discord.Message
        :return:
        """
        config = copy.deepcopy(self.check_server_config(msg.server).config['cookies']['cookie_rewards'])

        return {
            'title': 'Current cookie rewards:',
            'fields': Utils.convert_json_to_fields(config, func=lambda m: '\n'.join([str(val) for val in m]))
        }

    async def show_cookie_data(self, msg):
        """
        Show cookie data.

        :param msg: discord.Message
        :return:
        """
        data, embeds = self.calculate_cookie_reward(self.check_server_config(msg.server))

        return [(msg.channel, '', Embed(self.data, msg, js=embed), -1) for embed in embeds]

    async def jar_cookies(self, msg, amount):

        try:
            amount = int(amount)
        except ValueError:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(
                    msg, 'Argument in incorrect format. Only digits allowed for amount: ({})'.format(amount)
                ),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        user = self.check_user_config(msg.author)
        if user.config['cookies']['current_cookies'] < amount:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(
                    msg, 'Not enough cookies on hand to deposit supplied amount ``{}``.'.format(amount)
                ),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        user.config['cookies']['current_cookies'] = user.config['cookies']['current_cookies'] - amount
        user.config['cookies']['cookies_in_jar'] = user.config['cookies']['cookies_in_jar'] + amount

        user.write_config()

        server = self.check_server_config(msg.server)
        server.config['cookies']['cookie_jar'] = server.config['cookies']['cookie_jar'] + amount

        server.write_config()

        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={
                    'title': 'Added cookies to the jar:',
                    'description': 'Sent {} {} <- {}'
                    .format(amount, server.config['cookies']['emojis'][0], server.config['cookies']['emojis'][1])
                   }
            ),
            Utils.add_seconds(datetime.datetime.now(), 60)
        )

    async def unjar_cookies(self, msg, amount):

        try:
            amount = int(amount)
        except ValueError:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(
                    msg, 'Argument in incorrect format. Only digits allowed for amount: ({})'.format(amount)
                ),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        user = self.check_user_config(msg.author)
        if user.config['cookies']['cookies_in_jar'] < amount:
            return (
                msg.channel, '',
                Utils(self.data).error_embed(
                    msg, 'Not enough cookies in jar to withdraw supplied amount ``{}``.'.format(amount)
                ),
                Utils.add_seconds(datetime.datetime.now(), 60)
            )

        user.config['cookies']['cookies_in_jar'] = user.config['cookies']['cookies_in_jar'] - amount
        user.config['cookies']['current_cookies'] = user.config['cookies']['current_cookies'] + amount

        user.write_config()

        server = self.check_server_config(msg.server)
        server.config['cookies']['cookie_jar'] = server.config['cookies']['cookie_jar'] - amount

        server.write_config()

        return (
            msg.channel, '',
            Embed(
                self.data, msg,
                js={
                    'title': 'Took cookies from the jar:',
                    'description': 'Sent {} {} <- {}'
                    .format(amount, server.config['cookies']['emojis'][0], server.config['cookies']['emojis'][1])
                   }
            ),
            Utils.add_seconds(datetime.datetime.now(), 60)
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
                elif arg == 'show_full' or arg == 'show' or arg == 'show_cookie_rewards':
                    embed = await eval('self.{}(msg)'.format(arg))
                    embed = Embed(self.data, msg, js=embed)
                    commands.append((msg.channel, '', embed, Utils.add_seconds(datetime.datetime.now(), 60)))
                elif arg == 'set_cookie_emoji' or arg == 'set_jar_emoji' or arg == 'jar_cookies' or \
                        arg == 'unjar_cookies':
                    if len(args) > i + 1:
                        commands.append((await eval('self.{}(msg, args[i + 1])'.format(arg))))
                        skip += 1
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'give_cookies':
                    if len(args) > i + 3:
                        commands.append((
                            await eval(
                                'self.{}(msg, args=args[i+1:i+4])'.format(arg)
                            )
                        ))
                        skip += 3
                    elif len(args) > i + 2:
                        commands.append((await eval('self.{}(msg, args=args[i+1:i+3])'.format(arg))))
                        skip += 2
                    elif len(args) > i + 1:
                        commands.append((await eval('self.{}(msg, args=args[i+1:i+2])'.format(arg))))
                        skip += 1
                    else:
                        commands.append((await eval('self.{}(msg)'.format(arg))))
                elif arg == 'add_cookie_rewards':
                    if len(args) > i + 2:
                        commands.append((
                            await eval(
                                'self.{}(msg, args=args[i+1:])'.format(arg)
                            )
                        ))
                        skip += len(args[i+1])
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'remove_cookie_rewards':
                    if len(args) > i + 1:
                        commands.append((
                            await eval(
                                'self.{}(msg, args=args[i+1:])'.format(arg)
                            )
                        ))
                        skip += 1
                    else:
                        commands.append(self.insufficient_args(msg))
                elif arg == 'show_cookie_data':
                    embeds = await self.show_cookie_data(msg)
                    commands += embeds
            else:  # Command not found or not available for use.
                commands.append(self.arg_not_found(msg, arg))
        return commands
