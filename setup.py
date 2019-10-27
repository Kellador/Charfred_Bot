from setuptools import setup, find_packages

setup(
    name="Charfred",
    version="1.0beta4",
    packages=find_packages(),
    install_requires=[
        'yarl<1.2',
        'discord.py',
        'coloredlogs',
        'click',
        'toml'],
    extras_require={
        'uvloop': ['uvloop'],
        'aiomysql': ['aiomysql']
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
            'spiffy = spiffy:spiffy'
        ]
    }
)
