from player import playback_loop

import os


def main():
    music_folder = "./music"
    songs = os.listdir(music_folder)
    song_files = [f"{music_folder}/{song}" for song in songs]
    for song_file in song_files:
        playback_loop(song_file)


if __name__ == "__main__":
    main()
