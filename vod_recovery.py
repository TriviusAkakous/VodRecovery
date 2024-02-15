import datetime
import hashlib
import json
import csv
import os
import random
import re
import subprocess
from collections.abc import Iterable
from datetime import datetime, timedelta
import grequests
import requests
from bs4 import BeautifulSoup


def print_main_menu():
    menu_options = ["1) VOD Recovery", "2) Clip Recovery", "3) Unmute M3U8 File", "4) Verify Segment Availability", "5) Create M3U8 File (Comments out invalid segments)", "6) Download M3U8 File (.MP4 Extension)", "7) Help", "8) Exit"]
    print("\n".join(menu_options))
    return int(input("\nChoose an option: "))


def print_video_mode_menu():
    vod_type_options = ["1) Single Video Recovery", "2) Bulk video Recovery from SullyGnome CSV Export", "3) Exit"]
    print("\n".join(vod_type_options))
    return int(input("\nSelect VOD Recovery Mode: "))


def print_video_recovery_menu():
    vod_recovery_options = ["1) Manual Recovery", "2) Website Video Recovery", "3) Exit"]
    print("\n".join(vod_recovery_options))
    return int(input("\nSelect VOD Recovery Method: "))


def print_clip_type_menu():
    clip_type_options = ["1) Recover All Clips from a Single VOD", "2) Find Random Clips from a Single VOD", "3) Bulk Recover Clips from SullyGnome CSV Export", "4) Exit"]
    print("\n".join(clip_type_options))
    return int(input("\nSelect Clip Recovery Type: "))


def print_clip_recovery_menu():
    clip_recovery_options = ["1) Manual Clip Recovery", "2) Website Clip Recovery", "3) Exit"]
    print("\n".join(clip_recovery_options))
    return int(input("\nSelect Clip Recovery Method: "))


def print_bulk_clip_recovery_menu():
    bulk_clip_recovery_options = ["1) Single CSV File", "2) Multiple CSV Files", "3) Exit"]
    print("\n".join(bulk_clip_recovery_options))
    return input("\nSelect Bulk Clip Recovery Source: ")


def print_clip_format_menu():
    clip_format_options = ["1) Default Format ([VodID]-offset-[interval])", "2) Alternate Format (vod-[VodID]-offset-[interval])", "3) Legacy Format ([VodID]-index-[interval])", "4) Exit"]
    print("\n".join(clip_format_options))
    return input("\nSelect Clip URL Format (Delimited by Spaces): ")


def print_download_type_menu():
    download_type_options = ["1) M3U8 Link", "2) M3U8 File", "3) Exit"]
    print("\n".join(download_type_options))
    return int(input("\nSelect Download Type: "))


def read_config_file(config_file):
    with open(f"config/{config_file}.json") as config_file:
        config = json.load(config_file)
    return config


def read_config_by_key(config_file, key):
    with open(f"config/{config_file}.json", 'r') as input_config_file:
        config = json.load(input_config_file)
    return config.get(key, None)


def print_help():
    try:
        help_data = read_config_file('help')
        print("\n----- Help Section -----")
        for menu, options in help_data.items():
            print(f"\n{menu.replace('_', ' ').title()}:")
            for option, description in options.items():
                print(f"  {option}: {description}")
            print()
    except Exception as e:
        print(f"An error occurred: {e}")


def read_text_file(text_file_path):
    lines = []
    with open(text_file_path, "r") as text_file:
        for line in text_file:
            lines.append(line.rstrip())
    return lines


def write_text_file(input_text, destination_path):
    with open(destination_path, "a+") as text_file:
        text_file.write(input_text + '\n')


def write_m3u8_to_file(m3u8_link, destination_path):
    with open(destination_path, "w") as m3u8_file:
        m3u8_file.write(requests.get(m3u8_link).text)
    return m3u8_file


def read_csv_file(csv_file_path):
    with open(csv_file_path, "r") as csv_file:
        return list(csv.reader(csv_file))


def get_default_directory():
    default_directory = read_config_by_key('preferences', 'DEFAULT_DIRECTORY')
    return os.path.expanduser(default_directory)


def get_download_directory():
    default_directory = read_config_by_key('preferences', 'DOWNLOAD_DIRECTORY')
    return os.path.expanduser(default_directory)


def get_log_filepath(streamer_name, video_id):
    log_filename = os.path.join(get_default_directory(), f"{streamer_name}_{video_id}_log.txt")
    return log_filename


def get_vod_filepath(streamer_name, video_id):
    vod_filename = os.path.join(get_default_directory(), f"VodRecovery_{streamer_name}_{video_id}.m3u8")
    return vod_filename


def return_user_agent():
    user_agents = read_text_file('config/user_agents.txt')
    header = {
        'user-agent': random.choice(user_agents)
    }
    return header


def calculate_epoch_timestamp(timestamp, seconds):
    epoch_timestamp = ((datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(seconds=seconds)) - datetime(1970, 1, 1)).total_seconds()
    return epoch_timestamp


