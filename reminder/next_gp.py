import os
import boto3
import json
import datetime
import requests

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

s3 = boto3.client("s3")
BUCKET_NAME = 'f1-bot-channels'
FILE_KEY = 'guild_channel.json'

def get_schedules(path, year):
    with open(f"{path}/{year}.json", "r") as file:
        return json.load(file)
        
def get_gp_schedule(path, year, name):
    schedules = get_schedules(path, year)
    
    if name in schedules:
        return schedules[name]
    
    return {"error": "No schedule found for this GP!"}
    
def format_datetime(datetime_str):
    dt = datetime.datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    return dt.strftime("%A, %d %B 2024, %H:%M UTC")
    
def next_gp():
    today = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    location = None
    location_date = None
    
    schedules = get_schedules("data/schedule", datetime.date.today().year)
    
    for gp_name, info in schedules.items():
        date_str = info['sessions']['gp']
        gp_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        
        # Finding the next GP, closest date from today
        if gp_date > today:
            if location_date is None or gp_date < location_date:
                location = gp_name
                location_date = gp_date   
    
    return location

def generate_embed(location):
    schedule = get_gp_schedule("data/schedule", datetime.date.today().year, location)
    
    if 'sprint' in schedule['sessions']:
        embed = {
            "title": f"🏁 **Formula 1 - {schedule['name']} Grand Prix** 🏁",
            "description": "Grand Prix Schedule",
            "color": 16711680,  # Cor em decimal (neste caso, vermelho)
            "fields": [
                {
                    "name": "📍 Location",
                    "value": schedule['location'],
                    "inline": False
                },
                {
                    "name": "Practice 1",
                    "value": format_datetime(schedule['sessions']['fp1']),
                    "inline": False
                },
                {
                    "name": "Sprint Qualifying",
                    "value": format_datetime(schedule['sessions']['sprintQualifying']),
                    "inline": False
                },
                {
                    "name": "Sprint",
                    "value": format_datetime(schedule['sessions']['sprint']),
                    "inline": False
                },
                {
                    "name": "Qualifying",
                    "value": format_datetime(schedule['sessions']['qualifying']),
                    "inline": False
                },
                {
                    "name": "Race",
                    "value": format_datetime(schedule['sessions']['gp']),
                    "inline": False
                }
            ]
        }
    else:
        embed = {
            "title": f"🏁 **Formula 1 - {schedule['name']} Grand Prix** 🏁",
            "color": 16711680,  # Cor em decimal (neste caso, vermelho)
            "fields": [
                {
                    "name": "📍 Location",
                    "value": schedule['location'],
                    "inline": False
                },
                {
                    "name": "Practice 1",
                    "value": format_datetime(schedule['sessions']['fp1']),
                    "inline": False
                },
                {
                    "name": "Practice 2",
                    "value": format_datetime(schedule['sessions']['fp2']),
                    "inline": False
                },
                {
                    "name": "Practice 3",
                    "value": format_datetime(schedule['sessions']['fp3']),
                    "inline": False
                },
                {
                    "name": "Qualifying",
                    "value": format_datetime(schedule['sessions']['qualifying']),
                    "inline": False
                },
                {
                    "name": "Race",
                    "value": format_datetime(schedule['sessions']['gp']),
                    "inline": False
                }
            ]
        }
        
    return embed

def send_next_gp_message():
    response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    guilds = json.loads(response['Body'].read())
    channels = guilds.values()
    
    location = next_gp()
    embed = generate_embed(location)
    print(json.dumps(embed, indent=4))
    
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
    message_data = {
        "type": 4,
        "content": "**Reminder:** Don't miss the next Formula 1 Grand Prix!",
        "embeds": [embed]
    }
    
    for channel_id in channels:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        response = requests.post(url, headers=headers, data=json.dumps(message_data))
        print(f"Message sent to channel {channel_id} with status code {response.status_code}, {response.reason}")
        print(f"Response content: {response.content.decode()}")
        
if __name__ == "__main__":
    send_next_gp_message()
