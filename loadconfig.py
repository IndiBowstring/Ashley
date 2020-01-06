import json

settings = json.load(open("config.json", "r"))

cogs = [
    'cogs.dice',
    'cogs.admin',
    'cogs.downtime',
    'cogs.user'
]
