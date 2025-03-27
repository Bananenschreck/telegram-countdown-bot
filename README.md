# Telegram Countdown Bot

A Telegram bot that helps you track countdowns to important dates and events. The bot can:
- Create countdown events with custom names
- Show remaining time for any countdown
- List all your countdown events
- Send daily reminders for important dates
- Delete countdown events when they're no longer needed

## Features

- 🎯 Create countdowns with custom names
- ⏳ Check remaining time for any countdown
- 📋 List all your countdown events
- 🔔 Enable/disable daily reminders
- 🗑️ Delete countdown events
- 🌍 Timezone support
- 💾 Persistent storage using SQLite

## Commands

- `/start` - Start the bot and see available commands
- `/set <name> <date>` - Create a new countdown (date format: YYYY-MM-DD)
- `/countdown <name>` - Check remaining time for a specific countdown
- `/list` - List all your countdown events
- `/remind <name>` - Enable daily reminders for a countdown
- `/unremind <name>` - Disable daily reminders for a countdown
- `/delete <name>` - Delete a countdown event

## Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd telegram-countdown-bot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TIMEZONE=your_timezone_here  # e.g., UTC, America/New_York, Europe/London
DAILY_REMINDER_TIME=09:00  # 24-hour format
```

To get a Telegram bot token:
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use the `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather

## Local Development

To run the bot locally:
```bash
python main.py
```

## Deployment

### Option 1: Deploy on a VPS (Recommended)

1. Get a VPS from a provider like DigitalOcean, Linode, or AWS EC2
2. SSH into your VPS
3. Install Python and git:
```bash
sudo apt update
sudo apt install python3 python3-pip git
```

4. Clone your repository:
```bash
git clone <your-repo-url>
cd telegram-countdown-bot
```

5. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

6. Install dependencies:
```bash
pip install -r requirements.txt
```

7. Create and edit the `.env` file:
```bash
nano .env
```

8. Install and configure systemd service:
```bash
sudo nano /etc/systemd/system/telegram-countdown-bot.service
```

Add the following content:
```ini
[Unit]
Description=Telegram Countdown Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-countdown-bot
Environment=PYTHONPATH=/path/to/telegram-countdown-bot
ExecStart=/path/to/telegram-countdown-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

9. Enable and start the service:
```bash
sudo systemctl enable telegram-countdown-bot
sudo systemctl start telegram-countdown-bot
```

10. Check the status:
```bash
sudo systemctl status telegram-countdown-bot
```

### Option 2: Deploy on Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a `Procfile` in your project root:
```
worker: python main.py
```

3. Create a `runtime.txt` file:
```
python-3.9.18
```

4. Initialize git and deploy:
```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

5. Set environment variables on Heroku:
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token_here
heroku config:set TIMEZONE=your_timezone_here
heroku config:set DAILY_REMINDER_TIME=09:00
```

6. Scale the worker:
```bash
heroku ps:scale worker=1
```

### Option 3: Deploy on Railway.app

1. Create a Railway.app account
2. Connect your GitHub repository
3. Create a new project from your repository
4. Add environment variables in the Railway dashboard
5. Deploy the project

## Troubleshooting

1. **Bot not responding:**
   - Check if the bot token is correct
   - Ensure the bot is running (check logs)
   - Verify the bot has been added to the chat

2. **Database issues:**
   - Check if the database file has proper permissions
   - Ensure the database directory is writable

3. **Timezone issues:**
   - Verify the timezone in your `.env` file is correct
   - Use a valid timezone name from the [pytz database](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)

4. **Daily reminders not working:**
   - Check if the bot has permission to send messages
   - Verify the DAILY_REMINDER_TIME format is correct
   - Check the logs for any errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 