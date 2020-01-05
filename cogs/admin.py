import discord
import asyncio
from cogs.logger import logger
from discord.ext import commands

from loadconfig import __adminRole__
import loaduserdata

class Admin():
	def __init__(self, bot):
		self.bot = bot

	@commands.command (pass_context=True)
	async def say(self, ctx: commands.Context):
		if(checkAdmin(ctx.message.author)):
			await self.bot.delete_message(ctx.message)
			await self.bot.send_message(ctx.message.channel, ctx.message.content[5:])

	@commands.command (pass_context=True)
	async def addToAll(self, ctx: commands.Context, amttype: str, amt: int):
		if(checkAdmin(ctx.message.author)):
			for player in loaduserdata.__playerData__:
				for pc in loaduserdata.__playerData__[player].PCdict:
					if amttype == "downtime":
						loaduserdata.__playerData__[player].PCdict[pc].addDowntime(amt)
						logger.info(f'Admin {ctx.message.author} added {amt} {amttype} to all users')

					elif amttype == "xp":
						loaduserdata.__playerData__[player].PCdict[pc].addXp(amt)
						logger.info(f'Admin {ctx.message.author} added {amt} {amttype} to all users')

					else:
						logger.warning(f'Some users have no attribute {amttype}')


			loaduserdata.savedata()
			logger.info(f'Admin {ctx.message.author} added {amt} {amttype} to all users')

	@commands.command (pass_context=True)
	async def addDowntimeToCharacter(self, ctx: commands.Context, playername: str, pc: str, amt: int):
		if(checkAdmin(ctx.message.author)):
			try:
				player = discord.utils.find(lambda o: o.display_name == playername, self.bot.get_all_members())
				player = player.id
				newAmt = loaduserdata.__playerData__[player].PCdict[pc]["downtime"] + amt

				if(newAmt) > 0:
					loaduserdata.__playerData__[player].PCdict[pc]["downtime"] = newAmt
					loaduserdata.savedata()
					loguser = await self.bot.get_user_info(player)
					logger.info(f'Admin {ctx.message.author} added {amt} downtime to {loguser}\'s pc {pc}')
				else:
					raise ValueError("Invalid downtime value given.")

			except Exception as err:
				errlog = repr(err)
				logger.warning(f'{errlog}')

	@commands.command (pass_context=True)
	async def addXpToAll(self, ctx: commands.Context, amt: int):
		if(checkAdmin(ctx.message.author)):
			for player in loaduserdata.__playerData__:
				for pc in loaduserdata.__playerData__[player].PCdict:
					loaduserdata.__playerData__[player].PCdict[pc]["xp"] = loaduserdata.__playerData__[player].PCdict[pc]["xp"] + amt
			loaduserdata.savedata()
			logger.info(f'Admin {ctx.message.author} added {amt} downtime to all users')

	@commands.command (pass_context=True)
	async def addDowntimeToCharacter(self, ctx: commands.Context, playername: str, pc: str, amt: int):
		if(checkAdmin(ctx.message.author)):
			try:
				player = discord.utils.find(lambda o: o.display_name == playername, self.bot.get_all_members())
				player = player.id
				newAmt = loaduserdata.__playerData__[player].PCdict[pc]["downtime"] + amt

				if(newAmt) > 0:
					loaduserdata.__playerData__[player].PCdict[pc]["downtime"] = newAmt
					loaduserdata.savedata()
					loguser = await self.bot.get_user_info(player)
					logger.info(f'Admin {ctx.message.author} added {amt} downtime to {loguser}\'s pc {pc}')
				else:
					raise ValueError("Invalid downtime value given.")

			except Exception as err:
				errlog = repr(err)
				logger.warning(f'{errlog}')


	@commands.command (pass_context=True)
	async def subtractDowntimeFromCharacter(self, ctx: commands.Context, playername: str, pc: str, amt: int):
		if(checkAdmin(ctx.message.author)):
			try:
				player = discord.utils.find(lambda o: o.display_name == playername, self.bot.get_all_members())
				player = player.id
				newAmt = loaduserdata.__playerData__[player].PCdict[pc]["downtime"] - amt

				if(newAmt) >= 0:
					loaduserdata.__playerData__[player].PCdict[pc]["downtime"] = newAmt
					loaduserdata.savedata()
					loguser = await self.bot.get_user_info(player)
					logger.info(f'Admin {ctx.message.author} subtracted {amt} downtime from {loguser}\'s pc {pc}')
				else:
					raise ValueError("Invalid downtime value given.")

			except Exception as err:
				errlog = repr(err)
				logger.warning(f'{errlog}')

def checkAdmin(userMember):
	for role in userMember.roles:
		if(role.id == __adminRole__):
			return True
	return False

def setup(bot):
	bot.add_cog(Admin(bot))