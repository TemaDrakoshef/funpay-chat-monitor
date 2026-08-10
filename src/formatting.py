from rich.text import Text

COLOR_PALETTE: list[str] = [
    "bright_cyan",
    "bright_green",
    "bright_magenta",
    "bright_yellow",
    "bright_red",
    "bright_blue",
    "spring_green1",
    "orange1",
    "hot_pink",
    "deep_sky_blue1",
    "violet",
    "salmon1",
]


class UserPalette:
    """Стабильное присваивание каждому пользователю своего цвета."""

    def __init__(self, palette: list[str] | None = None) -> None:
        self._palette = list(palette) if palette else list(COLOR_PALETTE)
        self._colors: dict[str, str] = {}

    def color(self, author: str) -> str:
        """Возвращает цвет для автора, назначая новый при первом обращении."""
        color = self._colors.get(author)
        if color is None:
            color = self._palette[len(self._colors) % len(self._palette)]
            self._colors[author] = color
        return color

    @property
    def mapping(self) -> dict[str, str]:
        """Текущее соответствие автор -> цвет."""
        return dict(self._colors)


def build_message_lines(author: str, text: str, color: str) -> list[Text]:
    """Строит rich-строки сообщения.

    Если в тексте нет переносов — выводится одна строка:
        "Автор: текст"

    Если текст содержит '\n' — автор выводится отдельной строкой,
    а текст начинается со следующей строки:
        "Автор:"
        "первая строка текста"
        "вторая строка текста"
    """
    if "\n" in text:
        lines = [Text(f"{author}:", style=f"bold {color}")]
        lines.extend(Text(line) if line else Text("") for line in text.split("\n"))
        return lines

    line = Text()
    line.append(f"{author}: ", style=f"bold {color}")
    line.append(text)
    return [line]
