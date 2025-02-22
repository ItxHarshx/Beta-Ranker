import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import DefaultBotProperties
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
