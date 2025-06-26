from player import MusicPlayer

import os


def main():
    music_folder = input(
        f"Please enter the full/relative path of the music folder. The current path is - {os.getcwd()}: "
    )
    songs = os.listdir(music_folder)
    song_files = [f"{music_folder}/{song}" for song in songs]
    player = MusicPlayer(playlist=song_files)
    player.play_all_songs()


if __name__ == "__main__":
    main()
