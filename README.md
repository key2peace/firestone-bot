
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
- Caputres F5/Esc keypress in order to pause the bot

## Tasks supported

### Alchemist
- Experiments
- Transmute

### Character
- Quests

### Engineer
- Engineer:
  - Pick up tools

### Library
- Firestone research:
  - Claim finished tasks
  - Start new researches

### Magic quarter
- Train guardians
- Enlighten guardians
- Evolving guardians
- Chaos of Rift upgrades

### Guild
- Arcane Crystal:
  - Spending a maximum of 5 pickaxes per run
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

### Main
- Upgrade heroes when possible
- On (re)start/empower, the upgrade multiplier is enforced to a configurable value

### Map
- Claim finished tasks
- Pick new tasks in the order ``mystery``, ``dragon``, ``monster``, ``war``, ``adventure``, ``scout``
- Campaign Battles:
  - Pick up the loot
  - Run daily liberation missions

### Pirate ship
- Pirates price

### Shop
- Daily rewards
- Mystery box

### Tavern
- Scarab Game:
  - Play the game
  - Pickup scarab token
  - Pickup pharao's vault
- Tavern Game:
  - Play the game (spending a max of 10 tokens per run)
  - Convert beer to tokens

### Temple of eternals
- Collect when configurable percentage has been reached
  (Note: the + can still be seen as a 4, I *AM* trying to evade this...)

## Tasks not yet supported
### Alchemist:
- Below transmute (not yet unlocked)

### Bag
- Opening chests

### Battles
- Arena of kings

### Battle pass
- anything

### Engineer
- Engineer:
  - Read selected crew setup (for Arena of kings)
- Garage:
  - Upgrades
  - Blueprints
  - Rarity
  - Index machines (for Arena of kings)

### Events

### Exotic Merchant
- Sell items
- Exotic upgrades
- Emblem market

### Guild
- Tree of Life

### Library
- Meteorite Research

### Main
- Kill miner/dragons so they disappear quicker

### Map
- Campaign:
  - Select battles

### Oracle (not yet unlocked)
- anything

### Pirate ship
- Mercenaries

### Tavern
- Ancient artifacts:
  - Upgrade
  - Rarity

## Installation
- Ensure you have at least [Python 3.10](https://www.python.org/downloads/) installed
- Install [Tesseract](https://tesseractocr.org/#install)
- Ensure python and tesseract are in your path
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
- Wanna make a screenshot? Press the Print Screen, provide a name, and it will be saved in the capture subfolder

## License
This code is released under the MIT License, for more details, see [License](https://github.com/key2peace/firestone-bot/blob/main/LICENSE)
All trademarks are property/copyright of their respected owners.
