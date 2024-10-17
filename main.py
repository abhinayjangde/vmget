from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from yt_dlp import YoutubeDL

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video(url, quality=None, file_format="mp4", output_dir=None):
    if file_format not in ["mp4", "mp3"]:
        return f"Unsupported format: {file_format}"

    if not output_dir:
        output_dir = os.getcwd()  # Default to the current directory if no output directory is specified

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
    download_type = request.form['type']  # video or audio

    file_format = "mp4" if download_type == "video" else "mp3"

    try:
        file_path = download_video(url, quality=quality, file_format=file_format, output_dir=DOWNLOAD_FOLDER)
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "Failed to download the file."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(debug=True)
