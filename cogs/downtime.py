import discord
import asyncio
from discord.ext import commands

import loaduserdata

import time

class DT():
	def __init__(self, bot):
		self.bot = bot

	async def timeLoop():
		SECONDS_TO_TICK = 43200

		while True:
			await asyncio.sleep(SECONDS_TO_TICK)

			for player in loaduserdata.__playerdict__:
				for pc in loaduserdata.__playerdict__[player].PCdict:
					loaduserdata.__playerdict__[player].PCdict[pc] = loaduserdata.__playerdict__[player].PCdict[pc] + 1

			loaduserdata.savedata()
			print(f'Downtime ticking over')

def setup(bot):
	bot.add_cog(DT(bot))