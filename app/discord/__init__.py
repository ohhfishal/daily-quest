import httpx
import os
from datetime import datetime

import logging

logger = logging.getLogger("uvicorn")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
if not DISCORD_WEBHOOK_URL:
    logger.warn("Discord webhooks are not enabled")


async def submit_feedback(message: str, user_session=None):
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("Discord URL not configured corrrectly")

    embed = {
        "embeds": [
            {
                "title": "📝 New Feedback",
                "color": 0x5865F2,  # Discord blurple color
                "fields": [
                    {
                        "name": "Session",
                        "value": str(user_session.id) if user_session else "UNKNOWN",
                        "inline": True,
                    },
                    {
                        "name": "Message",
                        "value": message[:512],  # Discord embed field limit
                        "inline": False,
                    },
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Daily Quest Feedback"},
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(DISCORD_WEBHOOK_URL, json=embed, timeout=10.0)
        response.raise_for_status()
