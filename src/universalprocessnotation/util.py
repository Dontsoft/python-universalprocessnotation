from typing import Tuple, List

CHARWIDTH_LUT = {' ': 5, '!': 5, '"': 6, '#': 9, '$': 9, '%': 15, '&': 11, "'": 4, '(': 6, ')': 6, '*': 7, '+': 10, ',': 5, '-': 6, '.': 5, '/': 5, '0': 9, '1': 8, '2': 9, '3': 9, '4': 9, '5': 9, '6': 9, '7': 9, '8': 9, '9': 9, ':': 5, ';': 5, '<': 10, '=': 10, '>': 10, '?': 9, '@': 17, 'A': 11, 'B': 11, 'C': 12, 'D': 12, 'E': 11, 'F': 10, 'G': 13, 'H': 12, 'I': 5, 'J': 8, 'K': 11, 'L': 9, 'M': 14, 'N': 12,
                 'O': 13, 'P': 11, 'Q': 13, 'R': 12, 'S': 11, 'T': 10, 'U': 12, 'V': 11, 'W': 16, 'X': 11, 'Y': 11, 'Z': 10, '[': 5, '\\': 5, ']': 5, '^': 8, '_': 9, '`': 6, 'a': 9, 'b': 9, 'c': 8, 'd': 9, 'e': 9, 'f': 5, 'g': 9, 'h': 9, 'i': 4, 'j': 4, 'k': 8, 'l': 4, 'm': 14, 'n': 9, 'o': 9, 'p': 9, 'q': 9, 'r': 6, 's': 8, 't': 5, 'u': 9, 'v': 8, 'w': 12, 'x': 8, 'y': 8, 'z': 8, '{': 6, '|': 5, '}': 6, '~': 10}
CHARWIDTH_DEFAULT = 9
CHARHEIGHT = 17
MIN_WIDTH = 200
MIN_LINK_TEXT_WIDTH = 64
STROKE_WIDTH = 4
INNER_STROKE_WIDTH = 2
MAIN_COLOR = "#3D348B"
WHO_COLOR = "#44BBA4"
WITH_WHAT_COLOR = "#3F88C5"
ATTACHMENT_COLOR = "#666666"
RX = 8

Y_PADDING = 32
X_PADDING = 16
INNER_PADDING = 4
LINE_HEIGHT = 24
ATTACHMENT_SIZE = LINE_HEIGHT


def text_width(text: str) -> int:
    _width = 0
    for c in text:
        _width = _width + \
            (CHARWIDTH_LUT[c]
                if c in CHARWIDTH_LUT else CHARWIDTH_DEFAULT)
    return _width

def fit_text_to_width(text: str, width: int) -> List[str]:
    current_word = ""
    lines = []
    for word in text.split(" "):
        new_word = current_word + " " + word
        if text_width(new_word) > width:
            lines.append(current_word)
            current_word = word
        else:
            current_word = new_word
    if len(current_word) > 0:
        lines.append(current_word)
    return lines