def calculate_days_since_broadcast(start_timestamp):
    vod_age = datetime.today() - datetime.strptime(start_timestamp, '%Y-%m-%d %H:%M:%S')
    return max(vod_age.days, 0)


def is_video_muted(m3u8_link):
    response = requests.get(m3u8_link).text
    return bool("unmuted" in response)


def calculate_broadcast_duration_in_minutes(hours, minutes):
    return (int(hours) * 60) + int(minutes)


def calculate_max_clip_offset(video_duration):
    return (video_duration * 60) + 2000


def parse_streamer_from_csv_filename(csv_filename):
    _, file_name = os.path.split(csv_filename)
    streamer_name = file_name.strip()
    return streamer_name.split()[0]


def parse_streamer_from_m3u8_link(m3u8_link):
    indices = [i.start() for i in re.finditer('_', m3u8_link)]
    streamer_name = m3u8_link[indices[0] + 1:indices[-2]]
    return streamer_name


def parse_video_id_from_m3u8_link(m3u8_link):
    indices = [i.start() for i in re.finditer('_', m3u8_link)]
    video_id = m3u8_link[indices[0] + len(parse_streamer_from_m3u8_link(m3u8_link)) + 2:indices[-1]]
    return video_id


def parse_streamscharts_url(streamscharts_url):
    streamer_name = streamscharts_url.split("/channels/", 1)[1].split("/streams/")[0]
    video_id = streamscharts_url.split("/streams/", 1)[1]
    return streamer_name, video_id


def parse_twitchtracker_url(twitchtracker_url):
    streamer_name = twitchtracker_url.split(".com/", 1)[1].split("/streams/")[0]
    video_id = twitchtracker_url.split("/streams/", 1)[1]
    return streamer_name, video_id


def parse_sullygnome_url(sullygnome_url):
    streamer_name = sullygnome_url.split("/channel/", 1)[1].split("/stream/")[0]
    video_id = sullygnome_url.split("/stream/", 1)[1]
    return streamer_name, video_id


def parse_vod_filename(m3u8_video_filename):
    base = os.path.basename(m3u8_video_filename)
    streamer_name, video_id = base.split('VodRecovery_', 1)[1].split('.m3u8', 1)[0].rsplit('_', 1)
    return f"{streamer_name}_{video_id}"


def remove_chars_from_ordinal_numbers(datetime_string):
    ordinal_numbers = ["th", "nd", "st", "rd"]
    for exclude_string in ordinal_numbers:
        if exclude_string in datetime_string:
            return datetime_string.replace(datetime_string.split(" ")[1], datetime_string.split(" ")[1][:-len(exclude_string)])


def generate_website_links(streamer_name, video_id):
    website_list = [f"https://sullygnome.com/channel/{streamer_name}/stream/{video_id}",
                    f"https://twitchtracker.com/{streamer_name}/streams/{video_id}",
                    f"https://streamscharts.com/channels/{streamer_name}/streams/{video_id}"]

    return website_list


def extract_offset(clip_url):
    clip_offset = re.search(r'(?:-offset|-index)-(\d+)', clip_url)
    return clip_offset.group(1)


def get_clip_format(video_id, offsets):
    default_clip_list = [f"https://clips-media-assets2.twitch.tv/{video_id}-offset-{i}.mp4" for i in range(0, offsets, 2)]
    alternate_clip_list = [f"https://clips-media-assets2.twitch.tv/vod-{video_id}-offset-{i}.mp4" for i in range(0, offsets, 2)]
    legacy_clip_list = [f"https://clips-media-assets2.twitch.tv/{video_id}-index-{i:010}.mp4" for i in range(offsets)]

    clip_format_dict = {
        "1": default_clip_list,
        "2": alternate_clip_list,
        "3": legacy_clip_list
    }

    return clip_format_dict


def get_random_clip_information():
    while True:
        video_id = input("Enter the video ID: ")
        if video_id.strip():
            break
        else:
            print("Invalid video ID, please try again!")
    while True:
        hours = input("Enter stream duration hour value: ")
        if hours.strip().isdigit():
            break
        else:
            print("Invalid hour value, please try again!")
    while True:
        minutes = input("Enter stream duration minute value: ")
        if minutes.strip().isdigit():
            break
        else:
            print("Invalid minute value, please try again!")
    return video_id, hours, minutes


def manual_clip_recover():
    while True:
        streamer_name = input("Enter the Streamer Name: ")
        if streamer_name.lower().strip():
            break
        else:
            print("Invalid streamer name, Please try again!")
    while True:
        video_id = input("Enter the video ID: ")
        if video_id.strip():
            break
        else:
            print("Invalid video id, Please try again!")
    while True:
        hours = input("Enter stream duration hour value: ")
        if hours.strip().isdigit():
            break
        else:
            print("Invalid hour value, Please try again!")
    while True:
        minutes = input("Enter stream duration minute value: ")
        if minutes.strip().isdigit():
            break
        else:
            print("Invalid minute value, Please try again!")
    clip_recover(streamer_name, video_id, calculate_broadcast_duration_in_minutes(hours, minutes))


