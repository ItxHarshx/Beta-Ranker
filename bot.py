import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Load environment variables (Bot Token)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Start command
IMAGE_FILE_ID = "https://ibb.co/99h957S4"
KAISEN_GROUP_LINK = "https://t.me/KaisenWorld"

@dp.message(Command("start"))
async def start_command(message: Message):
    name = message.from_user.first_name
    # Create an inline button linking to Kaisen World
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Join Chat Group", url=KAISEN_GROUP_LINK)]
        ]
    )
    await message.answer_photo(
        IMAGE_FILE_ID, 
        caption="Hey **{name}**, Welcome to Kaisen Ranking Bot ! 🎉\n\n📜 **ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴇssᴇɴᴄᴇ ?**\n- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴇssᴇɴᴄᴇ.\n\nGet started now ! type /help for more commands.",
        reply_markup=keyboard, parse_mode="Markdown") # Add the button below the image

    
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
