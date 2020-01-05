import discord
import asyncio
from cogs.logger import logger
from discord.ext import commands
import json
import loaduserdata

xpToLevelList = [0, 0, 0, 0, 0, 10, 15, 20, 25, 30, 40, 40, 40, 40, 40, 40, 80, 120, 160, 200, 400]
playerClassList = ["bard", "barbarian", "fighter"]
START_LEVEL = 5


class PlayerWrapper():
    def __init__(self, bot):
        self.bot = bot

    # Member functions to manage Player PC's
    class Player():
        def __init__(self, bot=None, member=None, load_from_dict={}):
            if (load_from_dict):
                self.UID = load_from_dict.get('UID')
            else:
                self.UID = member.id

            self.PCdict = {}

        def addPC(self, name, pc):
            self.PCdict[name] = pc

        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__)

    # Container for PC variables
    class PC():
        def __init__(self, downtime=0, level=0, xp=0, playerclass=[], load_from_dict={}):

            if (load_from_dict):
                self.downtime = load_from_dict.get('downtime')
                self.level = load_from_dict.get('level')
                self.xp = load_from_dict.get('xp')
                self.playerclass = load_from_dict.get('playerclass')
            else:
                self.downtime = downtime
                self.level = level
                self.xp = xp
                self.playerclass = playerclass

        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__)

        def addDowntime(self, dt):
            self.downtime = self.downtime + dt

        def addXp(self, xp):
            self.xp = self.xp + xp
            if not self.level == 20:
                while self.xp >= xpToLevelList[self.level]:
                    self.levelUp()
                    self.addPlayerClass()

        def addPlayerClass(self, _playerClass):
            print(_playerClass)
            print(playerClassList)
            if _playerClass in playerClassList:
                self.playerclass.append(_playerClass)

        def levelUp(self):
            self.xp = self.xp - xpToLevelList[self.level]
            self.level = self.level + 1
            print("levelup")

    @commands.command(aliases=['nc'], pass_context=True)
    async def newCharacter(self, ctx: commands.Context, name: str):
        name = name.lower()
        if ctx.message.author.id in loaduserdata.__playerData__:
            if loaduserdata.__playerData__[ctx.message.author.id].PCdict.get(name) != None:
                logger.info(f'{ctx.message.author} attempted to make {name} who already exists.')
                await self.bot.send_message(ctx.message.author, f"Character \"{name}\" already exists.")
            else:
                newpc = self.PC()
                while (len(newpc.playerclass) < START_LEVEL):
                    await self.bot.send_message(ctx.message.author,
                                                f"You still have {(START_LEVEL - len(newpc.playerclass))} levels without classes.  Please type your class name, followed by how many levels you have in the class.  e.g. \"bard 5\"")
                    msg = await self.bot.wait_for_message(timeout=180, author=ctx.message.author)
                    if msg:
                        newpc.addPlayerClass(msg.content)
                        print(newpc.playerclass)

                    elif msg is None:
                        await self.bot.send_message(ctx.message.author, f"Character creation has timed out.")
                        return

                loaduserdata.__playerData__[ctx.message.author.id].PCdict[name] = newpc
                loaduserdata.savedata()
                logger.info(f'Character {name} added to {ctx.message.author}')
                newpc = None  # For some reason newpc isn't being cleared once it goes out of scope, investigate later
                try:
                    print(newpc.playerclass)
                except Exception:
                    print("Nonetype")
                await self.bot.send_message(ctx.message.author, f"Character \"{name}\" created!")

    @commands.command(aliases=['dc'], pass_context=True)
    async def delCharacter(self, ctx: commands.Context, name: str):
        if ctx.message.author.id in loaduserdata.__playerData__:
            try:
                loaduserdata.__playerData__[ctx.message.author.id].PCdict.pop(name)
                loaduserdata.savedata()
                logger.info(f'Character {name} deleted from {ctx.message.author}')
                await self.bot.send_message(ctx.message.channel, f"Character \"{name}\" deleted!")
            except Exception as err:
                errlog = repr(err)
                logger.info(f'{errlog} Unable to delete Character {name}')
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

        except Exception as err:
            errlog = repr(err)
            logger.warning(f'{errlog} User: {ctx.message.author}')
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

        except Exception as err:
            errlog = repr(err)
            logger.warning(f'{errlog} User: {ctx.message.author}')
            print(errlog)
            await self.bot.send_message(ctx.message.channel, 'Sorry, something is wrong!')

    async def msgLevelUp(self, ctx: commands.Context):
        await self.bot.send_message(ctx.message.author,
                                    "You have leveled up!  What class are you going to take your level in?")


def setup(bot):
    bot.add_cog(PlayerWrapper(bot))
