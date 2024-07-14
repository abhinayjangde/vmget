# VMGET
- vmget is a command line tool for downloading youtube videos and mp3 files
-
- ## You can build you own executable file
- ```bash
  pyinstaller --onefile vmget.py
  ```

  ```powershell
 PS C:\Users\Abhi> vmget -h
usage: vmget.exe [-h] [-o OUTPUT] url {mp4,mp3} [{360p,480p,720p,1080p}]

YT Video Downloader by [Abhi]

positional arguments:
  url                   URL of the YouTube video
  {mp4,mp3}             Desired file format (mp4 or mp3)
  {360p,480p,720p,1080p}
                        Desired video quality (optional if format is mp3)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for the downloaded file

Examples:
  python vmget.py "https://www.youtube.com/watch?v=S2sBNY9Wg8o" mp4 720p
  python vmget.py "https://www.youtube.com/watch?v=S2sBNY9Wg8o" mp3 -o C:\Users\Abhi\Downloads
```
  
