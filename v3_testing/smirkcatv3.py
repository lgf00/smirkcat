import discord
import pickle
import time
import random
import re
from discord.ext import commands

TOKEN = open("token.txt", "r").readline()
ADMIN = 155512383681462272

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

# bot.guild = []
# bot.db = {}  # change to {guild_id: {words: [], ...}, ...}
# bot.t0 = {}  # change to {guild_id: t0, ...}
# bot.b0 = {}
# # bot.words = [] #depracated
# bot.couples = {}


### EVENTS ###


@bot.event  # ON READY
async def on_ready():
    # with open("db.p", "rb") as fp:
    #     bot.db = pickle.load(fp)
    # with open("couples.p", "rb") as fp:
    #     bot.couples = pickle.load(fp)
    for guild in bot.guilds:
        await guild.me.edit(nick="😼? (prefix: ?)")
        # bot.t0[guild.id] = 0
        # bot.b0[guild.id] = 0
        print("### LOGGED IN AS {0.user}, guild: {1} ###".format(bot, guild))


@bot.event  # ON MESSAGE
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

    for trigger in ["feet", "foot", "toes", "toe"]:
        if f" {trigger} " in f" {message.content.lower()} ":
            await feet(message, trigger)

    for trigger in ["breeze"]:
        if f" {trigger} " in f" {message.content.lower()} ":
            await breeze(message)

    # for word in bot.db[message.guild.id]["words"]:
    #     if f" {word} " in f" {message.content} ":
    #         update_db(message, word)


# @bot.event  # MEMBER JOINS
# async def on_member_join(member):
#     print(member.guild, "NEW MEMBER...", member)
#     bot.db[member.guild.id][member.id] = {}
#     for word in bot.words:
#         bot.db[member.guild.id][member.id][word] = 0
#     dump_db()


### COMMANDS ###


# @bot.command()  # COUNT
# async def count(ctx, *, args):
#     print(ctx.guild, "COUNT...", args)
#     words = re.findall(r'"(.*?)"', args)
#     people = []
#     if args.rfind('"') != len(args) - 1:
#         people = args[args.rfind('"') + 2 : len(args)].split(" ")
#     if not words:
#         await ctx.send(get_invalid_message(ctx))
#         return
#     for word in words:
#         word = word.lower()
#         if word not in bot.db[ctx.guild.id]["words"]:
#             await new_word(ctx, word)
#         await print_count(ctx, word, people)


@bot.command()  # AVATAR
async def avatar(ctx, *args):
    print(ctx.guild, "AVATAR...", args)
    ea = discord.Embed()
    eb = discord.Embed()
    ea.color = discord.Colour.from_rgb(114, 137, 218)
    eb.color = discord.Colour.from_rgb(114, 137, 218)
    if len(args) == 2:
        pa = await get_member(ctx, args[0])
        pb = await get_member(ctx, args[1])
        if pa and pb:
            num = random.randint(1, 46)
            print("...pfp used:", num)
            a = bot.couples[str(num) + "a"]
            b = bot.couples[str(num) + "b"]
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
        elif pa and not pb:
            ea.title = str(pa)
            ea.description = "**[Avatar URL]({})**".format(pa.avatar_url)
            ea.set_image(pa.avatar_url_as(size=256))
            await ctx.send(embed=ea)
            print("...name not found:", args[1])
            await ctx.send("Could not find user with name: {}".format(args[1]))
        else:
            print("...name not found:", args[0])
            await ctx.send("Could not find user with name: {}".format(args[0]))
            eb.title = str(pb)
            eb.description = "**[Avatar URL]({})**".format(pa.avatar_url)
            eb.set_image(pb.avatar_url_as(size=256))
            await ctx.send(embed=eb)
    elif len(args) == 1 or len(args) >= 3:
        print(args)
        for name in args:
            p = await get_member(ctx, name)
            print(p)
            if p:
                await chance_send_furry(ctx, p, ea)
            else:
                print("...name not found:", name)
                await ctx.send("Could not find user with name: {}".format(name))
    else:
        await chance_send_furry(ctx, ctx.author, ea)


# @bot.command()  # WIPE
# async def wipe(ctx):
#     print(ctx.guild, "WIPE...")
#     if ctx.author.id == ADMIN:
#         bot.db = {}
#         for guild in bot.guilds:
#             bot.db[guild.id] = {}
#             bot.db[guild.id]["words"] = []
#             async for member in guild.fetch_members(limit=None):
#                 if not member.bot:
#                     bot.db[guild.id][member.id] = {}
#         dump_db()
#         await ctx.send("DB wiped and reset")
#         print("...DB WIPED AND RESET")
#     else:
#         await ctx.send(get_invalid_message(ctx))


