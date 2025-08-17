from exceptions import AiFormatError

import requests
import json

from logging import RootLogger


def sys_prompt(n_songs: int = 5):
    return (
        "You are a helpful assistant who will suggest a list of songs to be "
        "searched on YouTube according to the user's request. If the request isn't "
        f"explicit, suggest based on the user's mood. Please suggest {n_songs} songs. "
        "Please make sure the output adheres strictly to the specified JSON format."
    )


SYS_PROMPT = """You are a helpful assistant who will suggest a list of songs
to be searched on YouTube according to the user's request. If the request isn't
explicit, suggest based on the user's mood. The number of songs in the list is
to be determined from the user's request.Please make sure the output is in a 
JSON format.
"""


OPENROUTER_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "search_songs_yt",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "song_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of songs to be searched for on YouTube",
                }
            },
            "required": ["song_list"],
            "additionalProperties": False,
        },
    },
}


def get_ai_song_list(
    user_input: str,
    api_key: str,
    url: str,
    model: str,
    logger: RootLogger,
    n_songs: int = 5,
    sys_prompt: str = SYS_PROMPT,
    res_format: dict = OPENROUTER_RESPONSE_FORMAT,
    n_attempts: int = 3,
) -> list[str]:
    for attempt in range(n_attempts):  # retry only for AiFormatError
        res = requests.post(
            url=url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {
                        "role": "user",
                        "content": f"{user_input} Please suggest {n_songs}.",
                    },
                ],
                "response_format": res_format,
            },
        )
        logger.info(f"Response from AI:\n{res.content.decode()}")
        ai_res = res.json()["choices"][0]["message"]["content"]
        ai_res_dict = json.loads(ai_res)
        song_list = ai_res_dict["song_list"]
        if not type(song_list[0]) is str:
            logger.warning(
                f"Attempt {attempt + 1} failed for getting AI song list due to AiFormatError"
            )
            continue
        return song_list
    logger.error("Max retries exceeded for getting AI song list due to AiFormatError.")
    raise AiFormatError


def get_ai_song_list_retry(
    user_input: str,
    api_key: str,
    url: str,
    model: str,
    logger: RootLogger,
    n_songs: int = 5,
):
    try:
        return get_ai_song_list(
            user_input=user_input,
            api_key=api_key,
            url=url,
            model=model,
            logger=logger,
            n_songs=n_songs
        )
    except Exception as e:
        logger.error(f"Exception occurred with the AI: {e}")
        raise
