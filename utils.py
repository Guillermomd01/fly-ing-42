

class Colors():
    def __init__(self):
        # Mapeo de nombres del .txt a códigos de terminal
        self.colors_ascii = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "orange": "\033[33m",
            "black" : "\033[90m",
            "purple": "\033[35m",
            "white": "\033[97m",
            "reset": "\033[0m"
        }
        self.rgb = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "orange": (255, 165, 0),
            "yellow": (255, 255, 0),
            "purple": (128, 0, 128),
            "cyan": (0, 255, 255),
            "black": (30, 30, 30),
            "white": (255, 255, 255)
        }

    def color_text(self, text, color_name):
        color_code = self.colors_ascii.get(color_name.lower(), self.colors_ascii["reset"])
        return f"{color_code}{text}{self.colors_ascii['reset']}"
