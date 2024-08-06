from typing import Final
import os
from dotenv import load_dotenv
from discord import Client, Message, Intents
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

async def send_message(message: Message, user_massage: str) -> None:
    if not user_massage:
        print('Message is empty, intents were not enabled properly')

    if is_private := user_massage[0] == '?':
        user_massage = user_massage[1:]
        
    try:
        response: str = get_response(user_massage)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f'Error: {e}')
        
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')
    
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_massage: str = message.content
    channel: str = str(message.channel)
    
    print(f'[{channel}] {username}: "{user_massage}"')
    await send_message(message, user_massage)
    
def main() -> None:
    client.run(token=TOKEN)
    
main()