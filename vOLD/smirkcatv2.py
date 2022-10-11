import discord
import pickle
import time
import random
import re
from discord.ext import commands

TOKEN = open("token.txt","r").readline()
ADMIN = 155512383681462272

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='?', intents=intents)

bot.guild = []
bot.db = {}
bot.t0 = 0
bot.words = []
bot.couples = {}



### EVENTS ###



@bot.event #ON READY
async def on_ready():
    bot.guild = bot.get_guild(792880922525040670)
    await bot.guild.me.edit(nick="😼? (prefix: ?)")
    with open('db.p', 'rb') as fp:
        bot.db = pickle.load(fp)
    with open('words.p', 'rb') as fp:
        bot.words = pickle.load(fp)
    with open('couples.p', 'rb') as fp:
        bot.couples = pickle.load(fp)
    print('### LOGGED IN AS {0.user}, MAIN GUILD: {1} ###'.format(bot, bot.guild))

@bot.event #ON MESSAGE
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

    for trigger in ["feet", "foot", "toes", "toe"]:
        if f' {trigger} ' in f' {message.content.lower()} ':
            await feet(message, trigger)

    for word in bot.words:
        if f' {word} ' in f' {message.content} ':
            update_db(message, word)

@bot.event #MEMBER JOINS
async def on_member_join(member):
    print("\nNEW MEMBER...", member)
    bot.db[member.id] = {}
    for word in bot.words:
        bot.db[member.id][word] = 0
    dump_db()



### COMMANDS ###



@bot.command() #COUNT
async def count(ctx, *, args):
    print("\nCOUNT...", args)
    words = re.findall(r'"(.*?)"', args)
    people = []
    if (args.rfind("\"") != len(args) - 1):
        people = args[args.rfind("\"") + 2:len(args)].split(" ")
    if not words:
        await ctx.send(get_invalid_message())
        return
    for word in words:
        word = word.lower()
        if word not in bot.words:
            await new_word(ctx, word)
        await print_count(ctx, word, people)

@bot.command() #AVATAR
async def avatar(ctx, *args):
    print("\nAVATAR...", args)
    ea = discord.Embed()
    eb = discord.Embed()
    ea.color = discord.Colour.from_rgb(114, 137, 218)
    eb.color = discord.Colour.from_rgb(114, 137, 218)
    if len(args) == 2:
        pa = await get_member(args[0])
        pb = await get_member(args[1])
        if (pa and pb):
            num = random.randint(1,46)
            print("...pfp used:", num)
            a = bot.couples[str(num)+"a"]
            b = bot.couples[str(num)+"b"]
            fa, ua = get_pfp("downbad", str(num) + "a")
            fb, ub = get_pfp("downbad", str(num) + "b")
            ea.title = str(pa)
            eb.title = str(pb)
            ea.description = "**[Avatar URL]({})**".format(a)
            eb.description = "**[Avatar URL]({})**".format(b)
            ea.set_image(url=ua)
            eb.set_image(url=ub)
            await ctx.send(file=fa, embed=ea)
            await ctx.send(file=fb, embed=eb)
        elif (pa and not pb):
            ea.title = str(pa)
            ea.description = "**[Avatar URL]({}})**".format(pa.avatar_url)
            ea.set_image(pa.avatar_url_as(size=256))
            await ctx.send(embed=ea)
            print("...name not found:", args[1])
            await ctx.send("Could not find user with name: {}".format(args[1]))
        else:
            print("...name not found:", args[0])
            await ctx.send("Could not find user with name: {}".format(args[0]))
            eb.title = str(pb)
            eb.description = "**[Avatar URL]({}})**".format(pa.avatar_url)
            eb.set_image(pb.avatar_url_as(size=256))
            await ctx.send(embed=eb)       
    elif len(args) == 1 or len(args) >= 3:
        for name in args:           
            p = await get_member(name)
            if (p):
                ea.title = str(p)
                await chance_send_furry(ctx, p, ea)
            else:
                print("...name not found:", name)
                await ctx.send("Could not find user with name: {}".format(name))
    else:
        ea.title = str(ctx.author)
        await chance_send_furry(ctx, ctx.author, ea)

@bot.command() #WIPE
async def wipe(ctx):
    print("\nWIPE...")
    if ctx.author.id == ADMIN:
        bot.words = []
        bot.db = {}
        async for member in bot.guild.fetch_members(limit=None):
            if not member.bot:
                bot.db[member.id] = {}
        dump_db()
        dump_words()
        await ctx.send("Pickles wiped and reset")
        print("...PICKLES WIPED")
    else:
        await ctx.send(get_invalid_message())

@bot.command() #WORDS
async def words(ctx):
    print("WORDS...")
    await ctx.send("Tracked words: **{}**\nto add a word use ?count followed by the word/phrase in quotes (ex: ?count \"cum\")".format(bot.words))
    await ctx.send("to display the count for other users use ?count \"word/phrase\" followed by their names (ex: ?count \"cum inside me\" willem")



### HELPER FUNCTIONS ###



