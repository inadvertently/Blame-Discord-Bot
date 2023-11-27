# Blame Bot

<p align="center">
  <img src="https://i.imgur.com/3Yxtwyh.png" alt="Blame-Wallpaper cropped">
</p>

<p align="center">
  <a href="https://github.com/inadvertently/blamev2">
    <img src="https://img.shields.io/badge/deploy_to-heroku-997FBC.svg?style=for-the-badge&logo=Heroku">
  </a>
  <a href="https://discord.gg/AgRNafGd">
    <img src="https://img.shields.io/discord/818179462918176769.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge" alt="Support">
  </a>
  <a href="https://patreon.com/blamebot">
    <img src="https://img.shields.io/badge/patreon-donate-orange.svg?style=for-the-badge&logo=Patreon" alt="Python 3.7">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Made%20With-Python%203.8-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.8">
  </a>
  <a href="https://github.com/inadvertently/blamev2">
    <img src="https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge">
  </a>
  <a href="https://github.com/inadvertently/blamev2">
    <img src="https://img.shields.io/badge/license-agpl-e74c3c.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

---

<p align="center">
  <strong>A Discord bot with over 300 commands that make things easy! Some include:</strong>
</p>

<p align="center">
  • Advance Antinuke w/ caching, thresholds, penalties, alerts, etc<br>
  • Anti-Invite system w/ penalty system<br>
  • Antiraid w/ account age detection, profile picture, mass-joins<br>
  • Autoresponder & Autoreaction (mimics carl bot's feature)<br>
  • Autorole w/ role permission detection<br>
  • Moderation System<br>
  • Welcome & Goodbye system<br>
  • Fake Permissions (allows normal users to use moderation commands through the bot.)<br>
  • Discord games, connect4, tictactoe, battleship etc<br>
  • Greentea & Blacktea (mimics mudae bot's feature)<br>
  • Join-Dm, Ping-On-Join, Leave-Dm<br>
  • Server growth logs<br>
  • Namehistory (displays a user's name history on x dates)<br>
  • Reaction Roles<br>
  • Twitch Stream Channel alerts (mimics Mee6 bot's feature)<br>
  • Server Logging, bans, joins, voice channels, etc<br>
  • Voicemaster User Interface & Commands<br>
  • Spotify Search<br>
  • Youtube Search<br>
  • LastFM Integration<br>
  • Server Booster Rewards<br>
  • TikTok to MP4<br>
</p>

<p align="center"><b><i>
  *These are only some of the features; you can explore the source for more :)</b></i>
  <br>by Jacob, Cop, Kite & Curse. References include: Red Bot, Miso Bot & RoboDanny
</p>


---

# 📝 | Overview

Blame is meant to be an adavnced discord bot, this means all commands, modules and features can be enabled/disabled per guild. Each module that involves events, is cached opun the bot starting up. This was more of an official bot rather than something that was meant to be open-sourced - this means that it can be a bit difficult for some to get running as it contains many dependencies.

[Installation](#installation) is easy in the sense that you should have a bit of coding experience. For those that don't, i'd reccomend navigating to certain modules, extracting them, and adding them to your own bot.

---

# 📝 | Installation

* [Python 3.8+](https://www.python.org/downloads/)

* Install requirements

* **Create** a discord bot application

* Under **Privileged Gateway Intents** enable **ALL** intents [`PRESENCE INTENT`](https://discord.com/developers/applications), [`SERVER MEMBERS INTENT`](https://discord.com/developers/applications), [`MESSAGE CONTENT INTENT`](https://discord.com/developers/applications)

* Enable the required bot [permissions](https://discord.com/developers/docs/topics/permissions) (admin).

* Invite your bot to the server with the scopes [`bot & applications.commands`](https://discord.com/developers/applications/)

* Clone/Download the repo

* Create a MongoDB server (make sure to whitelist your ip address)

* You will have to create your MongoDB collections manually as this was not originally public

* Start a local redis server

```bash
pip install -r requirements.txt
```



* Insert your data within the ``.env`` file

```
MONGODB_URI = "your_mongodb_uri"
DATABASE = "your_mongodb_database"
DISCORD_TOKEN = "your_bot_token"
BOT_OWNER_ID = id
TWITCH_CLIENT_ID = "your_twitch_client_id"
TWITCH_CLIENT_SECRET = "your_twitch_client_secret"
REDIS_SERVER_IP = "your_redis_server_ip"
REDIS_SERVER_PASSWORD = "your_redis_server_password"
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
GITHUB_TOKEN = "token + your_github_token"
LASTFM_TOKEN = "your_lastfm_token"
```
*  <details><summary>How to get your Owner ID</summary>
    <p>

    1. Turn on Developer Mode under Discord Settings > Advanced 

    2. Right click on your profile icon in any chat and copy your ID 
    </p>
  </details>

* Run the main file

```bash
python main.py
```


> Important: custom emojis used by the bot will be shown as normal text due to them being hardcoded. This can simply be changed within the ``utils.py`` file, eg: `:BlurpleCheckmark:`. 

## 📌 | Usage

| Module                       | Action                                                                                                     |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `antinuke`  | Server protection, Custom limits, templates, backups, custom penalties, and so much more! |
| `antiraid`  | Detects raids, mass joins, new accounts, suspicious accounts, deafault profile pictures |
| `autoresponder`  | Allows you to set custom trigger words that it'll then respond to with custom responses |
| `anti-invite`  | Detects when invites are sent, custom punishments, whitelist specific channels |
| `goodbye`  | Custom goodbye messages, normal text, supports embeds, multiple/specific channel support |
| `welcome`  | Custom welcome messages, normal text, supports embeds, multiple/specific channel support |
| `emojis`  | Enlarge emojis, mass-add mutliple, mass-delete multiple |
| `filtersettings`  | filter specific channles to images only, text, file types, etc |
| `forcenick`  | Repetitively force a users nickname to anything until reset |
| `games`  | battleship, connect4, tictactoe, typerracer, hangman, greentea, blacktea
| `joindms`  | Set specific dm messages for users who join. Supports embeds, time intervals |
| `juul`  | Cool module where you can pass around a juul in your server, take turns using it, stealing it and breaking it until the battery reaches 0% |
| `lastfm`  | Connect your lastfm account, view server stats, global stats, etc |
| `pingonjoin`  | Set a specific channel where new joined users will be pinged upon verification (good for giveaways) |
| `namehistory`  | View all stored name changes for yourself or a friend |
| `prefix`  | Set the prefix for your server, multiple supported |
| `reactionroles`  | Create custom reaction roles for your server (most used for verification, similar to carl bot) |
| `rtfm`  | Search and retrieve all similar results from the discord.py docs to the given parameter |
| `tags`  | Set specific tags within your server which users can navigate through and retrieve results (good for servers that have documentation) |
| `twitch`  | Allow your server to get notified when a specific streamer streams. Supports multiple channels & streamers |
| `logs`  | Set log channels for the following: joins, leaves, channel creations, vc joins, vc leaves, kicks, bans, unbans |
| `voicemaster`  | Yea it's in the name. It's a literal remake of voicemaster but with an interface |
| `webhooks`  | Send, edit, delete webhooks with private codes rather than having the webhook URL's visible to staff |
| `moderation`  | Pretty much everything, it's too many commands to list |
| `autorole`  | Set a specific role which new users will be assigned when joining your server. Supports multiple roles and also makes sure the role does not have any dangerous perms |
| `autoreact`  | Allows you to set custom trigger words that it'll then respond to by reacting with specific emoji(s) |
| `boost`  | Custom roles, boost messages, and rewards upon a user boosting the server |
| `fakeperms`  | Set specific commands that normal users can use through the bot. Eg: ``;fakeperms set @jacob ban_members`` This will allow jacob to use any command through the bot that requires ``ban_members`` permission|

# ❓ | Why was blame discontinued?

Many reasons. My plan was not to discontinue blame but as the saying goes, all good things come to an end.

Project Blame began in January of 2021 with the main developer being Sorrow (We'll refer to him as Jacob). The goal was to create a bot that can protect against Server Nuking, Server Raids and bot abuse. As the year progressed, Kite, had stumbled across the project and later on joined the team and took charge of the bots marketing. Blame was officially released on Sepetember 25, 2021. Within the first month of development, the bot grew astronomically which gave us a ton of motivation to continue the project. During 2022, the bot began to progress but extremly faster than before. We were in need of a dev, not just any, we needed one with experience; then came along **zack**. Zack was able to scale the bot as it needed to be which we had failed to do beforehand.

Today, Blame has came a long way from it's humble beginnings and reached a guild count of 12,000 and a usercount of 10,000,000.
