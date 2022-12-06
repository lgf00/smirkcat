import random
import time
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import re
import requests
from PIL import Image
import os
from fuzzywuzzy import fuzz
from yt_dlp import YoutubeDL
import cv2
import RPi.GPIO as GPIO
import imageio
import json

load_dotenv()

GUILDS = [753006002533564596, 792880922525040670]
bot = commands.Bot(intents=nextcord.Intents.all())
bot.lick_timer = 0
bot.lick_max = 604800
bot.breeze_timer = 0
bot.breeze_max = 604800
bot.prev_ym = []
bot.count = {}
tiktok = re.compile(
    "([\\S\\s]*)(https:\\/\\/[a-z]+.tiktok.com\\/[t\\/]*[A-Za-z0-9]+\\/)([\\S\\s]*)"
)
yourmom = re.compile(
    "[\\S\\s]*y[\\S\\s]*o[\\S\\s]*u[\\S\\s]*r[\\S\\s]*m[\\S\\s]*o[\\S\\s]*m[\\S\\s]*"
)
link = re.compile(
    "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
)
decrec = re.compile("^(\\W+)|(\\W+)$")
bot.speed = 0.07
bot.on = True
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
bot.dev_user = None


@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game("with your mom"))
    for guild in bot.guilds:
        await guild.me.edit(nick="Meow Meow 🙀")
        print("### LOGGED IN AS {0.user}, guild: {1} ###".format(bot, guild))
    with open("count.json", "rb") as f:
        bot.count = json.load(f)
    bot.dev_user = await bot.fetch_user(155512383681462272)
    if bot.dev_user is not None:
        if bot.dev_user.dm_channel is None:
            await bot.dev_user.create_dm()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_member_join(member: nextcord.Member):
    print("new member")
    for text in bot.count:
        bot.count[text][str(member.id)] = 0
    dump_count()


@bot.event
async def on_message(mes: nextcord.Message):
    if mes.author == bot.user or mes.author.bot:
        return
    message_oneline = mes.content.replace("\n", "").lower()
    if getFuzzyRatio(message_oneline) > 80 or "your mom" in mes.content:
        print("YM same or YM")
    else:
        if re.fullmatch(
            yourmom,
            message_oneline,
        ) and not re.fullmatch(link, message_oneline):
            if len(bot.prev_ym) > 10:
                bot.prev_ym.pop(0)
            bot.prev_ym.append(message_oneline)
            print("contains your mom")
            async with mes.channel.typing():
                ac = findAc(message_oneline, "yourmom")
                bot.prev_ym.append(ac)
                await mes.channel.send(ac)
    for trigger in ["feet", "foot", "toes", "toe"]:
        if f" {trigger} " in f" {message_oneline} ":
            async with mes.channel.typing():
                await feet(mes, trigger)
    if "breeze" in message_oneline:
        async with mes.channel.typing():
            await breeze(mes)
    if tiktok.fullmatch(mes.content):
        print("tiktok found in message")
        async with mes.channel.typing():
            await sendDownloadedTiktok(mes, tiktok.match(mes.content).group(2))
    decon = deconstruct(message_oneline)
    print(f"dec msg '{decon}'")
    for text in bot.count["tocount"]:
        dec_text = text
        if len(text) != 1:
            dec_text = deconstruct(text)
        if dec_text in decon:
            print(f"count found... text")
            bot.count[text][str(mes.author.id)] += decon.count(dec_text)
            dump_count()


def replacer(match):
    if match.group(1) is not None:
        return "{} ".format(match.group(1))
    else:
        return " {}".format(match.group(2))


def deconstruct(mes):
    mes = " ".join([decrec.sub(replacer, word) for word in mes.split()])
    return mes


async def feet(message, word):
    print("FEET...", message.content)
    elapsed = time.time() - bot.lick_timer
    if elapsed > bot.lick_max:
        with open("lick.jpg", "rb") as f:
            picture = nextcord.File(f)
            await message.channel.send("Did someone say {}?".format(word))
            await message.channel.send(file=picture)
            bot.lick_timer = time.time()
    else:
        print(
            message.guild,
            "*** {0} not enough time passed: {1}s ***".format(
                word.upper(), int(elapsed)
            ),
        )


