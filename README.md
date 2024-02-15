# Welcome to VodRecovery

VodRecovery is the designed to recover Twitch Vods and Clips 

The aim is to continue development of the now archived[VodRecovery](https://github.com/Shishkebaboo/VodRecovery)


## Core Features

- Video Recovery: Choose between manual or web-based VOD recovery options.
- Clip Recovery: Recover clips manually or via mentioned websites.
- Bulk Clip Recovery: Easily recover multiple clips using CSV files from [Sullygnome](https://sullygnome.com/).
- Random Clip Recovery: Retrieve a selection of random clips (3 clips per iteration).
- Multiple Formats: Recovered M3U8 links are available in various formats, including - chunked (Source Quality), 1080p60, 1080p30, 720p60, 720p30, 480p60, 480p30
- Platform Compatibility: VodRecovery is compatible with popular platforms such as [Sullygnome](https://sullygnome.com/) and [Streamscharts](https://streamscharts.com/).
- Default Timezone: The script uses UTC as the default timezone for recovering VODs.
- Video Expiry Duration: Receive a notification if a VOD is older than 60 days, helping you stay informed about content availability.

## Updated New Features
- Added bat file for execution to prevent window closing on crash (so you can read the error messages)
- Fixed crash on 403 website response during vod recovery, added helpful error message

## Installation and Setup

1. Download and install [Python](https://www.python.org/downloads/).
2. Clone this repository.
3. Navigate to the project directory.
4. Install the required packages: `pip install -r requirements.txt`.

## Usage

Run vod_recovery.bat and follow the interactive menu:

```
1) VOD Recovery
2) Clip Recovery
3) Unmute M3U8 File
4) Verify Segment Availability
5) Create M3U8 File (Valid Segments Only)
6) Download M3U8 File (.MP4 Extension)
7) Help
8) Exit
```

## Configuration Options

The script uses multiple configuration files to minimize user input and tailor behavior. Descriptions of the settings in each file are provided below.

### Preferences.json

- `DEFAULT_DIRECTORY`: The default directory where files are stored.
- `DOWNLOAD_DIRECTORY`: The directory where downloads are stored.

### Settings.json

- `DOWNLOAD_M3U8_VIDEO_URL`: Command for downloading M3U8 video URLs.
- `DOWNLOAD_M3U8_VIDEO_URL_SLICE`: Command for downloading a sliced portion of M3U8 video URLs.
- `DOWNLOAD_M3U8_VIDEO_FILE`: Command for downloading M3U8 video files.
- `DOWNLOAD_M3U8_VIDEO_FILE_SLICE`: Command for downloading a sliced portion of M3U8 video files.
- `UNMUTE_VIDEO`: A boolean value indicating if the video should be unmuted.
- `CHECK_SEGMENTS`: A boolean value enabling or disabling the segment checking feature.
- `DOWNLOAD_CLIPS`: A boolean value specifying whether clips should be automatically downloaded.
- `REMOVE_LOG_FILE`: A boolean value controlling the automatic removal of log files post-operation.

## Menu Guide

The `help.json` file provides descriptions of all main and sub-menu options. You can refer to this file to understand each option's functionality.

## Domains.txt
The `domains.txt` file contains a list of domains that the script uses to retrieve videos. Each line in this file represents a domain.

## User_agents.txt
The `user_agents.txt` file contains a list of user agents that the script uses to scrape website data. Each line in this file represents a user agent string.

## FFmpeg Installation
To use FFmpeg with the script, you'll need to install FFmpeg on your system. You can download FFmpeg from the official website [here](https://ffmpeg.org/download.html) and follow the installation instructions for your operating system.


## Original Project

- **Author**: [Shishkebaboo](https://github.com/Shishkebaboo)
