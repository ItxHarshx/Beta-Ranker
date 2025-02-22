import asyncio
import logging
import os
import html
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from dotenv import load_dotenv
from features import user_profile, leveling
from features.user_profile import router as profile_router
from database import get_last_checkin, update_checkin, get_user_data, create_user_if_not_exists, get_top_users
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

    # Ensure the user exists in the database (updated to store first_name)
    await create_user_if_not_exists(user_id, safe_first_name)

    # Fetch user stats
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply("Error fetching your data. Try again later.")
        return

    health, gold_coins, exp, level, essence = user_data  

    # Inline button linking to KaisenWorld group
    chat_group_url = "https://t.me/KaisenWorld"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Join Chat Group", url=chat_group_url)]
        ]
    )

    caption = (
        f"Hey <a href='tg://user?id={user_id}'>{safe_first_name}</a>, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝖪𝖺𝗂𝗌𝖾𝗇 𝖱𝖺𝗇𝗄𝗂𝗇𝗀 𝖡𝗈𝗍! 🎉\n\n"
        f"<b>📜 ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴄᴏɪɴs?</b>\n"
        f"- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴄᴏɪɴs.\n\n"
        f"<b>➻ ʏᴏᴜʀ sᴛᴀᴛs:</b>\n- ʟᴇᴠᴇʟ: {level}\n- ᴄᴏɪɴs: {gold_coins:,}\n- ᴇssᴇɴᴄᴇ: {essence}\n\n"
        f"𝖦𝖾𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗇𝗈𝗐! 𝗍𝗒𝗉𝖾 /help 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌."
    )

    await message.answer_photo(
        photo="https://ibb.co/YFVsLtWN",
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    
# Help command
@dp.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "*Available Commands:*\n\n"
        "💠 *General Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show available commands\n\n"
        "👤 *User Commands:*\n"
        "/profile - View your profile\n"
        "/balance - Check your balance\n"
        "/daily - Claim your daily reward\n\n"
        "🏆 *Leaderboards:*\n"
        "/leaderboard - View top users\n"
    )

    await message.reply(help_text, parse_mode="Markdown")  # ✅ Proper indentation

dp.include_router(user_profile.router)
dp.include_router(leveling.router)

