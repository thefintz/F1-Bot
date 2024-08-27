# F1 Bot

## About
Discord bot for F1 fans. Use slash commands to get information about the next GP, the current championship standings, and more.
Also, the bot sends reminders to the Discord servers that are subscribed to it, informing weekly about the next Grand Prix schedule.

## Directory structure
- ```/commands```: Where the slash commands are defined and published.
- ```/reminder```: Script that sends reminder messages to the Discord servers that are subscribed to the bot.
- ```/src```: Discord bot main code, where the endpoint for the commands are defined and handled. 

## How to run locally

### Environment variables
Create two `.env` files in the directories with the following content:
- ```/commands```:
    - DISCORD_TOKEN
    - DISCORD_APPLICATION_ID
- ```/reminder```:
    - DISCORD_TOKEN
- ```/src```:
    - DISCORD_PUBLIC_KEY

### Steps to run
- ```/commands```:
    - Install dependencies in requirements.txt
    - Run ```publish_commands.py``` to publish the commands to the Discord API.
- ```/reminder```:
    - Install dependencies in requirements.txt
    - Run ```next_gp.py``` to message every server that is subscribed to the bot with the next GP schedule (maybe new reminders in the future?).
- ```/src```:
    - Install dependencies in requirements.txt (root directory)
    - Run ```main.py``` to start the bot.
    - Not sure if it work's correctly
    
You should also follow some commands written in code comments to use the correct paths and use the `.env` files correctly.

## Deploy

Commiting to the main branch automatically deploys the bot to AWS Lambda with Serverless Framework and Github Actions.

All the existing commands are also published to the Discord API.