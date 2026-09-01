
# firestone-bot
[SikuliX/OculiX](https://github.com/oculix-org/Oculix "SiuliX/OculiX") inspired bot for [Firestone - Idle Clicker](https://holydaygames.com/firestone "Firestone - Idle Clicker")

![](https://img.shields.io/github/stars/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/forks/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/tag/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/release/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/issues/key2peace/firestone-bot.svg)

## Introduction
With my history into botting for various reasons (eggdrop/sikuli/greasemonkey/idlerpg (irc)/multirpg (irc) in my brain and the game actually allowing botting, I simply couldn't resist the temptation. While writing around happily I noticed some strange behaviour in sikulix, stuff missmatching etc, I had 2.0.4 running and thought, hey, let's update...

But sadly, new OculiX IDE looking shiny on my desktop, getting frustrated by the IDE itself (I mean c'mon, 2 ways to close a tab??), I noticed that old time bugs still didn't disappear. So I turned to Gemini AI. What came out of this extensive collaboration is what you are seeing here.

## Highlights
- Pure python using cv2, pyautogui, mss, pydirectinput amongst other imports.
- Requires the game running fullscreen on the primary monitor at 1920x1080 resolution.
- Internal timeout mechanisms to reduce cpu load by skipping tasks that are surely not going to appear for a while.
- Verification of task images before clicking.
- Ollama support (llama3.2(-vision)) preffered as it already knows the game and is fast and small.

## Features
- Auto maximize and disable gamebar on crazygames
- Crazygames crash dialog detection
- Caputres F5/Esc keypress in order to pause the bot
- Configuration dialog
- Multi monitor support

## Tasks supported

### Alchemist
- Experiments (3 minutes before end for free)
- Transmute

### Battle field
- Bag:
  - Opening all chests except the first one (common mostly) in order to open those after sign-in to meet daily requirements
- Heroes level upgrading
  that is, if they are known, this is in order to facilitate users with less then 6 members in their party.
  If you do not see them being upgraded, they have not been captured yet,  in that case please submit an issue providing a 1:1 image capture
  of the area not being upgraded, and I will add them as soon as possible.
  See [this](https://github.com/key2peace/firestone-bot/tree/main/src/images/heroes) page for the current list of supported heroes
  **NOTE: IF YOU CHANGE YOUR PARTY SIZE, PRESS ESC OR F5 IN ORDER TO INITIALIZE A RELOAD OF THE PARTY CHECKER!**
- Special upgrades
- Battle pass
- Mail:
  - Claiming rewards
  - Deleting claimed messages
- On (re)start/empower, the upgrade multiplier is enforced to a configurable value
- Events:
  - mini events listed on wiki
  - calendar events listed on wiki
  Other events(/types) will be added as soon as I see/play them

### Character
- Quests
- Talents

### Engineer
- Engineer:
  - Pick up tools

### Exotic Merchant
- Sell items
- Exotic upgrades
- Emblem market

### Guild
- Arcane Crystal:
  - Spending a maximum of 5 pickaxes after welcome sign-in to complete daily
- Awakening
- Bank:
  - Perform max bank deposit
  - Visit treasury
  - Visit bank log
  - Claim Locker rewards
- Chaos Rift:
  - Fight monster
  - Supplies
- Forbidden Knowledge:
  - Perform upgrades and recruiting
- Guild expeditions
- Guild hall:
    - Guild log

### Library
- Firestone research:
  - Claim finished tasks (3 minutes before end for free)
  - Start new researches
- Meteorite Research

### Magic quarter
- Train guardians
- Enlighten guardians
- Evolving guardians
- Chaos of Rift upgrades

### Map
- Claim finished tasks (3 minutes before end for free)
- Refresh for free 3 minutes before end
- Pick new tasks in the order defined in config
- Experimental support for silver missions (not yet unlocked map level 10 to test)
- Campaign Battles:
  - Pick up the loot
  - Run daily liberation missions

### Oracle
- Rituals
- Blessings
- Obtain oracle gift from shop

### Pirate ship
- Pirates price

### Shop
- Amulet of the day (configurable)
  **WARNING**: This **will** spend either 20 keys or 2000 gems when the amulet(s) of choice becomes available.
- Daily rewards
- Mystery box

### Tavern
- Scarab Game:
  - Play the game
  - Pickup scarab token
  - Pickup pharao's vault
  - Pickup scarab milestones
  - Release beast
- Tavern Game:
  - Play the game (saving 10 tokens for dailies)
  - Convert beer to tokens
  - Crafting ancient artifacts

### Temple of eternals
- Collect when configurable percentage has been reached
- Use temple tokens at a configurable percentage

## Tasks/Features not (yet) supported

### Alchemist:
- Below transmute (not yet unlocked)

### Battles
- Arena of kings

### Engineer
- Garage:
  - Upgrades
  - Blueprints
  - Rarity

### Events
- Prepare for the bi-monthly 'Decorated Heroes' event, saving up needed materials

### General
- Walk through the beginning dialogs if you start fresh
- Settings Webserver
- More detailed logging what the bot is doing
- Improve OCR
- Finetune timeouts
- Server reconnect detection
- Test on other platforms (feel free to share your experience):
  - Operating systems:
    - Linux
    - MacOS
  - Game enviroments:
    - ArmorGames
    - Epic Games (do I really even wanna support that?)
    - Facebook
    - Kongregate
    - Miniplay
    - R2Games
    - Steam
    - Yandex

### Guild
- Tree of Life

### Hall of heroes
- Equipment unlocking
- Gear enchanting
- Jewel enchanting
- Seals of power
- Hero rarity

### Map
- Campaign:
  - Select battles

### Pirate ship
- Mercenaries

### Tavern
- Ancient artifacts:
  - Upgrade
  - Rarity
- Beasts:
  - Upgrade
  - Rarity

## Installation
- Ensure you have at least [Python 3.10](https://www.python.org/downloads/) installed
- Install [Tesseract](https://tesseractocr.org/#install)
- Ensure python and tesseract are in your PATH
- Then:
```
	git clone https://github.com/key2peace/firestone-bot.git
	cd firestone-bot
	pip install -r requirements.txt
```

## Starting
- Run the code:
```
cd firestone-bot/src
python main.py
```
- Start the game and go full-screen
- When ready, press the Scroll-Lock key.
- If things go wrong -> Scroll-Lock
- Press the HOME button to configure things

## License
This code is released under the MIT License, for more details, see [License](https://github.com/key2peace/firestone-bot/blob/main/LICENSE)
All trademarks are property/copyright of their respected owners.
