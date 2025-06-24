import vlc
import threading

from pathlib import Path

class MusicPlayer:
    def __init__(self, playlist:list[str|Path]):
        self.playlist:list[str|Path] = playlist
        self.index:int = 0
        self.stop_flag:threading.Event = threading.Event()
        self.player: vlc.MediaPlayer|None = None

    
    def next_track(self):
        # modulus to implement circular selection
        self.index = (self.index + 1) % len(self.playlist)


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
                elif cmd.lower() == "n":
                    self.next_track()
                else:
                    continue


    def playback_loop(self):
        song = self.playlist[self.index]
        self.player = vlc.MediaPlayer(song)
        self.player.play()
        while self.player.get_state() != vlc.State.Ended:
            continue
        self.index += 1

    def play_all_songs(self):
        threading.Thread(
            target=self.listen_to_inputs,
            daemon=True,
        ).start()
        while self.index < len(self.playlist):
            self.playback_loop()
        self.stop_flag.set()
