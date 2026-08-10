import html as html_mod
import json
import re
from typing import Any

from bs4 import BeautifulSoup
from curl_cffi import AsyncSession

from .config import BASE_URL, CHAT_PAGE, RUNNER_URL, TIMEOUT, USER_AGENT

_CSRF_RE = re.compile(r"csrf[_-]token\s*[=:]\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


class ChatClient:
    """Работа с API чата FunPay (получение сообщений через POST /runner/)."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None
        self.csrf_token: str | None = None
        self.tag = "init"
        self.last_message: int | None = 0

    async def __aenter__(self) -> "ChatClient":
        self.session = await AsyncSession(
            impersonate="firefox",
            headers={"User-Agent": USER_AGENT},
        ).__aenter__()
        await self._get_csrf_token()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.session is not None:
            await self.session.__aexit__(exc_type, exc, tb)

    async def _get_csrf_token(self) -> None:
        """Получает csrf_token со страницы чата."""
        if self.session is None:
            raise RuntimeError("Сессия не создана")
        resp = await self.session.get(f"{BASE_URL}{CHAT_PAGE}", timeout=TIMEOUT)
        html = resp.text
        self.csrf_token = None

        soup = BeautifulSoup(html, "lxml")

        meta = soup.find("meta", {"name": "csrf-token"})
        if meta and (content := meta.get("content")):
            self.csrf_token = content

        if not self.csrf_token:
            for tag in soup.find_all(attrs={"data-app-data": True}):
                try:
                    data = json.loads(html_mod.unescape(tag.get("data-app-data", "")))
                except json.JSONDecodeError:
                    continue
                token = data.get("csrf-token") or data.get("csrf_token")
                if token:
                    self.csrf_token = token
                    break

        if not self.csrf_token:
            match = _CSRF_RE.search(html)
            if match:
                self.csrf_token = match.group(1)

        if not self.csrf_token:
            raise RuntimeError("Не удалось получить csrf_token со страницы чата")

    async def poll_messages(self, node: str = "game-41") -> list[dict[str, Any]]:
        """Один запрос к /runner/ для получения новых сообщений ноды.

        Обновляет внутренние tag и last_message для следующего запроса.
        """
        if self.session is None:
            raise RuntimeError("Клиент не инициализирован")
        if not self.csrf_token:
            raise RuntimeError("Отсутствует csrf_token (клиент не инициализирован)")

        objects = [
            {
                "type": "chat_node",
                "id": node,
                "tag": self.tag,
                "data": {
                    "node": node,
                    "last_message": self.last_message,
                    "content": "",
                },
            }
        ]
        data = {
            "objects": json.dumps(objects),
            "request": "false",
            "csrf_token": self.csrf_token,
        }

        resp = await self.session.post(
            f"{BASE_URL}{RUNNER_URL}",
            data=data,
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{BASE_URL}{CHAT_PAGE}?node={node}",
            },
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"/runner/ вернул статус {resp.status_code}: {resp.text[:200]!r}"
            )

        result = resp.json()

        objects = result.get("objects")
        if not isinstance(objects, list) or not objects:
            return []

        obj = objects[0]
        if tag := obj.get("tag"):
            self.tag = tag

        messages = obj["data"].get("messages", [])
        for msg in messages:
            msg_id = msg.get("id")
            if isinstance(msg_id, int) and (
                self.last_message is None or msg_id > self.last_message
            ):
                self.last_message = msg_id

        return messages