# @bot.command()  # WORDS
# async def words(ctx):
#     print(ctx.guild, "WORDS...")
#     await ctx.send("Tracked words: **{}**".format(bot.db[ctx.guild.id]["words"]))


@bot.command()  # HELP
async def help(ctx):
    embed = discord.Embed(title="😼? Help", description="help page for a very good bot")
    embed.color = discord.Color.from_rgb(255, 255, 0)
    file = discord.File("lick.jpg", filename="lick.jpg")
    url = "attachment://lick.jpg"
    embed.set_thumbnail(url=url)
    embed.add_field(
        name="?avatar",
        inline=False,
        value="Displays members avatar correctly every time, the bot is never wrong\n\n\
        examples:\n\
        ?avatar\n\
        ?avatar name1 name2 ...\n",
    )
    # embed.add_field(
    #     name="?count",
    #     inline=False,
    #     value='Displays how many times members have typed a word (like the search feature in discord but for everyone to see)\n\n\
    #     examples:\n\
    #     ?count "yo mama"\n\
    #     ?count "yo mama" name1 name2 ...\n\n\
    #     notes:\n\
    #     Searching for a new word/phrase can take ~30m as it scans every message in each channel but depending on server size this can take even longer, you will be @\'d when it completes.\n\
    #     While searching, the bots speed to reply will be slower.\n\
    #     Once a word is added it will be tracked so the bot will not need to search every time.\n',
    # )
    # embed.add_field(
    #     name="?words",
    #     inline=False,
    #     value="Displays the tracked words/phrases that have been searched for already\n\n\
    #     example:\n\
    #     ?words\n",
    # )
    embed.set_footer(
        text="if the bot seems to be breaking or not working correctly please reach out to lgf#5547, thanks!"
    )
    await ctx.send(file=file, embed=embed)


### HELPER FUNCTIONS ###


# TODO: add plural checks 's and s
# SEARCHES FOR NEW WORD AND UPDATES PICKLES
# async def new_word(ctx, word):
#     await ctx.send("Counting new word, this may take a while... bot will be slower")
#     bot.db[ctx.guild.id]["words"].append(word)
#     t0 = time.time()
#     print(ctx.guild, "INITIATING NEW WORD COUNT...")

#     async with ctx.typing():
#         print(ctx.guild, "...creating db entries...")

#         async for member in ctx.guild.fetch_members(limit=None):
#             if not member.bot:
#                 bot.db[ctx.guild.id][member.id][word] = 0

#         print(ctx.guild, "...collecting messages...")
#         messages = []
#         channels = []
#         for channel in ctx.guild.channels:
#             if str(channel.type) == "text":
#                 channels.append(channel)

#         for channel in channels:
#             messages.extend(await channel.history(limit=None).flatten())

#         print(ctx.guild, "...counting...")
#         for msg in messages:
#             if msg.author.id in bot.db[msg.guild.id]:
#                 fluff = "!@#$%^&*()-_\"'<>.,"
#                 for f in fluff:
#                     msg.content = msg.content.replace(f, "")
#                 if msg.content.count("?") != len(msg.content):
#                     msg.content = msg.content.replace("?", "")
#                 bot.db[msg.guild.id][msg.author.id][
#                     word
#                 ] += f" {msg.content.lower()} ".count(f" {word} ")

#         print(ctx.guild, "...updating databases...")
#         dump_db()
#         t1 = time.time()
#         await ctx.send(
#             "{2} count complete, total messages searched: {0}, time elapsed: {1}m".format(
#                 len(messages), int((t1 - t0) / 60), ctx.author.mention
#             )
#         )
#         print(ctx.guild, "...FINISHED IN {}s".format(int(t1 - t0)))


# PRINTS WORD COUNT
# async def print_count(ctx, word, names):
#     if not len(names):
#         print(ctx.guild, "...printing count for author", "word:", word)
#         await ctx.send(
#             "{0} has used **{1}** `{2}` times".format(
#                 ctx.author.mention, word, bot.db[ctx.guild.id][ctx.author.id][word]
#             )
#         )
#     else:
#         async with ctx.typing():
#             for name in names:
#                 member = await get_member(ctx, name)
#                 if member:
#                     print(ctx.guild, "...printing count for", member, ", word:", word)
#                     await ctx.send(
#                         "{0} has used **{1}** `{2}` times".format(
#                             member.mention, word, bot.db[ctx.guild.id][member.id][word]
#                         )
#                     )
#                 else:
#                     print(ctx.guild, "...name not found:", name)
#                     await ctx.send("Could not find user {}".format(name))


