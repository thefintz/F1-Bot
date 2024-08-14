import os
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
import json
import datetime
import boto3

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")

s3 = boto3.client("s3")
BUCKET_NAME = 'f1-bot-channels'
FILE_KEY = 'guild_channel.json'

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app)

@app.route("/", methods=["POST"])
async def interactions():
    print(f"Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)

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

def update_channels(channel):
    channel_id = channel["id"]
    guild_id = channel["guild_id"]
    
    response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    data = json.loads(response['Body'].read())
    print(data)
        
    data[guild_id] = channel_id
    
    s3.put_object(Bucket=BUCKET_NAME, Key=FILE_KEY, Body=json.dumps(data))

# Comment decorator for local testing
@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    if raw_request["type"] == 1:
       return jsonify({"type": 1})
       
    update_channels(raw_request["channel"])

    data = raw_request["data"]
    command_name = data["name"]
    message_content = "I don't understand this command, try again!"
    
    if command_name == "hello":
        message_content = "Hello there!"
    elif command_name == "about":
        message_content = "I am a bot made to help you with your F1 needs!"
    elif command_name == "song":
        message_content = "The Dutch National Anthem never leaves my playlist!"
    elif command_name == "winner":
        message_content = "I don't have this info right now, but it should be Max Verstappen..."
    elif command_name == "gp":
        tag = data["options"][0]
        if tag["name"] == 'location':
            location = tag["options"][0]["value"]
        elif tag["name"] == 'next':
            location = 'Netherlands'
            
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
        
        if "error" in message_content:
            message_content = "Location name not found, try again with a valid Grand Prix location!"
        else:
            response_data = {
                "type": 4,
                "data": {
                    "content": "Here is the schedule for the requested Grand Prix:",
                    "embeds": [embed]
                }
            }
            return jsonify(response_data)
        
    response_data = {
        "type": 4,
        "data": {"content": message_content}
    }
        
    return jsonify(response_data)
    
if __name__ == "__main__":
    app.run(debug=True)