import os
import stripe

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