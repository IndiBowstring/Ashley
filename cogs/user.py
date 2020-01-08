import discord
import asyncio
from cogs.logger import logger
from discord.ext import commands
import json
import loaduserdata


class PlayerWrapper:
    def __init__(self, bot):
        self.bot = bot

    # Member functions to manage Player PC's
    class Player:
        def __init__(self, member=None, load_from_dict={}):
            if load_from_dict:
                self.UID = load_from_dict.get('UID')
            else:
                self.UID = member.id

            self.player_character_dict = {}

        def addPlayerCharacter(self, name, pc):
            self.player_character_dict[name] = pc

        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__)

    # Container for PC variables
    class PlayerCharacter:
        def __init__(self, downtime=0, xp=0, load_from_dict={}):

            if load_from_dict:
                self.downtime = load_from_dict.get('downtime')
                self.xp = load_from_dict.get('xp')
            else:
                self.downtime = downtime
                self.xp = xp

        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__)

        def addDowntime(self, dt):
            self.downtime = self.downtime + dt

        def addXp(self, xp):
            self.xp = self.xp + xp

    @commands.command(aliases=['nc'], pass_context=True)
    async def newCharacter(self, ctx: commands.Context, name: str):
        name = name.lower()
        if ctx.message.author.id in loaduserdata.__playerData__:
            if loaduserdata.__playerData__[ctx.message.author.id].PCdict.get(name) is not None:
                logger.info(f'{ctx.message.author} attempted to make {name} who already exists.')
                await self.bot.send_message(ctx.message.author, f"Character \"{name}\" already exists.")
            else:
                _new_player_character = self.PlayerCharacter()
                loaduserdata.__playerData__[ctx.message.author.id].PCdict[name] = _new_player_character
                loaduserdata.savedata()
                logger.info(f'Character {name} added to {ctx.message.author}')
                await self.bot.send_message(ctx.message.author, f"Character \"{name}\" created!")

    @commands.command(aliases=['dc'], pass_context=True)
    async def delCharacter(self, ctx: commands.Context, name: str):
        if ctx.message.author.id in loaduserdata.__playerData__:
            try:
                loaduserdata.__playerData__[ctx.message.author.id].PCdict.pop(name)
                loaduserdata.savedata()
                logger.info(f'Character {name} deleted from {ctx.message.author}')
                await self.bot.send_message(ctx.message.channel, f"Character \"{name}\" deleted!")
            except Exception as e:
                err = repr(e)
                logger.info(f'{err} Unable to delete Character {name}')
                await self.bot.send_message(ctx.message.channel, f"\"{name}\" does not exist.")

    @commands.command(aliases=['dt'], pass_context=True)
    async def downtime(self, ctx: commands.Context):
        _message = ".\n"
        for key, pc in loaduserdata.__playerData__[ctx.message.author.id].PCdict.items():
            _message = _message + key + ": " + str(pc.downtime) + "\n"
        await self.bot.send_message(ctx.message.channel, _message)

    @commands.command(aliases=['xp'], pass_context=True)
    async def experience(self, ctx: commands.Context):
        _message = ".\n"
        for key, pc in loaduserdata.__playerData__[ctx.message.author.id].PCdict.items():
            _message = _message + key + ": Level " + str(pc.level) + " [" + str(pc.xp) + "/" + str(
                xpToLevelList[pc.level]) + "]" + "\n"
        await self.bot.send_message(ctx.message.channel, _message)

    @commands.command(aliases=['udt'], pass_context=True)
    async def useDowntime(self, ctx: commands.Context, pc: str, amt: int):
        try:
            if amt <= 0 or amt > loaduserdata.__playerData__[ctx.message.author.id].PCdict[pc].downtime:
                raise ValueError('Invalid downtime value given.')
            else:
                loaduserdata.__playerData__[ctx.message.author.id].addDowntime(pc, amt)

                logger.info(f'{amt} downtime subtracted from {pc}, User: {ctx.message.author}')
                loaduserdata.savedata()
                await self.bot.send_message(ctx.message.channel, f'Successfully used {amt} downtime!')

        except Exception as e:
            err = repr(e)
            logger.warning(f'{err} User: {ctx.message.author}')
            await self.bot.send_message(ctx.message.channel, 'Sorry, something is wrong!')

        loaduserdata.savedata()

    @commands.command(aliases=['ax', 'axp'], pass_context=True)
    async def addXp(self, ctx: commands.Context, pc: str, amt: int):
        try:
            if amt <= 0:
                raise ValueError('Invalid xp value given.')
            else:
                loaduserdata.__playerData__[ctx.message.author.id].PCdict[pc].addXp(amt)

                logger.info(f'{amt} xp added to {pc}, User: {ctx.message.author}')
                loaduserdata.savedata()
                await self.bot.send_message(ctx.message.channel, f'Successfully added {amt} xp!')

        except Exception as e:
            err = repr(e)
            logger.warning(f'{err} User: {ctx.message.author}')
            print(err)
            await self.bot.send_message(ctx.message.channel, 'Sorry, something is wrong!')


def setup(bot):
    bot.add_cog(PlayerWrapper(bot))
