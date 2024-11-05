import telebot
from telebot import types
import logging
import yt_dlp
import os
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(Config.BOT_TOKEN)

# Store user states
user_states = {}

def setup_download_directory():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        welcome_msg = (
            "👋 Welcome to YouTube Video Downloader Bot!\n\n"
            "Please send me a YouTube video link to get started."
        )
        user_states[chat_id] = 'awaiting_link'
        bot.reply_to(message, welcome_msg)
        logger.info(f"User {chat_id} started the bot")
    except Exception as e:
        logger.error(f"Error in welcome handler: {e}")
        bot.reply_to(message, "An error occurred. Please try again with /start")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_link')
def handle_link(message):
    try:
        chat_id = message.chat.id
        video_url = message.text.strip()

        if not ('youtube.com' in video_url or 'youtu.be' in video_url):
            bot.reply_to(message, "⚠️ Please send a valid YouTube link!")
            return

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        qualities = ['720p', '480p', '360p', '240p']
        markup.add(*[types.KeyboardButton(quality) for quality in qualities])

        user_states[chat_id] = {
            'state': 'awaiting_quality',
            'url': video_url
        }
        
        bot.reply_to(
            message,
            "🎯 Please select video quality:",
            reply_markup=markup
        )
        logger.info(f"User {chat_id} submitted URL: {video_url}")
    except Exception as e:
        logger.error(f"Error in link handler: {e}")
        bot.reply_to(message, "❌ Error processing link. Please try again.")

@bot.message_handler(func=lambda message: isinstance(user_states.get(message.chat.id), dict) and user_states[message.chat.id].get('state') == 'awaiting_quality')
def handle_quality_selection(message):
    try:
        chat_id = message.chat.id
        quality = message.text
        
        if quality not in ['720p', '480p', '360p', '240p']:
            bot.reply_to(message, "⚠️ Please select a valid quality option!")
            return

        video_url = user_states[chat_id]['url']
        bot.reply_to(message, "⏳ Starting download... Please wait.", reply_markup=types.ReplyKeyboardRemove())
        
        # Download the video
        download_and_send_video(chat_id, video_url, quality)
        
    except Exception as e:
        logger.error(f"Error in quality handler: {e}")
        bot.reply_to(
            message,
            "❌ Error processing your request. Please start over with /start",
            reply_markup=types.ReplyKeyboardRemove()
        )

def download_and_send_video(chat_id, video_url, quality):
    try:
        setup_download_directory()
        file_path = f"downloads/{chat_id}_video"
        
        ydl_opts = {
            'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
            'outtmpl': file_path + '.%(ext)s',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        # Send the video
        with open(filename, 'rb') as video_file:
            bot.send_video(
                chat_id,
                video_file,
                caption="✅ Here's your video!",
                supports_streaming=True
            )

        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        user_states[chat_id] = 'awaiting_link'
        bot.send_message(
            chat_id,
            "🔄 Send another YouTube link to download more videos!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logger.error(f"Error in download handler: {e}")
        bot.send_message(
            chat_id,
            "❌ Error downloading video. Please try again with /start",
            reply_markup=types.ReplyKeyboardRemove()
        )

def run_bot():
    logger.info("Bot started...")
    while True:
        try:
            logger.info("Starting bot polling...")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Bot polling error: {e}", exc_info=True)
            continue

if __name__ == "__main__":
    run_bot()