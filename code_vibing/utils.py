from pytubefix import YouTube
from pytubefix.exceptions import PytubeFixError
import os
from datetime import datetime

import requests

import logging

from pathlib import Path


def download_track(url: str, dest: str, playlist: list[str], max_retries: int = 3):
    yt = YouTube(url)
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


def search_song_yt(query: str, api_key: str) -> str:
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"key": api_key, "part": "snippet", "q": query}
    res = requests.get(url=url, params=params)
    search_items = res.json()["items"]
    for item in search_items:
        try:
            return item["id"]["videoId"]
        except KeyError:
            continue
    raise KeyError


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


def get_yt_url_list(song_list: list[str], yt_api_key: str, logger: logging.RootLogger):
    video_url_list = []
    for song in song_list:
        try:
            video_id = search_song_yt(query=song, api_key=yt_api_key)
            video_url_list.append(f"https://www.youtube.com/watch?v={video_id}")
        except Exception as e:
            logger.error(
                f"Could not download track for {song}, due to the following error:\n{e}"
            )
            continue
    return video_url_list


def download_tracks_all(
    url_list: list[str],
    playlist_folder: str,
    playlist: list[str],
    logger: logging.RootLogger,
):
    for url in url_list:
        try:
            download_track(url=url, dest=playlist_folder, playlist=playlist)
        except PytubeFixError:
            logger.error(f"Error downloading track for url {url}")
            continue
