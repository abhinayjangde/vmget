import asyncio
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO
import os
import requests
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
import time
import telebot
import config
import json 
import threading 
from bot import run_bot
import logging

time.sleep(5)  # Delay for 5 seconds between requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.from_object(config.Config)
bot = telebot.TeleBot(app.config["BOT_TOKEN"])
socketio = SocketIO(app)  # Initialize SocketIO

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video(url, quality=None, file_format="mp4", output_dir=None):
    if file_format not in ["mp4", "mp3"]:
        return f"Unsupported format: {file_format}"

    if not output_dir:
        output_dir = os.getcwd()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    if file_format == "mp3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        ydl_opts['merge_output_format'] = 'mp3'
    else:
        if quality:
            ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]'
        ydl_opts['merge_output_format'] = 'mp4'

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        file_name = ydl.prepare_filename(info_dict)
        if file_format == "mp3":
            file_name = file_name.rsplit(".", 1)[0] + ".mp3"
        return file_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form.get('quality')
    download_type = request.form['type']

    file_format = "mp4" if download_type == "video" else "mp3"

    try:
        file_path = download_video(url, quality=quality, file_format=file_format, output_dir=DOWNLOAD_FOLDER)
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "Failed to download the file."
    except Exception as e:
        return f"An error occurred: {e}"

def download_instagram_content(url):
    # Make a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        return None, "Failed to retrieve content."

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the script tag containing the JSON data
    script_tag = soup.find('script', text=lambda t: t.startswith('window._sharedData'))
    if not script_tag:
        return None, "Could not find content."

    # Extract JSON data
    json_data = script_tag.string.split(' = ', 1)[1].rstrip(';')
    data = json.loads(json_data)

    # Navigate through the JSON to get media URLs
    try:
        post_data = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        if post_data['is_video']:
            media_url = post_data['video_url']
        else:
            media_url = post_data['display_url']

        # Download the media
        media_response = requests.get(media_url)
        media_filename = f"{post_data['shortcode']}.{'mp4' if post_data['is_video'] else 'jpg'}"

        with open(os.path.join(DOWNLOAD_FOLDER, media_filename), 'wb') as f:
            f.write(media_response.content)

        return os.path.join(DOWNLOAD_FOLDER, media_filename), None
    except Exception as e:
        return None, str(e)

@app.route("/insta_download", methods=["GET", "POST"])
def insta_download():
    if request.method == "POST":
        content_url = request.form["content_url"]
        filename, error = download_instagram_content(content_url)

        if error:
            return f"Error: {error}"
        return send_file(filename, as_attachment=True)

def update_progress(progress):
    socketio.emit('download_progress', {'progress': progress})




def start_bot():
    try:
        run_bot()
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True  # This ensures the thread will die when the main program exits
    bot_thread.start()
    
    # Run Flask app
    app.run(debug=True, use_reloader=False)