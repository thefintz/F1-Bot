import os
import boto3
import json
import datetime
import requests
from time import sleep
from utils import get_schedules, generate_schedule_embed

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

# Change for local testing
# SCHEDULE_PATH = "../data/schedule"
SCHEDULE_PATH = "data/schedule"

TOKEN = os.getenv('DISCORD_TOKEN')

s3 = boto3.client("s3")
BUCKET_NAME = 'f1-bot-channels'
FILE_KEY = 'guild_channel.json'
    
def next_gp():
    today = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    location = None
    location_date = None
    
    schedules = get_schedules(SCHEDULE_PATH, datetime.date.today().year)
    
    for gp_name, info in schedules.items():
        date_str = info['sessions']['gp']
        gp_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        
        # Finding the next GP, closest date from today
        if gp_date > today:
            if location_date is None or gp_date < location_date:
                location = gp_name
                location_date = gp_date   
    
    is_race_week = (location_date - today).days <= 5
    
    return location, is_race_week
    

def send_next_gp_message():
    response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    guilds = json.loads(response['Body'].read())
    channels = [item['channel_id'] for item in guilds.values() if item['sub'] is True]
    
    location, is_race_week = next_gp()
    embed = generate_schedule_embed(SCHEDULE_PATH, location)
    
    if is_race_week:
        content = f"**RACE WEEK!** Don't miss anything from the next Grand Prix weekend! 🏁"
    else:
        content = f"No Grand Prix this weekend, but here's the schedule for the next one!"
    
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
    message_data = {
        "type": 4,
        "content": content,
        "embeds": [embed]
    }
    
    for channel_id in channels:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        response = requests.post(url, headers=headers, data=json.dumps(message_data))
        print(f"Message sent to channel {channel_id} with status code {response.status_code}, {response.reason}")
        print(f"Response content: {response.content.decode()}")
        print(f"Rate limit remaining: {response.headers['X-RateLimit-Remaining']}")
        
        if response.headers['X-RateLimit-Remaining'] == '0':
            print(f"Waiting for rate limit reset: {response.headers['X-RateLimit-Reset-After']} seconds")
            sleep(float(response.headers['X-RateLimit-Reset-After']) + 1)


if __name__ == "__main__":
    send_next_gp_message()
