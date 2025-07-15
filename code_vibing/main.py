from player import MusicPlayer
from utils import search_song_yt, download_track
from ai import SYS_PROMPT, OPENROUTER_RESPONSE_FORMAT

from datetime import datetime
import requests
import json

import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

YT_API_KEY = os.getenv("yt_api_key")
OPENROUTER_API_KEY = os.getenv("openrouter_api_key")

TEMP_DIR = tempfile.gettempdir()

MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_recommended_song_list(
    url:str=OPENROUTER_URL,
    api_key:str=OPENROUTER_API_KEY,
    model:str=MODEL,
    sys_prompt:str=SYS_PROMPT,
    res_format:dict=OPENROUTER_RESPONSE_FORMAT,
):
    user_input = input("Tell me your vibes below for a great list of music: ")
    res = requests.post(
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": sys_prompt
                },
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            "response_format": res_format
        }
    )
    ai_res = res.json()['choices'][0]['message']['content']
    ai_res_dict = json.loads(ai_res)
    return ai_res_dict['songs']


def create_playlist(song_list:list[str], yt_api_key:str=YT_API_KEY):
    video_url_list = []
    for song in song_list:
        video_id = search_song_yt(query=song, api_key=yt_api_key)
        video_url_list.append(f"https://www.youtube.com/watch?v={video_id}")
    return video_url_list


def main():
    song_list = get_recommended_song_list()
    print(song_list)
    playlist = create_playlist(song_list=song_list)
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