async def breeze(message):
    print(message.guild, "BREEZE...", message.content)
    elapsed = time.time() - bot.breeze_timer
    if elapsed > bot.breeze_max:
        await message.channel.send("breeze isn't even that big guys")
        bot.breeze_timer = time.time()
    else:
        print(
            message.guild,
            "*** BREEZE not enough time passed: {0}s ***".format(int(elapsed)),
        )


def findAc(text, phrase):
    if len(phrase) == 0:
        return text
    letter = phrase[0]
    phrase = phrase[1:]
    pos = -1
    try:
        pos = text.index(letter)
    except ValueError:
        return text

    before = text[0:pos]
    after = text[pos + 1 :]

    return (
        before
        + "("
        + letter
        + ")"
        + " ".join(findAc(after, "".join(phrase)).split("( )"))
    ).replace(")(", "")


@bot.slash_command(
    description="Starts a new count on specified word or phrase",
    guild_ids=GUILDS,
)
async def countnew(
    interaction: nextcord.Interaction,
    text: str = nextcord.SlashOption(description="the word or phrase to be counted"),
):
    await interaction.response.defer(ephemeral=True)
    if text in bot.count["tocount"]:
        await interaction.send("already being counted, use /countlist to see a list of what is being counted\n/countget or /counttop to see the count", ephemeral=True)
    text = text.lower()
    bot.count[text] = {}
    bot.count["tocount"].append(text)
    t0 = time.time()
    print("new count started")
    print(bot.count)
    # CREATING NEW ENTRIES FOR TEXT
    print("creating dict entries")
    async for member in interaction.guild.fetch_members(limit=None):
        if not member.bot:
            bot.count[text][str(member.id)] = 0
    print(bot.count)
    # COLLECTING MESSAGES
    print("downloading all messages")
    msgs: list[nextcord.Message] = []
    for channel in interaction.guild.channels:
        if str(channel.type) == "text":
            msgs.extend(await channel.history(limit=None).flatten())
    # COUNTING
    print("counting all messages")
    dec_text = text
    if len(text) != 1:
    	dec_text = deconstruct(text)
    for msg in msgs:
        if msg.author.bot:
            continue
        dec = deconstruct(msg.content.lower())
        if dec_text in dec:
            bot.count[text][str(msg.author.id)] += dec.count(dec_text)
    # UPDATING JSON
    print("updating json")
    dump_count()
    t1 = time.time()
    print(f"finished in {t1-t0}s")
    await interaction.send(
        '{0} count complete on **{1}**\ntotal messages searched: {2}\ntime elapsed: {3}m'.format(
            interaction.user.mention,
            text,
            len(msgs),
            int((t1 - t0) / 60),
        )
    )


@bot.slash_command(
    description="get the count of specified phrase and users",
    guild_ids=GUILDS,
)
async def countget(
    interaction: nextcord.Interaction,
    text: str = nextcord.SlashOption(
        description="valid, already counted word or phrase (use /countlist to get a list of what is being counted)",
    ),
    users: str = nextcord.SlashOption(
        description="type one or more names (can be @mentions) separated by spaces"
    ),
):
    if text not in bot.count["tocount"]:
        await interaction.send("invalid text, use /countlist to get a list of what is being counted, otherwise start a new count using /countnew", ephemeral=True)
        return
    names = users.split(" ")
    names = [i for i in names if i != ""]
    content = ""
    for name in names:
        member: nextcord.Member = await get_member(interaction, name)
        content += f"{member.mention} has said **{text}** {bot.count[text][str(member.id)]} times\n"
    if len(content) == 0:
        await interaction.send("uhoh spaghetti-oh", ephemeral=True)
        return
    await interaction.send(content)


