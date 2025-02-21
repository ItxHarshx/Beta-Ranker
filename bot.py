import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Load environment variables (Bot Token)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Start command
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🔥 Welcome to Kaisen Ranking Bot! Type /help to see commands.")

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
