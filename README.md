# Charfred_Bot

> Charfred is a modular, run-it-yourself bot for Discord, with a mixed bag of capabilities, including extensions and a cli-tool for Minecraft server administration.

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/gluten-free.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/contains-technical-debt.svg)](https://forthebadge.com)

---

This repository only contains the base bot and administrative extensions, all other extensions are currently included in the 'cogs' submodule.

To make full use of Charfred's capabilities you will have to install and run the bot yourself;

Especially the Minecraft related extentions will not function if Charfred is not hosted on the same machine as your Minecraft server(s).

## Installation

__Python 3.6 or higher required__

Clone this repository:

`git clone https://github.com/Kellador/Charfred_Bot.git`

Install with pip:

`pip install -e </path/to/cloned/repo>`

This will install `charfred` as a command usable from your current python environment.

On first startup you will have to give Charfred a bot token via cli argument:

`charfred --token <yourbottokenhere>`

this will save initialize the bot config file and save the bot token for later,
so afterwards you only need to run `charfred` to start him up.

---

The rest of this readme is a work in progress, so just enjoy this cat gif for now:

[![INSERT YOUR GRAPHIC HERE](https://i.imgur.com/lVlPvCB.gif)]()
> found on imgur, credit to sheepfilms
