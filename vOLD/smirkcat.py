import discord
import pickle
import time
import datetime
import random
import re

TOKEN = open("token.txt","r").readline()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

client.guild = []
client.limit = "None"
client.db = {}
client.t0 = 0
client.words = []

@client.event #ON READY
async def on_ready():
    client.guild = client.get_guild(792880922525040670)
    print('### LOGGED IN AS {0.user}, MAIN GUILD: {1} ###'.format(client, client.guild))
    await client.guild.me.edit(nick="😼? (prefix: ?)")
    with open('db.p', 'rb') as fp:
        client.db = pickle.load(fp)
    with open('words.p', 'rb') as fp:
        client.words = pickle.load(fp)

@client.event #ON MESSAGE
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    elif message.content.startswith('?') and len(message.content) > 1 and message.content[1] != " " and message.content[1] != "?" and message.content[1] != "!":
        if message.author.id == 155512383681462272:
            print(message.content)
            command = ""
            if " " in message.content:
                command = message.content[1:message.content.find(" ")]
            else:
                command = message.content[1:len(message.content)]
            print("command")
            args = message.content[message.content.find(" ")+1:len(message.content)]
            print("command", command)
            print("args", args)
            #TODO: add leaderboard type message
            #TODO: add milestones
            #TODO: poll on single ? or to count ?? and ??? too
            if command == "count":
                words = re.findall(r'"(.*?)"', args)
                print("words", words)
                people = args[args.rfind("\"")+2:len(args)].split(" ")
                print("people", people)
                if not words:
                    await message.channel.send(get_invalid_message())
                    return
                for word in words:
                    if word not in client.words:
                        await new_word(message, word)
                    await print_count(message, word, people)
            elif command == "words":
                await message.channel.send("Tracked words: **{}** \n *to add a word use ?count followed by the word/phrase in quotes (ex: ?count \"cum\")*".format(client.words))
            elif command == "avatar":
                await tavatar(message, args)
            else:
                await message.channel.send(get_invalid_message())
            
            if message.author.id == 155512383681462272:
                if command == "disconnect":
                    await safe_close(message)
                elif command == "wipe":
                    await reset_pickles()
                elif command == "stop":
                    await restart()
        else:
            await message.channel.send("I'm busy go away")
            return
    elif "feet" in message.content.lower():
        await feet(message, "feet")
    elif "foot" in message.content.lower():
        await feet(message, "foot")
    elif "toes" in message.content.lower():
        await feet(message, "toes")
    elif "toe" in message.content.lower():
        await feet(message, "toe")
    
    for word in client.words:
        if f' {word} ' in f' {message.content} ':
            update_db(message, word)

@client.event #MEMBER JOINS
async def on_member_join(member):
    print("### NEW MEMBER ###")
    client.db[member.id] = {}
    for word in client.words:
        client.db[member.id][word] = 0
    dump_db()

#SEARCHES FOR NEW WORD AND UPDATES PICKLES
async def new_word(message, word):
    client.words.append(word)
    await message.channel.send("Counting new word, this may take a while (est: 25-30mins)")
    
    t0 = time.time()
    print("### INITIATING NEW WORD COUNT ###")
    
    async with message.channel.typing():
        print("// creating db entries //")
        async for member in client.guild.fetch_members(limit=None):
            if not member.bot:
                client.db[member.id][word] = 0
        
        print("// acquiring messages... //")
        messages = await client.get_channel(792880922525040674).history(limit=None).flatten()
        
        print("// counting... //")
        for msg in messages:
            if msg.author.id in client.db:
                client.db[msg.author.id][word] += f' {msg.content} '.count(f' {word} ')

    print("// updating databases //")
    dump_db()
    dump_words()

    t1 = time.time()
    print("### FINISHED IN {}s ###".format(int(t1 - t0)))

#UPDATES DB AND DUMPS
def update_db(message, word):
    client.db[message.author.id][word] += f' {message.content} '.count(f' {word} ')
    print(datetime.datetime.now(), message.author, "USED THE TRACKED WORD:", word)
    dump_db()

