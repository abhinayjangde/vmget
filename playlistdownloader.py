import argparse
from yt_dlp import YoutubeDL
import os

def download_video(url, quality=None, file_format="mp4", output_dir=None):
    if file_format not in ["mp4", "mp3"]:
        print(f"Unsupported format: {file_format}")
        return

    if not output_dir:
        output_dir = os.getcwd()  

    if file_format == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'merge_output_format': 'mp3',
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
        }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_playlist(playlist_url, quality=None, file_format="mp4", output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()

    ydl_opts = {
        'playlistend': 1,  # Download all videos in the playlist
        'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]' if file_format == "mp4" else 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4' if file_format == "mp4" else 'mp3',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def main():
    parser = argparse.ArgumentParser(
        description="YT Video Downloader by [Abhi]",
        epilog=(
            "Examples:\n"
            "  python vmget.py \"https://www.youtube.com/watch?v=S2sBNY9Wg8o\" mp4 720p\n"
            "  python vmget.py \"https://www.youtube.com/playlist?list=PL...\" mp4\n"
            "  python vmget.py \"https://www.youtube.com/watch?v=S2sBNY9Wg8o\" mp3 -o C:\\Users\\Abhi\\Downloads"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("url", help="URL of the YouTube video or playlist")
    parser.add_argument("file_format", choices=["mp4", "mp3"], help="Desired file format (mp4 or mp3)")
    parser.add_argument("quality", nargs="?", choices=["360p", "480p", "720p", "1080p"], help="Desired video quality (optional if format is mp3)")
    parser.add_argument("-o", "--output", help="Output directory for the downloaded file", default=os.getcwd())
    args = parser.parse_args()

    if "youtube.com/playlist" in args.url:
        download_playlist(args.url, args.quality, args.file_format, args.output)
    else:
        download_video(args.url, args.quality, args.file_format, args.output)

if __name__ == "__main__":
    main()
