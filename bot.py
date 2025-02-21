import asyncio
import logging
import os
import html
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.enums.parse_mode import ParseMode 
from aiogram.client.default import DefaultBotProperties

# Load environment variables (Bot Token)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Start command
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"  

    # Escape special characters to avoid issues
    safe_first_name = html.escape(first_name)

    # Correct user mention format
    user_link = f'<a href="tg://user?id={user_id}">{safe_first_name}</a>'

    # Inline button linking to KaisenWorld group
    chat_group_url = "https://t.me/KaisenWorld"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Join Chat Group", url=chat_group_url)]
        ]
    )

    # Welcome message
    caption = (
        f"Hey {user_link}, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 <b>𝖪𝖺𝗂𝗌𝖾𝗇 𝖱𝖺𝗇𝗄𝗂𝗇𝗀 𝖡𝗈𝗍</b>! 🎉\n\n"
        f"<b>📜 ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴛᴏᴋᴇɴs?</b>\n"
        f"- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴋᴀɪᴢᴇɴ ᴛᴏᴋᴇɴs.\n\n"
        f"𝖦𝖾𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗇𝗈𝗐! 𝗍𝗒𝗉𝖾 /help 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌."
    )

    # Send photo with caption and button
    await message.answer_photo(
        photo="https://imgur.com/a/hJU9sB4",
        caption=caption,
        reply_markup=keyboard
    )

    
# Help command
@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = "⚡ Available Commands:\n" \
                "/start - Start the bot\n" \
                "/help - Show available commands\n"
    await message.answer(help_text)

# Error handling
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
