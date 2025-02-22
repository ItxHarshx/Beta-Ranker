import asyncio
import logging
import os
import html
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from features import user_profile, leveling
from features.user_profile import router as profile_router
from database import get_last_checkin, update_checkin
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
        f"Hey {user_link}, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝖪𝖺𝗂𝗌𝖾𝗇 𝖱𝖺𝗇𝗄𝗂𝗇𝗀 𝖡𝗈𝗍! 🎉\n\n"
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

dp.include_router(user_profile.router)
dp.include_router(leveling.router)

@dp.message(Command("daily"))
async def daily_checkin(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    last_checkin = await get_last_checkin(user_id)

    if last_checkin:
        next_checkin_time = last_checkin + timedelta(hours=24)
        remaining_time = next_checkin_time - datetime.utcnow()

        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            await message.reply(f"{first_name}, you've already claimed today's rewards!\n"
                                f"⏳ You can check-in again in {int(hours)}h {int(minutes)}m.")
            return

    await update_checkin(user_id)
    await message.reply(f"{first_name}, you've checked in successfully!\n"
                        f"🎁 You received 75 Gold Coins & 5 Essence !")

# Error handling
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
