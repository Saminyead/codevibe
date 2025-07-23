class AiFormatError(Exception):
    def __init__(self):
        super().__init__("Wrong response format from AI.")
