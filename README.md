# Disclaimer
This bot is not intended to be distributed and is just an educational tool. Ubisoft does not have a public API for Rainbow Six Siege, so the bot retrieves data from r6.tracker.network via scraping. It is legal, but is against their terms of service. I am in contact with them to get permission to actually use the bot, but until then it is only to be observed as an exercise, and not for practical use.

# R6_Discord_Bot
Welcome to my Rainbow Six Siege Discord bot! This bot has many features and tracks the performance of any PC Rainbow Six Siege player via commands in Discord.
In addition, it automatically sends new patch notes when they come out.
This bot uses the BeautifulSoup framework to retrieve player data from r6.tracker.network and occasionally checks ubisoft.com for Rainbow 6 Siege patch note updates

## Commands
The bot features multiple commands which can be called by using the command prefix "!".
All of the commands can be viewed by typing !help in any server that the discord bot is in.<br><br>
**Here are the current commands:**
* !Help - outputs an explanation of each comamnd
* !SeasonStats [username] - measures a player's performance for the current ranked season
* !KD [username] - measures a player's performance for all ranked and unranked games.
* !TopOps [username] - shows a player's top 3 operators that they play

## Patch Note Detection
The bot checks Ubisoft.com's website every 10 minutes for new patch note updates. If a new patch note article is uploaded, the bot records it and sends
the link in the discord server.
