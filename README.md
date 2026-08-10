# funpay-chat

Мониторинг чата FunPay через неофициальный API.

## Возможности

- Асинхронный опрос чата FunPay через `curl_cffi.AsyncSession`.
- Автоматическое получение `csrf_token` со страницы чата.
- У каждого пользователя свой цвет.
- Отслеживание новых сообщений по `last_message` и динамическому `tag`.

## Установка

```bash
uv sync
```

## Запуск

```bash
uv run python main.py                               # чат game-41, интервал 2 c
uv run python main.py --node game-41 --interval 1   # другой интервал и чат
```

Список нод чата (примеры): `game-41`, `game-20`
`https://funpay.com/chat/?node=<node>`.

## Структура проекта

```
src/
├── config.py       # конфигурация (URL, задержки, User-Agent)
├── chat_client.py  # клиент API чата (csrf_token, POST /runner/)
├── parser.py       # парсинг HTML сообщений (автор, дата, текст)
├── formatting.py   # цвета пользователей и форматирование вывода
├── logo.py         # логотип и вотермарка
├── logger.py       # настройка логирования (rich)
├── main.py         # точка входа + асинхронный цикл мониторинга
└── __main__.py     # запуск через python -m src
```
