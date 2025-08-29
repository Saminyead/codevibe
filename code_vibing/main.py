import curses

import os
from dotenv import load_dotenv

from app import app
from utils import setup_logging, read_toml_ok
import functools

CONFIG_FILE = "config.toml"

MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SAVE_PLAYLIST_DIR = f"{os.path.expanduser('~')}/codevibe"

LOGGER = setup_logging("app.log", "./logs")

load_dotenv()
OPENROUTER_API_KEY = os.getenv("openrouter_api_key")


def main():
    config = read_toml_ok(config_path=CONFIG_FILE)
    if config:
        try:
            model = config["ai"]["model"]
            save_dir = config["directories"]["save_dir"]
        except KeyError:
            model = MODEL
            save_dir = SAVE_PLAYLIST_DIR
    else:
        model = MODEL
        save_dir = SAVE_PLAYLIST_DIR
    if not model:
        model = MODEL
    if not save_dir:
            save_dir = SAVE_PLAYLIST_DIR
    if not os.path.exists(save_dir):
         os.mkdir(save_dir)
    app_def_args = functools.partial(
        app,
        model=model,
        save_all_playlist_dir=save_dir,
        openrouter_url=OPENROUTER_URL,
        ai_api_key=OPENROUTER_API_KEY,
        logger=LOGGER,
    )
    curses.wrapper(app_def_args)


if __name__ == "__main__":
    main()
