# Changelog

All notable changes to **SoroushLite** are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-19

First public release: a from-scratch Soroush Plus Bot API framework built on
the same architecture as GramLite (Telegram) and BaleLite (Bale).

### Added
- **Sync `Bot` + async `AsyncBot`** with full surface parity; the async stack
  (`aiohttp`) is an optional extra imported lazily (PEP 562).
- **Verified method surface** — every wrapper maps to an endpoint documented at
  `soroushplus.com` (Bot platform docs, `api.splus.ir`): messaging, 11 media
  senders, edits, forward/copy, callback queries, files, stickers, pins and
  the command menu (`setMyCommands`/`getMyCommands`/`deleteMyCommands`).
- **Handler system** — decorator registration, first-match-wins routing,
  5 documented update kinds (`message`, `edited_message`, `channel_post`,
  `edited_channel_post`, `callback_query`), composable filters
  (`commands`, `regexp`, `content_types`, `chat_types`, `func`,
  custom `BaseFilter`, FSM `state`).
- **FSM** — `State`/`StateGroup`, `MemoryStorage`, atomic `JSONFileStorage`,
  optional `RedisStorage`; `(user_id, chat_id)` keyed.
- **Middleware** (sync + async chains) and a global exception handler.
- **HTTP client** — retry on 429/5xx honouring `retry_after`, exponential
  back-off, typed error hierarchy (`InvalidTokenError`, `BotBlockedError`,
  `RateLimitError`).
- **Files** — 4 media input forms (file_id / URL / file-like / path),
  `getFile` + download via `https://api.splus.ir/file/bot<token>/<file_path>`.
- **Webhooks** — ports 443/80/88/8443 documented; Flask/FastAPI seam via
  `process_webhook_update`.
- **Utilities** — `send_long_message`/`split_text`, `escape_html`,
  `escape_markdown`, `create_deep_link` (`splus.ir`).
- 7 runnable examples, 140 offline tests (139 passed + 1 optional-Redis skip),
  CI matrix Python 3.10–3.13, full type hints with `py.typed`.
- English (`README.md`) and complete Persian (`README_FA.md`) documentation,
  plus `ARCHITECTURE.md` design-decision records.

### Not included (deliberately)
Endpoints absent from the official Soroush Plus documentation are not
exposed: inline mode, polls, dice, venues, payments (`sendInvoice`),
group-admin moderation (`banChatMember`…), invite links and web-app buttons.
Endpoints the docs mark as *coming soon* (به‌زودی) — `getChat`,
`getUserProfilePhotos`, `sendChatAction`, `getStickerSet`, pin/unpin — are
wrapped and annotated.
