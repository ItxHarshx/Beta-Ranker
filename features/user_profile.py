import asyncpg
from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_data, create_user_if_not_exists  # Make sure these functions exist

router = Router()

@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Ensure the user exists in the database
    await create_user_if_not_exists(user_id)

    # Fetch user data
    user_data = await get_user_data(user_id)

    # Check if data is retrieved correctly
    if not user_data:
        await message.reply("Error fetching profile data. Try again later.")
        return

    # Extract user stats
    health, gold_coins, exp, level, essence = user_data

    profile_text = (
        f"👤 {first_name}'s Profile\n\n"
        f"❤️ Health: {health}\n"
        f"💰 Gold Coins: {gold_coins}\n"
        f"⚡ EXP: {exp}\n"
        f"📈 Level: {level}\n"
        f"🔮 Essence: {essence}"
    )

    await message.reply(profile_text)
