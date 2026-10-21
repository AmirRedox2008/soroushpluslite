# 📚 سروش‌لایت (SoroushLite) — مستندات کامل فارسی

**فریم‌ورک سبک و حرفه‌ای برای API بات سروش‌پلاس — کاملاً از صفر، با پشتیبانی همزمان و غیرهمزمان، FSM، میان‌افزار و منوی دستورها.**

> نسخه انگلیسی: [README.md](README.md) — English documentation
>
> دو پروژه خواهر همین خانواده:
> [GramLite](https://github.com/AmirRedox2008/gramlite) برای تلگرام و
> [BaleLite](https://github.com/AmirRedox2008/balelite) برای بله.

SoroushLite هیچ wrapper آماده‌ای دور خودش ندارد؛ تمام لایه‌ها — ترنسپورت HTTP،
سیاست تلاش مجدد، پارس تایپ‌ها، روتر، فیلترها، FSM و میان‌افزار — در حدود
۳,۴۰۰ خط پایتون تایپ‌دار و تست‌شده از صفر نوشته شده‌اند. تنها وابستگی زمان اجرا
`requests` است. سطح متدهای کتابخونه با **مستندات رسمی بات سروش‌پلاس**
(soroushplus.com ← توسعه‌دهندگان ← Bot platform) تطبیق داده شده است.

---

## 📖 فهرست مطالب

1. [ویژگی‌ها](#-ویژگی‌ها)
2. [تفاوت‌های سروش‌پلاس با تلگرام](#-تفاوت‌های-سروش‌پلاس-با-تلگرام)
3. [نصب](#-نصب)
4. [دریافت توکن از BotFather سروش](#-دریافت-توکن-از-botfather-سروش)
5. [شروع سریع](#-شروع-سریع)
6. [هندلرها و فیلترها](#-هندلرها-و-فیلترها)
7. [کیبوردها](#️-کیبوردها)
8. [منوی دستورها (ویژه سروش)](#-منوی-دستورها-ویژه-سروش)
9. [ماشین حالت (FSM)](#-ماشین-حالت-fsm)
10. [میان‌افزار (Middleware)](#-میان‌افزار-middleware)
11. [مدیریت خطاها](#-مدیریت-خطاها)
12. [کار با فایل‌ها](#-کار-با-فایل‌ها)
13. [پیام‌های طولانی و ابزارهای کمکی](#-پیام‌های-طولانی-و-ابزارهای-کمکی)
14. [بات غیرهمزمان (Async)](#-بات-غیرهمزمان-async)
15. [وب‌هوک](#-وب‌هوک)
16. [مرجع کامل متدها](#-مرجع-کامل-متدها)
17. [پیکربندی پیشرفته](#️-پیکربندی-پیشرفته)
18. [اجرای تست‌ها](#-اجرای-تست‌ها)
19. [ساختار پروژه](#-ساختار-پروژه)
20. [نکات گیت‌هاب و رزومه](#-نکات-گیت‌هاب-و-رزومه)

---

## ✨ ویژگی‌ها

- 🔌 **کلاینت کامل Bot API** — long polling، وب‌هوک (پورت‌های ۴۴۳/۸۰/۸۸/۸۴۴۳)،
  آپلود/دانلود فایل (تا ۲۰ مگابایت)، تلاش مجدد خودکار و مدیریت Flood Control (429)
- 🎯 **هندلرهای دکوریتیو** — `@bot.message_handler`، `@bot.callback_query_handler`،
  `@bot.edited_message_handler`، `@bot.channel_post_handler` و...
- 🧲 **فیلترهای ترکیب‌پذیر** — `commands`، `regexp`، `content_types`، `chat_types`،
  `state`، فیلتر سفارشی
- 🧠 **ماشین حالت داخلی (FSM)** — سه نوع ذخیره‌ساز: حافظه، فایل JSON و Redis
- 🧱 **میان‌افزار** — زنجیره‌ای که قبل از هر هندلر اجرا می‌شود (لاگ، ضداسپم، بن...)
- 📋 **منوی دستورها** — `setMyCommands` / `getMyCommands` / `deleteMyCommands`
- 😀 **استیکر** — `sendSticker` (WEBP/TGS/WEBM) و `getStickerSet`
- ⚡ **دوقلوی غیرهمزمان** — همان سطح API با `aiohttp` زیر کاپوت
- 🧵 **ارسال ترِدی‌شده** — فقط یک فلگ (`threaded=True`)؛ هندلرها موازی اجرا می‌شوند
- 🛠 **ابزارهای کمکی** — تقسیم پیام بلند، escape کردن HTML/Markdown، دیپ‌لینک `splus.ir`
- 🧪 **۱۴۰ تست آفلاین** — بدون توکن، بدون اینترنت
- 📦 **بسته‌بندی استاندارد** — `pyproject.toml`، type hint کامل، `py.typed`، CI گیت‌هاب

## 🆚 تفاوت‌های سروش‌پلاس با تلگرام

API بات سروش‌پلاس از روی Telegram Bot API ساخته شده ولی **کپی کامل نیست**.
SoroushLite دقیقاً برای همین واقعیت طراحی شده: هر متدی که ارائه می‌دهد در
مستندات رسمی سروش‌پلاس آمده و چیزی بیرون از مستندات تبلیغ نمی‌شود.

| عادت تلگرامی | واقعیت سروش‌پلاس | رفتار SoroushLite |
|---|---|---|
| `api.telegram.org` | `api.splus.ir` | خودکار مدیریت می‌شود |
| لینک `t.me/bot?start=x` | `splus.ir/bot?start=x` | `create_deep_link()` |
| BotFather | [splus.ir/botfather](https://splus.ir/botfather) | — |
| حالت inline (`@bot query`) | ❌ پشتیبانی نمی‌شود | expose نشده |
| نظرسنجی، تاس، venue، دکمه web-app | ❌ در مستندات نیست | expose نشده |
| پرداخت (`sendInvoice`) | ❌ در مستندات نیست (بله دارد، سروش ندارد) | expose نشده |
| مدیریت گروه (`banChatMember`، لینک دعوت...) | ❌ در مستندات نیست | expose نشده |
| منوی `setMyCommands` | ✅ مستند و فعال | ✅ کامل |
| `getChat`، عکس پروفایل، `sendChatAction`، `getStickerSet`، pin | مستند ولی «به‌زودی» | ✅ با توضیح ارائه شده |
| پورت‌های وب‌هوک | ۴۴۳، ۸۰، ۸۸، ۸۴۴۳ | مستند و پشتیبانی‌شده |

قاعده طلایی: **هر چیزی که در SoroushLite هست، در مستندات سروش‌پلاس هم هست.**
به همین دلیل پورت کردن بات از تلگرام فقط تغییر import و توکن است.

## 📦 نصب

```bash
pip install soroushlite            # فقط sync (نیازمند requests)
pip install "soroushlite[async]"   # + پشتیبانی async (aiohttp)
pip install "soroushlite[redis]"   # + ذخیره‌ساز Redis برای FSM

# از سورس
git clone https://github.com/AmirRedox2008/soroushlite
cd soroushlite && pip install -e .
```

پایتون ۳.۱۰ به بالا لازم است. وابستگی‌های اختیاری: `aiohttp` (async)،
`redis` (FSM)، `flask` یا `fastapi` (وب‌هوک).

## 🎫 دریافت توکن از BotFather سروش

1. در سروش‌پلاس به آدرس **[splus.ir/botfather](https://splus.ir/botfather)** بروید.
2. دستور ساخت بات جدید را بزنید و نام و نام‌کاربری انتخاب کنید.
3. توکن به شکل `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` به شما داده می‌شود.
4. توکن را مثل رمز عبور مخفی نگه دارید — آن را در کد public نگذارید.

تمام درخواست‌ها به شکل `https://api.splus.ir/bot<token>/METHOD` ارسال می‌شوند؛
این آدرس‌دهی در SoroushLite به‌طور خودکار انجام می‌شود.

## 🚀 شروع سریع

```python
from soroushlite import Bot

bot = Bot("توکن-بات-شما")

@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message, "سلام! من یک ربات سروش‌پلاسم 🤖")

@bot.message_handler(func=lambda m: m.text and "سلام" in m.text)
def greeting(message):
    bot.send_message(message.chat.id, f"سلام {message.from_user.first_name} جان!")

bot.infinity_polling()
```

اجرا: `python examples/echo_bot.py`

وقتی بات اجراست، هر پیامی که کاربر می‌فرستد به‌صورت `Update` دریافت و به
مناسب‌ترین هندلر (اولین تطبیق) تحویل داده می‌شود.

## 🎯 هندلرها و فیلترها

```python
# دستورها — /help و /help@mybot هر دو می‌آیند
@bot.message_handler(commands=["help"])
def help_cmd(message): ...

# عبارت باقاعده — فقط پیام‌های عددی در چت خصوصی
@bot.message_handler(regexp=r"^\d+$", chat_types=["private"])
def digits(message): ...

# دکمه‌های شیشه‌ای — فشار callback با regexp روی data
@bot.callback_query_handler(regexp=r"^page:")
def pager(call):
    bot.answer_callback_query(call.id, text=f"صفحه {call.data}")

# پیام‌های ویرایش‌شده
@bot.edited_message_handler()
def edited(message): ...

# پست‌های کانال (و ویرایششان)
@bot.channel_post_handler()
def post(message): ...

@bot.edited_channel_post_handler()
def edited_post(message): ...

# فیلتر تابعی — ترکیب هر شرط دلخواه
@bot.message_handler(func=lambda m: m.text and len(m.text) > 100)
def long_text(message): ...
```

انواع محتوا برای `content_types`: `text`، `audio`، `document`، `animation`،
`photo`، `sticker`، `video`، `video_note`، `voice`، `location`، `contact`،
`new_chat_members`، `left_chat_member`، `new_chat_title`، `pinned_message`
— یا `["all"]` برای همه.

چند نکته مهم:

- هندلرها **اولین تطبیق برنده است**؛ ترتیب ثبت اهمیت دارد.
- `message.from_user` همان فیلد `from` است (چون `from` کیورد پایتون است).
- `message.content_type` یک رشته انسانی مثل `"text"` یا `"photo"` می‌دهد.
- `message.is_command` و `message.extract_command()` برای کار با دستورها.

## ⌨️ کیبوردها

```python
from soroushlite import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, ForceReply,
)

# کیبورد شیشه‌ای — callback_data یا url
menu = InlineKeyboardMarkup(row_width=2)
menu.add(
    InlineKeyboardButton("خرید ☕️", callback_data="buy:1"),
    InlineKeyboardButton("سایت 🌐", url="https://example.com"),
)
bot.send_message(chat_id, "انتخاب کن:", reply_markup=menu)

# کیبورد معمولی — دکمه می‌تواند متن بفرستد یا شماره/لوکیشن بگیرد
kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(KeyboardButton("ارسال شماره", request_contact=True))
kb.add(KeyboardButton("ارسال لوکیشن", request_location=True))
bot.send_message(chat_id, "یکی را انتخاب کن:", reply_markup=kb)

# حذف کیبورد یا اجبار به ریپلای
bot.send_message(chat_id, "تمام!", reply_markup=ReplyKeyboardRemove())
bot.send_message(chat_id, "جواب بده:", reply_markup=ForceReply())
```

دکمه‌های شیشه‌ای در سروش‌پلاس فقط `text` به‌علاوه `url` یا `callback_data` دارند
(دقیقاً همان مجموعه‌ای که مستندات رسمی تعریف کرده؛ دکمه web-app یا login وجود ندارد).

## 📋 منوی دستورها (ویژه سروش)

برخلاف بله، سروش‌پلاس منوی دستورها (`setMyCommands`) دارد — کاربر با زدن `/`
منوی بات را می‌بیند:

```python
# تاپل، دیکشنری یا آبجکت BotCommand — هر سه قبول است
bot.set_my_commands([
    ("start", "شروع کار با بات"),
    ("help", "راهنما"),
    ("about", "درباره ما"),
])

commands = bot.get_my_commands()      # -> [BotCommand(command="start", ...), ...]
bot.delete_my_commands()              # حذف منو
```

مثال کامل: [`examples/commands_bot.py`](examples/commands_bot.py).

## 🧠 ماشین حالت (FSM)

برای فرم‌های چندمرحله‌ای نیازی به دیتابیس دستی نیست:

```python
from soroushlite import State, StateGroup

class Form(StateGroup):
    name = State()
    age = State()

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

سه ذخیره‌ساز آماده دارد:

```python
from soroushlite import MemoryStorage, JSONFileStorage, State

# 1) حافظه — پیش‌فرض؛ با ری‌استارت پاک می‌شود
bot = Bot(TOKEN)

# 2) فایل JSON — ماندگار بین ری‌استارت‌ها
from soroushlite import JSONFileStorage
bot = Bot(TOKEN, storage=JSONFileStorage("states.json"))

# 3) Redis — برای استقرار واقعی (نیازمند pip install "soroushlite[redis]")
from soroushlite.fsm import RedisStorage
bot = Bot(TOKEN, storage=RedisStorage(host="localhost", port=6379, db=0))
```

API کامل حالت‌ها: `set_state`، `get_state`، `reset_state`، `get_state_data`،
`update_state_data`، `clear_state_data`. فیلتر `state="*"` هم همه حالت‌ها را
می‌گیرد و `state=None` فقط وقتی کاربر در هیچ حالتی نیست.

## 🧱 میان‌افزار (Middleware)

```python
import time, logging

# لاگ زمان اجرا — قبل از هر هندلر پیام
@bot.register_middleware(update_types=["message"])
def logger(message, next_):
    start = time.time()
    next_()                                  # زنجیره را ادامه بده
    logging.info("message handler took %.1fms", (time.time() - start) * 1000)

# ضداسپم — اگر next_() صدا نزنی، هندلر اجرا نمی‌شود
@bot.register_middleware(update_types=["message"])
def anti_flood(message, next_):
    if is_spammer(message.from_user.id):
        return
    next_()
```

برای بات async همان دکوریتور روی `AsyncBot` کار می‌کند و `await next_()` می‌زنید.

## 🚨 مدیریت خطاها

```python
from soroushlite import SoroushError, NetworkError, ApiSoroushError, RateLimitError

try:
    bot.send_message(chat_id, "سلام")
except RateLimitError as e:
    time.sleep(e.retry_after)               # 429 — سروش گفته چند ثانیه صبر کن
except InvalidTokenError:
    print("توکن اشتباه است")
except ApiSoroushError as e:
    print(f"خطای API: {e.description} (کد {e.error_code})")
except NetworkError:
    print("اینترنت قطع است")
```

یا یک هندلر سراسری برای همه خطاهای هندلرها:

```python
@bot.exception_handler
def on_error(payload, exception):
    logging.exception("هندلر روی %s کرش کرد: %s", payload, exception)
```

درخت خطا: `SoroushError` ← `NetworkError`، `ApiHTTPError`، `ApiSoroushError`
(زیرشاخه‌ها: `InvalidTokenError` برای 401/404، `BotBlockedError` برای 403 و
`RateLimitError` برای 429 با فیلد `retry_after`).

## 📁 کار با فایل‌ها

چهار شکل ورودی برای همه متدهای رسانه‌ای قبول است:

```python
# 1) file_id (پیشنهادی — سریع‌ترین)
bot.send_photo(chat_id, "PHOTO-FILE-ID")

# 2) URL عمومی
bot.send_photo(chat_id, "https://example.com/cat.jpg")

# 3) فایل‌اپن
with open("report.pdf", "rb") as f:
    bot.send_document(chat_id, f)

# 4) مسیر فایل
bot.send_video(chat_id, "clip.mp4")

# آلبوم (۲ تا ۱۰ عکس/ویدیو):
from soroushlite import InputMediaPhoto, InputMediaVideo
bot.send_media_group(chat_id, [InputMediaPhoto("P1"), InputMediaPhoto("P2")])

# دانلود فایل (سقف ۲۰ مگابایت):
file = bot.get_file(message.document.file_id)
data = bot.download_file(file)                     # bytes
open("doc.pdf", "wb").write(data)
```

نکته: لینک دانلودی که `getFile` می‌دهد حداقل ۱ ساعت معتبر است؛ بعد از انقضا
دوباره `getFile` بزنید. نام و MIME اصلی فایل ممکن است حفظ نشود — خودتان ذخیره کنید.

## 📏 پیام‌های طولانی و ابزارهای کمکی

```python
# ارسال پیام بلند — خودکار به تکه‌های <=4096 کاراکتری تقسیم می‌شود
bot.send_long_message(chat_id, very_long_text)

# escape کردن متن کاربر برای parse_mode امن
from soroushlite import escape_html, escape_markdown, split_text, create_deep_link

safe = escape_html(user_input)          # < > & را امن می‌کند
chunks = split_text(very_long_text)     # لیست تکه‌های ۴۰۹۶ کاراکتری

# دیپ‌لینک — کاربر با کلیک، بات را با پارامتر start می‌بیند
create_deep_link("mybot", "ref42")      # https://splus.ir/mybot?start=ref42
```

## ⚡ بات غیرهمزمان (Async)

سطح API دقیقاً همان است؛ فقط همه متدها `await` می‌خواهند:

```python
import asyncio
from soroushlite import AsyncBot

bot = AsyncBot("توکن-بات-شما")

@bot.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id, "async! ⚡️")
    # می‌توانید همزمان کار دیگری هم بکنید:
    await asyncio.sleep(0)

bot.polling()          # بلوکه‌کننده
# یا داخل کد async خودتان:
# asyncio.run(bot.infinity_polling())
```

نکته‌ها:

- نصب async اختیاری است: `pip install "soroushlite[async]"`
- `async with AsyncBot(TOKEN) as bot:` هم کار می‌کند (بستن خودکار session)
- هندلرها می‌توانند sync یا async باشند؛ خودش تشخیص می‌دهد و await می‌کند

## 🪝 وب‌هوک

جای long polling، می‌توانید آدرس HTTPS بدهید تا خود سروش آپدیت‌ها را POST کند:

```python
bot.set_webhook("https://example.com/webhook")   # پورت‌های ۴۴۳، ۸۰، ۸۸، ۸۴۴۳
bot.get_webhook_info()                            # وضعیت صف و آخرین خطا
bot.delete_webhook()                              # بازگشت به getUpdates
```

سمت سرور با Flask:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    bot.process_webhook_update(request.get_json(force=True))
    return "ok", 200
```

نکته‌های امنیتی از مستندات رسمی:

- آدرس webhook را قابل حدس انتخاب نکنید (مثلاً توکن را بخشی از مسیر کنید)
- تا وقتی webhook فعال است، `getUpdates` کار نمی‌کند و برعکس
- آپدیت‌های دریافت‌نشده فقط ۲۴ ساعت روی سرور می‌مانند

## 📖 مرجع کامل متدها

### به‌روزرسانی‌ها و وب‌هوک

| متد | توضیح |
|---|---|
| `get_updates(offset, limit, timeout, allowed_updates)` | دریافت آپدیت‌ها با long polling |
| `set_webhook(url, ...)` | ثبت وب‌هوک (پورت ۴۴۳/۸۰/۸۸/۸۴۴۳) |
| `delete_webhook(drop_pending_updates)` | حذف وب‌هوک |
| `get_webhook_info()` | وضعیت وب‌هوک |
| `process_new_updates(updates)` | تحویل آپدیت‌ها به هندلرها |
| `process_webhook_update(update)` | پردازش یک payload وب‌هوک |
| `polling()` / `infinity_polling()` | حلقه‌های دریافت |

### پیام‌ها

| متد | توضیح |
|---|---|
| `send_message(chat_id, text, parse_mode, reply_markup, ...)` | ارسال متن |
| `reply_to(message, text)` | ریپلای سریع روی یک پیام |
| `send_long_message(chat_id, text)` | ارسال متن بلند با تقسیم خودکار |
| `forward_message(chat_id, from_chat_id, message_id)` | فوروارد |
| `copy_message(chat_id, from_chat_id, message_id, ...)` | کپی بدون لینک به منبع |
| `edit_message_text(...)` / `edit_message_caption(...)` / `edit_message_reply_markup(...)` | ویرایش پیام |
| `delete_message(chat_id, message_id)` | حذف (تا ۴۸ ساعت بعد از ارسال) |
| `send_chat_action(chat_id, action)` | حالت typing و... (به‌زودی در آپ‌استریم) |

### رسانه‌ها

| متد | توضیح |
|---|---|
| `send_photo(chat_id, photo, caption)` | عکس (حداکثر ۱۰MB) |
| `send_video(chat_id, video, caption)` | ویدیو MP4 |
| `send_audio(chat_id, audio, ...)` | موسیقی (performer/title دارد) |
| `send_voice(chat_id, voice, ...)` | پیام صوتی |
| `send_document(chat_id, document, caption)` | فایل عمومی |
| `send_animation(chat_id, animation, ...)` | GIF / ویدیوی بی‌صدا |
| `send_video_note(chat_id, video_note)` | ویدیوی گرد (تا ۶۰ ثانیه) |
| `send_sticker(chat_id, sticker)` | استیکر WEBP/TGS/WEBM |
| `send_media_group(chat_id, media)` | آلبوم ۲ تا ۱۰ آیتم |
| `send_location(chat_id, latitude, longitude)` | نقطه روی نقشه |
| `send_contact(chat_id, phone_number, first_name)` | مخاطب تلفنی |

### تعامل

| متد | توضیح |
|---|---|
| `answer_callback_query(id, text, show_alert, ...)` | پاسخ به فشار دکمه شیشه‌ای |
| `get_me()` | اطلاعات خود بات |
| `get_chat(chat_id)` | اطلاعات چت (به‌زودی در آپ‌استریم) |
| `get_user_profile_photos(user_id)` | عکس‌های پروفایل (به‌زودی) |
| `get_sticker_set(name)` | مجموعه استیکر (به‌زودی) |
| `pin_chat_message(...)` / `unpin_chat_message(...)` | سنجاق پیام (به‌زودی) |
| `get_file(file_id)` / `download_file(...)` | آماده‌سازی و دانلود فایل |

### منوی دستورها

| متد | توضیح |
|---|---|
| `set_my_commands(commands)` | ثبت منوی `/` (حداکثر ۱۰۰ دستور) |
| `get_my_commands(language_code)` | خواندن منوی فعلی |
| `delete_my_commands(language_code)` | حذف منو |

### مدیریت بات

| متد | توضیح |
|---|---|
| `set_state / get_state / reset_state` | مدیریت حالت FSM |
| `get_state_data / update_state_data / clear_state_data` | داده‌های هر حالت |
| `register_middleware(...)` / `exception_handler` | میان‌افزار و خطای سراسری |
| `stop_polling()` / `close()` | توقف تمیز |
| `threaded=True` در سازنده | ارسال موازی هندلرها |

## ⚙️ پیکربندی پیشرفته

```python
bot = Bot(
    TOKEN,
    base_url="https://api.splus.ir",   # تغییر برای پروکسی/سرور محلی
    timeout=30,                        # تایم‌اوت هر درخواست (ثانیه)
    max_retries=3,                     # تلاش مجدد روی 429/5xx
    parse_mode="HTML",                 # پارس‌مود پیش‌فرض همه پیام‌ها
    threaded=True,                     # هندلرها در تردهای موازی
    storage=JSONFileStorage("s.json"), # ذخیره‌ساز FSM
)

# کانتکست‌منیجر — بستن خودکار
with Bot(TOKEN) as bot:
    bot.polling()

# لاگ‌بندی یکپارچه
from soroushlite import setup_logging
setup_logging("DEBUG")
```

## 🧪 اجرای تست‌ها

```bash
pip install -e ".[dev]"
python -m pytest -q
```

نتیجه: **۱۳۹ پاس + ۱ رد (skip اختیاری Redis)** — کاملاً آفلاین؛ هیچ درخواست
واقعی به `api.splus.ir` زده نمی‌شود. کل مجموعه در زیر ۱ ثانیه اجرا می‌شود.

## 🗂 ساختار پروژه

```
soroushlite/
├── src/soroushlite/
│   ├── __init__.py       # خروجی‌های عمومی + AsyncBot تنبل
│   ├── api_client.py     # ترنسپورت HTTP، retry، مدیریت 429
│   ├── bot.py            # Bot همگام: ۵۰+ متد، FSM، میان‌افزار
│   ├── async_bot.py      # AsyncBot روی aiohttp
│   ├── handlers.py       # روتر، فیلترها، دکوریتورها
│   ├── fsm.py            # StateGroup + سه ذخیره‌ساز
│   ├── middleware.py     # زنجیره sync/async
│   ├── polling.py        # حلقه‌های polling و infinity
│   ├── types.py          # Update/Message/کیبوردها/BotCommand
│   ├── utils.py          # تقسیم متن، escape، دیپ‌لینک
│   ├── log.py            # setup_logging
│   └── exceptions.py     # درخت SoroushError
├── examples/             # ۷ مثال آماده اجرا
├── tests/                # ۱۴۰ تست آفلاین
├── .github/workflows/    # CI روی پایتون ۳.۱۰ تا ۳.۱۳
├── README.md             # مستندات انگلیسی
├── README_FA.md          # همین فایل
├── ARCHITECTURE.md       # معماری داخلی (برای مصاحبه!)
├── CHANGELOG.md
├── pyproject.toml
└── LICENSE               # MIT
```

## 🎯 نکات گیت‌هاب و رزومه

- در About مخزن بنویسید: `A from-scratch Soroush Plus Bot API framework — sync+async, FSM, middleware`
- تاپیک‌ها (Topics): `soroush` `soroush-plus` `bot-framework` `python` `fsm` `async` `middleware`
- سه مخزن GramLite + BaleLite + SoroushLite را Pin کنید — خانواده‌ای از
  فریم‌ورک‌های هم‌معماری که نشان می‌دهد الگوها را یک بار یاد گرفته و سه بار
  روی سه API واقعی پیاده کرده‌اید.
- در مصاحبه: فایل `ARCHITECTURE.md` نقاط تصمیم معماری (دو رجیستری، کلید
  `(chat_id, user_id)` در FSM، نوشتن اتمیک فایل، پوشش middleware روی dispatch
  و...) را توضیح می‌دهد.
- بج CI بعد از اولین push سبز می‌شود؛ تست‌ها آفلاین‌اند و همیشه پاس می‌شوند.

## 📄 لایسنس

MIT — متن کامل در [LICENSE](LICENSE).

