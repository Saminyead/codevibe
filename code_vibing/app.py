from ai import get_ai_song_list_retry
import curses
from curses.textpad import Textbox

import os
import subprocess
import sys
import threading
from datetime import datetime

from utils import download_tracks_all, get_yt_obj_list
import tempfile

from logging import RootLogger

from save import save_playlist
from pathlib import Path


def get_user_input_textbox(begin_pos: tuple[int, int]):
    user_input_win = curses.newwin(3, curses.COLS, begin_pos[0], begin_pos[1])
    user_input_box = Textbox(win=user_input_win, insert_mode=True)
    # Enter is not end-of-signal by default
    # key 7 is Ctrl + G (end-of-signal in curses textbox), 10 is Enter
    user_input_box.edit(lambda x: 7 if x == 10 else x)
    return user_input_box.gather()


def get_n_songs_from_user(stdscr: curses.window, n_songs: int = 5):
    n_songs_prompt = (
        "How many songs do you want in the playlist? " "Enter a number (default = 5) "
    )
    prompt_pos = stdscr.getyx()[0] + 2, 0
    stdscr.addstr(prompt_pos[0], prompt_pos[1], n_songs_prompt)
    stdscr.refresh()
    curses.echo()
    n_songs_str = stdscr.getstr()
    curses.noecho()
    stdscr.refresh()
    try:
        return int(n_songs_str)
    except ValueError:
        return n_songs


def get_recommended_song_list(
    stdscr: curses.window,
    scr_pos: tuple[int, int],
    url: str,
    model: str,
    ai_api_key: str,
    logger: RootLogger,
) -> list[str]:
    user_input_prompt = "Tell me your vibes below for a great list of music: "
    stdscr.addstr(scr_pos[0], scr_pos[1], user_input_prompt)
    stdscr.refresh()
    textbox_pos = stdscr.getyx()[0] + 2, 0
    user_input = get_user_input_textbox(begin_pos=textbox_pos)
    stdscr.refresh()
    stdscr.addstr(stdscr.getyx()[0] + 2, 0, user_input)
    stdscr.refresh()
    n_songs = get_n_songs_from_user(stdscr)
    error_msg_y = stdscr.getyx()[0] + 2
    while True:
        try:
            return get_ai_song_list_retry(
                user_input=user_input,
                url=url,
                api_key=ai_api_key,
                model=model,
                logger=logger,
                n_songs=n_songs,
            )
        except Exception as e:
            logger.error(f"Encountered the following error with the AI:\n{e}")
            stdscr.addstr(
                error_msg_y,
                0,
                "We encountered an error with the AI. Do you wish to retry "
                "prompting the AI? Press y to retry, or any other key to quit "
                "the program.",
            )
            if stdscr.getkey() not in ("y", "Y"):
                raise
            stdscr.move(error_msg_y, 0)
            stdscr.clrtobot()
            stdscr.refresh()


def get_api_keys_from_user(
    stdscr: curses.window,
    openrouter_api_key: str | None,
) -> str:
    openrouter_api_key_input = None
    if not openrouter_api_key:
        init_pos = stdscr.getyx()
        stdscr.addstr(
            init_pos[0] + 2, 0, "This program requires an Openrouter API KEY."
        )
        enter_openrouter_prompt = "Please enter your Openrouter API Key here: "
        stdscr.addstr(init_pos[0] + 3, 0, enter_openrouter_prompt)
        curses.echo()
        openrouter_api_key_input = (
            stdscr.getstr(init_pos[0] + 3, len(enter_openrouter_prompt))
            .decode()
            .strip()
        )
        curses.noecho()
        os.environ["openrouter_api_key"] = openrouter_api_key_input
        openrouter_api_key = os.environ["openrouter_api_key"]
    stdscr.addstr(
        stdscr.getyx()[0] + 2,
        0,
        "Do you wish to save the API key? Press y to save, press n to cancel.",
    )
    save_status_user_input = stdscr.getkey()
    if save_status_user_input in ("y", "Y"):
        env_path = ".env"
        is_empty = not os.path.exists(env_path) or os.stat(env_path).st_size == 0
        with open(file=env_path, mode="a") as fp:
            if not is_empty:
                fp.write("\n")
            if openrouter_api_key_input:
                fp.write(f"openrouter_api_key={openrouter_api_key}\n")
    stdscr.clear()
    return openrouter_api_key