def website_clip_recover():
    tracker_url = input("Enter Streamscharts/Sullygnome url:  ")
    if not tracker_url.startswith("https://"):
        tracker_url = "https://" + tracker_url
    if "streamscharts" in tracker_url:
        streamer, video_id = parse_streamscharts_url(tracker_url)
        clip_recover(streamer, video_id, parse_duration_streamscharts(tracker_url))
    elif "twitchtracker" in tracker_url:
        streamer, video_id = parse_twitchtracker_url(tracker_url)
        clip_recover(streamer, video_id, int(parse_duration_twitchtracker(tracker_url)))
    elif "sullygnome" in tracker_url:
        streamer, video_id = parse_sullygnome_url(tracker_url)
        clip_recover(streamer, video_id, int(parse_duration_sullygnome(tracker_url)))
    else:
        print("Link not supported.. Returning to main menu.")
        return


def manual_vod_recover():
    while True:
        streamer_name = input("Enter the Streamer Name: ")
        if streamer_name.lower().strip():
            break
        else:
            print("Invalid streamer name, Please try again!")
    while True:
        video_id = input("Enter the video ID: ")
        if video_id.strip():
            break
        else:
            print("Invalid video id, Please try again!")
    while True:
        timestamp = input("Enter VOD start time (YYYY-MM-DD HH:MM:SS): ")
        if timestamp:
            break
        else:
            print("Invalid timestamp format, Please try again!")
    m3u8_link = vod_recover(streamer_name, video_id, timestamp)
    process_m3u8_configuration(m3u8_link)


def website_vod_recover():
    tracker_url = input("Enter Streamscharts/Sullygnome url:  ").strip()
    if not tracker_url.startswith("https://"):
        tracker_url = "https://" + tracker_url
    if "streamscharts" in tracker_url:
        streamer, video_id = parse_streamscharts_url(tracker_url)
        m3u8_link = vod_recover(streamer, video_id, parse_datetime_streamscharts(tracker_url))
        if m3u8_link is not None:
            process_m3u8_configuration(m3u8_link)
            m3u8_duration = return_m3u8_duration(m3u8_link)
            streamscharts_duration = int(parse_duration_streamscharts(tracker_url))
            if streamscharts_duration >= m3u8_duration + 10:
                print("Streamscharts is generally considered the most reliable source for this data. The discrepancy in durations is likely an anomaly.")
        else:
            print("m3u8_link retrieval failure.. Returning to main menu.")
            return
    elif "twitchtracker" in tracker_url:
        streamer, video_id = parse_twitchtracker_url(tracker_url)
        m3u8_link = vod_recover(streamer, video_id, parse_datetime_twitchtracker(tracker_url))
        if m3u8_link is not None:
            process_m3u8_configuration(m3u8_link)
            m3u8_duration = return_m3u8_duration(m3u8_link)
            streamer = parse_streamer_from_m3u8_link(m3u8_link)
            video_id = parse_video_id_from_m3u8_link(m3u8_link)
            streamscharts_url = generate_website_links(streamer, video_id)[2]
            modified_streamscharts_url = streamscharts_url[:streamscharts_url.rfind('/')]
            twitchtracker_duration = int(parse_duration_twitchtracker(tracker_url))
            if twitchtracker_duration >= m3u8_duration + 10:
                print(f"The duration from Twitchtracker exceeds the M3U8 duration by over 10 minutes. Consider checking Streamscharts for a split stream. URL: {modified_streamscharts_url}")
    elif "sullygnome" in tracker_url:
        streamer, video_id = parse_sullygnome_url(tracker_url)
        m3u8_link = vod_recover(streamer, video_id, parse_datetime_sullygnome(tracker_url))
        if m3u8_link is not None:
            process_m3u8_configuration(m3u8_link)
            m3u8_duration = return_m3u8_duration(m3u8_link)
            streamer = parse_streamer_from_m3u8_link(m3u8_link)
            video_id = parse_video_id_from_m3u8_link(m3u8_link)
            streamscharts_url = generate_website_links(streamer, video_id)[2]
            modified_streamscharts_url = streamscharts_url[:streamscharts_url.rfind('/')]
            sullygnome_duration = int(parse_duration_sullygnome(tracker_url))
            if sullygnome_duration >= m3u8_duration + 10:
                print(f"The duration from Sullygnome exceeds the M3U8 duration by over 10 minutes. Consider checking Streamscharts for a split stream. URL: {modified_streamscharts_url}")
    else:
        print("Link not supported.. Returning to main menu.")
        return


def get_all_clip_urls(clip_format_dict, clip_format_list):
    combined_clip_format_list = []
    for key, value in clip_format_dict.items():
        if key in clip_format_list:
            combined_clip_format_list += value
    return combined_clip_format_list


def get_vod_urls(streamer_name, video_id, start_timestamp):
    m3u8_link_list, successful_m3u8_link_list = [], []
    domains = read_text_file('config/domains.txt')
    for seconds in range(60):
        base_url = f"{streamer_name}_{video_id}_{int(calculate_epoch_timestamp(start_timestamp, seconds))}"
        hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
        for domain in domains:
            m3u8_link_list.append(f"{domain}{hashed_base_url}_{base_url}/chunked/index-dvr.m3u8")
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in m3u8_link_list]
    for response in grequests.imap(rs, size=100):
        if response.status_code == 200:
            successful_m3u8_link_list.append(response.url)
    if successful_m3u8_link_list:
        return random.choice(successful_m3u8_link_list)
    else:
        return


