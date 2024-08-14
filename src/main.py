import os
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
import json
import datetime
import boto3
from src.utils import generate_schedule_embed

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

# Change for local testing
# SCHEDULE_PATH = "../data/schedule"
SCHEDULE_PATH = "data/schedule"

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
            
        embed = generate_schedule_embed(SCHEDULE_PATH, location)
        
        if "error" in embed:
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