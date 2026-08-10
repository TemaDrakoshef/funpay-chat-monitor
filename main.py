import argparse
import asyncio

from rich.console import Console

from src.chat_client import ChatClient
from src.config import DEFAULT_NODE, POLL_INTERVAL
from src.formatting import UserPalette, build_message_lines
from src.logger import setup_logger
from src.parser import parse_message

console = Console()
log = setup_logger()
palette = UserPalette()

logo = r"""
  _____            ____                    ____ _           _   
 |  ___|   _ _ __ |  _ \ __ _ _   _       / ___| |__   __ _| |_ 
 | |_ | | | | '_ \| |_) / _` | | | |_____| |   | '_ \ / _` | __|
 |  _|| |_| | | | |  __/ (_| | |_| |_____| |___| | | | (_| | |_ 
 |_|   \__,_|_| |_|_|   \__,_|\__, |      \____|_| |_|\__,_|\__|
                               |___/                             
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Мониторинг чата FunPay")
    parser.add_argument(
        "--node",
        default=DEFAULT_NODE,
        help=f"Нода чата (по умолчанию: {DEFAULT_NODE})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=POLL_INTERVAL,
        help="Интервал опроса в секундах",
    )
    return parser


async def _run(node: str, interval: float) -> None:
    console.print(f"[green]Запуск мониторинга чата [bold]{node}[/bold]...[/green]")
    async with ChatClient() as client:
        while True:
            try:
                messages = await client.poll_messages(node)
                for msg in messages:
                    parsed = parse_message(msg["html"])
                    author = (
                        parsed["author"]
                        if parsed["author"] != "Unknown"
                        else str(msg.get("author", "Unknown"))
                    )
                    color = palette.color(author)
                    for line in build_message_lines(author, parsed["text"], color):
                        console.print(line)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                console.print(f"[red]Ошибка: {exc}[/red]")
                log.error("Ошибка в цикле мониторинга: %s", exc)
                await asyncio.sleep(interval * 2)


def show_banner() -> None:
    """Очищает консоль и выводит по центру логотип и вотермарку."""
    console.clear()
    lines = [line.rstrip() for line in logo.strip("\n").splitlines()]
    max_width = max(len(line) for line in lines)
    left_pad = max(0, (console.width - max_width) // 2)
    for line in lines:
        console.print(" " * left_pad + line, style="bold bright_cyan", highlight=False)
    console.print()
    console.print(
        "Разработал - t.me/drakoshef_dev",
        justify="center",
        style="bold yellow",
        highlight=False,
    )
    console.print()


def main() -> None:
    args = _build_parser().parse_args()
    show_banner()
    try:
        asyncio.run(_run(args.node, args.interval))
    except KeyboardInterrupt:
        console.print("\n[red]Мониторинг остановлен.[/red]")


if __name__ == "__main__":
    main()