def return_supported_qualities(m3u8_link):
    valid_resolutions = []
    resolutions = ["chunked", "1080p60", "1080p30", "720p60", "720p30", "480p60", "480p30"]
    if m3u8_link is None:
        return None
    request_list = [grequests.get(m3u8_link.replace("chunked", resolution)) for resolution in resolutions]
    responses = grequests.map(request_list, size=100)
    for resolution, response in zip(resolutions, responses):
        if response and response.status_code == 200:
            valid_resolutions.append(resolution)
            print(f"{len(valid_resolutions)}. {resolution}")
    try:
        choice = int(input("Please choose a quality: "))
        if 1 <= choice <= len(valid_resolutions):
            quality = valid_resolutions[choice - 1]
            user_option = m3u8_link.replace("chunked", quality)
            return user_option
        else:
            print("Invalid option. Please try again!")
            return
    except ValueError:
        print("Invalid option. Please try again!")
        return


def parse_website_duration(duration_string):
    if isinstance(duration_string, list):
        duration_string = ' '.join(duration_string)
    if not isinstance(duration_string, str):
        if isinstance(duration_string, Iterable) and not isinstance(duration_string, (str, bytes)):
            duration_string = ' '.join(duration_string)
        else:
            duration_string = str(duration_string)
    pattern = r"(\d+)\s*(h(?:ou)?r?s?|m(?:in)?(?:ute)?s?)"
    matches = re.findall(pattern, duration_string, re.IGNORECASE)
    hours = 0
    minutes = 0
    for value, unit in matches:
        if 'h' in unit.lower():
            hours = int(value)
        elif 'm' in unit.lower():
            minutes = int(value)
    return calculate_broadcast_duration_in_minutes(hours, minutes)


def parse_duration_streamscharts(streamcharts_url):
    retries = 10
    reqs = [grequests.get(streamcharts_url, headers=return_user_agent()) for _ in range(retries)]
    for response in grequests.imap(reqs, size=10):
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, 'html.parser')
            streamcharts_duration = bs.find_all('div', {'class': 'text-xs font-bold'})[3].text
            streamcharts_duration_in_minutes = parse_website_duration(streamcharts_duration)
            return streamcharts_duration_in_minutes
        print("Failed to fetch webpage after 10 retries.")
    return None


def parse_duration_twitchtracker(twitchtracker_url):
    response = requests.get(twitchtracker_url, headers=return_user_agent())
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, 'html.parser')
        twitchtracker_duration = bs.find_all('div', {'class': 'g-x-s-value'})[0].text
        return twitchtracker_duration
    else:
        print("Error: Unable to fetch webpage. Status code:", response.status_code)
        if response.status_code == 403:
            print("Error: TwitchTracker has blocked requests from this script, please try another supported website")
        return None


def parse_duration_sullygnome(sullygnome_url):
    response = requests.get(sullygnome_url, headers=return_user_agent())
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, 'html.parser')
        sullygnome_duration = bs.find_all('div', {'class': 'MiddleSubHeaderItemValue'})[7].text.split(",")
        sullygnome_duration_in_minutes = parse_website_duration(sullygnome_duration)
        return sullygnome_duration_in_minutes
    else:
        print("Error: Unable to fetch webpage. Status code:", response.status_code)
        if response.status_code == 403:
            print("Error: Sullygnome has blocked requests from this script, please try another supported website")
        return None


def parse_datetime_streamscharts(streamscharts_url):
    retries = 10
    reqs = [grequests.get(streamscharts_url, headers=return_user_agent()) for _ in range(retries)]
    for response in grequests.imap(reqs, size=10):
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, 'html.parser')
            streamscharts_datetime = bs.find_all('time', {'class': 'ml-2 font-bold'})[0].text.strip().replace(",", "") + ":00"
            return datetime.strptime(streamscharts_datetime, "%d %b %Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    print("Failed to fetch webpage after 10 retries.")
    return None


def parse_datetime_twitchtracker(twitchtracker_url):
    response = requests.get(twitchtracker_url, headers=return_user_agent())
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, 'html.parser')
        twitchtracker_datetime = bs.find_all('div', {'class': 'stream-timestamp-dt'})[0].text
        return twitchtracker_datetime
    else:
        print("Error: Unable to fetch webpage. Status code:", response.status_code)
        if response.status_code == 403:
            print("Error: TwitchTracker has blocked requests from this script, please try another supported website")
        return None


