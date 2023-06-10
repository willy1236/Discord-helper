import discord,asyncio
from datetime import datetime, timezone, timedelta,time
from discord.ext import commands,tasks
from ctypes import CDLL
import copy

from core.classes import Cog_Extension
from starcord import Jsondb
from starcord.errors import *
from starcord.type.game import DatabaseGame
from starcord.rpg.map import sunmon_area

tz = timezone(timedelta(hours=+8))

# Note that custom_ids can only be up to 100 characters long.
class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Green",style=discord.ButtonStyle.green,custom_id="persistent_view:green")
    async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)

    @discord.ui.button(label="Red", style=discord.ButtonStyle.red, custom_id="persistent_view:red")
    async def red(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is red.", ephemeral=True)

    @discord.ui.button(label="Grey", style=discord.ButtonStyle.grey, custom_id="persistent_view:grey")
    async def grey(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("This is grey.", ephemeral=True)

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Short Input"))
        self.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="Short Input", value=self.children[0].value)
        embed.add_field(name="Long Input", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])

class RPG_advanture_panel(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.map_l = 15
        self.map_w = 15
        self.area = sunmon_area(self.map_l,self.map_w)
        self.player_x = 0
        self.player_y = 0
        self.text = ''
        
    def map_display(self):
        self.text = ''
        area_display = copy.deepcopy(self.area)
        area_display[self.player_y][self.player_x] = '2'
        for i in area_display:
            self.text += " ".join(i) + '\n'
        return self.text

    @discord.ui.button(label="↑",style=discord.ButtonStyle.green)
    async def up(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_y != 0 and self.area[self.player_y-1][self.player_x] == '0':
            self.player_y -= 1
            await interaction.response.edit_message(content=self.map_display(),view=self)
        else:
            await interaction.response.edit_message(content=self.text,view=self)

    @discord.ui.button(label="↓",style=discord.ButtonStyle.green)
    async def down(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_y != self.map_l-1 and self.area[self.player_y+1][self.player_x] == '0':
            self.player_y += 1
            await interaction.response.edit_message(content=self.map_display(),view=self)
        else:
            await interaction.response.edit_message(content=self.text,view=self)

    @discord.ui.button(label="←",style=discord.ButtonStyle.green)
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_x != 0 and self.area[self.player_y][self.player_x-1] == '0':
            self.player_x -= 1
            await interaction.response.edit_message(content=self.map_display(),view=self)
        else:
            await interaction.response.edit_message(content=self.text,view=self)
    
    @discord.ui.button(label="→",style=discord.ButtonStyle.green)
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_x != self.map_w-1 and self.area[self.player_y][self.player_x+1] == '0':
            self.player_x += 1
            await interaction.response.edit_message(content=self.map_display(),view=self)
        else:
            await interaction.response.edit_message(content=self.text,view=self)

class debug(Cog_Extension):
    pass
    @commands.slash_command(description='測試指令')
    async def test(self,ctx):
        await ctx.defer()
        view = RPG_advanture_panel()
        await ctx.respond(view.map_display(),view=view)

    # @commands.slash_command()
    # async def modal_slash(self,ctx: discord.ApplicationContext):
    #     """Shows an example of a modal dialog being invoked from a slash command."""
    #     modal = MyModal(title="Modal Slash Command")
    #     await ctx.send_modal(modal)
    
    # @commands.command()
    # @commands.is_owner()
    # async def embed(self,ctx,msg):
    #     embed=discord.Embed(title="Bot Radio Station",description=f'{msg}',color=0xc4e9ff)
    #     embed.set_footer(text='廣播電台 | 機器人全群公告')
    #     await ctx.send(embed=embed)

    # @commands.command()
    # @commands.is_owner()
    # async def debug(self,ctx,role):
    #     role = await find.role(ctx,role)
    #     dict = {}
    #     dict[str(role.id)] = {}
    #     dict[str(role.id)]['name']=role.name
    #     dict[str(role.id)]['color']=role.color.to_rgb()
    #     dict[str(role.id)]['time']=role.created_at.strftime('%Y%m%d')
    #     print(dict)
    
    # @commands.command()
    # @commands.is_owner()
    # async def task_test(self, ctx,arg):
    #     task = tasks.Loop.get_task(arg)
    #     print(task)
    #     if task:
    #         ctx.send(task.is_running())
    #     else:
    #         ctx.send('Not found')

    # @commands.command()
    # @commands.is_owner()
    # async def prepare(self,ctx: commands.Context):
    #     """Starts a persistent view."""
    #     # In order for a persistent view to be listened to, it needs to be sent to an actual message.
    #     # Call this method once just to store it somewhere.
    #     # In a more complicated program you might fetch the message_id from a database for use later.
    #     # However this is outside of the scope of this simple example.
    #     await ctx.send("What's your favourite colour?", view=PersistentView(self))
    
    # @commands.command()
    # @commands.is_owner()
    # async def derole(self,ctx: commands.Context):
    #     role = self.bot.get_guild(613747262291443742).get_role(706794165094187038)
    #     channel = self.bot.get_channel(706810474326655026)
    #     permission = discord.Permissions(view_channel=True)
    #     #overwrites = {}
    #     for user in role.members:
    #         #overwrites[user] = discord.PermissionOverwrite(view_channel=True)    
    #         await channel.set_permissions(user,view_channel=True)
    #         await asyncio.sleep(0.5)
    #     await ctx.message.add_reaction('✅')

def setup(bot):
    bot.add_cog(debug(bot))