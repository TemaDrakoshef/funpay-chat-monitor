from typing import Any

from bs4 import BeautifulSoup


def parse_message(html: str) -> dict[str, Any]:
    """Извлекает имя автора, дату и текст сообщения из HTML."""
    soup = BeautifulSoup(html, "lxml")

    author_tag = soup.find("a", class_="chat-msg-author-link")
    author = author_tag.get_text(strip=True) if author_tag else "Unknown"

    date_tag = soup.find("div", class_="chat-msg-date")
    date = date_tag.get("title", "") if date_tag else ""
    time = date_tag.get_text(strip=True) if date_tag else ""

    text_tag = soup.find("div", class_="chat-msg-text")
    text = text_tag.get_text(strip=True) if text_tag else ""

    message_id = parse_message_id(soup)

    return {
        "author": author,
        "date": date,
        "time": time,
        "text": text,
        "message_id": message_id,
    }


def parse_message_id(soup: BeautifulSoup) -> int | None:
    """Извлекает числовой id сообщения из атрибута id корневого элемента."""
    item = soup.find("div", class_="chat-msg-item")
    if not item:
        return None
    raw = item.get("id", "")
    if not raw.startswith("message-"):
        return None
    try:
        return int(raw.split("-", 1)[1])
    except (ValueError, IndexError):
        return None
