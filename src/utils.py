import json
import datetime

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
    
def generate_schedule_embed(schedule_path, location):
    schedule = get_gp_schedule(schedule_path, datetime.date.today().year, location)
    
    if 'error' in schedule:
        return schedule

    if 'sprint' in schedule['sessions']:
        return {
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
    
    return {
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
