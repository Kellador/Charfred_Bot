#!/usr/bin/env python

import discord
from discord.ext import commands
import configs as cfg
import keywords
import re
import random
import asyncio
import pexpect as pexp

serverRX = re.compile(('|'.join(map(re.escape, list(cfg.servers.keys())))))
rawPattern = '(({})\s*.*?((?=\s*and|,)|(?=\s*\W*$)|(?=\s*({}))|(?=\s*,?\s*({})$)))'.format(
    '|'.join(list(cfg.commands.keys())),
    '|'.join(list(cfg.commands.keys())),
    '|'.join(map(re.escape, keywords.keyphrases)))
cmdPattern = re.compile(rawPattern)


description = ('Charfred is a gentleman through and through,'
               ' he will do almost anything you ask of him.'
               ' He can be quite rude however.')
charfred = commands.Bot(command_prefix='#', description=description,
                        pm_help=True)


def roleCall(user, requiredRole):
    for role in user.roles:
        if role.name in cfg.roles:
            if cfg.roles.index(role.name) >= cfg.roles.index(requiredRole):
                return True


async def cmdResolution(message, c):
    if re.search('[^\w, ]', c):
        print('Buggery detected! ' + c + ' by ' + message.author.name)
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.errormsgs) +
                                     '\n' + c))
        return
    if (roleCall(message.author, cfg.commands[c.split()[0]]['MinRank'])):
        print('Command accepted! ' + c)
        await charfred.send_message(message.channel,
                                    random.choice(keywords.acks))
        await charfred.send_typing(message.channel)
        response = await globals()[cfg.commands[c.split()[0]]['Type']](c)
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.replies) +
                                     '\n```\n' +
                                     response +
                                     '\n```'))
    else:
        print('No permission! ' + c)
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.errormsgs) +
                                     '\n' + c))


async def serverCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    response = []
    for server in cSplit[1:]:
        if (server in cfg.servers) and (cmd not in cfg.servers[server]):
            sshcmd = cfg.commands[cmd]['Pattern'].format(
                ssh=cfg.sshName,
                script=cfg.commands[cmd]['Script'],
                cmd=cmd,
                args=server)
            # response.append(pexp.run(sshcmd, events={'(?i)(passphrase|password)':
            #                                          cfg.sshPass}))
            response.append(sshcmd)
            # await asyncio.sleep(1)
        else:
            print('Invalid target! {}'.format(server))
            response.append(('Invalid target! {}'.format(server)))
    return ('\n'.join(response))


async def playerCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    if len(cSplit) > 2:
        argument = " " + cSplit[2]
    else:
        argument = ""
    sshcmd = cfg.commands[cmd]['Pattern'].format(
        ssh=cfg.sshName,
        script=cfg.commands[cmd]['Script'],
        cmd=cmd,
        args=cSplit[1] + argument)
    # response = pexp.run(sshcmd, events={'(?i)(passphrase|password)':
    #                                     cfg.sshPass})
    response = sshcmd
    return response


async def specialCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    sshcmd = cfg.commands[cmd]['Pattern'].format(
        ssh=cfg.sshName,
        script=cfg.commands[cmd]['Script'],
        cmd=cmd,
        args=cSplit[1:])
    # response = pexp.run(sshcmd, events={'(?i)(passphrase|password)':
    #                                     cfg.sshPass})
    response = sshcmd
    return response


@charfred.event
async def on_ready():
    print('Logged in as:')
    print(charfred.user.name)
    print(charfred.user.id)
    print('=============')


@charfred.event
async def on_message(message):
    msg = message.content
    cmds = cmdPattern.findall(msg)
    if (msg.startswith('Charfred,') and len(cmds) > 0):
        # cmdList = [re.sub('[^\w ]', '', n[0]) for n in cmds]
        cmdList = [n[0] for n in cmds]
        print('Command recieved!')
        print(*cmdList, sep='\n')
        print(message.author.name)
        for c in cmdList:
            await cmdResolution(message, c)
    elif (msg.startswith('Charfred,')):
        await charfred.send_message(message.channel,
                                    random.choice(keywords.nacks))


if cfg.liveMode:
    charfred.run(cfg.liveBotToken)
else:
    charfred.run(cfg.stageBotToken)
