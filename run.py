from os import getenv
from random import randint
import discord
import sqlite3

intents = discord.Intents.default()
intents.members= True
bot = discord.Bot(intents=intents)
  
db = sqlite3.connect(':memory:')
cursor = db.cursor()

cursor.execute("""CREATE TABLE roulette (
                              user_id INTEGER,
                              guild_id INTEGER,
                              roles TEXT
                          )""")

@bot.event
async def on_ready():
  print('bot is online')

@bot.event
async def on_thread_create(thread):
    await thread.join()

@bot.event
async def on_member_join(member):
  cursor.execute(f'SELECT roles FROM roulette WHERE user_id={member.id} AND guild_id={member.guild.id}')
  results = cursor.fetchone()[0]
  roles = []
  for result in eval(results):
    class role_class:
      id = result
    roles.append(role_class)
  await member.add_roles(*roles)
  
  cursor.execute(f'DELETE FROM roulette WHERE user_id={member.id} AND guild_id={member.guild.id}')

@bot.slash_command(name='reverse-roulette', description='1 in 6 chance to not get kicked')
async def roulette(ctx):
  if randint(0, 5) != 5: 
    if type(ctx.channel) == discord.Thread:
      invite = await ctx.channel.parent.create_invite(max_age=0, max_uses=1)
    else:
      invite = await ctx.channel.create_invite(max_age=0, max_uses=1)
    roles = []
    for role in ctx.author.roles:
      if role.name != '@everyone':
        roles.append(role.id)
    cursor.execute("INSERT INTO roulette (user_id, guild_id, roles) VALUES (%d, %d, '%s')" % (ctx.user.id, ctx.guild.id, str(roles)))
    await ctx.author.send(invite)
    try:
      await ctx.author.kick()
      await ctx.send(f'{ctx.author.mention} was unlucky. Goodbye!')
    except discord.errors.Forbidden:
      await ctx.respond("you couldn't be kicked because you're a discord mod (gross)")
  else:
    await ctx.respond('you are safe.')

bot.run(getenv('TOKEN'))