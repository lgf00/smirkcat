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
from yt_dlp.utils import DownloadError

load_dotenv()

GUILDS = [753006002533564596, 792880922525040670]
bot = commands.Bot(intents=nextcord.Intents.all())
bot.lick_timer = 0
bot.lick_max = 604800
bot.breeze_timer = 0
bot.breeze_max = 604800
bot.prev_ym = []
tiktok = re.compile(
    "([\\S\\s]*)(https:\\/\\/[a-z]+.tiktok.com\\/[t\\/]*[A-Za-z0-9]+\\/)([\\S\\s]*)"
)
yourmom = re.compile(
    "[\\S\\s]*y[\\S\\s]*o[\\S\\s]*u[\\S\\s]*r[\\S\\s]*m[\\S\\s]*o[\\S\\s]*m[\\S\\s]*"
)
link = re.compile(
    "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=nextcord.Game("with your mom"))
    for guild in bot.guilds:
        await guild.me.edit(nick="Meow Meow 🙀")
        print("### LOGGED IN AS {0.user}, guild: {1} ###".format(bot, guild))


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
            ac = findAc(mes.content.lower(), "yourmom")
            bot.prev_ym.append(ac)
            await mes.channel.send(ac)
    for trigger in ["feet", "foot", "toes", "toe"]:
        if f" {trigger} " in f" {message_oneline} ":
            await feet(mes, trigger)
    if "breeze" in message_oneline:
        await breeze(mes)
    if tiktok.fullmatch(mes.content):
        print("tiktok found in message")
        await sendDownloadedTiktok(mes, tiktok.match(mes.content))


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
            await interaction.send(f"Could not find user with name: {name}")


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


async def sendDownloadedTiktok(mes: nextcord.Message, match: re.Match):
    async with mes.channel.typing():
        yt_ops = {
            "outtmpl": "./dltiktok.%(ext)s",
            "format": "bv[vcodec=h264]+ba/w+[format_id!=play_addr]",
        }
        try:
            with YoutubeDL(yt_ops) as ydl:
                ydl.download([match.group(2)])
            await mes.reply(file=nextcord.File(r"./dltiktok.mp4"))
            os.remove("./dltiktok.mp4")
        except DownloadError:
            print("download error, most likely slide show")
            await mes.reply("slide show :nauseated_face:")


bot.run(os.environ["TOKEN"])
