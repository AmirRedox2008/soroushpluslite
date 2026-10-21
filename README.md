# 🟣 SoroushLite

**A lightweight Soroush Plus (سروش‌پلاس) Bot API framework written completely from scratch — sync + async, FSM, middleware, commands.**

> 🇮🇷 **مستندات کامل فارسی:** [README_FA.md](README_FA.md) — راهنمای گام‌به‌گام با نمونه‌کدهای آماده

> SoroushLite is not a wrapper around an existing SDK and not a port of
> pyTelegramBotAPI. Every layer — HTTP transport, retry policy, type parsing,
> router, filters, FSM, middleware — is implemented in ~3,400 lines of typed,
> tested Python with only `requests` as the runtime dependency. The method
> surface is **verified against the official Soroush Plus bot documentation**
> (`soroushplus.com` → Developers → Bot platform, `api.splus.ir`).

![CI](https://github.com/AmirRedox2008/soroushlite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-140%20offline-brightgreen)

---

## Why SoroushLite

Soroush Plus ships a Bot API modelled on the Telegram Bot API, but it is
**not identical**: no inline mode, no polls, no payments, no group-admin
moderation methods, different deep links (`splus.ir`), and a command menu API
(`setMyCommands`) that its sibling messengers do not expose. SoroushLite is
built for that reality — every method it exposes is documented by Soroush Plus,
and nothing else is advertised. Methods the upstream docs mark as *coming soon*
(به‌زودی) — `getChat`, `getUserProfilePhotos`, `sendChatAction`,
`getStickerSet`, pin/unpin — are included and clearly annotated.

| | SoroushLite | typical DIY requests code |
|---|---|---|
| Core dependency | `requests` only | copy-pasted handlers |
| Sync **and** async APIs | ✅ shared types/filters | ❌ |
| Programming model | decorators (`@bot.message_handler`) | manual `if` chains |
| FSM (states) | ✅ 3 storages built-in | ❌ roll your own |
| Middleware | ✅ sync + async | ❌ |
| Command menu (`setMyCommands`) | ✅ | ❌ |
| License | MIT | — |
| Code size to read end-to-end | ~3.4k lines | — |

And if you already know pyTelegramBotAPI or have a Telegram bot, the code looks
familiar on purpose — see [Porting a Telegram bot to Soroush Plus](#porting-a-telegram-bot-to-soroush-plus).

## Features

- 🔌 **Full Bot API client** — long polling, webhooks (ports 443/80/88/8443),
  file upload/download (20 MB), automatic retries and Flood Control (429) handling
- 🎯 **Decorator handlers** — `@bot.message_handler`, `@bot.callback_query_handler`,
  `@bot.edited_message_handler`, `@bot.channel_post_handler` and more
- 🧲 **Composable filters** — `commands`, `regexp`, `content_types`, `chat_types`,
  `state`, custom filters
- 🧠 **Built-in FSM** — memory, JSON-file and Redis storages
- 🧱 **Middleware** — chain runs before every handler (logging, anti-flood, bans…)
- 📋 **Command menu** — `setMyCommands` / `getMyCommands` / `deleteMyCommands`
  with `(command, description)` tuples
- 😀 **Stickers** — `sendSticker` (WEBP/TGS/WEBM) and `getStickerSet`
- ⚡ **Async twin** — same API surface, `aiohttp` under the hood
- 🧵 **Threaded dispatch** — one flag (`threaded=True`), handlers run in parallel
- 🛠 **Utilities** — long-message splitting, HTML/Markdown escaping, `splus.ir` deep links
- 🧪 **140 offline tests** — no token, no internet, no mocks leaking into CI
- 📦 **Packaging** — `pyproject.toml`, full type hints, `py.typed`, GitHub Actions CI

## Installation

```bash
pip install soroushlite            # sync only (requests)
pip install "soroushlite[async]"   # + async support (aiohttp)
pip install "soroushlite[redis]"   # + Redis FSM storage

# from source
git clone https://github.com/AmirRedox2008/soroushlite
cd soroushlite && pip install -e .
```

Python 3.10+ required. Optional extras: `aiohttp` (async), `redis` (FSM), `flask`/`fastapi` (webhooks).

## Quick start — first bot in 10 lines

Get a token from **[splus.ir/botfather](https://splus.ir/botfather)** (the BotFather
inside Soroush Plus), then:

```python
from soroushlite import Bot

bot = Bot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message, "سلام! من یک ربات سروش‌پلاسم 🤖")

bot.infinity_polling()
```

Run it: `python examples/echo_bot.py`

## Handlers & filters

```python
@bot.message_handler(commands=["help"])                 # /help, /help@mybot
@bot.message_handler(func=lambda m: "👋" in (m.text or ""))
def hi(message): ...

@bot.message_handler(regexp=r"^\d+$", chat_types=["private"])   # digits only, DMs only
def digits(message): ...

@bot.callback_query_handler(regexp=r"^page:")           # inline keyboard presses
def pager(call):
    bot.answer_callback_query(call.id, text=f"{call.data}")
```

Content types: `text`, `audio`, `document`, `animation`, `photo`, `sticker`,
`video`, `video_note`, `voice`, `location`, `contact`, `new_chat_members`,
`left_chat_member`, `new_chat_title`, `pinned_message` — or `["all"]`.

## Inline keyboards & callbacks

```python
from soroushlite import InlineKeyboardButton, InlineKeyboardMarkup

menu = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Buy ☕️", callback_data="buy:coffee"),
    InlineKeyboardButton("Site 🌐", url="https://example.com"),
)
bot.send_message(chat_id, "Choose:", reply_markup=menu)
```

Inline buttons support `text` + `url` / `callback_data` — exactly the set the
official docs define (no web-app or login-url buttons).

## Command menu — a Soroush speciality

```python
bot.set_my_commands([                       # tuples, dicts or BotCommand objects
    ("start", "Start the bot"),
    ("help", "How to use"),
])
bot.get_my_commands()       # -> [BotCommand(command="start", ...)]
bot.delete_my_commands()
```

## FSM — multi-step forms

```python
from soroushlite import StateGroup

class Form(StateGroup):
    name, age = State(), State()

@bot.message_handler(commands=["form"])
def ask_name(message):
    bot.set_state(message.from_user.id, Form.name, message.chat.id)
    bot.reply_to(message, "اسمت چیه؟")

@bot.message_handler(state=Form.name)
def ask_age(message):
    bot.update_state_data(message.from_user.id, message.chat.id, name=message.text)
    bot.set_state(message.from_user.id, Form.age, message.chat.id)
    bot.reply_to(message, "چند سالته؟")

@bot.message_handler(state=Form.age)
def done(message):
    data = bot.get_state_data(message.from_user.id, message.chat.id)
    bot.reset_state(message.from_user.id, message.chat.id)
    bot.reply_to(message, f"خوش اومدی {data['name']} عزیز!")
```

Full Persian registration form: [`examples/fsm_bot.py`](examples/fsm_bot.py).

## Middleware & error handling

```python
@bot.register_middleware(update_types=["message"])
def anti_flood(message, next_):
    if is_spammer(message.from_user.id):
        return                    # drop — handler never runs
    next_()

@bot.exception_handler
def on_error(payload, exception):
    logging.exception("Handler crashed: %s", exception)
```

Errors: `SoroushError` → `NetworkError`, `ApiHTTPError`, `ApiSoroushError`
(`InvalidTokenError`, `BotBlockedError`, `RateLimitError` with `retry_after`).

## Files

```python
# four accepted media inputs: file_id, HTTPS URL, file-like object, path
bot.send_photo(chat_id, "PHOTO-FILE-ID")
bot.send_document(chat_id, open("report.pdf", "rb"))

file = bot.get_file(message.document.file_id)          # 20 MB limit
data = bot.download_file(file)                          # bytes
```

## Async bot — same surface

```python
from soroushlite import AsyncBot

bot = AsyncBot("YOUR-BOT-TOKEN")

@bot.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id, "async! ⚡️")

bot.polling()   # or: asyncio.run(bot.infinity_polling())
```

## Webhooks

Soroush Plus accepts webhooks on ports **443, 80, 88 and 8443**; put
Flask/FastAPI behind a reverse proxy:

```python
bot.set_webhook("https://example.com/webhook")

@app.route("/webhook", methods=["POST"])
def webhook():
    bot.process_webhook_update(request.get_json(force=True))
    return "ok", 200
```

## Porting a Telegram bot to Soroush Plus

| Telegram habit | Soroush Plus reality | SoroushLite |
|---|---|---|
| `api.telegram.org` | `api.splus.ir` | handled for you |
| `t.me/bot?start=x` links | `splus.ir/bot?start=x` | `create_deep_link()` |
| BotFather | [splus.ir/botfather](https://splus.ir/botfather) | — |
| inline mode (`@bot query`) | ❌ not supported | not exposed |
| polls, dice, venue, web-app buttons | ❌ not documented | not exposed |
| payments (`sendInvoice`) | ❌ not documented (Bale has it, Soroush doesn't) | not exposed |
| group admin (`banChatMember`, invites…) | ❌ not documented | not exposed |
| `setMyCommands` menu | ✅ documented & live | ✅ |
| `getChat` / profile photos / `sendChatAction` / `getStickerSet` / pin | documented as *coming soon* (به‌زودی) | ✅ annotated |
| webhook ports 443, 80, 88, 8443 | all four accepted | documented |

The rule: **if it's in SoroushLite, it's in Soroush Plus's docs.** That makes
porting a matter of changing the import and the token.

## Utility helpers

```python
from soroushlite import create_deep_link, escape_html, split_text

create_deep_link("mybot", "ref42")   # https://splus.ir/mybot?start=ref42
```

## Running the tests

```bash
pip install -e ".[dev]"
python -m pytest -q     # 139 passed, 1 skipped (optional redis) — fully offline
```

## Project structure

```
soroushlite/
├── src/soroushlite/
│   ├── api_client.py     # HTTP transport, retries, 429 handling
│   ├── bot.py            # sync Bot: 50+ methods, FSM, middleware, polling
│   ├── async_bot.py      # AsyncBot: same surface on aiohttp
│   ├── handlers.py       # router, filters, decorators
│   ├── fsm.py            # StateGroup + 3 storages
│   ├── middleware.py     # sync/async chains
│   ├── polling.py        # blocking & infinity loops
│   ├── types.py          # Update/Message/keyboards/BotCommand…
│   ├── utils.py          # splitting, escaping, deep links
│   └── exceptions.py     # SoroushError hierarchy
├── examples/             # echo, async, FSM, keyboards, middleware, commands, webhook
├── tests/                # 140 offline tests
└── .github/workflows/    # CI: 3.10 → 3.13
```

## The messenger trilogy

SoroushLite is the third member of a from-scratch framework family:

- [GramLite](https://github.com/AmirRedox2008/gramlite) — Telegram
- [BaleLite](https://github.com/AmirRedox2008/balelite) — Bale
- **SoroushLite** — Soroush Plus (this repo)

Same architecture, three APIs — each one verified against its official docs.

## License

MIT — see [LICENSE](LICENSE). Built as a from-scratch demonstration that a
framework's core is smaller than it looks.