def app(
    stdscr: curses.window,
    ai_api_key: str | None,
    openrouter_url: str,
    model: str,
    save_playlist_dir: str | Path,
    logger: RootLogger,
    init_scr_pos: tuple[int, int] = (0, 0),
):
    # sometimes plugin path not properly detected in Linux
    if sys.platform == "linux":
        check_vlc_plugin_path = subprocess.check_output(
            ["find", "/usr/lib", "-type", "d", "-name", "plugins", "-path", "*/vlc/*"],
            text=True,
        )
        plugin_path = check_vlc_plugin_path.strip()
        os.environ["VLC_PLUGIN_PATH"] = plugin_path
    # Windows throws error during the very import of vlc Python package
    # if VLC is not installed
    try:
        from player import MusicPlayer
    # the exception is different when running normally vs frozen.
    # need to keep an eye out if other kinds of exceptions occur
    except Exception as e:
        import platform

        bit_version = platform.architecture()[0]
        logger.error(f"The following error occurred while import the VLC package: {e}")
        stdscr.addstr(
            0,
            0,
            "This program requires VLC Media Player to run. Please install "
            "VLC Media Player and launch the program again. If it is already "
            f"installed make sure it is the {bit_version} version of VLC.",
        )
        stdscr.addstr(stdscr.getyx()[0] + 2, 0, "Press any key to exit.")
        stdscr.getch()
        return
    try:
        import vlc

        vlc.Instance()  # best way to test for Linux
    except NameError:
        stdscr.addstr(
            0,
            0,
            "This program requires VLC Media Player to run. Please install "
            "VLC Media Player and launch the program again.",
        )
        stdscr.addstr(stdscr.getyx()[0] + 2, 0, "Press any key to exit.")
        stdscr.getch()
        return
    if not ai_api_key:
        ai_api_key = get_api_keys_from_user(
            stdscr,
            openrouter_api_key=ai_api_key,
        )
    try:
        song_list = get_recommended_song_list(
            stdscr,
            scr_pos=init_scr_pos,
            ai_api_key=ai_api_key,
            url=openrouter_url,
            model=model,
            logger=logger,
        )
    except Exception:
        return
    stdscr.refresh()
    song_list_y, song_list_x = stdscr.getyx()[0] + 2, 0
    song_list_str = f"Songs recommended by AI: "
    for i, song in enumerate(song_list):
        song_list_str = f"{song_list_str}\n\t{i+1}. {song}"
    stdscr.addstr(song_list_y, song_list_x, song_list_str)
    stdscr.refresh()
    all_playlist_folder = "codevibe"
    playlist_folder_prefix = "codevibe_playlist_"
    temp_dir = tempfile.gettempdir()
    codevibe_folder = f"{temp_dir}/{all_playlist_folder}"
    dt_format = "%Y-%m-%d_%H-%M-%S"
    date_now = datetime.now().strftime(dt_format)
    playlist_dir_name = f"{playlist_folder_prefix}{date_now}"
    playlist_folder = f"{codevibe_folder}/{playlist_folder_prefix}{date_now}"
    save_playlist(
        playlist_dir_name=playlist_dir_name,
        playlist_dir=codevibe_folder,
        save_dir=save_playlist_dir,
        stdscr=stdscr,
        scr_pos=(stdscr.getyx()[0] + 2, 0)
    )
    if not os.path.exists(codevibe_folder):
        os.mkdir(codevibe_folder)
    playlist = get_yt_obj_list(song_list=song_list, logger=logger)
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
            "yt_list": playlist,
            "playlist_folder": playlist_folder,
            "playlist": player.playlist,
            "logger": logger,
        },
    ).start()
    player.play_all_songs()
