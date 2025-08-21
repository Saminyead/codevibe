from pytubefix import YouTube, Search
from pytubefix.exceptions import PytubeFixError
import os
from datetime import datetime

import logging

from pathlib import Path

import toml


def download_track(yt: YouTube, dest: str, playlist: list[str], max_retries: int = 3):
    ys = yt.streams.get_audio_only()
    if not ys:
        raise Exception(f"Error finding audio for {yt.title}")
    song_path = ys.download(output_path=dest, max_retries=max_retries)
    if song_path:
        playlist.append(song_path)


def find_latest_playlist(playlist_path: str | Path, dt_format: str):
    playlists = os.listdir(playlist_path)
    pl_dt_dict = {p: datetime.strptime(p, dt_format) for p in playlists}
    return max(pl_dt_dict)


def search_song_yt(query: str) -> YouTube:
    results = Search(query)
    for result in results.all:
        if not result.watch_url:
            continue
        return result


def setup_logging(
    log_file: str | Path, log_dir: str | Path = "./logs"
) -> logging.RootLogger:
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    file_path = f"{log_dir}/{log_file}"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(file_path, encoding="utf=8"),
        ],
    )
    return logging


def get_yt_obj_list(song_list: list[str], logger: logging.RootLogger):
    yt_obj_list = []
    for song in song_list:
        try:
            yt_obj = search_song_yt(query=song)
            yt_obj_list.append(yt_obj)
        except Exception as e:
            logger.error(
                f"Could not download track for {song}, due to the following error:\n{e}"
            )
            continue
    return yt_obj_list


def download_tracks_all(
    yt_list: list[YouTube],
    playlist_folder: str,
    playlist: list[str],
    logger: logging.RootLogger,
):
    for yt in yt_list:
        try:
            download_track(yt=yt, dest=playlist_folder, playlist=playlist)
        except PytubeFixError:
            logger.error(f"Error downloading track for url {yt.watch_url}")
            continue


def read_toml_ok(config_path: str | Path) -> dict | None:
    """Checks if the toml file is okay. If okay, then returns the toml 
    contents as dict."""
    if not os.path.exists(config_path):
        return
    with open(config_path, "r") as fp:
        config_str = fp.read()
    try:
        return toml.loads(config_str)
    except (toml.decoder.TomlDecodeError):
        return


def get_ai_model(config_path: str | Path, default_model: str):
    config = read_toml_ok(config_path=config_path)
    if not config:
        return default_model
    try:
        model = config["ai"]["model"] if config["ai"]["model"] else default_model
    except (KeyError):
        model = default_model
    return model
