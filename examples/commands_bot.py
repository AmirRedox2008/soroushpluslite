"""Bot commands menu + sticker helpers.

Soroush Plus supports setMyCommands, so users get a "/" menu in the chat.
Run:  python examples/commands_bot.py
"""

import soroushlite
from soroushlite import Bot, InlineKeyboardButton, InlineKeyboardMarkup

bot = Bot("YOUR_BOT_TOKEN")

# Publish the "/" menu once at startup (works like Telegram's setMyCommands).
bot.set_my_commands([
    ("start", "Start the bot"),
    ("help", "How to use the bot"),
    ("about", "About this bot"),
])


@bot.message_handler(commands=["start"])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Website", url="https://soroushplus.com"),
        InlineKeyboardButton("About me", callback_data="about"),
    )
    bot.send_message(
        message.chat.id,
        "سلام! من با *SoroushLite* ساخته شدم 🤖",
        parse_mode=soroushlite.ParseMode.MARKDOWN,
        reply_markup=markup,
    )


@bot.message_handler(commands=["about"])
def about(message):
    bot.send_message(message.chat.id, "SoroushLite v1.0.0 — from-scratch Soroush Bot API framework.")


@bot.callback_query_handler(func=lambda c: c.data == "about")
def about_callback(callback):
    bot.answer_callback_query(callback.id, text="Built with SoroushLite!")


@bot.message_handler(content_types=["sticker"])
def sticker(message):
    bot.reply_to(message, "استیکر قشنگی بود! 🎨")


if __name__ == "__main__":
    bot.infinity_polling()
