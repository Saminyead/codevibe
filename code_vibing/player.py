import vlc
import threading
import curses
import time

from pathlib import Path
from typing import Callable


class MusicPlayer:
    def __init__(
        self, playlist: list[str | Path], screen: curses.window, screen_init_pos=(0, 0)
    ):
        self.playlist: list[str | Path] = playlist
        self.index: int = 0
        self.instance: vlc.Instance = vlc.Instance(
            "--quiet", "--no-xlib", "--verbose=0"
        )
        self.player: vlc.MediaPlayer = self.instance.media_player_new()
        self.screen: curses.window = screen
        self.screen_init_pos: tuple[int, int] = screen_init_pos
        self.stop_flag: threading.Event = threading.Event()
        self.next_flag: threading.Event = threading.Event()
        self.prev_flag: threading.Event = threading.Event()
        self.ff_flag: threading.Event = threading.Event()
        self.rew_flag: threading.Event = threading.Event()
        self.playback_cmds: dict[str, Callable] = {
            # player being None initially causing AttributeError
            "p": lambda: (self.player.pause() if self.player else time.sleep(0.5)),
            ">": self.next_flag.set,
            "<": self.prev_flag.set,
            ".": self.ff_flag.set,
            ",": self.rew_flag.set,
        }

    def _get_elapsed_time(self):
        song_len = self.player.get_length()
        song_len_seconds = song_len / 1000
        song_len_min_sec = divmod(song_len_seconds, 60)
        song_len_min_sec_str = f"{int(song_len_min_sec[0])}:{int(song_len_min_sec[1])}"
        current_time = self.player.get_time()
        current_time_seconds = current_time / 1000
        current_time_min_sec = divmod(current_time_seconds, 60)
        current_time_min_sec_str = (
            f"{int(current_time_min_sec[0])}:{int(current_time_min_sec[1])}"
        )
        return f"{current_time_min_sec_str}/{song_len_min_sec_str}"

    def show_elapsed_time(self, scr_pos: tuple[int, int]):
        elapsed_time = self._get_elapsed_time()
        pos_y, pos_x = scr_pos
        self.screen.addstr(pos_y, pos_x, elapsed_time)

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

    def fast_forward(self, seconds=10):
        current_time = self.player.get_time()
        self.player.set_time(current_time + seconds * 1000)
        self.ff_flag.clear()

    def rewind(self, seconds=10):
        current_time = self.player.get_time()
        self.player.set_time(max(0, current_time - seconds * 1000))
        self.rew_flag.clear()

    def print_cmds(self):
        cmds = """Commands:
            p - toggle pause/resume
            > - go to next track
            < - go to previous track
            . - ff by 10 seconds
            , - rewind by 10 seconds
            any number - go that timestamp"""
        pos_y, pos_x = self.screen_init_pos
        self.screen.addstr(pos_y, pos_x, cmds)

    def listen_to_inputs(self):
        while not self.stop_flag.is_set():
            cmd = self.screen.getkey()
            if cmd in self.playback_cmds:
                self.playback_cmds[cmd]()
            else:
                continue

    def monitor_playback(self, elapsed_time_pos:tuple[int, int]):
        while self.player.get_state() != vlc.State.Ended:
            time.sleep(0.2)
            self.show_elapsed_time(scr_pos=elapsed_time_pos)
            self.screen.refresh()
            if self.next_flag.is_set():
                self.next_track()
                return
            if self.prev_flag.is_set():
                self.prev_track()
                return
            if self.ff_flag.is_set():
                self.fast_forward()
                continue
            if self.rew_flag.is_set():
                self.rewind()
                continue
        self.index += 1
    
    def show_now_playing(self, scr_pos: tuple[int, int]):
        curr_track = self.player.get_media()
        curr_track.parse()
        title = curr_track.get_meta(vlc.Meta.Title)
        now_playing_str = f"Now playing: {title}"
        pos_y, pos_x = scr_pos
        self.screen.move(pos_y, pos_x)
        self.screen.clrtoeol()
        self.screen.addstr(pos_y, pos_x, now_playing_str)
        self.screen.refresh()

    def play_current_song(
        self,
        now_playing_scr_pos: tuple[int, int],
        elapsed_time_scr_pos: tuple[int, int],
    ):
        song = self.playlist[self.index]
        media = self.instance.media_new(song)
        self.player.set_media(media)
        self.player.play()
        self.show_now_playing(scr_pos=now_playing_scr_pos)
        self.monitor_playback(elapsed_time_pos=elapsed_time_scr_pos)

    def play_all_songs(self):
        self.print_cmds()
        self.screen.refresh()
        curr_scr_pos = self.screen.getyx()
        now_playing_scr_pos = curr_scr_pos[0] + 1, 0
        elapsed_time_scr_pos = curr_scr_pos[0] + 2, 0        
        threading.Thread(
            target=self.listen_to_inputs,
            daemon=True,
        ).start()
        while self.index < len(self.playlist):
            self.play_current_song(now_playing_scr_pos, elapsed_time_scr_pos)
        self.stop_flag.set()
