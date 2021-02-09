from setuptools import setup, find_packages

setup(
    name="Charfred",
    version="1.0beta6",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'discord.py',
        'coloredlogs',
        'click',
        'toml',
        'humanize',
        'psutil'],
    extras_require={
        'uvloop': ['uvloop'],
        'asyncpg': ['asyncpg']
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
