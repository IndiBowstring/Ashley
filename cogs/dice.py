import discord
import asyncio
import re
from random import randint
from cogs.logger import logger
from discord.ext import commands

PB_MIN = 24
PB_MAX = 31

class Dice():
	def __init__(self, bot):
		self.bot = bot

	def roll(self, die):
		return randint(1, die)

	@commands.command(aliases=['r', 'roll', 'rollAdvantage', 'rolladv', 'rollAdv', 'ra', 'rollDisadvantage', 'rolldisadv', 'rollDisadv', 'rd'], pass_context=True,
		description='Roll dice in ndm+p format.')
	async def rollDice(self, ctx: commands.Context, ndn: str):
		
		invoker = ctx.invoked_with

		try:
			rollsList = []
			validatedString = ndn #re.search("\d+[d]\d+[+|-]\d*", ndn).group(0)

			# PARSE NUMBER OF DICE TO BE ROLLED
			amount = re.search("\d+[d]", validatedString)
			if amount:
				amount = int(amount.group(0)[:-1])

				if(amount > 20):
					await self.bot.send_message(ctx.message.channel, f'Can\'t roll more than 20 dice at once!')
					return
			else:
				amount = 1

			# PARSE DIE FACE
			die = int(re.search("[d]\d+", validatedString).group(0)[1:])

			# PARSE MODIFIER
			mod = re.search("[+|-]\d*", validatedString)
			if mod:
				mod = int(mod.group(0))
			else:
				mod = 0

			if invoker in ['r', 'roll']:
				# Roll dice, calculate total, and construct string.  Append to rollsList and loop
				for x in range(0, amount):
					roll = self.roll(die)
					tot = roll+mod
					if(mod < 0):
						rollsList.append(''.join(['(', str(roll), ')', str(mod), ' = ', str(tot)]))

					elif(mod >= 0):
						rollsList.append(''.join(['(', str(roll), ')+', str(mod), ' = ', str(tot)]))
			
			else:
				for x in range(0, amount):
					roll_1 = self.roll(die)
					roll_2 = self.roll(die)
					tot = None
					if invoker in ['rollAdvantage', 'rolladv', 'rollAdv', 'ra']:
						tot = max(roll_1, roll_2)+mod
					elif invoker in ['rollDisadvantage', 'rolldisadv', 'rollDisadv', 'rd']:
						tot = min(roll_1, roll_2)+mod

					if(mod < 0):
						rollsList.append(''.join(['(', str(roll_1), ',', str(roll_2), ')', str(mod), ' = ', str(tot)]))

					elif(mod >= 0):
						rollsList.append(''.join(['(', str(roll_1), ',', str(roll_2), ')+', str(mod), ' = ', str(tot)]))
			
			# Begin message, concatenate each roll string onto message, end message and display
			_message = '\n```'
			for roll in rollsList:
				_message = _message + roll + '\n'
			_message = _message + '```'

			await self.bot.send_message(ctx.message.channel, _message)

		# On error, display error message to end user and console
		except Exception as err:
			await self.bot.send_message(ctx.message.channel, f"Sorry, I can\'t understand that.")
			errlog = repr(err)
			logger.warning(f'{errlog}')

	@commands.command(aliases=['stats'], pass_context=True,
		description='Roll stats between a specified PBE.')
	async def rollStats(self, ctx: commands.Context):
		
		PBE = {
			'18' : 19,
			'17' : 15,
			'16' : 12,
			'15' : 9,
			'14' : 7,
			'13' : 5,
			'12' : 4,
			'11' : 3,
			'10' : 2,
			'9' : 1,
			'8' : 0,
			'7' : -1,
			'6' : -2,
			'5' : -4,
			'4' : -6,
			'3' : -9
		}
		
		numtrys = 0
		#4d6-min
		def _Roll():
			val = 0
			min = 7
			for x in range(0,4):
				currval = randint(1,6)
				val+=currval
				if(currval < min):
					min = currval
			return val-min
			
		while True:
			#roll stats
			numtrys+=1
			stats = []
			pointBuyVal = 0
			for r in range(0, 6):
				roll = _Roll()
				stats.append(roll)
				pointBuyVal += PBE[str(roll)]
				
			if pointBuyVal > PB_MAX:
				continue
			elif pointBuyVal < PB_MIN:
				continue
			else:
				stats.sort()
				logStr = ""
				statStr = "Your stats are:\n``"
				for stat in stats:
					statStr = statStr + str(stat) + ", "
					logStr = logStr + str(stat) + ","
				logStr = logStr[:-1]
				statStr = statStr[:-2] + "``.\n"
				statStr = statStr + "Which is a ``" + str(pointBuyVal) + "`` Point Buy Equivalent.  I rolled ``" + str(numtrys) + "`` times."
				logger.info(f"{ctx.message.author} rolled for stats {logStr}. {numtrys} tries {pointBuyVal} PBE")
				
				await self.bot.send_message(ctx.message.channel, statStr)
				break
					
def setup(bot):
	bot.add_cog(Dice(bot))