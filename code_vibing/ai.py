SYS_PROMPT = """You are a helpful assistant who will suggest a list of songs
to be searched on YouTube according to the user's request. If the request isn't
explicit, suggest based on the user's mood. The number of songs in the list is
to be determined from the user's request. If the user has not specified a number,
the list should contain 10 songs. Please make sure the output is in a JSON format.
"""


OPENROUTER_RESPONSE_FORMAT =  {
    "type": "json_object",
    "json_schema": {
        "name": "search_songs_yt",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "song_list": {
                    "type": "array",
                    "items": {
                            "type": "string"
                        },
                    "description": "A list of songs to be searched for on YouTube"
                }
            },
            "required": ["song_list"],
            "additionalProperties": False
        }
    }
}
