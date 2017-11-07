import os
import importlib
import click
from cogs.utils.config import Config

botDir = os.path.dirname(os.path.realpath(__file__))

cfg = Config(f'{botDir}/cogs/configs/botCfg.json')


def _cogs():
    for _cog in os.listdir(f'{botDir}/cogs'):
        if os.path.isfile(os.path.join(f'{botDir}/cogs', _cog)):
            yield _cog[:-3]


def _cmds():
    click.echo('We\'ll set up the permission nodes for all currently '
               'installed cogs (extensions) now. If the cog defines '
               'checks for it\'s commands then these checks will run '
               'against these permissions.\n'
               'For every permission node you will be asked to provide '
               'all the Discord roles that will be allowed to run that '
               'particular command;\n'
               'As well as all the channels (IDs) where the command is '
               'allowed to be run.\n'
               'So let\'s get started!')
    for _cog in _cogs():
        cog = importlib.import_module(f'cogs.{_cog}')
        nodes = getattr(cog, 'permissionNodes', None)
        if nodes is None:
            continue
        click.echo('Beginning setup for permission nodes defined for '
                   f'{_cog}!')
        for node in nodes:
            cfg['commands'][node] = {}
            cfg['commands'][node]['ranks'] = []
            ranks = click.prompt('Please enter all Discord roles which will be '
                                 f'allowed to run \"{node}\", seperated by spaces only!').split()
            cfg['commands'][node]['ranks'] = ranks
            cfg['commands'][node]['channels'] = []
            channels = click.prompt('Please enter all Discord channels\' IDs where '
                                    f'\"{node}\" is allowed to be run, seperated by '
                                    'spaces only!').split()
            channels = list(map(int, channels))
            cfg['commands'][node]['channels'] = channels
        else:
            click.echo(f'Done with all permission nodes for {_cog}!')
    else:
        click.echo('Excellent, we\'re all done with the permission nodes now!')


@click.group(invoke_without_command=True)
@click.pass_context
def wizard(ctx):
    if ctx.invoked_subcommand is None:
        cfg._load()
        click.echo('Beginning Charfred setup! yay!\n'
                   'We\'ll be walking through a bunch of configuration options, '
                   'but you don\'t have to work through them all now,'
                   'there will be a breakpoint after the absolute requirements.\n'
                   'If you decide to stop at the breakpoint, you can resume later '
                   'by running \"charwizard cmds\", or you can start the setup over again!\n')
        click.confirm('If you have already ran the wizard before, this will '
                      'reset any configuration options you\'ve already saved!\n'
                      'Are you sure you want to continue?', abort=True)
        token = click.prompt('Alright! Please enter your bot token')
        cfg['botToken'] = token
        click.echo('We\'ll now setup the prefixes that Charfred will accept '
                   'one by one, you\'ll be asked if you want to add more after '
                   'every one.\n' 'Anything you enter (including whitespace) '
                   'will become a prefix.\n')
        cfg['prefixes'] = []
        prefix = click.prompt('Please enter the first prefix!')
        cfg['prefixes'].append(prefix)
        while click.confirm('Wanna add one more?'):
            prefix = click.prompt('Please enter another prefix!')
            cfg['prefixes'].append(prefix)
        click.echo('Perfect! Now comes the channel ID for the default command '
                   'channel. This will be used in our permission system.\n'
                   'When you run a command the channel where the command is '
                   'issued will be first checked against this ID. '
                   'So all commands will be allowed to run in this channel!')
        defaultCmdCh = click.prompt('Please enter the numeric channel ID now!',
                                    type=int)
        cfg['defaultCmdCh'] = defaultCmdCh
        cfg['commands'] = {}
        cfg._save()
        click.confirm('Great! We\'ve reached the breakpoint! The absolute basics '
                      'have been set up. This next part is gonna a lot longer!\n'
                      'You wanna continue now?', abort=True)
        _cmds()
        cfg._save()
        click.echo('All done, yay! You\'re ready to start using Charfred now! '
                   'If you\'ve setup everything correctly that is ;)\n'
                   'If you have any problems you can just run this wizard again!')


@wizard.group(invoke_without_command=True)
@click.pass_context
def cmds(ctx):
    cfg._load()
    click.echo('Loaded existing configs for Charfred.')
    if ctx.invoked_subcommand is None:
        _cmds()
        cfg._save()
        click.echo('Configs for Charfred saved!')


@cmds.command()
def edit():
    while True:
        for cmd in cfg['commands']:
            click.echo(cmd)
        cmd = click.prompt('Which command\'s permissions would you like to edit?\n'
                           'This will wipe all current permissions for the selected '
                           'command! You\'ll be shown the current permissions and '
                           'then asked to enter new permissions.')
        if cmd not in cfg['commands']:
            click.echo(f'{cmd} is not a registered command!')
            return
        click.echo('Current entries for allowed ranks:\n' +
                   ' '.join(cfg['commands'][cmd]['ranks']))
        ranks = click.prompt('Please enter all Discord roles which will be '
                             f'allowed to run \"{cmd}\", seperated by spaces only!').split()
        cfg['commands'][cmd]['ranks'] = ranks
        click.echo('Current entries for allowed channels:\n' +
                   ' '.join(cfg['commands'][cmd]['channels']))
        channels = click.prompt('Please enter all Discord channels\' IDs where '
                                f'\"{cmd}\" is allowed to be run, seperated by '
                                'spaces only!').split()
        channels = list(map(int, channels))
        cfg['commands'][cmd]['channels'] = channels
        click.echo(f'Done editing permissions for {cmd}!')
        if not click.confirm('Would you like to edit more?'):
            break


@wizard.command()
def token():
    click.echo('Current Token: ' + cfg['botToken'])
    if click.confirm('Would you like to change it?'):
        token = click.prompt('Please enter the new Token!')
        cfg['botToken'] = token


@wizard.command()
def prefixes():
    click.echo('Current prefixes:\n')
    for prefix in cfg['prefixes']:
        click.echo(prefix)
    if click.confirm('Would you like to enter new prefixes?\n'
                     'This will replace all current ones!'):
        cfg['prefixes'] = []
        prefix = click.prompt('Please enter the first prefix!')
        cfg['prefixes'].append(prefix)
        while click.confirm('Wanna add one more?'):
            prefix = click.prompt('Please enter another prefix!')
            cfg['prefixes'].append(prefix)


@wizard.command()
def cmdChannel():
    click.echo('Current default command channel: ' + cfg['defaultCmdCh'])
    if click.confirm('Would you like to change it?'):
        cmdCh = click.prompt('Please enter the new default command channel\'s ID!',
                             type=int)
        cfg['defaultCmdCh'] = cmdCh


@wizard.command()
def status():
    cfg._load()
    # TODO: This needs improving, some kind of pretty printing.
    print(cfg.cfgs)


if __name__ == '__main__':
    wizard()