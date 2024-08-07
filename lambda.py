import requests

def handler(event, context):
    response = requests.get('https://api.github.com')
    return {
        'statusCode': response.status_code,
        'body': response.json(),
        'event': event,
        'context': context
    }