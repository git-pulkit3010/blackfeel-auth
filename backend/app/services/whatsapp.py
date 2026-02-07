# backend/app/services/whatsapp.py
import httpx
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
BASE_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}"

async def send_verification_whatsapp(to_phone: str, token: str, user_email: str):
    """
    Sends the verification OTP/Link via the 'verify_blackweave_whatsapp' template.
    """
    url = f"{BASE_URL}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": "verify_blackweave_whatsapp",  # <--- YOUR NEW TEMPLATE NAME
            "language": {"code": "en_US"},
            "components": [
                # --- BODY COMPONENTS ---
                {
                    "type": "body",
                    "parameters": [
                        # {{1}}: User Identifier (We use email since we don't have a name)
                        {
                            "type": "text",
                            "text": user_email 
                        },
                        # {{2}}: The context string
                        {
                            "type": "text",
                            "text": "your email address" 
                        }
                    ]
                },
                # --- BUTTON COMPONENT ---
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0, # The first button
                    "parameters": [
                        # The dynamic suffix for the URL (The 128-char token)
                        {
                            "type": "text",
                            "text": token 
                        }
                    ]
                }
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        
        # Simple logging to help you debug
        if response.status_code != 200:
            print(f"❌ WhatsApp API Error: {response.text}")
        else:
            print(f"✅ WhatsApp Sent to {to_phone}")
            
        return response.json()