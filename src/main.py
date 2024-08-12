import os
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
import json
import datetime

# Uncomment for local testing
# from dotenv import load_dotenv
# load_dotenv()

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")

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

# Comment decorator for local testing
@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    if raw_request["type"] == 1:
       return jsonify({"type": 1})

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
        elif tag["name"] == 'year':
            location = 'Belgium'
            
        schedule = get_gp_schedule("data/schedule", 2024, location)
        
        message_content = f"""
        🏁 **Formula 1 - Qatar Grand Prix** 🏁
        📍 **Location:** {data['location']}, Qatar
        
        **Sessions:**
        - **Practice 1:** {format_datetime(data['sessions']['fp1'])}
        - **Sprint Qualifying:** {format_datetime(data['sessions']['sprintQualifying'])}
        - **Sprint:** {format_datetime(data['sessions']['sprint'])}
        - **Qualifying:** {format_datetime(data['sessions']['qualifying'])}
        - **Race:** {format_datetime(data['sessions']['gp'])}
        """ if 'sprint' in data['sessions'] else 
        f"""
        🏁 **Formula 1 - Las Vegas Grand Prix** 🏁
        📍 **Location:** {data['location']}, Nevada, USA
        
        **Sessions:**
        - **Practice 1:** {format_datetime(data['sessions']['fp1'])}
        - **Practice 2:** {format_datetime(data['sessions']['fp2'])}
        - **Practice 3:** {format_datetime(data['sessions']['fp3'])}
        - **Qualifying:** {format_datetime(data['sessions']['qualifying'])}
        - **Race:** {format_datetime(data['sessions']['gp'])}
        """
        
        if "error" in message_content:
            message_content = "Location name not found, try again with a valid Grand Prix location!"
        
    response_data = {
        "type": 4,
        "data": {"content": message_content}
    }
        
    return jsonify(response_data)
    
if __name__ == "__main__":
    app.run(debug=True)