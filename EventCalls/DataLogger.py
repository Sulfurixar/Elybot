class DataLogger(object):

    def __init__(self, data):
        self.data = data

    async def server_update(self, tup):
        before, after = tup
        server = self.data.servers[after.id]
        server.check_region()
        server.check_name()
        server.check_owner()
        server.write_config()

    async def server_join(self, discord_server):
        discord_server, = discord_server
        self.data.load_server(discord_server)

    async def server_remove(self, discord_server):
        discord_server, = discord_server
        self.data.servers[discord_server.id].write_config()
        self.data.servers.pop(discord_server.id)

    async def server_role_create(self, role):
        role, = role
        server = self.data.servers[role.server.id]
        server.check_roles()
        server.write_config()

    async def server_role_delete(self, role):
        role, = role
        server = self.data.servers[role.server.id]
        server.check_roles()
        server.write_config()

    async def server_role_update(self, tup):
        before, after = tup
        server = self.data.servers[after.server.id]
        server.check_roles()
        server.write_config()

    async def server_available(self, discord_server):
        discord_server, = discord_server
        server = self.data.servers[discord_server.id]
        server.check_config_values()
        server.write_config()

    async def server_unavailable(self, discord_server):
        discord_server, = discord_server
        server = self.data.servers[discord_server.id]
        server.check_availabiliy()
        server.write_config()

    async def member_ban(self, member):
        member, = member
        server = self.data.servers[member.server.id]
        user = server.load_user(member)
        user.update_value('bans', 'banned')
        user.write_config()

    async def member_unban(self, tup):
        discord_server, user = tup
        server = self.data.servers[discord_server.id]
        user = server.load_user(user)
        user.update_value('bans', 'unbanned')
        user.write_config()

    async def member_join(self, member):
        member, = member
        server = self.data.servers[member.server.id]
        user = server.load_user(member)
        user.update()

    async def member_update(self, tup):
        before, after = tup
        server = self.data.servers[after.server.id]
        user = server.load_user(after)
        user.update()

    async def voice_state_update(self, tup):
        before, after = tup
        server = self.data.servers[after.server.id]
        user = server.load_user(after)
        user.check_voice()
        user.write_config()

    async def message(self, msg):
        msg, = msg
        discord_user = msg.author
        discord_server = msg.server
        channel = msg.channel

        server = self.data.servers[discord_server.id]
        server.update_activity(discord_user, channel)
        server.write_config()

        user = server.load_user(discord_user)
        user.update_activity(channel)
        user.write_config()