#PRINTS WORD COUNT
async def print_count(message, word, people):
    print(datetime.datetime.now(), "PRINT COUNT USED")
    if not len(people):
        await message.channel.send("{0} has used **{1}** `{2}` times".format(message.author.mention, word, client.db[message.author.id][word]))
    else:
        async with message.channel.typing():
            for person in people:
                found = False
                async for member in client.guild.fetch_members(limit=None):
                    if not member.bot:
                        if member.nick and person.lower() in member.nick.lower() or person.lower() in member.name.lower():
                            found = True
                            await message.channel.send("{0} has used **{1}** `{2}` times".format(member.mention, word, client.db[member.id][word]))
                            break
                if not found:
                    await message.channel.send("Could not find user {}".format(person))

#DID SOMEONE SAY FEET?
async def feet(message, word):
    print(datetime.datetime.now(), "FEET TRIGGERED:", message.content)
    elapsed = time.time() - client.t0
    if elapsed > 43200:
        with open('lick.jpg', 'rb') as f:
            picture = discord.File(f)
            await message.channel.send("Did someone say {}?".format(word))
            await message.channel.send(file=picture)
            client.t0 = time.time()
    else:
        print("*** {0} not enough time passed: {1}s ***".format(word.upper(), int(elapsed)))

#10% CHANCE OF DISPLAYING FURRY PFP
async def tavatar(message, people):
    embed = discord.Embed()
    embed.description = "**[Avatar URL](https://www.netflix.com/title/81054847)**"
    embed.color = discord.Colour.from_rgb(114, 137, 218)
    chance = random.randint(1, 100)
    if len(people):
        for person in people:
                found = False
                async for member in client.guild.fetch_members(limit=None):
                    if not member.bot:
                        if member.nick and person.lower() in member.nick.lower() or person.lower() in member.name.lower():
                            found = True
                            embed.title = str(member)
                            chance = random.randint(1, 100)
                            print(datetime.datetime.now(), "TAVATAR USED chance:", chance, "%")
                            if chance <= 50:
                                file, url = get_random_pfp()
                                embed.set_image(url=url)
                                await message.channel.send(file=file, embed=embed)
                                break
                            else:
                                embed.set_image(url=member.avatar_url_as(size=256))
                                await message.channel.send(embed=embed)
                                break
                if not found:
                    await message.channel.send("Could not find user {}".format(person))
    else:
        embed.title = str(message.author)
        chance = random.randint(1, 100)
        print(datetime.datetime.now(), "TAVATAR USED chance:", chance, "%")
        if chance <= 50:
            file, url = get_random_pfp()
            embed.set_image(url=url)
            await message.channel.send(file=file, embed=embed)
        else:
            embed.set_image(url=message.author.avatar_url_as(size=256))
            await message.channel.send(embed=embed)

def get_random_pfp():
    r = random.randint(1,40)
    file = ""
    url = ""
    if r in [6, 25, 31]:
        file = discord.File("kms/{}.gif".format(r), filename="kys.gif")
        url="attachment://kys.gif"
    else:
        file = discord.File("kms/{}.jpg".format(r), filename="kys.jpg")
        url="attachment://kys.jpg"
    return file, url

#DUMPS DB
def dump_db():
    with open('db.p', 'wb') as fp:
        pickle.dump(client.db, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("### DB UPDATED ###")

#DUMPS WORDS
def dump_words():
    with open('words.p', 'wb') as fp:
        pickle.dump(client.words, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("### WORDS UPDATED ###")

#SAVE AND DISCONNECT BOT
async def safe_close(message):
    await message.channel.send("Dumping databases and disconnecting, BYE!")
    dump_db()
    dump_words()
    await client.close()
    print("### DISCONNECTED ###")

#GETS RANDOM INVALID COMMAND MESSAGE
def get_invalid_message():
    print(datetime.datetime.now(), "INVALID MESSAGE USED")
    mes = ["invalid command, dumbass", "invalid command, idiot", "try again", "I'm sorry what?", "cringe for that", "what?", "huh?"]
    return random.choice(mes)

#RESETS DATABASES
async def reset_pickles():
    client.words = []
    client.db = {}
    async for member in client.guild.fetch_members(limit=None):
        if not member.bot:
            client.db[member.id] = {}
    dump_db()
    dump_words()

#RESTARTS BOT
async def restart():
    await client.close()
    await client.run(TOKEN)

client.run(TOKEN)