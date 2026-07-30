import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ROLE_ID = os.getenv("ROLE_ID", "")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
