import httpx
from typing import List, Optional

EXPO_PUSH_API_URL = "https://exp.host/--/api/v2/push/send"

async def send_push_notification(
    token: str,
    title: str,
    message: str,
    data: Optional[dict] = None
) -> dict:
    """
    Send a push notification to a single Expo push token.
    """
    if not token.startswith("ExponentPushToken[") and not token.startswith("ExponentPushToken("):
        return {"status": "error", "message": "Invalid Expo push token format"}

    payload = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": message,
        "data": data or {}
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EXPO_PUSH_API_URL,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Failed to send push notification: {e}")
        return {"status": "error", "message": str(e)}

async def send_push_notifications(
    tokens: List[str],
    title: str,
    message: str,
    data: Optional[dict] = None
) -> dict:
    """
    Send push notifications to multiple Expo push tokens.
    """
    valid_tokens = [t for t in tokens if t.startswith("ExponentPushToken[") or t.startswith("ExponentPushToken(")]
    
    if not valid_tokens:
        return {"status": "error", "message": "No valid tokens provided"}

    messages = [
        {
            "to": token,
            "sound": "default",
            "title": title,
            "body": message,
            "data": data or {}
        }
        for token in valid_tokens
    ]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EXPO_PUSH_API_URL,
                json=messages,
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Failed to send push notifications: {e}")
        return {"status": "error", "message": str(e)}
