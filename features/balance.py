from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_data

router = Router()

    user_id = message.from_user.id
    first_name = message.from_user.first_name

    user_data = await get_user_data(user_id)

@router.message(Command("balance"))
async def check_balance(message: types.Message):

    if user_data:
        gold_coins = user_data["gold_coins"]
        essence = user_data["essence"]
        await message.reply(
            f"💰 **{first_name}'s Balance**\n\n"
            f"🔹 Gold Coins: {gold_coins}\n"
            f"🌀 Essence: {essence}"
        )
    else:
        await message.reply("⚠️ You are not registered. Try sending a message first!")
