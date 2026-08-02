import json
import os
import re
import time
from datetime import datetime

import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import WEBHOOK_URL, CHECK_INTERVAL, ROLE_ID
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://www.hpgamestream.com/api/content/homepage"

HEADERS = {
    "User-Agent": "OGH-UL-1101.2607.3.0",
    "AppVersion_OGH": "1101.2607.3.0",
    "Client-id": "279d5b10-2464-44e7-846b-76fa09f34b45",
    "platform": "OTHER",
    "country": "IN",
    "appLaunchCount": "1",
    "deviceType": "Other",
    "language": "en",
    "currentTimestamp": str(int(time.time())),
    "connectedDevices": "",
    "template": "2",
    "appVersion": "1101.2607.3.0",
    "featureByte": "",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Host": "www.hpgamestream.com"
}

PAYLOAD = {}

session = requests.Session()

retries = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
)

session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))

POSTED_FILE = "posted.json"


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return {"seen": []}

    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posted(data):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_website_json(giveaways):
   with open("omen.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "updated": int(time.time()),
            "count": len(giveaways),
            "items": giveaways,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def extract_game_name(description, title):
    patterns = [
        r"FREE copy of (.+?)[!.]",
        r"copy of (.+?)[!.]",
        r"win (.+?)[!.]",
        r"claim (.+?)[!.]",
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return title


def get_giveaways():

    HEADERS["currentTimestamp"] = str(int(time.time()))

    r = session.post(
        API_URL,
        headers=HEADERS,
        json=PAYLOAD,
        timeout=30,
        verify=False
    )

    log(f"API Status: {r.status_code}")

    r.raise_for_status()

    homepage = r.json()

    giveaways = []

    for item in homepage:

        button = item.get("buttonParameter", "")

        if "sweepwidget.com" not in button.lower():
            continue

        description = item.get("description", "")
        title = item.get("title", "")

        giveaways.append({
            "codename": item.get("codename", ""),
            "game": extract_game_name(description, title),
            "title": title,
            "description": description,
            "button": button,
            "image": item.get("url", ""),
            "expire": item.get("expireTime", 0),
        })

    return giveaways


def send_webhook(data):

    

    embed = {
    "author": {
        "name": "HP Omen Sweepstakes",
        "icon_url": "https://file.garden/afbSsuts32dZ5wSl/120px-HP_Omen_logo.svg.png"
    },

    "title": data["game"],
    "url": data["button"],

    "color": 0x5865F2,

    "fields": [
        {
            "name": "Ends at",
            "value": f"<t:{data['expire']}:F>\n(<t:{data['expire']}:R>)",
            "inline": True
        },
        {
            "name": "Type",
            "value": "Raffle 🎟",
            "inline": True
        }
    ],

    "image": {
        "url": data["image"]
    },

    "footer": {
        "text": "Subho's HP OMEN Informer",
        "icon_url": "https://files.catbox.moe/qttqpy.png"
    },


    }

    payload = {
        "content": f"<@&{ROLE_ID}>" if ROLE_ID else "",
        "embeds": [embed]
    }

    response = session.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30,
        verify=False
    )

    response.raise_for_status()
    log("Discord notification sent successfully.")


def main():

    log("HP OMEN Giveaway Notifier Started")

    try:

        giveaways = get_giveaways()

        save_website_json(giveaways)

        if not giveaways:
            log("No giveaway found.")
            return

        posted = load_posted()
        seen = set(posted.get("seen", []))

        found_new = False

        for giveaway in giveaways:

            if giveaway["codename"] in seen:
                continue

            log(f"New giveaway detected: {giveaway['game']}")

            send_webhook(giveaway)

            seen.add(giveaway["codename"])

            found_new = True

        save_posted({
            "seen": sorted(seen)
        })

        log(f"Saved history: {sorted(seen)}")

        if not found_new:
            log("No new giveaway.")

    except requests.exceptions.RequestException as e:
        log(f"Network/API Error: {e}")

    except Exception as e:
        log(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
