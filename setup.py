from setuptools import setup, find_packages

setup(
    name="Charfred",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'git+https://github.com/Rapptz/discord.py@rewrite',
        'coloredlogs',
        'ttldict',
        'psutil',
        'click'],
    author="Kella",
    author_email="kellador@gmail.com",
    description="Charfred is a modular Discord bot with capabilities to manage your minecraft servers.",
    keywords="discord bot minecraft management"
)