# GET MEMBER OBJECT FROM NAME
async def get_member(ctx, name):
    m = None
    async for member in ctx.guild.fetch_members(limit=None):
        if not member.bot:
            if (
                member.nick
                and name.lower() in member.nick.lower()
                or name.lower() in member.name.lower()
            ):
                m = member
                break
    return m


# GETS FILE AND URL FROM IMAGE NAME
def get_pfp(folder, name):
    file = ""
    url = ""
    if name in ["3a", "3b", "6", "25", "31"]:
        file = discord.File("{0}/{1}.gif".format(folder, name), filename="downbad.gif")
        url = "attachment://downbad.gif"
    else:
        file = discord.File("{0}/{1}.jpg".format(folder, name), filename="downbad.jpg")
        url = "attachment://downbad.jpg"
    return file, url


# SEND FURRY OR NOT
async def chance_send_furry(ctx, member, embed):
    embed.title = str(member)
    if random.randint(0, 100) < 20:
        print(ctx.guild, "...furry pfp used")
        f, u = get_pfp("kms", str(random.randint(1, 40)))
        embed.set_image(url=u)
        await ctx.send(file=f, embed=embed)
    else:
        print(ctx.guild, "...member pfp used")
        embed.description = "**[Avatar URL]({})**".format(member.avatar_url)
        embed.set_image(url=member.avatar_url_as(size=256))
        await ctx.send(embed=embed)


# breeze isn't even that big guys
async def breeze(message):
    print(message.guild, "BREEZE...", message.content)
    elapsed = time.time() - bot.b0[message.guild.id]
    if elapsed > 43200:
        await message.channel.send("breeze isn't even that big guys")
        bot.b0[message.guild.id] = time.time()
    else:
        print(
            message.guild,
            "*** BREEZE not enough time passed: {0}s ***".format(int(elapsed)),
        )


# DID SOMEONE SAY FEET?
async def feet(message, word):
    print(message.guild, "FEET...", message.content)
    elapsed = time.time() - bot.t0[message.guild.id]
    if elapsed > 43200:
        with open("lick.jpg", "rb") as f:
            picture = discord.File(f)
            await message.channel.send("Did someone say {}?".format(word))
            await message.channel.send(file=picture)
            bot.t0[message.guild.id] = time.time()
    else:
        print(
            message.guild,
            "*** {0} not enough time passed: {1}s ***".format(
                word.upper(), int(elapsed)
            ),
        )


# TODO: UPDATE DETECTION
# UPDATES DB AND DUMPS
# def update_db(message, word):
#     print(message.guild, "TRACKED WORD...", message.author, ":", word)
#     bot.db[message.guild.id][message.author.id][word] += f" {message.content} ".count(
#         f" {word} "
#     )
#     dump_db()


# DUMPS DB
# def dump_db():
#     with open("db.p", "wb") as fp:
#         pickle.dump(bot.db, fp, protocol=pickle.HIGHEST_PROTOCOL)
#     with open("couples.p", "wb") as fp:
#         pickle.dump(bot.couples, fp, protocol=pickle.HIGHEST_PROTOCOL)
#     print("...DB.p UPDATED\n")


# GETS RANDOM INVALID COMMAND MESSAGE
def get_invalid_message(ctx):
    print(ctx.guild, "...INVALID MESSAGE\n")
    mes = [
        "invalid command, dumbass",
        "invalid command, idiot",
        "try again",
        "I'm sorry, what?",
        "cringe for that",
        "what?",
        "huh?",
    ]
    return random.choice(mes)


### ERROR HANDLING ###


# @count.error
# async def count_error(ctx, error):
#     print(ctx.guild, "### count error ###", error)
#     await ctx.send(get_invalid_message(ctx))


@avatar.error
async def avatar_error(ctx, error):
    print(ctx.guild, "### avatar error ###", error)
    await ctx.send(get_invalid_message(ctx))


# @wipe.error
# async def count_error(ctx, error):
#     print(ctx.guild, "### wipe error ###", error)
#     await ctx.send(get_invalid_message(ctx))


# @words.error
# async def words_error(ctx, error):
#     print(ctx.guild, "### words error ###", error)
#     await ctx.send(get_invalid_message(ctx))


bot.run(TOKEN)
