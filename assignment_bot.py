# assignment_bot.py - Compatible Version
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8292745525:AAGayCnqqlMLG5bVdByB2JYh_iuT8df_1x4")

# REPLACE THESE WITH YOUR ACTUAL GROUP IDs
CLASS_GROUPS = {
    "Prosthodontics": "-1001234567890",
    "Orthodontics": "-1001234567891", 
    "Restorative & Aesthetic": "-1001234567892",
    "Basic Sciences": "-1001234567893"
}

# Store user class selections
user_classes = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message with class buttons"""
    keyboard = [
        [InlineKeyboardButton("🦷 Prosthodontics", callback_data="class_Prosthodontics")],
        [InlineKeyboardButton("🔵 Orthodontics", callback_data="class_Orthodontics")],
        [InlineKeyboardButton("💎 Restorative & Aesthetic", callback_data="class_Restorative & Aesthetic")],
        [InlineKeyboardButton("🔬 Basic Sciences", callback_data="class_Basic Sciences")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "🎓 Welcome to Assignment Submission Bot!\n\n"
        "Please select your class:",
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle class selection"""
    query = update.callback_query
    query.answer()
    
    class_name = query.data.replace("class_", "")
    user_id = query.from_user.id
    
    # Store user's class
    user_classes[user_id] = class_name
    
    query.edit_message_text(
        f"✅ You selected: {class_name}\n\n"
        "📎 Now please upload your assignment file:\n"
        "• PDF documents\n"
        "• Word files (.doc, .docx)\n" 
        "• Images (JPG, PNG)\n"
        "• Or any other document"
    )

def handle_file(update: Update, context: CallbackContext) -> None:
    """Handle file uploads"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    
    if user_id not in user_classes:
        update.message.reply_text("❌ Please use /start first to select your class.")
        return
    
    class_name = user_classes[user_id]
    
    # Get file info
    if update.message.document:
        file_name = update.message.document.file_name
    elif update.message.photo:
        file_name = f"photo_from_{user_name}.jpg"
    else:
        update.message.reply_text("❌ Please send a valid file (PDF, Word, Image, etc.)")
        return
    
    try:
        # Confirm to student
        update.message.reply_text(
            f"✅ Assignment submitted successfully!\n\n"
            f"📚 Class: {class_name}\n"
            f"📄 File: {file_name}\n"
            f"👤 Student: {user_name}\n\n"
            f"Thank you! Your teacher will review it."
        )
        
        logger.info(f"New assignment: {user_name} -> {class_name} -> {file_name}")
        
    except Exception as e:
        logger.error(f"Error processing assignment: {e}")
        update.message.reply_text("❌ Error submitting assignment. Please try again or contact your teacher.")

def handle_text(update: Update, context: CallbackContext) -> None:
    """Handle text messages"""
    user_id = update.message.from_user.id
    if user_id in user_classes:
        update.message.reply_text("📎 Please upload your assignment file (PDF, Word, Image, etc.)")
    else:
        update.message.reply_text("👋 Welcome! Use /start to begin assignment submission.")

def help_command(update: Update, context: CallbackContext) -> None:
    """Help command"""
    update.message.reply_text(
        "📚 Assignment Bot Help:\n\n"
        "/start - Begin submission\n"
        "/help - This message\n\n"
        "How to submit:\n"
        "1. Click /start\n"
        "2. Select your class\n"
        "3. Upload your file\n\n"
        "Your submissions are private! ✅"
    )

def get_group_id(update: Update, context: CallbackContext) -> None:
    """Command to get group ID - for setup only"""
    chat_id = update.message.chat_id
    update.message.reply_text(f"This group ID is: `{chat_id}`", parse_mode='Markdown')

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found! Set it as environment variable.")
        return
    
    logger.info("🤖 Starting Telegram Assignment Bot...")
    
    try:
        # Create updater
        updater = Updater(BOT_TOKEN)
        
        # Get dispatcher to register handlers
        dispatcher = updater.dispatcher
        
        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("getid", get_group_id))
        dispatcher.add_handler(CallbackQueryHandler(button_handler))
        dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
        
        # Start the Bot
        updater.start_polling()
        logger.info("✅ Bot started successfully!")
        
        # Run the bot until you press Ctrl-C
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == '__main__':
    main()