import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TELEGRAM_BOT_TOKEN, TIMEZONE, DAILY_REMINDER_TIME
from models import get_db, CountdownEvent

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# Common timezones for quick selection
COMMON_TIMEZONES = [
    "Europe/Berlin",
    "UTC",
    "America/New_York",
    "Europe/London",
    "Asia/Tokyo",
    "Australia/Sydney"
]

def start(update: Update, context):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Countdown Bot!\n\n"
        "Here's how to use me:\n"
        "1. Create a countdown: /set <name> <date>\n"
        "   Example: /set birthday 2024-12-31\n"
        "2. Check countdown: /countdown <name>\n"
        "3. List all countdowns: /list\n"
        "4. Enable daily reminders: /remind <name>\n"
        "5. Disable daily reminders: /unremind <name>\n"
        "6. Delete a countdown: /delete <name>\n"
        "7. Set timezone: /timezone <name>"
    )
    update.message.reply_text(welcome_message)

def set_timezone(update: Update, context):
    """Set timezone for a countdown event."""
    try:
        db = next(get_db())
        
        if not context.args:
            update.message.reply_text("Please provide a countdown name.\nExample: /timezone birthday")
            return

        name = context.args[0]
        event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()

        if not event:
            update.message.reply_text(f"No countdown found with name '{name}'")
            return

        # Create inline keyboard with common timezones
        keyboard = []
        for tz in COMMON_TIMEZONES:
            keyboard.append([InlineKeyboardButton(tz, callback_data=f"tz_{name}_{tz}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f"Select timezone for '{name}':",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error setting timezone: {e}")
        update.message.reply_text("An error occurred while setting the timezone.")
    finally:
        db.close()

def timezone_callback(update: Update, context):
    """Handle timezone selection callback."""
    query = update.callback_query
    query.answer()
    
    try:
        _, name, timezone = query.data.split('_')
        db = next(get_db())
        
        event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()
        if event:
            event.timezone = timezone
            db.commit()
            query.edit_message_text(f"✅ Timezone for '{name}' set to {timezone}")
        else:
            query.edit_message_text(f"❌ Countdown '{name}' not found")
    except Exception as e:
        logger.error(f"Error in timezone callback: {e}")
        query.edit_message_text("An error occurred while setting the timezone.")
    finally:
        db.close()

def set_countdown(update: Update, context):
    """Set a new countdown event."""
    try:
        db = next(get_db())
        
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Please provide a name and date.\nExample: /set birthday 2024-12-31")
            return

        name = args[0]
        date_str = args[1]

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Use the default timezone from config
            target_date = pytz.timezone(TIMEZONE).localize(target_date)
        except ValueError:
            update.message.reply_text("Invalid date format. Please use YYYY-MM-DD")
            return

        existing_event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()
        if existing_event:
            update.message.reply_text(f"A countdown with name '{name}' already exists.")
            return

        new_event = CountdownEvent(
            name=name,
            target_date=target_date,
            chat_id=update.effective_chat.id,
            created_by=update.effective_user.id,
            created_at=datetime.now(pytz.timezone(TIMEZONE)),
            timezone=TIMEZONE  # Set default timezone
        )

        db.add(new_event)
        db.commit()

        update.message.reply_text(f"✅ Countdown '{name}' set for {target_date.strftime('%Y-%m-%d')}")
    except Exception as e:
        logger.error(f"Error setting countdown: {e}")
        update.message.reply_text("An error occurred while setting the countdown.")
    finally:
        db.close()

def get_countdown(update: Update, context):
    """Get the remaining time for a countdown event."""
    try:
        db = next(get_db())
        
        if not context.args:
            update.message.reply_text("Please provide a countdown name.\nExample: /countdown birthday")
            return

        name = context.args[0]
        event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()

        if not event:
            update.message.reply_text(f"No countdown found with name '{name}'")
            return

        # Convert target date to event's timezone
        event_tz = pytz.timezone(event.timezone)
        now = datetime.now(event_tz)
        target_date = event.target_date.astimezone(event_tz)
        remaining = target_date - now

        if remaining.days < 0:
            update.message.reply_text(f"❌ The event '{name}' has already passed!")
            return

        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        message = f"⏳ Countdown for '{name}':\n"
        message += f"Timezone: {event.timezone}\n"
        message += f"Remaining: {days} days, {hours} hours, {minutes} minutes"
        
        update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting countdown: {e}")
        update.message.reply_text("An error occurred while getting the countdown.")
    finally:
        db.close()

def list_countdowns(update: Update, context):
    """List all countdown events."""
    try:
        db = next(get_db())
        
        events = db.query(CountdownEvent).filter(
            CountdownEvent.chat_id == update.effective_chat.id
        ).all()

        if not events:
            update.message.reply_text("No countdown events found.")
            return

        message = "📋 Your countdown events:\n\n"
        for event in events:
            event_tz = pytz.timezone(event.timezone)
            now = datetime.now(event_tz)
            target_date = event.target_date.astimezone(event_tz)
            remaining = target_date - now
            days = remaining.days if remaining.days >= 0 else 0
            
            reminder_status = "🔔" if event.daily_reminder else "🔕"
            message += f"{reminder_status} {event.name} ({event.timezone}): {days} days remaining\n"

        update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error listing countdowns: {e}")
        update.message.reply_text("An error occurred while listing countdowns.")
    finally:
        db.close()

def toggle_reminder(update: Update, context, enable: bool):
    """Enable or disable daily reminders for a countdown event."""
    try:
        db = next(get_db())
        
        if not context.args:
            update.message.reply_text("Please provide a countdown name.")
            return

        name = context.args[0]
        event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()

        if not event:
            update.message.reply_text(f"No countdown found with name '{name}'")
            return

        event.daily_reminder = enable
        db.commit()

        status = "enabled" if enable else "disabled"
        update.message.reply_text(f"✅ Daily reminders for '{name}' have been {status}.")
    except Exception as e:
        logger.error(f"Error toggling reminder: {e}")
        update.message.reply_text("An error occurred while toggling the reminder.")
    finally:
        db.close()

def delete_countdown(update: Update, context):
    """Delete a countdown event."""
    try:
        db = next(get_db())
        
        if not context.args:
            update.message.reply_text("Please provide a countdown name.")
            return

        name = context.args[0]
        event = db.query(CountdownEvent).filter(CountdownEvent.name == name).first()

        if not event:
            update.message.reply_text(f"No countdown found with name '{name}'")
            return

        db.delete(event)
        db.commit()

        update.message.reply_text(f"✅ Countdown '{name}' has been deleted.")
    except Exception as e:
        logger.error(f"Error deleting countdown: {e}")
        update.message.reply_text("An error occurred while deleting the countdown.")
    finally:
        db.close()

def send_daily_reminders(context):
    """Send daily reminders for all events with reminders enabled."""
    try:
        db = next(get_db())
        
        events = db.query(CountdownEvent).filter(CountdownEvent.daily_reminder == True).all()
        
        for event in events:
            event_tz = pytz.timezone(event.timezone)
            now = datetime.now(event_tz)
            target_date = event.target_date.astimezone(event_tz)
            remaining = target_date - now
            
            if remaining.days < 0:
                continue
                
            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            
            message = f"⏰ Daily Reminder for '{event.name}':\n"
            message += f"Timezone: {event.timezone}\n"
            message += f"Remaining: {days} days, {hours} hours, {minutes} minutes"
            
            try:
                context.bot.send_message(
                    chat_id=event.chat_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Error sending reminder for {event.name}: {e}")
                
    except Exception as e:
        logger.error(f"Error in daily reminders: {e}")
    finally:
        db.close()

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set", set_countdown))
    dispatcher.add_handler(CommandHandler("countdown", get_countdown))
    dispatcher.add_handler(CommandHandler("list", list_countdowns))
    dispatcher.add_handler(CommandHandler("remind", lambda update, context: toggle_reminder(update, context, True)))
    dispatcher.add_handler(CommandHandler("unremind", lambda update, context: toggle_reminder(update, context, False)))
    dispatcher.add_handler(CommandHandler("delete", delete_countdown))
    dispatcher.add_handler(CommandHandler("timezone", set_timezone))
    
    # Add callback handler for timezone selection
    dispatcher.add_handler(CallbackQueryHandler(timezone_callback, pattern="^tz_"))

    # Set up daily reminders
    hour, minute = map(int, DAILY_REMINDER_TIME.split(':'))
    scheduler.add_job(
        send_daily_reminders,
        trigger=CronTrigger(hour=hour, minute=minute),
        id='daily_reminders'
    )
    scheduler.start()

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 