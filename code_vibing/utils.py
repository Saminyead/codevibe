from pytubefix import YouTube
import os
from datetime import datetime

import requests

import logging

from pathlib import Path


def download_track(
    url: str, dest: str, playlist: list[str], max_retries: int = 3
):
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

def setup_logging(log_file: str | Path) -> logging.RootLogger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file,encoding="utf=8"),
        ]
    )
    return logging
