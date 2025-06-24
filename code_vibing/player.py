import vlc
import threading

from pathlib import Path


def listen_to_inputs(player: vlc.MediaPlayer, stop_flag: threading.Event):
    while not stop_flag.is_set():
        cmd = input(
            "Enter p to toggle pause/resume, enter a number to jump to that timestamp: "
        )
        try:
            jump_time = int(cmd)
            player.set_time(jump_time * 1000)
        except ValueError:
            if cmd.lower() == "p":
                player.pause()
            else:
                continue


def playback_loop(song_i: int, playlist: list[str|Path]):
    song = playlist[song_i]
    player = vlc.MediaPlayer(song)
    player.play()
    stop_flag = threading.Event()
    input_thread = threading.Thread(
        target=listen_to_inputs,
        args=(
            player,
            stop_flag,
        ),
        daemon=True,
    )
    input_thread.start()
    while player.get_state() != vlc.State.Ended:
        continue
    stop_flag.set()
