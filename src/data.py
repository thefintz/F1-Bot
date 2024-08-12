import json

def get_schedules(path, year):
    with open(f"{path}/{year}.json", "r") as file:
        return json.load(file)
        
def get_gp_schedule(path, year, name):
    schedules = get_schedules(path, year)
    
    if name in schedules:
        return schedules[name]
    
    return {"error": "No schedule found for this GP!"}
    

path = "../data/schedule"
year = 2024

print(get_schedules(path, str(year)))