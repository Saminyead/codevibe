import vlc
import threading
import time

from pathlib import Path
from typing import Callable


class MusicPlayer:
    def __init__(self, playlist: list[str | Path]):
        self.playlist: list[str | Path] = playlist
        self.index: int = 0
        self.player: vlc.MediaPlayer | None = None
        self.stop_flag: threading.Event = threading.Event()
        self.next_flag: threading.Event = threading.Event()
        self.prev_flag: threading.Event = threading.Event()
        self.playback_cmds: dict[str, Callable] = {
            # player being None initially causing AttributeError
            "p": lambda: (
                self.player.pause() if self.player else print("Player not ready.")
            ),
            ">": self.next_flag.set,
            "<": self.prev_flag.set,
        }

    def next_track(self):
        self.player.stop()
        # modulus to implement circular selection
        self.index = (self.index + 1) % len(self.playlist)
        self.next_flag.clear()

    def prev_track(self):
        self.player.stop()
        # modulus to implement circular selection
        self.index = (self.index - 1) % len(self.playlist)
        self.prev_flag.clear()

    def listen_to_inputs(self):
        while not self.stop_flag.is_set():
            cmd = input(
                """Commands:
                    p - toggle pause/resume
                    > - go to next track
                    < - go to previous track
                    any number - go that timestamp
                Enter any command:
                """
            )
            cmd = cmd.lower().strip()
            if cmd.isdigit():
                jump_time = int(cmd)
                self.player.set_time(jump_time * 1000)
            elif cmd in self.playback_cmds:
                self.playback_cmds[cmd]()
            else:
                continue

    def monitor_playback(self):
        while self.player.get_state() != vlc.State.Ended:
            time.sleep(0.2)
            if self.next_flag.is_set():
                self.next_track()
                return
            if self.prev_flag.is_set():
                self.prev_track()
                return
        self.index += 1

    def play_current_song(self):
        song = self.playlist[self.index]
        self.player = vlc.MediaPlayer(song)
        self.player.play()
        self.monitor_playback()

    def play_all_songs(self):
        threading.Thread(
            target=self.listen_to_inputs,
            daemon=True,
        ).start()
        while self.index < len(self.playlist):
            self.play_current_song()
        self.stop_flag.set()
