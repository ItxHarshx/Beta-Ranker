import asyncpg
from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_data, create_user_if_not_exists

router = Router()

@router.message(Command("balance"))
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Ensure the user exists in the database
    await create_user_if_not_exists(user_id)

    # Fetch user data
    user_data = await get_user_data(user_id)

    # Check if data is retrieved correctly
    if not user_data:
        await message.reply("Error fetching balance data. Try again later.")
        return

    # Extract currency stats
    _, gold_coins, _, _, essence = user_data  # Extract only Gold Coins & Essence

    # Format balance text
    balance_text = (
        f"💰 {first_name}'s Balance\n\n"
        f"💵 Gold Coins: {gold_coins:,}\n"  # ✅ Adds commas for readability
        f"🔮 Essence: {essence}\n"
    )

    await message.reply(balance_text, parse_mode="HTML")  # ✅ Use HTML mode to prevent errors
