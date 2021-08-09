import discord
import pickle
import time

TOKEN = open("token.txt","r").readline()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

client.guild = []
client.limit = "None"
client.q_count = {}
client.t0 = 0

@client.event
async def on_ready():
    client.guild = client.get_guild(792880922525040670)
    print('Logged in as {0.user}, main guild: {1}'.format(client, client.guild))
    await client.guild.me.edit(nick="😼? (prefix: ~)")
    with open('data.p', 'rb') as fp:
        client.q_count = pickle.load(fp)

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    elif message.content == '?':
        update_q_count(message.author)
    elif message.content.startswith('~'):
        args = list(message.content[1::].split(" "))
        command = args.pop(0).lower()
        
        #TODO: add leaderboard type message
        #TODO: add milestones
        #TODO: poll on single ? or to count ?? and ??? too
        if command == "?" and not len(args):
            await message.channel.send("{0} has sent `{1}` ?'s".format(message.author.mention, client.q_count[message.author.id]))
        elif command == "?":
            await print_q_count(message, args)
        elif command == "search":
            await search_history(message)
    elif "feet" in message.content:
        await feet(message, "feet")
    elif "foot" in message.content:
        await feet(message, "foot")
    elif "toes" in message.content:
        await feet(message, "toes")
    elif "toe" in message.content:
        await feet(message, "toe")

@client.event
async def on_member_join(member):
    print("### NEW MEMBER ###")
    client.q_count[member.id] = 0
    with open('data.p', 'wb') as fp:
            pickle.dump(client.q_count, fp, protocol=pickle.HIGHEST_PROTOCOL)
    print("q count created for", member)

def update_q_count(author):
    client.q_count[author.id] += 1
    print(author, "added to their q_count")

async def search_history(message):
    print("### SEARCH ###")
    if message.author.id == 155512383681462272 or message.author.guild_permissions.administrator:
        print("### AUTHORIZED ###")
        t0 = time.time()
        new_q_count = {}
        await message.channel.send("Starting search, this will take a while, you will be notified when done")
        async with message.channel.typing():
            async for member in client.guild.fetch_members(limit=None):
                if not member.bot:
                    new_q_count[member.id] = 0
            async for msg in client.get_channel(792880922525040674).history(limit=None):
                if msg.author.id in new_q_count and msg.content == "?":
                    new_q_count[msg.author.id] += 1
        with open('data.p', 'wb') as fp:
            pickle.dump(new_q_count, fp, protocol=pickle.HIGHEST_PROTOCOL)
        client.q_count = new_q_count
        t1 = time.time()
        await message.channel.send("{0} searched finished. Elapsed time: {1}s".format(message.author.mention, int(t1 - t0)))
        print("### FINISHED IN {}s ###".format(int(t1 - t0)))
    else:
        print("### DECLINED ###") 
        await message.channel.send("You do not have permission to use this command")
    

async def print_q_count(message, args):
    async with message.channel.typing():
        for arg in args:
            arg_found = False
            async for member in client.guild.fetch_members(limit=None):
                if not member.bot:
                    if member.nick and arg.lower() in member.nick.lower() or arg.lower() in member.name.lower():
                        arg_found = True
                        await message.channel.send("{0} has sent `{1}` ?'s".format(member.mention, client.q_count[member.id]))
                        break
            if not arg_found:
                await message.channel.send("Could not find user {}".format(arg))

async def feet(message, var):
    elapsed = time.time() - client.t0
    if elapsed > 3600:
        with open('lick.jpg', 'rb') as f:
            picture = discord.File(f)
            await message.channel.send("Did someone say {}?".format(var))
            await message.channel.send(file=picture)
            client.t0 = time.time()
    else:
        print("{0} not enough time passed: {1}s".format(var.upper(), int(elapsed)))

client.run(TOKEN)