import asyncpg
from aiogram import Router, types
from aiogram.filters import Command
from features.leveling import get_exp_required  # Function to get required EXP
from database import get_user_data, create_user_if_not_exists, get_last_checkin
from datetime import datetime

router = Router()

@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Ensure the user exists in the database
    await create_user_if_not_exists(user_id)

    # Fetch user data
    user_data = await get_user_data(user_id)
    last_checkin = await get_last_checkin(user_id)

    # Check if data is retrieved correctly
    if not user_data:
        await message.reply("Error fetching profile data. Try again later.")
        return

    # Extract user stats
    health, gold_coins, exp, level, essence = user_data

    # Get required EXP for next level
    required_exp = get_exp_required(level)

    # Format last check-in
    last_checkin_text = last_checkin.strftime('%Y-%m-%d %H:%M:%S') if last_checkin else "Never"
    
    # Format profile text
    profile_text = (
        f"👤 {first_name}'s Profile\n\n"
        f"💰 Gold Coins: {gold_coins:,}\n"  # ✅ Adds commas to gold coins
        f"📈 Level: {level}\n"
        f"✨ EXP: {exp}/{required_exp}\n"  # ✅ Shows current/required EXP correctly
        f"❤️ Health: {health}\n"
        f"🔮 Essence: {essence}"\n\n
        f"📅 Last Check-in: `{last_checkin_text}`"
    )

    await message.reply(profile_text, parse_mode="HTML")  # ✅ Use HTML mode to prevent errors
