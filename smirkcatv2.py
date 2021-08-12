import discord
import pickle
import time
import datetime
import random
import re
from discord.ext import commands

TOKEN = open("token.txt","r").readline()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='?', intents=intents)

bot.guild = []
bot.limit = "None"
bot.db = {}
bot.t0 = 0
bot.words = []

@bot.event #ON READY
async def on_ready():
    bot.guild = bot.get_guild(792880922525040670)
    print('### LOGGED IN AS {0.user}, MAIN GUILD: {1} ###'.format(bot, bot.guild))
    await bot.guild.me.edit(nick="😼? (prefix: ?)")
    with open('db.p', 'rb') as fp:
        bot.db = pickle.load(fp)
    with open('words.p', 'rb') as fp:
        bot.words = pickle.load(fp)

@bot.event #ON MESSAGE
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)
    for word in bot.words:
        if f' {word} ' in f' {message.content} ':
            update_db(message, word)

@bot.event #MEMBER JOINS
async def on_member_join(member):
    print("### NEW MEMBER ###")
    bot.db[member.id] = {}
    for word in bot.words:
        bot.db[member.id][word] = 0
    dump_db()

@bot.command()
async def count(ctx, *, args):
    if ctx.author.id == 155512383681462272:
        words = re.findall(r'"(.*?)"', args)
        people = []
        if (args.rfind("\"") != len(args) - 1):
            people = args[args.rfind("\"") + 2:len(args)].split(" ")
        if not words:
            await ctx.send(get_invalid_message())
            return
        for word in words:
            if word not in bot.words:
                await new_word(ctx, word)
            await print_count(ctx, word, people)
    else:
        ctx.send(random.choice(["fuck off", "go away I'm busy", "no", "shut up", "lol", "I'd fuck willem"]))

@bot.command()
async def avatar(ctx, *, args):
    ctx.send(random.choice(["fuck off", "go away I'm busy", "no", "shut up", "lol", "I'd fuck willem"]))

#SEARCHES FOR NEW WORD AND UPDATES PICKLES
async def new_word(ctx, word):
    bot.words.append(word)
    await ctx.send("Counting new word, this may take a while (est: 25-30mins)")
    
    t0 = time.time()
    print("### INITIATING NEW WORD COUNT ###")
    
    async with ctx.typing():
        print("// creating db entries //")
        async for member in bot.guild.fetch_members(limit=None):
            if not member.bot:
                bot.db[member.id][word] = 0
        
        print("// acquiring messages... //")
        messages = await bot.get_channel(792880922525040674).history(limit=None).flatten()
        
        print("// counting... //")
        for msg in messages:
            if msg.author.id in bot.db:
                bot.db[msg.author.id][word] += f' {msg.content} '.count(f' {word} ')
        
        print("// updating databases //")
        dump_db()
        dump_words()

        t1 = time.time()
        print("### FINISHED IN {}s ###".format(int(t1 - t0)))

#PRINTS WORD COUNT
async def print_count(ctx, word, people):
    print(datetime.datetime.now(), "PRINT COUNT USED")
    if not len(people):
        await ctx.send("{0} has used **{1}** `{2}` times".format(ctx.author.mention, word, bot.db[ctx.author.id][word]))
    else:
        async with ctx.typing():
            for person in people:
                found = False
                async for member in bot.guild.fetch_members(limit=None):
                    if not member.bot:
                        if member.nick and person.lower() in member.nick.lower() or person.lower() in member.name.lower():
                            found = True
                            await ctx.send("{0} has used **{1}** `{2}` times".format(member.mention, word, bot.db[member.id][word]))
                            break
                if not found:
                    await ctx.send("Could not find user {}".format(person))

#UPDATES DB AND DUMPS
def update_db(message, word):
    bot.db[message.author.id][word] += f' {message.content} '.count(f' {word} ')
    print(datetime.datetime.now(), message.author, "USED THE TRACKED WORD:", word)
    dump_db()

#DUMPS DB
def dump_db():
    with open('db.p', 'wb') as fp:
        pickle.dump(bot.db, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("### DB UPDATED ###")

#DUMPS WORDS
def dump_words():
    with open('words.p', 'wb') as fp:
        pickle.dump(bot.words, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("### WORDS UPDATED ###")

#GETS RANDOM INVALID COMMAND MESSAGE
def get_invalid_message():
    print(datetime.datetime.now(), "INVALID MESSAGE USED")
    mes = ["invalid command, dumbass", "invalid command, idiot", "try again", "I'm sorry what?", "cringe for that", "what?", "huh?"]
    return random.choice(mes)



### ERROR HANDLING ###

@count.error
async def count_error(ctx, error):
    await ctx.send(get_invalid_message())

@avatar.error
async def avatar_error(ctx, error):
    ctx.send(random.choice(["fuck off", "go away I'm busy", "no", "shut up", "lol", "I'd fuck willem"]))

bot.run(TOKEN)