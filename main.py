import discord
import requests
from discord.ext import commands
from discord.ext import tasks
from bs4 import BeautifulSoup

BOT_TOKEN = "Your Token"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)

#Manages the most recent patch note link
class PatchNotesManager:
    def __init__(self):
        self.last_PatchNotes = None
        self.prev_PatchNotes = None

    def update_patch_notes(self, new_patch_notes):
        self.last_PatchNotes = new_patch_notes

    def update_prev_notes(self, prev_patch_notes):
        self.prev_PatchNotes = prev_patch_notes

    def get_last_patch_notes(self):
        return self.last_PatchNotes
    
    def get_prev_patch_notes(self):
        return self.prev_PatchNotes
    
patch_notes_manager = PatchNotesManager()

async def find_patch_notes():
    URL = f"https://www.ubisoft.com/en-us/game/rainbow-six/siege/news-updates"
    page = requests.get(URL)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")
    updatesfeed_item = soup.find('a', class_='updatesFeed__item')
    if updatesfeed_item:
        last_PatchNotes = 'https://www.ubisoft.com' + updatesfeed_item.get('href')
        patch_notes_manager.update_patch_notes(last_PatchNotes)
        #When a new patch note is found, trigger the print_patch_notes function and update the patch note manager
        if patch_notes_manager.get_last_patch_notes() != patch_notes_manager.get_prev_patch_notes():
            print("New patches found, printing")
            patch_notes_manager.update_prev_notes(patch_notes_manager.get_last_patch_notes())
            await print_patch_notes()
    else:
        print("Last patch notes not found")

async def print_patch_notes():
    for guild in bot.guilds:
        channel = guild.system_channel #getting system channel
        if channel.permissions_for(guild.me).send_messages: #making sure you have permissions
            await channel.send(patch_notes_manager.get_last_patch_notes())


@bot.event
async def on_ready():
    URL = f"https://www.ubisoft.com/en-us/game/rainbow-six/siege/news-updates"
    page = requests.get(URL)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")
    updatesfeed_item = soup.find('a', class_='updatesFeed__item')
    if updatesfeed_item:
        prev_PatchNotes = 'https://www.ubisoft.com' + updatesfeed_item.get('href')
        patch_notes_manager.update_prev_notes(prev_PatchNotes)
        print("prev patch notes: ", prev_PatchNotes)
    else:
        print("Last patch notes not found")
    print("Hello world!")

@tasks.loop(minutes=10.0, count=None)
async def backround_patchnotes_checker():
    print("Checking patch")
    await find_patch_notes()



bot.remove_command("help")


@bot.command()
async def Help(ctx):
    message = (
            f"------------------------------\n"
            f"R6 Bot retrieves stats for Rainbow 6 Siege\n\n"
            f"List of commands\n"
            f"\t!SeasonStats [username] - Lists the kd and winrate for the current season\n"
            f"\t!KD [username] - Lists the kd for unranked and all ranked seasons\n"
            f"\t!TopOps [username] - Lists the top 3 operators of a player\n"
            f"------------------------------"
        )
    await ctx.send(message)


@bot.command()
async def KD(ctx, username):
    try:
        URL = f"https://r6.tracker.network/profile/pc/{username}"
        page = requests.get(URL)
        page.raise_for_status()
       
        soup = BeautifulSoup(page.text, "html.parser")

        kills_div = soup.find('div', {'data-stat': 'RankedKills'})
        kills_value = int(kills_div.get_text(strip=True).replace(',', ''))

        deaths_div = soup.find('div', {'data-stat': 'RankedDeaths'})
        deaths_value = int(deaths_div.get_text(strip=True).replace(',', ''))  # Convert to integer

        u_kills_div = soup.find('div', {'data-stat': 'UnRankedKills'})
        u_kills_value = int(u_kills_div.get_text(strip=True).replace(',', ''))

        u_deaths_div = soup.find('div', {'data-stat': 'UnRankedDeaths'})
        u_deaths_value = int(u_deaths_div.get_text(strip=True).replace(',', ''))  # Convert to integer

        kd_ratio = kills_value / deaths_value if deaths_value != 0 else 0.0
        u_kd_ratio = u_kills_value / u_deaths_value if u_deaths_value != 0 else 0.0

        message = (
            f"{username}'s KD:\n"
            f"------------------------------\n"
            f"All ranked seasons:\n"
            f"\tKills: {kills_value}\n"
            f"\tDeaths: {deaths_value}\n"
            f"\tKDA: {kd_ratio:.2f}\n\n"
            f"Unranked:\n"
            f"\tKills: {u_kills_value}\n"
            f"\tDeaths: {u_deaths_value}\n"
            f"\tKDA: {u_kd_ratio:.2f}\n"
            f"------------------------------\n"   
        )
        await ctx.send(message)
    except requests.RequestException as e:
        await ctx.send(f"Error: Invalid username")

@bot.command()
async def TopOps(ctx, username):
    try:
        URL = f"https://r6.tracker.network/profile/pc/{username}"
        page = requests.get(URL)
        page.raise_for_status()
       
        soup = BeautifulSoup(page.text, "html.parser")

        operators_div = soup.find('div', class_='trn-defstat__value')
        operator_titles = [img['title'] for img in operators_div.find_all('img')]
        if len(operator_titles) == 0:
            await ctx.send("User not found")
            return


        formatted_operator_titles = "\n".join([f"{i+1}. {title.capitalize()}" for i, title in enumerate(operator_titles)])
        message = (
            f"{username}'s Top Operators:\n"
            f"------------------------------\n"
            f"{formatted_operator_titles}\n" 
            f"------------------------------\n"
        )
        await ctx.send(message)
    except requests.RequestException as e:
        await ctx.send(f"Error: Invalid username")

@bot.command()
async def SeasonStats(ctx, username):
    try:
        URL = f"https://r6.tracker.network/profile/pc/{username}"
        page = requests.get(URL)
        page.raise_for_status()
       
        soup = BeautifulSoup(page.text, "html.parser")

        season_stats_div = soup.find('div', class_='r6-season__stats')

        kills_name_div = season_stats_div.find('div', class_='trn-defstat__name', string='Kills')
        kills_value = int(kills_name_div.find_next('div', class_='trn-defstat__value').get_text(strip=True).replace(',', ''))

        deaths_name_div = season_stats_div.find('div', class_='trn-defstat__name', string='Deaths')
        deaths_value = int(deaths_name_div.find_next('div', class_='trn-defstat__value').get_text(strip=True).replace(',', ''))

        if not deaths_value:
            await ctx.send("Player does not exist")

        winrate_name_div = season_stats_div.find('div', class_='trn-defstat__name', string='Win %')
        winrate_value = winrate_name_div.find_next('div', class_='trn-defstat__value').get_text(strip=True)

        currentRank_name_div = season_stats_div.find('div', class_='trn-defstat__name', string='Rank')
        currentRank_value = currentRank_name_div.find_next('div', class_='trn-defstat__value').get_text(strip=True)

        kd_ratio = kills_value / deaths_value if deaths_value != 0 else 0.0
        message = (
            f"{username}'s stats:\n"
            f"------------------------------\n"
            f"Rank: {currentRank_value}\n"
            f"Kills: {kills_value}\n"
            f"Deaths: {deaths_value}\n"
            f"KD Ratio: {kd_ratio:.2f}\n"
            f"Winrate: {winrate_value}%\n"
            f"------------------------------"
        )
        await ctx.send(message)
    except requests.RequestException as e:
        await ctx.send(f"Error: Invalid Username")



bot.run(BOT_TOKEN)