from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_data, create_user_if_not_exists

router = Router()  # Create a Router for balance commands

@router.message(Command("balance"))
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Ensure the user exists in the database
    await create_user_if_not_exists(user_id)

    # Fetch user data
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply("Error fetching balance data. Try again later.")
        return

    # Extract Gold Coins & Essence
    _, gold_coins, _, _, essence = user_data

    # Format balance text
    balance_text = (
        f"💰 {first_name}'s Balance\n\n"
        f"💵 Gold Coins: {gold_coins:,}\n"
        f"🔮 Essence: {essence}\n"
    )

    await message.reply(balance_text, parse_mode="HTML")
