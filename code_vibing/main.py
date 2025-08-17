import curses

import os
from dotenv import load_dotenv

import toml

from app import app
from utils import setup_logging
import functools


MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

LOGGER = setup_logging("app.log", "./logs")

load_dotenv()
OPENROUTER_API_KEY = os.getenv("openrouter_api_key")


def main():
    with open("config.toml", "r") as fp:
        config_str = fp.read()
    config = toml.loads(config_str)
    model = config['ai']['model'] if config['ai']['model'] else MODEL
    app_def_args = functools.partial(
        app,
        model=model,
        openrouter_url=OPENROUTER_URL,
        ai_api_key=OPENROUTER_API_KEY,
        logger=LOGGER,
    )
    curses.wrapper(app_def_args)


if __name__ == "__main__":
    main()