@bot.slash_command(
    description="get the top 5 users of a specified phrase",
    guild_ids=GUILDS,
)
async def counttop(
    interaction: nextcord.Interaction,
    text: str = nextcord.SlashOption(
        description="valid, already counted word or phrase (use /countlist to get a list of what is being counted)",
    )
):
    if text not in bot.count["tocount"]:
        await interaction.send("invalid text, use /countlist to get a list of what is being counted, otherwise start a new count using /countnew", ephemeral=True)
        return
    top5 = sorted(bot.count[text], key=bot.count[text].get, reverse=True)[:5]
    content = f"TOP 5 ***{text}***:\n"
    for t in top5:
        member: nextcord.Member = await interaction.guild.fetch_member(t)
        content += f"{member.mention} - {bot.count[text][t]}\n"
    await interaction.send(content)


@bot.slash_command(
    description="list of text that is currently being counted",
    guild_ids=GUILDS,
)
async def countlist(
    interaction: nextcord.Interaction
):
    content = ""
    for text in bot.count["tocount"]:
        content += f"**{text}**, "
    if len(content) == 0:
        await interaction.send("nothing has been counted, use /countnew to change that", ephemeral=True)
        return
    await interaction.send(content[:-2], ephemeral=True)


def rescale_frame(frame, percent):
    if percent == 100:
        return frame
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def on_callback(channel):
    if bot.on:
        bot.on = False
        GPIO.output(16, GPIO.HIGH)
    else:
        bot.on = True
        GPIO.output(16, GPIO.LOW)


@bot.slash_command(
    description="Takes a picture of lucas at his desk, options: gif, scale (named by willem)",
    guild_ids=GUILDS,
)
async def peekaboo(
    interaction: nextcord.Interaction,
    gif: bool = nextcord.SlashOption(
        description="get a fun little gif of lucas instead", required="false"
    ),
    scale: int = nextcord.SlashOption(
        description="the larger it is the longer it takes to create (default 25 for gif, 100 for image)",
        required="false",
        choices={10, 25, 100},
    ),
):
    await interaction.response.defer(ephemeral=True)
    print("peekaboo")
    if not bot.on:
        await interaction.send("mimimimimi :sleeping_accommodation:")
        return
    vid = cv2.VideoCapture(0)
    blink_time = 5 / (bot.speed * 2)
    scale_by = 100
    if gif:
        while blink_time > 0:
            GPIO.output(10, GPIO.HIGH)
            time.sleep(bot.speed)
            GPIO.output(10, GPIO.LOW)
            time.sleep(bot.speed)
            blink_time -= 1
        print("capturing gif")
        frames = []
        count = 0
        if scale:
            scale_by = scale
        else:
            scale_by = 25
        time.sleep(0.5)
        GPIO.output(10, GPIO.HIGH)
        while True:
            ret, frame = vid.read()
            if not ret:
                print("ret error capturing frame")
                await bot.dev_user.dm_channel.send("ret error capturing frame")
                interaction.send(
                    content="```diff\n- Something went wrong!\n```", ephemeral=True
                )
                return
            frames.append(
                rescale_frame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), percent=scale_by)
            )
            count += 1
            if count == 150:
                break
        GPIO.output(10, GPIO.LOW)
        print("creating gif")
        try:
            imageio.mimsave("./dancemonkeydance.gif", frames, fps=30)
            print("done creating gif")
            await interaction.send(file=nextcord.File("./dancemonkeydance.gif"))
        except Exception as e:
            print(e)
            await bot.dev_user.dm_channel.send(e)
            await interaction.send(
                content="```diff\n- File probably too big!\n```", ephemeral=True
            )
    else:
        while blink_time > 0:
            GPIO.output(8, GPIO.HIGH)
            time.sleep(bot.speed)
            GPIO.output(8, GPIO.LOW)
            time.sleep(bot.speed)
            blink_time -= 1
        print("capturing image")
        time.sleep(0.5)
        GPIO.output(8, GPIO.HIGH)
        ret, frame = vid.read()
        if not ret:
            print("ret error capturing frame")
            await bot.dev_user.dm_channel.send("ret error capturing frame")
            interaction.send(
                content="```diff\n- Something went wrong!\n```", ephemeral=True
            )
            return
        GPIO.output(8, GPIO.LOW)
        print("done capturing image")
        if scale:
            scale_by = scale
        try:
            frame = rescale_frame(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), percent=scale_by
            )
            cv2.imwrite("capture.jpg", frame)
            await interaction.send(file=nextcord.File("./capture.jpg"))
        except Exception as e:
            print(e)
            await bot.dev_user.dm_channel.send(e)
            await interaction.send(
                content="```diff\n- Something went wrong!\n```", ephemeral=True
            )
    vid.release()


