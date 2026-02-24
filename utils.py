import time
import math

class Colors():
    def __init__(self):
        # Mapeo de nombres del .txt a códigos de terminal
        self.colors_ascii = {
            "red": "\033[91m",
            "crimson": "\u001b[38;5;161m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "gold": "\033[38;5;220m",
            "magenta": "\033[35m",
            "lime": "\033[32m",
            "cyan": "\033[96m",
            "orange": "\033[38;2;255;165;0m",
            "black" : "\033[90m",
            "rainbow": "\033[38;5;201m",
            "purple": "\033[35m",
            "violet": "\033[35m",
            "white": "\033[97m",
            "maroon": "\033[33m",
            "brown": "\033[33m",
            "darkred": "\33[33m",
            "reset": "\033[0m"
        }
        self.rgb = {
            "red": (255, 0, 0),
            "crimson": (220, 20, 60),
            "green": (0, 255, 0),
            "lime": (0, 255, 0),
            "blue": (0, 0, 255),
            "orange": (255, 165, 0),
            "yellow": (255, 255, 0),
            "gold": (255, 215, 0),
            "purple": (128, 0, 128),
            "violet": (128, 0, 128),
            "rainbow": (148, 0, 211),
            "cyan": (0, 255, 255),
            "black": (30, 30, 30),
            "maroon": (150, 75, 0),
            "brown": (150, 75, 0),
            "darkred": (150, 74, 0),
            "white": (255, 255, 255)
        }

    def get_rgb(self, color_name):
        if color_name.lower() == "rainbow":
            # Genera un color que cambia con el tiempo (efecto arcoíris animado)
            t = time.time() * 3  
            r = int(math.sin(t) * 127 + 128)
            g = int(math.sin(t + 2) * 127 + 128)
            b = int(math.sin(t + 4) * 127 + 128)
            return (r, g, b)
        
        return self.rgb_static.get(color_name.lower(), (255, 255, 255))

    def color_text(self, text, color_name):
        if color_name.lower() == "rainbow":
            # Aplicamos un color distinto a cada letra
            rainbow_colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
            colored_text = ""
            for i, char in enumerate(text):
                color = rainbow_colors[i % len(rainbow_colors)]
                colored_text += f"{color}{char}"
            return f"{colored_text}\033[0m"
        
        color_code = self.colors_ascii.get(color_name.lower(), self.colors_ascii["reset"])
        return f"{color_code}{text}{self.colors_ascii['reset']}"
