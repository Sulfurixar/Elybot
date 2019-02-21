from Utils import Utils
from Embed import Embed
import traceback
import datetime
import discord
import copy
import sys
import re


class CommandCaller(object):

    def __init__(self, data):
        self.data = data
        self.error_buffer = []
        try:
            self.prefix = data.config['commands']['prefix']
        except KeyError:
            self.prefix = 'e!'
        try:
            self.ai = data.config['commands']['use_ai']
        except KeyError:
            self.ai = False

    def error(self):
        exc_type, exc_value, tb = sys.exc_info()
        if len(self.error_buffer) > 0:
            if self.error_buffer[-1] != exc_type:
                self.error_buffer.append(exc_type)
                traceback.print_tb(tb, limit=30)
                print(exc_type)
        else:
            self.error_buffer.append(exc_type)
            traceback.print_tb(tb, limit=30)
            print(exc_type)
        if len(self.error_buffer) > 10:
            self.error_buffer.pop(0)

    async def message(self, msg):
        msg, = msg

        if msg.author.id == self.data.client.user.id:
            return  # Bot won't accept commands from itself

        if not msg.content.startswith(self.prefix):
            if self.ai:
                if self.data.client.user.id in msg.raw_mentions:
                    try:
                        await self.ai_handle(msg)
                    except Exception as e:
                        print(e)
                        self.error()
            else:
                return  # AI not enabled and message didn't start with the prefix
        try:
            await self.command_handle(msg.content[len(self.prefix):], msg)  # we received a traditional command :)
        except Exception as e:
            print(e)
            self.error()

    async def ai_handle(self, msg):
        pass

    def get_aliases(self):
        aliases = []
        alias_command = []
        disabled_aliases = []
        disabled_command = []
        for cmd in self.data.command_calls:
            for alias in self.data.command_calls[cmd](self.data).aliases:
                if alias not in aliases and alias not in disabled_aliases:
                    aliases.append(alias)
                    alias_command.append(cmd)
                else:
                    i = aliases.index(alias)
                    disabled_aliases.append(aliases[i])
                    disabled_command.append(alias_command[i])
                    aliases.pop(i)
                    alias_command.pop(i)
                    disabled_aliases.append(alias)
                    disabled_command.append(cmd)
        s = 'Disabled aliases: '
        for i in range(len(disabled_aliases)):
            s += '{}: {};'.format(disabled_command[i], disabled_aliases[i])

        return aliases, alias_command, disabled_aliases, disabled_command

    async def send_message(self, channel, author, msg, embed, time):
        server = self.data.servers[channel.server.id]
        sent_messages = server.config['sent_messages']
        if author.id in sent_messages:
            if len(sent_messages[author.id]) >= 10:
                try:
                    self.data.client.logs_from(
                        server.server.get_channel(sent_messages[author.id][0][0]),
                        around=Utils.get_full_time(sent_messages[author.id][0][2]).utcnow()
                    )
                    try:
                        sent_message = await self.data.client.get_message(
                            server.server.get_channel(sent_messages[author.id][0][0]),
                            sent_messages[author.id][0][1]
                        )
                        await self.data.client.delete_message(sent_message)
                    except Exception as e:
                        if e is discord.HTTPException:
                            self.data.error()
                except Exception as e:
                    if e is discord.HTTPException:
                        self.data.error()
                self.data.servers[channel.server.id].config['sent_messages'][author.id].pop(0)
        if time != -1:
            time = Utils.get_full_time_string(time)

        if embed.js is None:
            embed.embed = discord.Embed.Empty

        if embed.embed is discord.Embed.Empty:
            if msg is None or msg == '':
                return  # there is no message to send
            send_message = self.data.client.send_message(channel, msg)
        else:
            send_message = self.data.client.send_message(channel, msg, embed=embed.embed)
            
        print("send_message")
        if author.id not in self.data.servers[channel.server.id].config['sent_messages']:
            self.data.servers[channel.server.id].config['sent_messages'][author.id] = [[
                channel.id,
                (await send_message).id,
                Utils.get_full_time_string(),
                time
            ]]
        else:
            self.data.servers[channel.server.id].config['sent_messages'][author.id].append([
                channel.id,
                (await send_message).id,
                Utils.get_full_time_string(),
                time
            ])

    def text_splitter(self, text, split_level=0):
        levels = ['\n', '.', '!', '?', ' ']
        limit = 1950
        if not isinstance(text, list):
            text = [text]
        lines = []
        for line in text:
            if len(line) > limit:
                splits = line.split(levels[split_level])
                for i, split in enumerate(splits):
                    splits[i] = split + levels[split_level]
                skip = 0
                add = ''
                for i, split in enumerate(splits):
                    if skip:
                        skip -= 1
                        continue
                    if len(split) < limit:
                        while len(add) < limit:
                            if len(splits) > i + skip:
                                if len(add + splits[i + skip]) < limit:
                                    add += splits[i + skip]
                                    skip += 1
                                else:
                                    break
                            else:
                                break
                    else:
                        lines.append(split)
                    if add != '':
                        lines.append(add)
                    add = ''
            else:
                lines.append(line)
        needs_shortening = False
        for line in lines:
            if len(line) > limit:
                needs_shortening = True
        if needs_shortening:
            lines = self.text_splitter(lines, split_level=split_level + 1)
        return lines

    def embed_splitter(self, embed):
        if embed.embed is not discord.Embed.Empty:
            js = embed.embed.to_dict()
        else:
            return [embed]
        limit = 1950
        if not len(str(js)) > limit:
            return [embed]
        if 'fields' in js:
            fields = copy.deepcopy(js['fields'])
        else:
            fields = []
        if 'description' in js:
            description = copy.deepcopy(js['description'])
        else:
            description = '__   __'
        js['description'] = '__   __'
        js['fields'] = []
        embeds = []
        if len(js['description']) > limit:
            descriptions = self.text_splitter(description)
        else:
            descriptions = [copy.deepcopy(description)]
        for description in descriptions:
            njs = copy.deepcopy(js)
            njs['description'] = description
            embeds.append(
                Embed(self.data, embed.msg, js=njs, error=embed.error, developer=embed.developer, help=embed.help)
            )
        nfields = []
        skip = 0
        for i, field in enumerate(fields):
            if skip:
                skip -= 1
                continue
            if len(str(field)) < limit:
                while len(str(nfields)) < limit - 500:
                    if len(fields) > i + skip:
                        if len(str(nfields) + str(fields[i+skip])) < limit-500:
                            nfields.append(fields[i+skip])
                            skip += 1
                        else:
                            skip -= 1
                            break
                    else:
                        skip -= 1
                        break
            else:
                field['value'] = 'Field value too long.'
                nfields.append(field)
            if len(nfields) > 0:
                njs = copy.deepcopy(js)
                njs['fields'] = nfields
                embeds.append(
                    Embed(self.data, embed.msg, js=njs, error=embed.error, developer=embed.developer, help=embed.help)
                )
            nfields = []
        return embeds

    async def command_handle(self, content, msg):
        args = []
        if ' ' in content:
            args = content.split(' ')
            command = args[0]
            args = ' '.join(args[1:])
        else:
            command = content

        if len(args):
            args = re.findall(r'\[.*\]|{.*}|"[^"]*"|\'[^\']*\'|[^ ]*', args)
            args = list(filter(None, args))
            for i, arg in enumerate(args):
                if arg.startswith('"') or arg.startswith("'"):
                    arg = arg[1:]
                if arg.endswith('"') or arg.endswith("'"):
                    arg = arg[:-1]
                args[i] = arg

        # make sure no aliases overlap
        aliases, alias_command, disabled_aliases, disabled_command = self.get_aliases()
        if command in aliases:
            i = aliases.index(command)
            responses = await self.data.command_calls[alias_command[i]](self.data).execute(msg, args=args)
            for response in responses:
                channel, message, embed, time = response

                for line in list(filter(None, self.text_splitter(message))):
                    await self.send_message(channel, msg.author, line, Embed(self.data, msg), time)
                for embed in self.embed_splitter(embed):
                    await self.send_message(channel, msg.author, '', embed, time)
            await self.data.client.delete_message(msg)
            return

        elif command in disabled_aliases:
            embed = Utils(self.data).error_embed(msg, "That alias ({}) is currently disabled.".format(command))
        else:
            embed = Utils(self.data).error_embed(msg, "Unrecognized command ({}).".format(command))
        await self.send_message(msg.channel, msg.author, '', embed, Utils.add_seconds(datetime.datetime.now(), 60))
        await self.data.client.delete_message(msg)
