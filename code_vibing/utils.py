from pytubefix import YouTube
import os
from datetime import datetime

import requests

from pathlib import Path

def download_track(url:str, dest:str):
    yt = YouTube(url)
    ys = yt.streams.get_audio_only()
    if not ys:
        raise Exception(f"Error finding audio for {yt.title}")
    ys.download(output_path=dest)


def find_latest_playlist(playlist_path:str|Path, dt_format:str):
    playlists = os.listdir(playlist_path)
    pl_dt_dict = {p:datetime.strptime(p,dt_format) for p in playlists}
    return max(pl_dt_dict)

def search_song_yt(query:str, api_key:str):
    url = "https://www.googleapis.com/youtube/v3/playlists"
    params = {"key":api_key, "part":"snippet", "q":query}
    res = requests.get(url=url, params=params)
    return res.json()['items'][0]['id']['videoId']
