from fastapi import APIRouter, Request, HTTPException, Query, Response # <--- Import Response
import os

router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])

# Meta requires this GET endpoint to verify your webhook URL
@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Log these to your console to confirm Meta is actually hitting your server
    print(f"--- Webhook Verification ---")
    print(f"Token: {hub_verify_token}")
    print(f"Challenge: {hub_challenge}")

    if hub_mode == "subscribe" and hub_verify_token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        # Return the challenge as raw text with a 200 status code
        return Response(content=str(hub_challenge), media_type="text/plain")
    
    return Response(content="Verification failed", status_code=403)


@router.post("")
async def handle_whatsapp_event(request: Request):
    data = await request.json()
    
    # Logic to parse the message
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender_id = message["from"]
            text = message.get("text", {}).get("body", "")
            
            print(f"New message from {sender_id}: {text}")
            
            # Here you could trigger your AI design pipeline for BlkcFeel
            # or simply log the interaction to your DB.
            
    except (KeyError, IndexError):
        pass

    return {"status": "success"}