from utils import search_song_yt, download_track, setup_logging
from ai import SYS_PROMPT, OPENROUTER_RESPONSE_FORMAT

from exceptions import AiFormatError
from pytubefix.exceptions import PytubeFixError
from logging import RootLogger

from datetime import datetime
import requests
import json
import curses

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

LOGGER = setup_logging("app.log", "./logs")


def get_ai_song_list(
    user_input: str,
    url: str = OPENROUTER_URL,
    api_key: str = OPENROUTER_API_KEY,
    model: str = MODEL,
    sys_prompt: str = SYS_PROMPT,
    res_format: dict = OPENROUTER_RESPONSE_FORMAT,
) -> list[str]:
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
    song_list = ai_res_dict["songs"]
    if not type(song_list[0]) is str:
        raise AiFormatError
    return song_list


def get_ai_song_list_retry(
    user_input: str, n_attempts: int = 3, logger: RootLogger = LOGGER
):
    for attempt in range(n_attempts):
        try:
            return get_ai_song_list(user_input=user_input)
        except Exception as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt + 1} failed for getting AI song list with {type(e).__name__}: {e}"
            )
    logger.error("Max retries exceeded for getting AI song list.")
    raise last_exception


def get_recommended_song_list(
    stdscr: curses.window,
    scr_pos: tuple[int, int],
) -> list[str]:
    user_input_prompt = "Tell me your vibes for a great list of music: "
    stdscr.addstr(scr_pos[0], scr_pos[1], user_input_prompt)
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(scr_pos[0], scr_pos[1] + len(user_input_prompt)).decode()
    curses.noecho()
    return get_ai_song_list_retry(user_input)


def get_yt_url_list(
    song_list: list[str], yt_api_key: str = YT_API_KEY, logger: RootLogger = LOGGER
):
    video_url_list = []
    for song in song_list:
        try:
            video_id = search_song_yt(query=song, api_key=yt_api_key)
        except Exception as e:
            logger.error(
                f"Could not download track for {song}, due to the following error:\n{e}"
            )
            continue
        video_url_list.append(f"https://www.youtube.com/watch?v={video_id}")
    return video_url_list


def download_tracks_all(
    url_list: list[str],
    playlist_folder: str,
    playlist: list[str],
    logger: RootLogger = LOGGER,
):
    for url in url_list:
        try:
            download_track(url=url, dest=playlist_folder, playlist=playlist)
        except PytubeFixError:
            logger.error(f"Error downloading track for url {url}")
            continue


def app(stdscr: curses.window, init_scr_pos: tuple[int, int] = (0, 0)):
    try:  
        # Windows throws error during the very import of vlc Python package.
        from player import MusicPlayer
    except NameError:
        import platform
        bit_version = platform.architecture()[0]
        stdscr.addstr(
            0,
            0,
            f"""This program requires VLC Media Player to run. Please install
            VLC Media Player and launch the program again. If it is installed
            make sure it is the {bit_version} version of VLC."""
        )
        stdscr.addstr(1,0,"Press any key to exit.")
        stdscr.getch()
    song_list = get_recommended_song_list(stdscr, init_scr_pos)
    stdscr.refresh()
    song_list_y, song_list_x = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(song_list_y, song_list_x, f"{song_list}")
    stdscr.refresh()
    playlist = get_yt_url_list(song_list=song_list)
    playlist_y, playlist_x = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(playlist_y, playlist_x, f"{playlist}")
    stdscr.refresh()
    all_playlist_folder = "codevibe"
    playlist_folder_prefix = "codevibe_playlist_"
    codevibe_folder = f"{TEMP_DIR}/{all_playlist_folder}"
    if not os.path.exists(codevibe_folder):
        os.mkdir(codevibe_folder)
    dt_format = "%Y-%m-%d_%H-%M-%S"
    date_now = datetime.now().strftime(dt_format)
    playlist_folder = f"{codevibe_folder}/{playlist_folder_prefix}{date_now}"
    os.mkdir(playlist_folder)
    player_init_pos = stdscr.getyx()[0] + 3, 0
    player = MusicPlayer(
        playlist_folder=playlist_folder,
        expected_len=len(playlist),
        screen=stdscr,
        screen_init_pos=player_init_pos,
    )
    threading.Thread(
        target=download_tracks_all,
        kwargs={
            "url_list": playlist,
            "playlist_folder": playlist_folder,
            "playlist": player.playlist,
        },
    ).start()
    player.play_all_songs()


def main():
    curses.wrapper(app)


if __name__ == "__main__":
    main()
