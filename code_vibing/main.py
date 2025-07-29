from utils import search_song_yt, download_track, setup_logging, check_and_save_api_key
from ai import SYS_PROMPT, OPENROUTER_RESPONSE_FORMAT

from exceptions import AiFormatError
from pytubefix.exceptions import PytubeFixError
from logging import RootLogger
import vlc

from datetime import datetime
import requests
import json
import curses

import threading

import os
import tempfile
from dotenv import load_dotenv

TEMP_DIR = tempfile.gettempdir()

MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

LOGGER = setup_logging("app.log", "./logs")

load_dotenv()
OPENROUTER_API_KEY=os.getenv("openrouter_api_key")
YT_API_KEY=os.getenv("yt_api_key")


def get_ai_song_list(
    user_input: str,
    api_key: str,
    url: str = OPENROUTER_URL,
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
    user_input: str, api_key:str, n_attempts: int = 3, logger: RootLogger = LOGGER
):
    for attempt in range(n_attempts):
        try:
            return get_ai_song_list(user_input=user_input, api_key=api_key)
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
    ai_api_key: str
) -> list[str]:
    user_input_prompt = "Tell me your vibes for a great list of music: "
    stdscr.addstr(scr_pos[0], scr_pos[1], user_input_prompt)
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(scr_pos[0], scr_pos[1] + len(user_input_prompt)).decode()
    curses.noecho()
    return get_ai_song_list_retry(user_input=user_input, api_key=ai_api_key)


def get_yt_url_list(
    song_list: list[str], yt_api_key: str, logger: RootLogger = LOGGER
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


def get_api_keys_from_user(
    stdscr: curses.window, 
    openrouter_api_key:str | None = OPENROUTER_API_KEY,
    yt_api_key:str | None = YT_API_KEY
) -> dict[str,str]:
    openrouter_api_key_input = None
    yt_api_key_input = None
    if not openrouter_api_key:
        init_pos = stdscr.getyx()
        stdscr.addstr(
            init_pos[0] + 2,
            0,
            "This program requires an Openrouter API KEY."
        )
        enter_openrouter_prompt = "Please enter your Openrouter API Key here: "
        stdscr.addstr(init_pos[0] + 3, 0, enter_openrouter_prompt)
        curses.echo()
        openrouter_api_key_input = stdscr.getstr(
            init_pos[0] + 3, len(enter_openrouter_prompt)
        ).decode().strip()
        curses.noecho()
        os.environ["openrouter_api_key"] = openrouter_api_key_input
        openrouter_api_key = os.environ["openrouter_api_key"]
    if not yt_api_key:
        init_pos = stdscr.getyx()
        stdscr.addstr(
            init_pos[0] + 2,
            0,
            "This program requires an Google Developer API Key."
        )
        enter_yt_prompt = "Please enter your Google Developer API Key here: "
        stdscr.addstr(init_pos[0] + 3, 0, enter_yt_prompt)
        curses.echo()
        yt_api_key_input = stdscr.getstr(
            init_pos[0] + 3, len(enter_yt_prompt)
        ).decode().strip()
        curses.noecho()
        os.environ["yt_api_key"] = yt_api_key_input
        yt_api_key = os.environ["yt_api_key"]
    stdscr.addstr(
        stdscr.getyx()[0] + 2,
        0,
        "Do you wish to save the API keys? Press y to save, press n to cancel."
    )
    save_status_user_input = stdscr.getkey()
    if save_status_user_input in ("y","Y"):
        env_path = ".env"
        is_empty = not os.path.exists(env_path) or os.stat(env_path).st_size == 0
        with open(file=env_path, mode="a") as fp:
            if is_empty:
                fp.write("\n")
            if openrouter_api_key_input:
                fp.write(f"openrouter_api_key={openrouter_api_key_input}\n")
            if yt_api_key_input:
                fp.write(f"yt_api_key={yt_api_key_input}\n")
    stdscr.clear()
    return {
        "openrouter_api_key": openrouter_api_key,
        "yt_api_key": yt_api_key
    }


def app(
    stdscr: curses.window,
    ai_api_key: str | None = OPENROUTER_API_KEY,
    yt_api_key: str | None = YT_API_KEY,
    init_scr_pos: tuple[int, int] = (0, 0)
):
    try:  
        # Windows throws error during the very import of vlc Python package.
        from player import MusicPlayer
    except FileNotFoundError:
        import platform
        bit_version = platform.architecture()[0]
        stdscr.addstr(
            0,
            0,
            f"""This program requires VLC Media Player to run. Please install
            VLC Media Player and launch the program again. If it is already 
            installed make sure it is the {bit_version} version of VLC."""
        )
        stdscr.addstr(stdscr.getyx()[0] + 2, 0, "Press any key to exit.")
        stdscr.getch()
        return
    try:
        vlc.Instance()
    except NameError:
        stdscr.addstr(
            0,
            0,
            """This program requires VLC Media Player to run. Please install
            VLC Media Player and launch the program again."""
        )
        stdscr.addstr(stdscr.getyx()[0] + 2, 0, "Press any key to exit.")
        stdscr.getch()
        return
    if not ai_api_key or not yt_api_key:
        api_keys = get_api_keys_from_user(stdscr)
        ai_api_key = api_keys["openrouter_api_key"]
        yt_api_key = api_keys["yt_api_key"]
    song_list = get_recommended_song_list(stdscr, init_scr_pos, ai_api_key)
    stdscr.refresh()
    song_list_y, song_list_x = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(song_list_y, song_list_x, f"{song_list}")
    stdscr.refresh()
    playlist = get_yt_url_list(song_list=song_list, yt_api_key=yt_api_key)
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