@bot.slash_command(
    description="Displays a users avatar and is never wrong", guild_ids=GUILDS
)
async def avatar(
    interaction: nextcord.Interaction,
    users: str = nextcord.SlashOption(
        description="type one or more names (can be @mentions) separated by spaces"
    ),
):
    names = users.split(" ")
    names = [i for i in names if i != ""]
    print(names)
    for name in names:
        member: nextcord.Member = await get_member(interaction, name)
        if member:
            embed = nextcord.Embed()
            embed.color = nextcord.Color.from_rgb(114, 137, 218)
            embed.title = str(member)
            if random.random() <= 0.2:
                embed.description = f"**[Avatar URL]({await get_pfp()})**"
                file = nextcord.File("pfp.png", filename="pfp.png")
                embed.set_image(url="attachment://pfp.png")
                await interaction.send(file=file, embed=embed)
            else:
                embed.description = f"**[Avatar URL]({member.avatar.url})**"
                embed.set_image(url=member.avatar.with_size(256).url)
                await interaction.send(embed=embed)
        else:
            print(f"{name} not found")
            await interaction.send(
                f"```diff\n- Could not find user with name: {name}\n```", ephemeral=True
            )


# GET MEMBER OBJECT FROM NAME
async def get_member(ctx, name):
    m = None
    async for member in ctx.guild.fetch_members(limit=None):
        if (
            member.nick
            and name.lower() in member.nick.lower()
            or name.lower() in member.name.lower()
            or name == member.mention
        ):
            m = member
            break
    return m


async def get_pfp():
    r = requests.request(
        "GET",
        "https://v2.yiff.rest/furry/bulge/image",
        headers={"User-Agent": 'Smirkcat/4.0.0 (lgf#5547; "Discord")'},
    )
    if r.status_code == 200:
        open("pfp.png", "wb").write(r.content)
        old_im = Image.open("pfp.png")
        old_im.thumbnail((256, 256))
        old_size = old_im.size

        new_size = (256, 256)
        new_im = Image.new("RGB", new_size)  # luckily, this is already black!
        box = tuple((n - o) // 2 for n, o in zip(new_size, old_size))
        new_im.paste(old_im, box)

        new_im.save("pfp.png")
        return r.headers.get("x-yiffy-short-url")
    return None


def getFuzzyRatio(mes):
    if len(bot.prev_ym) == 0:
        return 0
    ratio = max([fuzz.ratio(mes, s) for s in bot.prev_ym])
    return ratio


async def sendDownloadedTiktok(mes: nextcord.Message, link):
    yt_ops = {
        "outtmpl": "./dltiktok.%(ext)s",
        "format": "bv[vcodec=h264]+ba/w+[format_id!=play_addr]",
    }
    try:
        with YoutubeDL(yt_ops) as ydl:
            if "www" in link:
                link = link.replace("www", "vm")
                print(link)
            ydl.download(link)
        await mes.reply(file=nextcord.File(r"./dltiktok.mp4"))
        os.remove("./dltiktok.mp4")
    except Exception as e:
        print(e)
        bot.dev_user.send(e)
        await mes.reply("slide show :nauseated_face:")


def dump_count():
    with open("count.json", "w") as f:
        json.dump(bot.count, f)


GPIO.add_event_detect(12, GPIO.RISING, callback=on_callback)
bot.run(os.environ["TOKEN"])
