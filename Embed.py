import dateparser
import discord


class Embed:

    def __init__(self, data, msg, js=None, error=False, developer=False, help=False):
        self.embed = discord.embeds.Embed()
        self.error = error
        self.developer = developer
        self.help = help
        self.data = data
        self.msg = msg
        self.js = js
        if help:
            self.embed.colour = int(str(data.servers[msg.server.id].config['embed_colours']['help']), 0)
        elif error:
            self.embed.colour = int(str(data.servers[msg.server.id].config['embed_colours']['error']), 0)
        elif developer:
            self.embed.colour = int(str(data.servers[msg.server.id].config['embed_colours']['developer']), 0)
        else:
            self.embed.colour = int(str(data.servers[msg.server.id].config['embed_colours']['default']), 0)
        if js is not None:
            self.unconfigured = self.configure_embed(js)
        else:
            self.embed = discord.Embed.Empty

    def configure_embed(self, js):

        structure = {
            'title': '',
            'type': '',
            'description': '',
            'url': '',
            'timestamp': '',
            'colour': '',
            'footer': {
                'text': '',
                'icon_url': ''
            },
            'image': '',
            'thumbnail': '',
            'video': '',  # needs testing, not implemented yet
            'author': {
                'name': '',
                'url': '',
                'icon_url': ''
            },
            'fields': [
                {
                    'header': '',
                    'text': '',
                    'inline': True
                },
                {
                    'name': '',
                    'value': '',
                    'inline': True
                }
            ]
        }

        unrecognized = []
        for key, value in js.items():
            key = key.lower()
            if key not in structure:
                unrecognized.append('{}: {}; Reason: unrecognised!'.format(key, value))
                continue
            try:
                if key == 'title':
                    self.embed.title = str(value)
                if key == 'type':
                    self.embed.type = str(value)
                if key == 'description':
                    self.embed.description = str(value)
                if key == 'url':
                    self.embed.url = str(value)
                if key == 'timestamp':
                    time = dateparser.parse(value)
                    self.embed.timestamp = time
                if key == 'colour' or key == 'color':
                    if value.startswith('0x'):
                        value = int(value[2:], 16)
                    elif value.startswith('#'):
                        value = int(value[1:], 16)
                    else:
                        value = int(value)
                    self.embed.colour = value
                if key == 'footer':
                    text = discord.Embed.Empty
                    icon_url = discord.Embed.Empty
                    for _key, _value in value.items():
                        if _key == 'text':
                            text = str(_value)
                        if _key == 'icon_url':
                            icon_url = str(_value)
                    self.embed.set_footer(text=text, icon_url=icon_url)
                if key == 'image':
                    self.embed.set_image(url=str(value))
                if key == 'thumbnail':
                    self.embed.set_thumbnail(url=str(value))
                if key == 'author':
                    name = ''
                    url = discord.Embed.Empty
                    icon_url = discord.Embed.Empty
                    for _key, _value in value.items():
                        if _key == 'name':
                            name = str(_value)
                        if _key == 'url':
                            url = str(_value)
                        if _key == 'icon_url':
                            icon_url = str(_value)
                    self.embed.set_author(name=name, url=url, icon_url=icon_url)
                if key == 'fields':
                    for dictionary in value:
                        header = '',
                        text = ''
                        inline = True
                        for _key, _value in dictionary.items():
                            if _key == 'header' or _key == 'name':
                                header = str(_value)
                            if _key == 'text' or _key == 'value':
                                text = str(_value)
                            if _key == 'inline':
                                inline = bool(_value)
                        self.embed.add_field(name=header, value=text, inline=inline)
            except Exception as e:
                print(e)
                unrecognized.append('{}: {}; Reason: Error!!!'.format(key, value))
                self.data.error()

        return unrecognized
