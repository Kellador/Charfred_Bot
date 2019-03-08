from setuptools import setup, find_packages

setup(
    name="Charfred",
    version="1.0beta3",
    packages=find_packages(),
    install_requires=[
        'yarl<1.2',
        'discord.py',
        'coloredlogs',
        'click'],
    dependency_links=[
        'git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py'
    ],
    extras_require={
        'uvloop': ['uvloop']
    },
    package_data={
        '': ['*.json', '*.json_default']
    },
    author="Kella",
    author_email="kellador@gmail.com",
    description="Charfred is a modular Discord bot with capabilities to manage your minecraft servers.",
    keywords="discord-bot discord.py minecraft minecraft-administration",
    entry_points={
        'console_scripts': [
            'charfred = charfred:run',
            'charfreduv = charfred:run [uvloop]',
            'charwizard = charwizard:wizard',
            'spiffy = spiffy:spiffy'
        ]
    }
)
