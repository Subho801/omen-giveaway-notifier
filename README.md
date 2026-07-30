# HP OMEN Giveaway Notifier

A Python notifier that monitors HP OMEN Gaming Hub Sweepstakes giveaways and sends Discord webhook notifications whenever a new giveaway is published.

## Features

- Discord webhook notifications
- Automatic retry logic
- Duplicate prevention
- Timestamped logging
- Automatic game name extraction
- Multiple giveaway support
- Role ping support

## Installation

```bash
git clone https://github.com/yourusername/omen-giveaway-notifier.git

cd omen-giveaway-notifier

pip install -r requirements.txt
```

## Configuration

Edit `config.py`

```python
WEBHOOK_URL = "..."
ROLE_ID = "..."
CHECK_INTERVAL = 300
```

## Run

```bash
python main.py
```
