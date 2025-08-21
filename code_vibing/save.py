import shutil
import curses

import os

from pathlib import Path

def save_playlist(
    playlist_dir_name: str | Path,
    playlist_dir: str | Path,
    save_dir:str | Path,
    stdscr: curses.window,
    scr_pos: tuple[int, int]
):
    stdscr.addstr(
        scr_pos[0],
        scr_pos[1],
        "Do you want to save this playlist? Press y to save, n to cancel. "
    )
    key = stdscr.getkey()
    if key not in ("y", "Y"):
        return
    save_playlist_dir = f"{save_dir}/{playlist_dir_name}"
    if os.path.exists(f"{save_playlist_dir}"):
        stdscr.addstr(
            scr_pos[0] + 2,
            scr_pos[1],
            "The playlist already exists. Do you want to overwrite it, or save "
            "to a new directory? Press y to overwrite, n to save it to a new "
            "directory, or any other key to cancel."
        )
    key = stdscr.getkey()
    if key not in ("y", "Y", "n", "N"):
        return
    elif key in ("n", "N"):
        save_playlist_dir = f"{save_playlist_dir}_1"
    shutil.copytree(src=playlist_dir, dst=save_playlist_dir)
