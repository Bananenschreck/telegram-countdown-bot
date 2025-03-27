import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///countdown.db')

# Timezone for the bot
TIMEZONE = os.getenv('TIMEZONE', 'UTC')

# Daily reminder time (24-hour format)
DAILY_REMINDER_TIME = os.getenv('DAILY_REMINDER_TIME', '09:00') 