def parse_datetime_sullygnome(sullygnome_url):
    response = requests.get(sullygnome_url, headers=return_user_agent())
    if response.status_code == 200:
        bs = BeautifulSoup(response.content, 'html.parser')
        stream_date = bs.find_all('div', {'class': 'MiddleSubHeaderItemValue'})[6].text
        modified_stream_date = remove_chars_from_ordinal_numbers(stream_date)
        formatted_stream_date = datetime.strptime(modified_stream_date, "%A %d %B %I:%M%p").strftime("%m-%d %H:%M:%S")
        return str(datetime.now().year) + "-" + formatted_stream_date
    else:
        print("Error: Unable to fetch webpage. Status code:", response.status_code)
        if response.status_code == 403:
            print("Error: Sullygnome has blocked requests from this script, please try another supported website")
        return None


def unmute_vod(m3u8_link):
    counter = 0
    video_filepath = get_vod_filepath(parse_streamer_from_m3u8_link(m3u8_link), parse_video_id_from_m3u8_link(m3u8_link))
    write_m3u8_to_file(m3u8_link, video_filepath)
    file_contents = read_text_file(video_filepath)
    if is_video_muted(m3u8_link):
        with open(video_filepath, "w") as video_file:
            for segment in file_contents:
                m3u8_link = m3u8_link.replace("index-dvr.m3u8", "")
                if "-unmuted" in segment and not segment.startswith("#"):
                    counter += 1
                    video_file.write(f"{m3u8_link}{counter - 1}-muted.ts\n")
                elif "-unmuted" not in segment and not segment.startswith("#"):
                    counter += 1
                    video_file.write(f"{m3u8_link}{counter - 1}.ts\n")
                else:
                    video_file.write(f"{segment}\n")
        print(f"{os.path.normpath(video_filepath)} Has been unmuted!")
    else:
        with open(video_filepath, "w") as video_file:
            for segment in file_contents:
                m3u8_link = m3u8_link.replace("index-dvr.m3u8", "")
                if not segment.startswith("#"):
                    video_file.write(f"{m3u8_link}{counter}.ts\n")
                    counter += 1
                else:
                    video_file.write(f"{segment}\n")


def mark_invalid_segments_in_playlist(m3u8_link):
    unmute_vod(m3u8_link)
    vod_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(m3u8_link), parse_video_id_from_m3u8_link(m3u8_link))
    with open(vod_file_path, "r") as f:
        lines = f.read().splitlines()
    segments = validate_playlist_segments(get_all_playlist_segments(m3u8_link))
    if not segments:
        print("No segments are valid. Cannot generate M3U8! Returning to main menu.")
        os.remove(vod_file_path)
        return
    playlist_segments = [segment for segment in segments if segment in lines]
    modified_playlist = []
    for line in lines:
        if line in playlist_segments:
            modified_playlist.append(line)
        elif line.startswith("#"):
            modified_playlist.append(line)
        elif line.endswith(".ts"):
            modified_playlist.append("#" + line)
        else:
            modified_playlist.append(line)
    with open(vod_file_path, "w") as f:
        f.write("\n".join(modified_playlist))


