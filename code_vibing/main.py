from player import MusicPlayer
from utils import search_song_yt, download_track
from ai import SYS_PROMPT, OPENROUTER_RESPONSE_FORMAT

from datetime import datetime
import requests
import json
import curses

from pathlib import Path
import threading

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
    stdscr: curses.window,
    scr_pos: tuple[int, int],
    url: str = OPENROUTER_URL,
    api_key: str = OPENROUTER_API_KEY,
    model: str = MODEL,
    sys_prompt: str = SYS_PROMPT,
    res_format: dict = OPENROUTER_RESPONSE_FORMAT,
) -> list[str]:
    user_input_prompt = "Tell me your vibes for a great list of music: "
    stdscr.addstr(scr_pos[0], scr_pos[1], user_input_prompt)
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(scr_pos[0], scr_pos[1] + len(user_input_prompt)).decode()
    curses.noecho()
    res = requests.post(
        url=url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
            "response_format": res_format,
        },
    )
    ai_res = res.json()["choices"][0]["message"]["content"]
    ai_res_dict = json.loads(ai_res)
    return ai_res_dict["songs"]


def download_tracks_all(url_list: str, playlist_folder: str | Path):
    for url in url_list:
        download_track(url=url, dest=playlist_folder)


def create_playlist(song_list: list[str], yt_api_key: str = YT_API_KEY):
    video_url_list = []
    for song in song_list:
        video_id = search_song_yt(query=song, api_key=yt_api_key)
        video_url_list.append(f"https://www.youtube.com/watch?v={video_id}")
    return video_url_list


def app(stdscr: curses.window, init_scr_pos: tuple[int, int] = (0, 0)):
    song_list = get_recommended_song_list(stdscr, init_scr_pos)
    stdscr.refresh()
    song_list_y, song_list_x = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(song_list_y, song_list_x, f"{song_list}")
    stdscr.refresh()
    playlist = create_playlist(song_list=song_list)
    playlist_y, playlist_x = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(playlist_y, playlist_x, f"{playlist}")
    stdscr.refresh()
    playlist_folder_prefix = "codevibe_playlist_"
    dt_format = "%Y-%m-%d_%H-%M-%S"
    date_now = datetime.now().strftime(dt_format)
    playlist_folder = f"{TEMP_DIR}/{playlist_folder_prefix}{date_now}"
    os.mkdir(playlist_folder)
    threading.Thread(
        target=download_tracks_all,
        kwargs={"url_list": playlist, "playlist_folder": playlist_folder},
    ).start()
    player_init_pos = stdscr.getyx()[0] + 3, 0
    player = MusicPlayer(
        playlist_folder=playlist_folder,
        expected_len=len(playlist),
        screen=stdscr,
        screen_init_pos=player_init_pos,
    )
    player.play_all_songs()


def main():
    curses.wrapper(app)


if __name__ == "__main__":
    main()
