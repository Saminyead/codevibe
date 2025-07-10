from player import MusicPlayer
from utils import search_song_yt, download_track

from datetime import datetime

import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

YT_API_KEY = os.getenv("yt_api_key")
TEMP_DIR = tempfile.gettempdir()

def input_playlist(api_key:str):
    print("Please enter your list of songs.")
    user_input = None
    video_url_list = []
    while True:
        user_input = input(
            "Please enter a name of your song to add to playlist. If you don't want to add no more, just enter 's': "
        )
        if user_input=="s":
            break
        video_id = search_song_yt(query=user_input, api_key=api_key)
        video_url_list.append(f"https://www.youtube.com/watch?v={video_id}")
    return video_url_list


def main():
    playlist = input_playlist(YT_API_KEY)
    print(playlist)
    playlist_folder_prefix = "codevibe_playlist_"
    dt_format = "%Y-%m-%d_%H-%M-%S"
    date_now = datetime.now().strftime(dt_format)
    playlist_folder = f"{TEMP_DIR}/{playlist_folder_prefix}{date_now}"
    for url in playlist:
        download_track(url=url, dest=playlist_folder)
    playlist_song_files = os.listdir(playlist_folder)
    playlist = [os.path.join(playlist_folder,song) for song in playlist_song_files]
    player = MusicPlayer(playlist=playlist)
    player.play_all_songs()


if __name__ == "__main__":
    main()