def return_m3u8_duration(m3u8_link):
    total_duration = 0
    file_contents = requests.get(m3u8_link, stream=True).text.splitlines()
    for line in file_contents:
        if line.startswith("#EXTINF:"):
            segment_duration = float(line.split(":")[1].split(",")[0])
            total_duration += segment_duration
    total_minutes = int(total_duration // 60)
    return total_minutes


def process_m3u8_configuration(m3u8_link):
    playlist_segments = get_all_playlist_segments(m3u8_link)
    if is_video_muted(m3u8_link):
        print(m3u8_link, "\nVideo contains muted segments")
        if read_config_by_key('settings', 'UNMUTE_VIDEO'):
            unmute_vod(m3u8_link)
    else:
        print(m3u8_link, "\nVideo does NOT contain muted segments")
        os.remove(get_vod_filepath(parse_streamer_from_m3u8_link(m3u8_link), parse_video_id_from_m3u8_link(m3u8_link)))
    if read_config_by_key('settings', 'CHECK_SEGMENTS'):
        validate_playlist_segments(playlist_segments)


def get_all_playlist_segments(m3u8_link):
    counter = 0
    segment_list = []
    video_file_path = get_vod_filepath(parse_streamer_from_m3u8_link(m3u8_link), parse_video_id_from_m3u8_link(m3u8_link))
    write_m3u8_to_file(m3u8_link, video_file_path)
    file_contents = read_text_file(video_file_path)
    with open(video_file_path, "w") as video_file:
        for segment in file_contents:
            m3u8_link = m3u8_link.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                new_segment = f"{m3u8_link}{counter - 1}-muted.ts"
                video_file.write(f"{new_segment}\n")
                segment_list.append(new_segment)
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                new_segment = f"{m3u8_link}{counter - 1}.ts"
                video_file.write(f"{new_segment}\n")
                segment_list.append(new_segment)
            else:
                video_file.write(f"{segment}\n")
    video_file.close()
    return segment_list


def validate_playlist_segments(segments):
    valid_segments = []
    all_segments = [url.strip() for url in segments]
    available_segment_count = 0
    request_session = grequests.Session()
    rs = (grequests.head(u, session=request_session) for u in all_segments)
    responses = grequests.imap(rs, size=100)
    for i, response in enumerate(responses):
        print(f"\rChecking segments.. {i + 1} / {len(all_segments)}", end="")
        if response is not None:
            if response.status_code == 200:
                available_segment_count += 1
                valid_segments.append(response.url)
    if (available_segment_count == len(all_segments)) or (available_segment_count == 0):
        print(f"\n{available_segment_count} out of {len(all_segments)} Segments are Available.")
    elif available_segment_count < len(all_segments):
        print(f"\n{available_segment_count} out of {len(all_segments)} Segments are Available. Please see option 5 of the main menu!")
    return valid_segments


def vod_recover(streamer_name, video_id, timestamp):
    if timestamp is None:
        return
    else: 
        print("Searching for videos...")
        vod_age = calculate_days_since_broadcast(timestamp)
        if vod_age > 60:
            print("Video is older than 60 days. Chances of recovery are very slim.\n")
        vod_url = return_supported_qualities(get_vod_urls(streamer_name, video_id, timestamp))
        if vod_url is None:
            alternate_websites = '\n'.join(generate_website_links(streamer_name, video_id))
            print(f"No videos found using the current domain list. Try using an alternate website:\n{alternate_websites}")
            return
        else:
            return vod_url


def bulk_vod_recovery():
    csv_file_path = get_and_validate_csv_filename()
    streamer_name = parse_streamer_from_csv_filename(csv_file_path)
    csv_file = parse_vod_csv_file(csv_file_path)
    for timestamp, video_id in csv_file.items():
        print("\n" + "Recovering Video....", video_id)
        m3u8_link = get_vod_urls(streamer_name.lower(), video_id, timestamp)
        if m3u8_link is not None:
            process_m3u8_configuration(m3u8_link)
        else:
            print("No vods found using the current domain list.")


def clip_recover(streamer, video_id, duration):
    iteration_counter, valid_counter = 0, 0
    valid_url_list = []
    clip_format = print_clip_format_menu().split(" ")
    full_url_list = get_all_clip_urls(get_clip_format(video_id, calculate_max_clip_offset(duration)), clip_format)
    request_session = requests.Session()
    rs = [grequests.head(u, session=request_session) for u in full_url_list]
    for response in grequests.imap(rs, size=100):
        iteration_counter += 1
        print(f'\rSearching for clips..... {iteration_counter} of {len(full_url_list)}', end=" ", flush=True)
        if response.status_code == 200:
            valid_counter += 1
            valid_url_list.append(response.url)
    print(f"\n{valid_counter} Clip(s) Found")
    if valid_url_list:
        for url in valid_url_list:
            write_text_file(url, get_log_filepath(streamer, video_id))
        if read_config_by_key('settings', 'DOWNLOAD_CLIPS') or input("Do you want to download the recovered clips (Y/N): ").upper() == "Y":
            download_clips(get_download_directory(), streamer, video_id)
        if read_config_by_key('settings', 'REMOVE_LOG_FILE'):
            os.remove(get_log_filepath(streamer, video_id))
        else:
            keep_log_option = input("Do you want to remove the log file? ")
            if keep_log_option.upper() == "Y":
                os.remove(get_log_filepath(streamer, video_id))
    else:
        print("No clips found! Returning to main menu.")


def get_and_validate_csv_filename():
    while True:
        file_path = input("Please enter the absolute path of the CSV file: ").replace('"', '')
        csv_filename = os.path.basename(file_path)
        pattern = r"^[a-zA-Z0-9_]{4,25} - Twitch stream stats"
        if bool(re.match(pattern, csv_filename)):
            return file_path
        else:
            print("The CSV filename MUST be the original filename that was downloaded from sullygnome!")


def parse_clip_csv_file(file_path):
    vod_info_dict = {}
    lines = read_csv_file(file_path)[1:]
    for line in lines:
        if line:
            stream_date = remove_chars_from_ordinal_numbers(line[1].replace('"', ""))
            modified_stream_date = datetime.strptime(stream_date, "%A %d %B %Y %H:%M").strftime("%d-%B-%Y")
            video_id = line[2].partition("stream/")[2].replace('"', "")
            duration = line[3]
            if video_id != '0':
                max_clip_offset = calculate_max_clip_offset(int(duration))
                vod_info_dict.update({video_id: (modified_stream_date, max_clip_offset)})
    return vod_info_dict


def parse_vod_csv_file(file_path):
    vod_info_dict = {}
    lines = read_csv_file(file_path)[1:]
    for line in lines:
        if line:
            stream_date = remove_chars_from_ordinal_numbers(line[1].replace('"', ""))
            modified_stream_date = datetime.strptime(stream_date, "%A %d %B %Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
            video_id = line[2].partition("stream/")[2].split(",")[0].replace('"', "")
            vod_info_dict.update({modified_stream_date: video_id})
    return vod_info_dict


def merge_csv_files(csv_filename, directory_path):
    csv_list = [file for file in os.listdir(directory_path) if file.endswith(".csv")]
    header_saved = False
    with open(os.path.join(directory_path, f"{csv_filename.title()}_MERGED.csv"), "w", newline="") as output_file:
        writer = csv.writer(output_file)
        for file in csv_list:
            reader = read_csv_file(os.path.join(directory_path, file))
            header = reader[0]
            if not header_saved:
                writer.writerow(header)
                header_saved = True
            for row in reader[1:]:
                writer.writerow(row)
    print("CSV files merged successfully!")


def random_clip_recovery(video_id, hours, minutes):
    counter = 0
    display_limit = 3
    clip_format = print_clip_format_menu().split(" ")
    full_url_list = get_all_clip_urls(get_clip_format(video_id, calculate_max_clip_offset(calculate_broadcast_duration_in_minutes(hours, minutes))), clip_format)
    random.shuffle(full_url_list)
    print(f"Total Number of URLs: {len(full_url_list)}")
    request_session = requests.Session()
    rs = (grequests.head(url, session=request_session) for url in full_url_list)
    responses = grequests.imap(rs, size=100)
    for response in responses:
        if counter < display_limit:
            if response.status_code == 200:
                counter += 1
                print(response.url)
            if counter == display_limit:
                user_option = input("Do you want to see more URLs (Y/N): ")
                if user_option.upper() == "Y":
                    display_limit += 3
        else:
            break


def bulk_clip_recovery():
    vod_counter, total_counter, valid_counter, iteration_counter = 0, 0, 0, 0
    streamer_name, csv_file_path = "", ""
    bulk_recovery_option = print_bulk_clip_recovery_menu()
    if bulk_recovery_option == "1":
        csv_file_path = get_and_validate_csv_filename()
        streamer_name = parse_streamer_from_csv_filename(csv_file_path)
    elif bulk_recovery_option == "2":
        csv_directory = input("Enter the full path where the sullygnome csv files exist: ").replace('"', '')
        streamer_name = input("Enter the streamer's name: ")
        merge_files = input("Do you want to merge the CSV files in the directory? (Y/N): ")
        if merge_files.upper() == "Y":
            merge_csv_files(streamer_name, csv_directory)
            csv_file_path = os.path.join(csv_directory, f"{streamer_name.title()}_MERGED.csv")
        else:
            csv_file_path = get_and_validate_csv_filename()
            csv_file_path = csv_file_path.replace('"', '')
    elif bulk_recovery_option == "3":
        exit()
    user_option = input("Do you want to download all clips recovered (Y/N)? ")
    clip_format = print_clip_format_menu().split(" ")
    stream_info_dict = parse_clip_csv_file(csv_file_path)
    for video_id, values in stream_info_dict.items():
        vod_counter += 1
        print(
            f"\nProcessing Past Broadcast:\n"
            f"Stream Date: {values[0].replace('-', ' ')}\n"
            f"Vod ID: {video_id}\n"
            f"Vod Number: {vod_counter} of {len(stream_info_dict)}\n")
        original_vod_url_list = get_all_clip_urls(get_clip_format(video_id, values[1]), clip_format)
        request_session = requests.Session()
        rs = [grequests.head(u, session=request_session) for u in original_vod_url_list]
        for response in grequests.imap(rs, size=100):
            total_counter += 1
            iteration_counter += 1
            print(f'\rSearching for clips..... {iteration_counter} of {len(original_vod_url_list)}', end=" ", flush=True)
            total_counter = 0
            if response.status_code == 200:
                valid_counter += 1
                write_text_file(response.url, get_log_filepath(streamer_name, video_id))
            else:
                continue
        print(f'\n{valid_counter} Clip(s) Found')
        if valid_counter != 0:
            if user_option.upper() == "Y":
                download_clips(get_default_directory(), streamer_name, video_id)
                os.remove(get_log_filepath(streamer_name, video_id))
            else:
                print("Recovered clips logged to " + get_log_filepath(streamer_name, video_id))
        else:
            print("No clips found!... Moving on to next vod." + "\n")
        total_counter, valid_counter, iteration_counter = 0, 0, 0


def download_clips(directory, streamer_name, video_id):
    print("Starting Download....")
    download_directory = os.path.join(directory, f"{streamer_name.title()}_{video_id}")
    os.makedirs(download_directory, exist_ok=True)
    file_contents = read_text_file(get_log_filepath(streamer_name, video_id))
    if not file_contents:
        print("File is empty!")
        return
    mp4_links = [link for link in file_contents if os.path.basename(link).endswith(".mp4")]
    reqs = [grequests.get(link, stream=False) for link in mp4_links]
    for response in grequests.imap(reqs, size=12):
        if response.status_code == 200:
            offset = extract_offset(response.url)
            file_name = f"{streamer_name.title()}_{video_id}_{offset}.mp4"
            with open(os.path.join(download_directory, file_name), 'wb') as x:
                x.write(response.content)
            print(f"Downloading... {response.url}")
        else:
            print(f"Failed to download.... {response.url}")


def download_m3u8_video_url(m3u8_link, output_filename):
    command = read_config_by_key('settings', 'DOWNLOAD_M3U8_VIDEO_URL').format(m3u8_link, os.path.join(get_default_directory(), output_filename))
    subprocess.call(command, shell=True)


def download_m3u8_video_url_slice(m3u8_link, output_filename, video_start_time, video_end_time):
    command = read_config_by_key('settings', 'DOWNLOAD_M3U8_VIDEO_URL_SLICE').format(video_start_time, video_end_time, m3u8_link, os.path.join(get_default_directory(), output_filename))
    subprocess.call(command, shell=True)


def download_m3u8_video_file(m3u8_file_path, output_filename):
    command = read_config_by_key('settings', 'DOWNLOAD_M3U8_VIDEO_FILE').format(m3u8_file_path, os.path.join(get_default_directory(), output_filename))
    subprocess.call(command, shell=True)


def download_m3u8_video_file_slice(m3u8_file_path, output_filename, video_start_time, video_end_time):
    command = read_config_by_key('settings', 'DOWNLOAD_M3U8_VIDEO_FILE_SLICE').format(video_start_time, video_end_time, m3u8_file_path, os.path.join(get_default_directory(), output_filename))
    subprocess.call(command, shell=True)


def run_vod_recover():
    print("WELCOME TO VOD RECOVERY" + "\n")
    menu = 0
    while menu < 8:
        menu = print_main_menu()
        if menu == 8:
            exit()
        elif menu == 1:
            vod_mode = print_video_mode_menu()
            if vod_mode == 1:
                vod_recovery_method = print_video_recovery_menu()
                if vod_recovery_method == 1:
                    manual_vod_recover()
                elif vod_recovery_method == 2:
                    website_vod_recover()
                elif vod_recovery_method == 3:
                    exit()
                else:
                    print("Invalid option returning to main menu.")
            elif vod_mode == 2:
                bulk_vod_recovery()
            elif vod_mode == 3:
                exit()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 2:
            clip_type = print_clip_type_menu()
            if clip_type == 1:
                clip_recovery_method = print_clip_recovery_menu()
                if clip_recovery_method == 1:
                    manual_clip_recover()
                elif clip_recovery_method == 2:
                    website_clip_recover()
                elif clip_recovery_method == 3:
                    exit()
                else:
                    print("Invalid option returning to main menu.")
            elif clip_type == 2:
                video_id, hour, minute = get_random_clip_information()
                random_clip_recovery(video_id, hour, minute)
            elif clip_type == 3:
                bulk_clip_recovery()
            elif clip_type == 4:
                exit()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 3:
            url = input("Enter M3U8 Link: ").strip()
            if is_video_muted(url):
                unmute_vod(url)
            else:
                print("Vod does NOT contain muted segments")
        elif menu == 4:
            url = input("Enter M3U8 Link: ").strip()
            validate_playlist_segments(get_all_playlist_segments(url))
            os.remove(get_vod_filepath(parse_streamer_from_m3u8_link(url), parse_video_id_from_m3u8_link(url)))
        elif menu == 5:
            url = input("Enter M3U8 Link: ").strip()
            mark_invalid_segments_in_playlist(url)
        elif menu == 6:
            download_type = print_download_type_menu()
            if download_type == 1:
                vod_url = input("Enter M3U8 Link: ").strip()
                vod_filename = "{}_{}.mp4".format(parse_streamer_from_m3u8_link(vod_url), parse_video_id_from_m3u8_link(vod_url))
                trim_vod = input("Would you like to specify the start and end time of the vod (Y/N)? ")
                if trim_vod.upper() == "Y":
                    vod_start_time = input("Enter start time (HH:MM:SS): ")
                    vod_end_time = input("Enter end time (HH:MM:SS): ")
                    download_m3u8_video_url_slice(vod_url, vod_filename, vod_start_time, vod_end_time)
                    print("Vod downloaded to {}".format(os.path.join(get_default_directory(), vod_filename)))
                else:
                    download_m3u8_video_url(vod_url, vod_filename)
                    print("Vod downloaded to {}".format(os.path.join(get_default_directory(), vod_filename)))
            elif download_type == 2:
                m3u8_file_path = input("Enter absolute file path of the M3U8: ").strip()
                trim_vod = input("Would you like to specify the start and end time of the vod (Y/N)? ")
                if trim_vod.upper() == "Y":
                    vod_start_time = input("Enter start time (HH:MM:SS): ")
                    vod_end_time = input("Enter end time (HH:MM:SS): ")
                    download_m3u8_video_file_slice(m3u8_file_path, parse_vod_filename(m3u8_file_path) + ".mp4", vod_start_time, vod_end_time)
                    print("Vod downloaded to {}".format(os.path.join(get_default_directory(), parse_vod_filename(m3u8_file_path) + ".mp4")))
                else:
                    download_m3u8_video_file(m3u8_file_path, parse_vod_filename(m3u8_file_path) + ".mp4")
                    print("Vod downloaded to {}".format(os.path.join(get_default_directory(), parse_vod_filename(m3u8_file_path) + ".mp4")))
            elif download_type == 3:
                exit()
        elif menu == 7:
            print_help()
        else:
            print("Invalid Option! Exiting...")


if __name__ == '__main__':
    run_vod_recover()

