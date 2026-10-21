"""The synchronous :class:`Bot` — the main entry point of SoroushLite.

The class groups the Soroush Bot API methods by theme (updates, messaging,
media, commands, files) and always returns parsed :mod:`soroushlite.types`
objects instead of raw dicts. Media helpers accept a file_id string, a public
URL, a file-like object or a filesystem path — mirroring the convenience users
know from pyTelegramBotAPI.

Extras: FSM states (:mod:`soroushlite.fsm`), middleware
(:mod:`soroushlite.middleware`), a global exception handler, threaded dispatch,
long-message auto-splitting and file downloads.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Union

from .api_client import APIClient
from .types import (
    BotCommand,
    Chat,
    File,
    Message,
    MessageId,
    SoroushObject,
    Sticker,
    Update,
    User,
    WebhookInfo,
)
from .utils import split_text
from .fsm import BaseStorage, MemoryStorage, State, state_full_name
from .handlers import HandlerRegistry, HandlerRegistrationMixin
from .middleware import MiddlewareManager
from .polling import run_infinity_polling, run_polling

logger = logging.getLogger("soroushlite")

__all__ = ["Bot"]


class Bot(HandlerRegistrationMixin):
    """A synchronous Soroush bot.

    Example::

        from soroushlite import Bot

        bot = Bot("TOKEN")

        @bot.message_handler(commands=["start"])
        def welcome(message):
            bot.reply_to(message, "Hello!")

        bot.infinity_polling()
    """

    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        client: Optional[APIClient] = None,
        threaded: bool = False,
        num_workers: int = 8,
        storage: Optional[BaseStorage] = None,
        parse_mode: Optional[str] = None,
        bot_username: Optional[str] = None,
    ) -> None:
        self.client = client or APIClient(
            token=token, base_url=base_url, timeout=timeout, max_retries=max_retries
        )
        self.router = HandlerRegistry()
        self.router.bot_username = bot_username
        self.middleware = MiddlewareManager()
        self.router.middleware = self.middleware
        self.storage: BaseStorage = storage or MemoryStorage()
        self.parse_mode = parse_mode
        self.threaded = threaded
        self._executor = (
            ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix="soroushlite")
            if threaded
            else None
        )
        self._stop_event = threading.Event()
        self._user: Optional[User] = None
        self._username_fetched = False

    # ------------------------------------------------------------- lifecycle
    @property
    def token(self) -> str:
        return self.client.token

    @property
    def user(self) -> Optional[User]:
        """The bot's own identity (``getMe``), fetched once and cached."""
        if self._user is None:
            self._user = self.get_me()
        return self._user

    @property
    def username(self) -> Optional[str]:
        """The bot's @username (without the @), or None when unavailable."""
        user = self._user
        return getattr(user, "username", None) if user is not None else None

    def stop_polling(self) -> None:
        """Signal the running polling loop to stop (takes effect within one
        long-poll cycle)."""
        self._stop_event.set()

    def close(self) -> None:
        """Stop polling and release worker threads."""
        self.stop_polling()
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = None

    def __enter__(self) -> "Bot":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    # ==================================================================
    # Updates
    # ==================================================================
    def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = 0,
        allowed_updates: Optional[Iterable[str]] = None,
    ) -> List[Update]:
        """Fetch pending updates via long polling (``timeout`` in seconds)."""
        params: Dict[str, Any] = {"offset": offset, "limit": limit, "timeout": timeout}
        if allowed_updates is not None:
            params["allowed_updates"] = json.dumps(list(allowed_updates))
        result = self.client.request("getUpdates", params)
        return Update.de_list(result)  # type: ignore[return-value]

    def set_webhook(
        self,
        url: str,
        drop_pending_updates: Optional[bool] = None,
        allowed_updates: Optional[Iterable[str]] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
    ) -> bool:
        """Register an HTTPS webhook. Soroush Plus only accepts ports
        **443, 80, 88** and **8443**."""
        params: Dict[str, Any] = {
            "url": url,
            "drop_pending_updates": drop_pending_updates,
            "ip_address": ip_address,
            "max_connections": max_connections,
        }
        if allowed_updates is not None:
            params["allowed_updates"] = json.dumps(list(allowed_updates))
        return self.client.request("setWebhook", params)

    def delete_webhook(self, drop_pending_updates: Optional[bool] = None) -> bool:
        return self.client.request("deleteWebhook", {"drop_pending_updates": drop_pending_updates})

    def get_webhook_info(self) -> WebhookInfo:
        return WebhookInfo.de_json(self.client.request("getWebhookInfo"))  # type: ignore[return-value]

    # ==================================================================
    # Profile & chat info
    # ==================================================================
    def get_me(self) -> User:
        return User.de_json(self.client.request("getMe"))  # type: ignore[return-value]

    def get_chat(self, chat_id: Union[int, str]) -> Chat:
        """Up-to-date info about a chat.

        .. note:: The official Soroush docs mark ``getChat`` as *coming soon*
            (به‌زودی) — the endpoint exists but may not be enabled for all
            tokens yet.
        """
        return Chat.de_json(self.client.request("getChat", {"chat_id": chat_id}))  # type: ignore[return-value]

    def get_user_profile_photos(self, user_id: int, offset: Optional[int] = None, limit: Optional[int] = None) -> SoroushObject:
        """A user's profile photos (documented upstream as *coming soon*)."""
        params: Dict[str, Any] = {"user_id": user_id, "offset": offset, "limit": limit}
        return SoroushObject.de_json(self.client.request("getUserProfilePhotos", params))

    # ==================================================================
    # Commands
    # ==================================================================
    def set_my_commands(self, commands) -> bool:
        """Publish the bot's command menu (max 100 commands).

        Accepts a list of :class:`~soroushlite.types.BotCommand`,
        ``(command, description)`` tuples or dicts.
        """
        payload = json.dumps(BotCommand.de_list(commands))
        return self.client.request("setMyCommands", {"commands": payload})

    def get_my_commands(self, language_code: Optional[str] = None) -> List[BotCommand]:
        """The current command menu for the bot."""
        result = self.client.request("getMyCommands", {"language_code": language_code})
        return [
            BotCommand.de_json(item) if isinstance(item, dict) else item
            for item in (result or [])
        ]

    def delete_my_commands(self, language_code: Optional[str] = None) -> bool:
        """Remove the bot's command menu for the given language."""
        return self.client.request("deleteMyCommands", {"language_code": language_code})

    # ==================================================================
    # Messaging
    # ==================================================================
    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[List[dict]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Message:
        return Message.de_json(self.client.request("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode or self.parse_mode,
            "entities": entities,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "protect_content": protect_content,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }))  # type: ignore[return-value]

    def reply_to(self, message: Message, text: str, **kwargs: Any) -> Message:
        """Shortcut: send a reply inside the same chat as ``message``."""
        return self.send_message(
            message.chat.id, text, reply_to_message_id=message.message_id, **kwargs
        )

    def send_long_message(
        self, chat_id: Union[int, str], text: str, **kwargs: Any
    ) -> List[Message]:
        """Send a text of any length — automatically split at 4096 chars."""
        return [
            self.send_message(chat_id, chunk, **kwargs)
            for chunk in split_text(text)
        ]

    def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Union[Message, bool]:
        result = self.client.request("editMessageText", {
            "text": text,
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "parse_mode": parse_mode or self.parse_mode,
            "reply_markup": reply_markup,
        })
        return True if result is True else Message.de_json(result)  # type: ignore[return-value]

    def edit_message_caption(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Union[Message, bool]:
        result = self.client.request("editMessageCaption", {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "caption": caption,
            "parse_mode": parse_mode or self.parse_mode,
            "reply_markup": reply_markup,
        })
        return True if result is True else Message.de_json(result)  # type: ignore[return-value]

    def edit_message_reply_markup(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Union[Message, bool]:
        result = self.client.request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "reply_markup": reply_markup,
        })
        return True if result is True else Message.de_json(result)  # type: ignore[return-value]

    def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        return self.client.request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
    ) -> MessageId:
        return MessageId.de_json(self.client.request("forwardMessage", {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
            "protect_content": protect_content,
        }))  # type: ignore[return-value]

    def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> MessageId:
        return MessageId.de_json(self.client.request("copyMessage", {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": parse_mode or self.parse_mode,
            "disable_notification": disable_notification,
            "protect_content": protect_content,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }))  # type: ignore[return-value]

    def send_chat_action(self, chat_id: Union[int, str], action: str) -> bool:
        """Show a status (``typing``, ``upload_photo``, ``record_video``, ...)."""
        return self.client.request("sendChatAction", {"chat_id": chat_id, "action": action})

    def pin_chat_message(
        self, chat_id: Union[int, str], message_id: int,
        disable_notification: Optional[bool] = None,
    ) -> bool:
        return self.client.request("pinChatMessage", {
            "chat_id": chat_id, "message_id": message_id,
            "disable_notification": disable_notification,
        })

    def unpin_chat_message(
        self, chat_id: Union[int, str], message_id: Optional[int] = None
    ) -> bool:
        """Remove a message from the pinned list (documented upstream as *coming soon*)."""
        return self.client.request("unpinChatMessage", {
            "chat_id": chat_id, "message_id": message_id,
        })

    # ==================================================================
    # Media — one shared implementation, thin wrappers
    # ==================================================================
    def send_photo(self, chat_id, photo, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("photo", "sendPhoto", chat_id, photo, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def send_sticker(self, chat_id, sticker, **kwargs: Any) -> Message:
        """Send a static WEBP, animated TGS or video WEBM sticker."""
        return self._send_media("sticker", "sendSticker", chat_id, sticker, **kwargs)

    def send_video(self, chat_id, video, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("video", "sendVideo", chat_id, video, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def send_audio(self, chat_id, audio, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("audio", "sendAudio", chat_id, audio, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def send_voice(self, chat_id, voice, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("voice", "sendVoice", chat_id, voice, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def send_document(self, chat_id, document, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("document", "sendDocument", chat_id, document, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def send_animation(self, chat_id, animation, caption=None, parse_mode=None, **kwargs: Any) -> Message:
        return self._send_media("animation", "sendAnimation", chat_id, animation, caption=caption,
                                parse_mode=parse_mode, **kwargs)

    def _send_media(
        self,
        kind: str,
        method: str,
        chat_id: Union[int, str],
        media: Any,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Message:
        params: Dict[str, Any] = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode or self.parse_mode,
            "disable_notification": disable_notification,
            "protect_content": protect_content,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }
        files = None
        opened = None
        try:
            if isinstance(media, str):
                # file_id or public URL — the API accepts both as strings.
                params[kind] = media
            elif hasattr(media, "read"):
                name = os.path.basename(getattr(media, "name", "") or "upload")
                files = {kind: (name, media)}
            else:  # treat as filesystem path
                opened = open(str(media), "rb")
                files = {kind: (os.path.basename(str(media)), opened)}
            result = self.client.request(method, params, files=files)
        finally:
            if opened is not None:
                opened.close()
        return Message.de_json(result)  # type: ignore[return-value]

    def send_media_group(
        self,
        chat_id: Union[int, str],
        media: Sequence[SoroushObject],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> List[Message]:
        """Send an album of 2-10 photos/videos (``InputMediaPhoto/Video`` with
        file_id or URL media)."""
        result = self.client.request("sendMediaGroup", {
            "chat_id": chat_id,
            "media": [item.to_dict() for item in media],
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
        })
        return Message.de_list(result)  # type: ignore[return-value]

    # ==================================================================
    # Location and contact
    # ==================================================================
    def send_location(
        self,
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Message:
        return Message.de_json(self.client.request("sendLocation", {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }))  # type: ignore[return-value]

    def send_contact(
        self,
        chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        reply_markup: Optional[SoroushObject] = None,
    ) -> Message:
        return Message.de_json(self.client.request("sendContact", {
            "chat_id": chat_id, "phone_number": phone_number,
            "first_name": first_name, "last_name": last_name,
            "reply_markup": reply_markup,
        }))  # type: ignore[return-value]

    # ==================================================================
    # Callbacks
    # ==================================================================
    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> bool:
        """Answer a callback query from an inline keyboard button.

        ``text`` shows a notification (or an alert when ``show_alert=True``).
        """
        return self.client.request("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
            "url": url,
            "cache_time": cache_time,
        })

    # ==================================================================
    # Files
    # ==================================================================
    def get_file(self, file_id: str) -> File:
        return File.de_json(self.client.request("getFile", {"file_id": file_id}))  # type: ignore[return-value]

    def download_file_url(self, file_or_path: Union[File, str]) -> str:
        """Build the direct download URL for a :class:`File` (or raw ``file_path``)."""
        file_path = getattr(file_or_path, "file_path", None) or str(file_or_path)
        return self.client.file_download_url(file_path)

    def download_file(self, file_or_path: Union[File, str], timeout: Optional[float] = None) -> bytes:
        """Download a file's content as ``bytes`` (``getFile`` + fetch)."""
        file_path = getattr(file_or_path, "file_path", None) or str(file_or_path)
        return self.client.get_bytes(self.download_file_url(file_path), timeout=timeout)

    # ==================================================================
    # Stickers
    # ==================================================================
    def get_sticker_set(self, name: str) -> SoroushObject:
        """A sticker set by ``name`` (documented upstream as *coming soon*).

        Returned as a dynamic :class:`~soroushlite.types.SoroushObject` with
        ``name``, ``title`` and a ``stickers`` list of
        :class:`~soroushlite.types.Sticker`.
        """
        data = self.client.request("getStickerSet", {"name": name})
        obj = SoroushObject.de_json(data)
        if obj is not None and getattr(obj, "stickers", None):
            obj.stickers = Sticker.de_list(obj.stickers)
        return obj

    # ==================================================================
    # FSM (finite-state machine)
    # ==================================================================
    def set_state(self, user_id: int, state: Union[State, str, None], chat_id: int = 0) -> None:
        """Put a user into a state (``None`` clears it)."""
        self.storage.set_state(user_id, chat_id, state_full_name(state))

    def get_state(self, user_id: int, chat_id: int = 0) -> Optional[str]:
        """The user's current canonical state string, or None."""
        return self.storage.get_state(user_id, chat_id)

    def reset_state(self, user_id: int, chat_id: int = 0) -> None:
        self.storage.reset_state(user_id, chat_id)

    def get_state_data(self, user_id: int, chat_id: int = 0) -> Dict[str, Any]:
        return self.storage.get_data(user_id, chat_id)

    def update_state_data(self, user_id: int, chat_id: int = 0, **data: Any) -> Dict[str, Any]:
        """Merge ``data`` into the stored state data; returns the full dict."""
        return self.storage.update_data(user_id, chat_id, **data)

    def clear_state_data(self, user_id: int, chat_id: int = 0) -> None:
        self.storage.clear(user_id, chat_id)

    # ==================================================================
    # Middleware & error handling
    # ==================================================================
    def register_middleware(
        self, update_types: Optional[Sequence[str]] = None
    ) -> Callable[[Any], Any]:
        """Decorator: run a function around every dispatch (see
        :mod:`soroushlite.middleware`)::

            @bot.register_middleware(update_types=["message"])
            def logger(message, next_):
                next_()
        """
        manager = self.middleware

        def decorator(fn: Any) -> Any:
            return manager.register(fn, update_types)

        return decorator

    def exception_handler(
        self, fn: Any
    ) -> Any:
        """Decorator: catch every exception raised by handlers/middleware::

            @bot.exception_handler
            def on_error(payload, exception):
                logging.exception("Unhandled error")
        """
        self.router.exception_handler = fn
        return fn

    # ==================================================================
    # Update intake — polling and webhooks
    # ==================================================================
    def _dispatch_update(self, update: Update) -> None:
        self._ensure_bot_username()
        if self._executor is not None:
            self._executor.submit(self.router.process_update, update)
        else:
            self.router.process_update(update)

    def _ensure_bot_username(self) -> None:
        """Lazily learn the bot's username (for ``/cmd@bot`` matching) — only
        when at least one command handler is registered, and only once."""
        if self.router.bot_username is not None or self._username_fetched:
            return
        self._username_fetched = True
        if any(h.commands for h in self.router._handlers["message"]):
            self.router.bot_username = self.username  # best-effort; None on failure

    def process_new_updates(self, updates: Iterable[Union[Update, dict]]) -> int:
        """Feed updates (already fetched, e.g. from a webhook request) to the router."""
        count = 0
        for update in updates:
            if isinstance(update, dict):
                update = Update.de_json(update)
            self._dispatch_update(update)
            count += 1
        return count

    def process_webhook_update(self, update: Union[Update, dict]) -> None:
        """Process exactly one webhook payload — the Flask/FastAPI seam."""
        self.process_new_updates([update])

    def polling(
        self,
        interval: float = 0,
        long_polling_timeout: int = 10,
        allowed_updates: Optional[Iterable[str]] = None,
        skip_pending: bool = False,
    ) -> None:
        """Blocking long-polling loop. Stops on KeyboardInterrupt or
        :meth:`stop_polling`."""
        run_polling(
            self, self.router,
            interval=interval,
            long_polling_timeout=long_polling_timeout,
            allowed_updates=allowed_updates,
            skip_pending=skip_pending,
            stop_event=self._stop_event,
            dispatch=self._dispatch_update,
        )

    def infinity_polling(
        self,
        interval: float = 0,
        long_polling_timeout: int = 10,
        allowed_updates: Optional[Iterable[str]] = None,
        skip_pending: bool = False,
        max_backoff: float = 60.0,
    ) -> None:
        """Polling that survives crashes — restarts with exponential back-off."""
        run_infinity_polling(
            self, self.router,
            interval=interval,
            long_polling_timeout=long_polling_timeout,
            allowed_updates=allowed_updates,
            skip_pending=skip_pending,
            max_backoff=max_backoff,
            stop_event=self._stop_event,
            dispatch=self._dispatch_update,
        )
