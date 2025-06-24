import vlc
import threading

from pathlib import Path

class MusicPlayer:
    def __init__(self, playlist:list[str|Path]):
        self.playlist = playlist
        self.index = 0
        self.stop_flag = threading.Event()
        self.player: vlc.MediaPlayer|None = None


    def listen_to_inputs(self):
        while not self.stop_flag.is_set():
            cmd = input(
                "Enter p to toggle pause/resume, enter a number to jump to that timestamp: "
            )
            try:
                jump_time = int(cmd)
                self.player.set_time(jump_time * 1000)
            except ValueError:
                if cmd.lower() == "p":
                    self.player.pause()
                else:
                    continue


    def playback_loop(self):
        song = self.playlist[self.index]
        self.player = vlc.MediaPlayer(song)
        self.player.play()
        while self.player.get_state() != vlc.State.Ended:
            continue

    def play_all_songs(self):
        threading.Thread(
            target=self.listen_to_inputs,
            daemon=True,
        ).start()
        for i in range(len(self.playlist)):
            self.index = i
            self.playback_loop()
        self.stop_flag.set()
