
# firestone-bot
[SikuliX/OculiX](https://github.com/oculix-org/Oculix "SiuliX/OculiX") inspired bot for [Firestone - Idle Clicker](https://holydaygames.com/firestone "Firestone - Idle Clicker")

![](https://img.shields.io/github/stars/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/forks/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/tag/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/release/key2peace/firestone-bot.svg) ![](https://img.shields.io/github/issues/key2peace/firestone-bot.svg)

## Introduction
With my history into botting for various reasons (eggdrop/sikuli/greasemonkey/idlerpg (irc)/multirpg (irc) in my brain and the game actually allowing botting, I simply couldn't resist the temptation. While writing around happily I noticed some strange behaviour in sikulix, stuff missmatching etc, I had 2.0.4 running and thought, hey, let's update...

But sadly, new OculiX IDE looking shiny on my desktop, getting frustrated by the IDE itself (I mean c'mon, 2 ways to close a tab??), I noticed that old time bugs still didn't disappear. So I turned to Gemini AI. What came out of this extensive collaboration is what you are soon will be seeing here.

## Highlights
- SikuliX/OculiX turned out to have some nasty bugs we couldn't work around, so we decided to implement a shiny new mini core addressing OpenCV directly, emulating the parts of sikulix we need to maintain compatibility for the existing code. The mini core turned out to become bloody fast.
- Pattern image files are being optimized for better matching performance
- We utilize RAM for image processing, disk i/o is being minimized

## License
This code is released under the MIT License
for more details, see [License](https://github.com/key2peace/firestone-bot/blob/main/LICENSE)
