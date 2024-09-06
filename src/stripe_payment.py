import os
import json
import stripe
import boto3
import requests
from flask import Flask, jsonify, request

# Uncomment for local testing
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
discord_token = os.getenv('DISCORD_TOKEN')

s3 = boto3.client("s3")
BUCKET_NAME = 'f1-bot-channels'

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    event = None
    payload = request.data
    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    # sig_header = request.headers.get('Stripe-Signature')

    # try:
    #     # Verifica a autenticidade do evento enviado pelo Stripe
    #     event = stripe.Webhook.construct_event(
    #         payload, sig_header, webhook_secret
    #     )
    # except ValueError as e:
    #     return jsonify({'error': str(e)}), 400
    # except stripe.error.SignatureVerificationError as e:
    #     return jsonify({'error': 'Invalid signature'}), 400
    if event:
        update_payment_status(event)

    return jsonify({'status': 'success'}), 200

def generate_payment_link(user_id):
    stripe.api_key = os.getenv("STRIPE_API_KEY")

    starter_subscription = stripe.Product.create(
        name="F1 Ticket",
        # description="$5/Month subscription",
    )

    starter_subscription_price = stripe.Price.create(
        unit_amount=2000,
        currency="usd",
        # recurring={"interval": "month"},
        product=starter_subscription['id'],
    )

    link = stripe.PaymentLink.create(
        line_items=[{"price": starter_subscription_price['id'], "quantity": 1}],
        metadata={"user_id": user_id},
    )

    return link.url

def dm_message(user_id):
    headers = {
        'Authorization': f'Bot {discord_token}',
        'Content-Type': 'application/json'
    }

    # DM channel creation
    dm_url = 'https://discord.com/api/v9/users/@me/channels'
    dm_data = {
        'recipient_id': user_id
    }
    response = requests.post(dm_url, headers=headers, json=dm_data)

    if response.status_code == 200:
        dm_channel_id = response.json()['id']
        content = "Your payment has been successfully processed! Thanks for buying the ticket!"

        # Send the message to the DM channel created
        message_url = f'https://discord.com/api/v10/channels/{dm_channel_id}/messages'
        message_data = {
            "type": 4,
            "content": content,
        }

        message_response = requests.post(message_url, headers=headers, json=message_data)

def update_payment_status(event):
    response = s3.get_object(Bucket=BUCKET_NAME, Key='guild_channel.json')
    data = json.loads(response['Body'].read())

    payment_intent = event['data']['object']
    user_id = payment_intent['metadata']['user_id']  # Obtém o ID do usuário do Discord

    if (event['type'] == 'payment_intent.succeeded'):
        dm_message(user_id)

    s3.put_object(Bucket=BUCKET_NAME, Key='guild_channel.json', Body=json.dumps(data))

def check_payment_status(user_id):
    sessions = stripe.checkout.Session.list(limit=100)
    print(len(sessions.data))

    for session in sessions.data:
        # Verifica se a sessão contém metadados com o user_id
        if session.metadata.get('user_id') == user_id:
            # Verifica o status do pagamento
            if session.payment_status == 'paid':
                print(f"Pagamento encontrado e bem-sucedido para o user_id: {user_id}")
                return True
    
    # Se não encontrar nenhum pagamento associado ao user_id
    print(f"Nenhum pagamento encontrado para o user_id: {user_id}")
    return False
