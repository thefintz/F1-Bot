from typing import Final
import requests
import yaml
import os

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
APPLICATION_ID: Final[str] = os.getenv('DISCORD_APPLICATION_ID')
URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"

def yaml_to_json(file_path: str):
    with open(file_path, "r") as file:
        yaml_content = file.read()

    commands = yaml.safe_load(yaml_content)

    return commands

def publish_commands(file_path: str):
    commands = yaml_to_json(file_path)
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

    # Send the POST request for each command
    for command in commands:
        response = requests.post(URL, json=command, headers=headers)
        command_name = command["name"]
        # No futuro adicionar tratamento de erro
        print(f"Command {command_name} created: {response.status_code}")

def main():
    publish_commands("commands/bot_commands.yaml")

if __name__ == "__main__":
    main()