@dp.message(Command("daily"))
async def daily_checkin(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    last_checkin = await get_last_checkin(user_id)

    # If last_checkin is None (first-time check-in), allow claiming immediately
    if last_checkin:
        # Ensure last_checkin is timezone-aware
        if last_checkin.tzinfo is None:
            last_checkin = last_checkin.replace(tzinfo=timezone.utc)

        # Calculate next check-in time
        next_checkin_time = last_checkin + timedelta(hours=24)

        # Calculate remaining time
        remaining_time = next_checkin_time - datetime.now(timezone.utc)

        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            await message.reply(f"{first_name}, you've already claimed today's rewards!\n"
                                f"⏳ You can check-in again in {int(hours)}h {int(minutes)}m.")
            return  # Stop execution if check-in is not yet available

    # Update check-in timestamp & reward user
    await update_checkin(user_id)
    await message.reply(f"{first_name}, you've checked in successfully!\n"
                        f"🎁 You received 75 Gold Coins & 5 Essence!")

# ✅ **Balance Command**
@dp.message(Command("balance"))
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Ensure user exists in the database
    await create_user_if_not_exists(user_id, first_name)

    # Fetch user data
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply("❌ Error: Could not fetch balance data.")
        return

    # Extract Gold Coins & Essence
    _, gold_coins, _, _, essence = user_data

    # Format balance text
    balance_text = (
        f"➻ {first_name}'s Balance:\n\n"
        f"💰 Gold Coins: {gold_coins:,}\n"
        f"🔮 Essence: {essence}\n"
    )

    await message.reply(balance_text)

# 🏆 Leaderboard Categories
LEADERBOARD_CATEGORIES = {
    "level": "🔰 Level",
    "gold": "💰 Coins",
    "essence": "🔮 Essence"
}

def get_leaderboard_keyboard():
    """Creates inline buttons to switch between leaderboards."""
    keyboard = InlineKeyboardBuilder()
    for stat, label in LEADERBOARD_CATEGORIES.items():
        keyboard.button(text=label, callback_data=f"leaderboard_{stat}")
    return keyboard.as_markup()

async def send_leaderboard(message: types.Message, category="level", edit=False):  # ✅ Default set to "level"
    """Fetches leaderboard data and sends (or updates) the message."""
    top_users = await get_top_users(category)

    if not top_users:
        leaderboard_text = "No users found in the leaderboard yet."
    else:
        leaderboard_text = f"🏆 **Leaderboard - {LEADERBOARD_CATEGORIES[category]}** 🏆\n\n"
        for rank, (user_id, first_name, stat_value) in enumerate(top_users, start=1):
            user_link = f"[{first_name}](tg://user?id={user_id})"
            # ✅ Add commas only if the category is 'gold' (Gold Coins)
            formatted_value = f"{stat_value:,}" if category == "gold" else stat_value
            leaderboard_text += f"**{rank}** - {user_link} ➝ {formatted_value}\n"
    if edit:
        await message.edit_text(leaderboard_text, reply_markup=get_leaderboard_keyboard(), parse_mode="Markdown")
    else:
        await message.reply(leaderboard_text, reply_markup=get_leaderboard_keyboard(), parse_mode="Markdown")

@dp.message(Command("leaderboard"))
async def leaderboard_handler(message: types.Message):
    """Handles the /leaderboard command and shows the Level leaderboard first."""
    await send_leaderboard(message, category="level")  # ✅ Default to "level"

@dp.callback_query(lambda c: c.data.startswith("leaderboard_"))
async def switch_leaderboard(callback: CallbackQuery):
    """Handles inline button clicks to switch leaderboard categories."""
    category = callback.data.split("_")[1]  # Extracts the chosen category
    await send_leaderboard(callback.message, category=category, edit=True)
    await callback.answer()  # Acknowledge the button click

#@dp.message(Command("dev"))
#async def dev_command(message: Message):
#    dev_text = (
#        " *📜 Bᴏᴛ Dᴇᴠ. Lᴏɢs:*\n\n"
#        f"➻ *Bot Name:*   Bot\n"
#        f"➻ *Version:* 0.1\n"
#        f"➻ *Developer: [Harsh](tg://user?id=6329058409)\n\n*"
#        "⚙️ *Technical Details:*\n"
#        "➻ *Language:* Python (Aiogram 3)\n"
#        "➻ *Database:* PostgreSQL\n"
#        "💡 *More Features Coming Soon...*"
#    )

#    await message.reply(dev_text, parse_mode="Markdown")

# ------------𝗦𝗛𝗢𝗣---------------
from aiogram.utils.callback_data import CallbackData  # ✅ Correct import

# ✅ Define CallbackData correctly
shop_callback = CallbackData("shop", "action", "page")  # Aiogram v3 format

# Shop items (Booster section)
SHOP_ITEMS = [
    {"name": "2x Booster (30 min)", "price": 150, "id": "booster_30"},
    {"name": "2x Booster (1 hour)", "price": 300, "id": "booster_60"},
    {"name": "2x Booster (24 hours)", "price": 3000, "id": "booster_1440"},
]

ITEMS_PER_PAGE = 3  # Number of items per page

# Function to generate shop page
def get_shop_page(page: int = 1):
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    items = SHOP_ITEMS[start:end]

    # Shop message
    shop_text = "🛒 **Welcome to the Shop!** 🛒\n\n"
    for item in items:
        shop_text += f"💠 {item['name']} - {item['price']} Gold Coins\n"

    # Inline buttons for purchasing items
    buttons = [
        [InlineKeyboardButton(item["name"], callback_data=f"buy_{item['id']}")]
        for item in items
    ]

    # Navigation buttons
    nav_buttons = []
    if start > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=shop_callback.new(action="prev", page=page - 1)))
    if end < len(SHOP_ITEMS):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=shop_callback.new(action="next", page=page + 1)))
    
    if nav_buttons:
        buttons.append(nav_buttons)

    # Back button
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="close_shop")])

    return shop_text, InlineKeyboardMarkup(inline_keyboard=buttons)

# Command to open the shop
@dp.message(Command("shop"))
async def shop_handler(message: types.Message):
    """Handles the /shop command and shows the first shop page."""
    shop_text, reply_markup = get_shop_page(1)
    await message.answer(shop_text, reply_markup=reply_markup)

# Handling navigation & back button
@dp.callback_query(shop_callback.filter())
async def shop_navigation(call: types.CallbackQuery, callback_data: dict):
    """Handles shop navigation (Previous/Next page)."""
    action = callback_data["action"]
    page = int(callback_data["page"])

    if action in ["prev", "next"]:
        shop_text, reply_markup = get_shop_page(page)
        await call.message.edit_text(shop_text, reply_markup=reply_markup)

    await call.answer()

# Handling back button
@dp.callback_query(lambda call: call.data == "close_shop")
async def close_shop(call: types.CallbackQuery):
    """Closes the shop message."""
    await call.message.delete()
    await call.answer()
# -------------------------------

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
        
if __name__ == "__main__":
    asyncio.run(main())
