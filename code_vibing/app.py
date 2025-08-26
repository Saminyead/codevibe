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

from pathlib import Path

VLC_INSTALLED = False
PLATFORM_ARCH = None

# -- I hate having to do all of the below, but this is the best way I found
# to import the VLC package, and make sure there are no errors because of the
# way VLC python package works. UGH!
# Windows throws error during the very import of vlc Python package
# if VLC is not installed
try:
    from player import MusicPlayer
    VLC_INSTALLED = True
except Exception as e:
    import platform
    PLATFORM_ARCH = platform.architecture()[0]
    print(
        "This program requires VLC Media Player to run. Please install "
        "VLC Media Player and launch the program again. If it is already "
        f"installed make sure it is the {PLATFORM_ARCH} version of VLC.",
    )
    input("Press Enter to exit")
    raise

# sometimes plugin path not properly detected in Linux
if sys.platform == "linux":
    check_vlc_plugin_path = subprocess.check_output(
        ["find", "/usr/lib", "-type", "d", "-name", "plugins", "-path", "*/vlc/*"],
        text=True,
    )
    plugin_path = check_vlc_plugin_path.strip()
    os.environ["VLC_PLUGIN_PATH"] = plugin_path
try:
    import vlc
    vlc.Instance()  # best way to test for Linux
    VLC_INSTALLED = True
except NameError:
    print(
        "This program requires VLC Media Player to run. Please install "
        "VLC Media Player and launch the program again.",
    )
    input("Press Enter to exit")
    raise


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


def get_new_playlist(
    stdscr:curses.window,
    init_scr_pos:tuple[int,int],
    ai_api_key:str,
    openrouter_url:str,
    model:str,
    player:MusicPlayer,
    save_all_playlist_dir:str | Path,
    logger:RootLogger
) -> int | None:
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
    stdscr.addstr(
        stdscr.getyx()[0] + 2,
        0,
        "Do you want to save this playlist? Press y to save, n to cancel. ",
    )
    stdscr.refresh()
    to_save = False
    to_save_key = stdscr.getkey()
    if to_save_key in ("y", "Y"):
        to_save = True
    all_playlist_folder = "codevibe"
    playlist_folder_prefix = "codevibe_playlist_"
    temp_dir = tempfile.gettempdir()
    codevibe_folder = f"{temp_dir}/{all_playlist_folder}"
    dt_format = "%Y-%m-%d_%H-%M-%S"
    date_now = datetime.now().strftime(dt_format)
    playlist_dir_name = f"{playlist_folder_prefix}{date_now}"
    playlist_folder = f"{codevibe_folder}/{playlist_dir_name}"
    if not os.path.exists(codevibe_folder):
        os.mkdir(codevibe_folder)
    playlist = get_yt_obj_list(song_list=song_list, logger=logger)
    os.mkdir(playlist_folder)
    threading.Thread(
        target=download_tracks_all,
        kwargs={
            "yt_list": playlist,
            "playlist_folder": playlist_folder,
            "playlist": player.playlist,
            "logger": logger,
            "to_save": to_save,
            "save_all_playlist_dir": save_all_playlist_dir,
            "save_playlist_name": playlist_dir_name
        },
    ).start()
    return len(playlist) 


def get_saved_playlist(
    stdscr: curses.window,
    scr_pos: tuple[int, int],
    save_dir: str | Path
) -> list[str] | None:
    stdscr.addstr(
        scr_pos[0],
        scr_pos[1],
        "Saved playlists found. Do you want to play from the existing "
        "playlists? Press y to select from the existing playlists, or "
        "press n to make a new playlist."
    )
    key = stdscr.getkey()
    if key not in ("y", "Y"):
        stdscr.clrtobot()
        stdscr.refresh()
        return
    stdscr.addstr(
        stdscr.getyx()[0] + 2,
        0,
        "Press the number of the corresponding playlist to select the playlist."
    )
    playlist_list = [
        os.path.join(save_dir,playlist) for playlist in os.listdir(save_dir)
    ]
    playlist_list_str = ""
    for i, playlist in enumerate(playlist_list):
        playlist_list_str = f"{playlist_list_str}{i+1}. {playlist}\n"
    stdscr.addstr(
        stdscr.getyx()[0] + 2,
        0,
        playlist_list_str
    )
    playlist_index = None
    next_scr_pos = stdscr.getyx()[0] + 2, 0
    while not playlist_index:
        stdscr.move(next_scr_pos[0], next_scr_pos[1])
        playlist_index_str = stdscr.getkey()
        stdscr.clrtoeol()
        if not playlist_index_str.isdigit():
            stdscr.addstr("You have not pressed a number. Try again.")
            stdscr.refresh()
            continue
        playlist_index = int(playlist_index_str) - 1
        if playlist_index not in range(0, len(playlist_list)):
            stdscr.addstr(
                "The number you entered does not match any playlist. Try again."
            )
            playlist_index = None
            stdscr.refresh()
            continue
    selected_playlist_folder = playlist_list[playlist_index]
    selected_playlist = [
        os.path.join(selected_playlist_folder, song) for song in 
        os.listdir(selected_playlist_folder)
    ]
    stdscr.clrtobot()
    stdscr.refresh()
    return selected_playlist


def app(
    stdscr: curses.window,
    ai_api_key: str | None,
    openrouter_url: str,
    model: str,
    save_all_playlist_dir: str | Path,
    logger: RootLogger,
    init_scr_pos: tuple[int, int] = (0, 0),
):
    if not ai_api_key:
        ai_api_key = get_api_keys_from_user(
            stdscr,
            openrouter_api_key=ai_api_key,
        )
    selected_playlist = None
    if os.listdir(save_all_playlist_dir):
        selected_playlist = get_saved_playlist(
            stdscr=stdscr, 
            scr_pos=(stdscr.getyx()[0] + 2, 0),
            save_dir=save_all_playlist_dir
        )
    player = MusicPlayer(
        screen=stdscr
    )
    if not selected_playlist:
        expected_len = get_new_playlist(
            stdscr=stdscr,
            ai_api_key=ai_api_key,
            init_scr_pos=init_scr_pos,
            logger=logger,
            model=model,
            openrouter_url=openrouter_url,
            save_all_playlist_dir=save_all_playlist_dir,
            player=player
        )
    else:
        expected_len = len(selected_playlist)
        player.playlist = selected_playlist
    if not expected_len:
        return
    player_init_pos = stdscr.getyx()[0] + 3, 0
    player.screen_init_pos = player_init_pos
    player.expected_len = expected_len
    player.play_all_songs()