#SEARCHES FOR NEW WORD AND UPDATES PICKLES
async def new_word(ctx, word):
    bot.words.append(word)
    await ctx.send("Counting new word, this may take a while (est: 25-30mins)")
    
    t0 = time.time()
    print("INITIATING NEW WORD COUNT...")
    
    async with ctx.typing():
        print("...creating db entries...")
        async for member in bot.guild.fetch_members(limit=None):
            if not member.bot:
                bot.db[member.id][word] = 0
        
        print("...collecting messages...")
        messages = await bot.get_channel(792880922525040674).history(limit=None).flatten()
        
        print("...counting...")
        for msg in messages:
            if msg.author.id in bot.db:
                fluff = "!@#$%^&*()-_\"\'<>."
                for f in fluff:
                    msg.content = msg.content.replace(f, "")
                if msg.content.count("?") != len(msg.content):
                    msg.content = msg.content.replace("?", "")
                bot.db[msg.author.id][word] += f' {msg.content.lower()} '.count(f' {word} ')
        
        print("...updating databases...")
        dump_db()
        dump_words()

        t1 = time.time()
        print("...FINISHED IN {}s".format(int(t1 - t0)))

#PRINTS WORD COUNT
async def print_count(ctx, word, names):
    if not len(names):
        print("...printing count for author", "word:", word)
        await ctx.send("{0} has used **{1}** `{2}` times".format(ctx.author.mention, word, bot.db[ctx.author.id][word]))
    else:
        async with ctx.typing():
            for name in names:
                member = await get_member(name)
                if (member):
                    print("...printing count for", member, ", word:", word)
                    await ctx.send("{0} has used **{1}** `{2}` times".format(member.mention, word, bot.db[member.id][word]))
                else:
                    print("...name not found:", name)
                    await ctx.send("Could not find user {}".format(name))

#GET MEMBER OBJECT FROM NAME
async def get_member(name):
    m = None
    async for member in bot.guild.fetch_members(limit=None):
        if not member.bot:
            if member.nick and name.lower() in member.nick.lower() or name.lower() in member.name.lower():
                m = member
                break
    return m

#GETS FILE AND URL FROM IMAGE NAME
def get_pfp(folder, name):
    file = ""
    url = ""
    if name in ["3a", "3b", "6", "25", "31"]:
        file = discord.File("{0}/{1}.gif".format(folder, name), filename="hiwillem.gif")
        url="attachment://hiwillem.gif"
    else:
        file = discord.File("{0}/{1}.jpg".format(folder, name), filename="iwishwillemwouldfme.jpg")
        url="attachment://iwishwillemwouldfme.jpg"
    return file, url

#SEND FURRY OR NOT
async def chance_send_furry(ctx, member, embed):
    embed.title = str(member)
    if (random.randint(0, 100) < 20):
        print("...furry pfp used")
        f, u = get_pfp("kms", str(random.randint(1,40)))
        embed.set_image(url=u)
        await ctx.send(file=f, embed=embed)
    else:
        print("...member pfp used")
        embed.description = "**[Avatar URL]({})**".format(member.avatar_url)
        embed.set_image(url=ctx.author.avatar_url_as(size=256))
        await ctx.send(embed=embed)    

#DID SOMEONE SAY FEET?
async def feet(message, word):
    print("\nFEET...", message.content)
    elapsed = time.time() - bot.t0
    if elapsed > 43200:
        with open('lick.jpg', 'rb') as f:
            picture = discord.File(f)
            await message.channel.send("Did someone say {}?".format(word))
            await message.channel.send(file=picture)
            bot.t0 = time.time()
    else:
        print("*** {0} not enough time passed: {1}s ***".format(word.upper(), int(elapsed)))

#UPDATES DB AND DUMPS
def update_db(message, word):
    print("TRACKED WORD...", message.author, ":" , word)
    bot.db[message.author.id][word] += f' {message.content} '.count(f' {word} ')
    dump_db()

#DUMPS DB
def dump_db():
    with open('db.p', 'wb') as fp:
        pickle.dump(bot.db, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("...DB.p UPDATED\n")

#DUMPS WORDS
def dump_words():
    with open('words.p', 'wb') as fp:
        pickle.dump(bot.words, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("...WORDS.p UPDATED\n")

#GETS RANDOM INVALID COMMAND MESSAGE
def get_invalid_message():
    print("...INVALID MESSAGE\n")
    mes = ["invalid command, dumbass", "invalid command, idiot", "try again", "I'm sorry what?", "cringe for that", "what?", "huh?"]
    return random.choice(mes)



### ERROR HANDLING ###



@count.error
async def count_error(ctx, error):
    print("\n### count error ###", error)
    await ctx.send(get_invalid_message())

@avatar.error
async def avatar_error(ctx, error):
    print("\n### avatar error ###", error)
    await ctx.send(get_invalid_message())

@wipe.error
async def count_error(ctx, error):
    print("\n### wipe error ###", error)
    await ctx.send(get_invalid_message())

@words.error
async def words_error(ctx, error):
    print("\n### words error ###", error)
    await ctx.send(get_invalid_message())

bot.run(TOKEN)