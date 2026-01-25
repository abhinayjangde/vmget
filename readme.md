# VMGET

A fast and simple command-line tool for downloading videos and audio from YouTube and 1000+ other sites, powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features

- Download videos in multiple formats (MP4, WebM, MKV)
- Extract audio in various formats (MP3, M4A, FLAC, WAV, AAC, Opus)
- Support for playlists with selective downloading
- Quality selection from 360p to 4K
- Colored terminal output for better readability
- Interactive mode for easy use
- Configuration file support for default settings
- Progress bar with download speed and ETA
- Thumbnail saving option

## Installation

### From PyPI

```bash
pip install vmget
```

### From Source

```bash
git clone https://github.com/abhinayjangde/vmget.git
cd vmget
pip install -e .
```

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --name vmget src/vmget/__main__.py
```

## Requirements

- Python 3.11 or higher
- FFmpeg (required for audio extraction and some video conversions)

### Installing FFmpeg

- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

## Usage

### Basic Usage

```bash
# Download video (defaults to MP4 @ 720p)
vmget "https://www.youtube.com/watch?v=VIDEO_ID"

# Download with specific format and quality
vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp4 1080p

# Download audio only
vmget "https://www.youtube.com/watch?v=VIDEO_ID" mp3
```

### Interactive Mode

Run without arguments to enter interactive mode:

```bash
vmget
```

Or use the `-i` flag:

```bash
vmget -i
```

Interactive mode will prompt you for:
- Video URL
- Download type (video/audio)
- Format and quality
- Output directory
- Thumbnail option

### Using Flags

```bash
# Specify format and quality with flags
vmget "URL" -F mp4 -q 1080p

# Specify output directory
vmget "URL" mp4 720p -o ./downloads

# Save thumbnail
vmget "URL" mp4 --thumbnail

# Disable progress bar
vmget "URL" mp4 --no-progress
```

### Multiple URLs

```bash
# Multiple URLs on command line
vmget "URL1" "URL2" "URL3" -F mp4 -q 720p

# Read URLs from file
vmget -f urls.txt -F mp4 -q 720p
```

### Playlist Downloads

```bash
# Download entire playlist
vmget "https://www.youtube.com/playlist?list=PLAYLIST_ID" mp4 720p

# Download specific items from playlist
vmget "https://www.youtube.com/playlist?list=PLAYLIST_ID" mp4 --items 1-5,10

# Skip playlist, download only the video
vmget "https://www.youtube.com/watch?v=ID&list=PLAYLIST" mp4 --no-playlist
```

### Audio Formats

```bash
vmget "URL" mp3    # MP3 (most compatible)
vmget "URL" m4a    # M4A (AAC audio)
vmget "URL" flac   # FLAC (lossless)
vmget "URL" wav    # WAV (uncompressed)
vmget "URL" opus   # Opus (efficient)
vmget "URL" aac    # AAC
```

### Video Formats

```bash
vmget "URL" mp4    # MP4 (most compatible)
vmget "URL" webm   # WebM
vmget "URL" mkv    # MKV (Matroska)
```

### Quality Options

- `360p` - Low quality
- `480p` - Standard definition
- `720p` - HD (default)
- `1080p` - Full HD
- `1440p` - 2K
- `2160p` - 4K
- `best` - Best available quality

## Configuration File

Create a configuration file to set default options. VMGET looks for config files in these locations (in order):

1. `$VMGET_CONFIG` environment variable
2. `~/.config/vmget/config.toml` (Linux/macOS)
3. `%APPDATA%\vmget\config.toml` (Windows)
4. `~/.vmgetrc`
5. `~/vmget.toml`

### Sample Configuration

Run `vmget --show-config` to see the sample configuration:

```toml
# VMGET Configuration File

# Default output format (mp4, webm, mkv, mp3, m4a, wav, flac, aac, opus)
format = "mp4"

# Default video quality (360p, 480p, 720p, 1080p, 1440p, 2160p, best)
quality = "720p"

# Default output directory (use ~ for home directory)
# output_dir = "~/Videos/vmget"

# Show progress bar during download
show_progress = true

# Save video thumbnail as JPG file
thumbnail = false
```

## Command Reference

```
usage: vmget [-h] [-F FORMAT] [-q QUALITY] [-f FILE] [-o DIR] [--items RANGE]
             [--no-playlist] [--no-progress] [--thumbnail] [-i]
             [--show-config] [-v]
             [url ...]

positional arguments:
  url                   URL(s) to download, optionally followed by format and quality

options:
  -h, --help            Show help message and exit
  -F, --format FORMAT   Output format (mp4, webm, mkv, mp3, m4a, wav, flac, aac, opus)
  -q, --quality QUALITY Video quality (360p, 480p, 720p, 1080p, 1440p, 2160p, best)
  -f, --file FILE       Read URLs from a file (one URL per line)
  -o, --output DIR      Output directory for downloaded file(s)
  --items RANGE         Playlist items to download (e.g., '1-3,5,7-10')
  --no-playlist         Download only the video, not the playlist
  --no-progress         Disable progress bar display
  --thumbnail           Save video thumbnail as JPG file
  -i, --interactive     Run in interactive mode
  --show-config         Show sample configuration file and exit
  -v, --version         Show version number and exit
```

## Supported Sites

VMGET supports 1000+ sites through yt-dlp, including:

- YouTube (videos, playlists, channels)
- Vimeo
- Twitter/X
- TikTok
- Instagram
- Facebook
- SoundCloud
- Bandcamp
- Twitch
- Reddit
- And many more!

See the full list at: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## Examples

```bash
# Download a YouTube video in 1080p
vmget "https://www.youtube.com/watch?v=dQw4w9WgXcQ" mp4 1080p

# Download audio from a video
vmget "https://www.youtube.com/watch?v=dQw4w9WgXcQ" mp3

# Download a playlist to a specific folder
vmget "https://www.youtube.com/playlist?list=PLrAXtmErZgOe..." mp4 720p -o ~/Music/Playlist

# Download first 5 videos from a playlist
vmget "https://www.youtube.com/playlist?list=PLrAXtmErZgOe..." mp4 --items 1-5

# Download from Twitter
vmget "https://twitter.com/user/status/123456789" mp4 best

# Download audio from SoundCloud
vmget "https://soundcloud.com/artist/track" mp3

# Interactive mode for guided download
vmget -i
```

## Output

VMGET provides colored output for better readability:

- **Green**: Success messages
- **Red**: Error messages  
- **Blue**: Informational messages
- **Yellow**: Warnings
- **Cyan**: Highlighted information

Before downloading, VMGET displays:
- Video title
- Channel/uploader name
- Duration
- Approximate file size

After completion, it shows:
- Success confirmation
- Output directory path
- Downloaded filename

## Troubleshooting

### FFmpeg not found

If you see "FFmpeg not found in PATH", install FFmpeg and ensure it's in your system PATH.

### Download errors

- Check if the URL is valid and accessible
- Some sites may have geographic restrictions
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Quality not available

If the requested quality isn't available, VMGET will download the best available quality up to the specified limit.

## Contributing

Pull requests are welcome! Please ensure:

1. Code follows existing style
2. Tests pass: `pytest tests/`
3. New features include tests

## License

MIT License - see LICENSE file for details.

## Author

Created by [Abhinay Jangde](https://github.com/abhinayjangde)

## Links

- Repository: https://github.com/abhinayjangde/vmget
- Issues: https://github.com/abhinayjangde/vmget/issues
- yt-dlp: https://github.com/yt-dlp/yt-dlp
