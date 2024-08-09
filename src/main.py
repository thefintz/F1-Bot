import os
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator

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

# Comment decorator for local testing
@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    if raw_request["type"] == 1:
        response_data = {"type": 1}
    else:
        data = raw_request["data"]
        command_name = data["name"]
        
        if command_name == "hello":
            message_content = "Hello there!"
        elif command_name == "about":
            message_content = "I am a bot made to help you with your F1 needs!"
        elif command_name == "song":
            message_content = "The Dutch National Anthem never leaves my playlist!"
        elif command_name == "winner":
            message_content = "I don't have this info right now, but it should be Max Verstappen..."
        elif command_name == "echo":
            original_message = data["options"][0]["value"]   
            message_content = f"Echoing: {original_message}"
        else:
            message_content = "I don't understand this command, try again!"
            
        response_data = {
            "type": 4,
            "data": {"content": message_content}
        }
        
    return jsonify(response_data)
    
if __name__ == "__main__":
    app.run(debug=True)