from pytubefix import YouTube


def download_track(url:str, dest:str):
    yt = YouTube(url)
    ys = yt.streams.get_audio_only()
    if not ys:
        raise Exception(f"Error finding audio for {yt.title}")
    ys.download(output_path=dest)
