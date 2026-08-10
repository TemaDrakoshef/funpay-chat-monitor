import logging

from rich.logging import RichHandler


def setup_logger(name: str = "funpay_chat_monitor") -> logging.Logger:
    """Возвращает настроенный логгер с выводом через rich."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_path=False,
            markup=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
