from aiogram import types, Router
import psycopg2
from aiogram.filters import Command

# Create a Router for the profile module
router = Router()

# Database Connection (Import your DB connection here)
from database import conn

cursor = conn.cursor()

@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT first_name, health, gold_coins, exp, level, essence FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        first_name, health, gold, exp, level, essence = user
    else:
        # Insert new user if not found
        first_name = message.from_user.first_name
        cursor.execute("INSERT INTO users (user_id, first_name) VALUES (%s, %s)", (user_id, first_name))
        conn.commit()
        health, gold, exp, level, essence = 100, 0, 0, 1, 0

    profile_text = (
        f"👤 <b>{first_name}'s Profile</b>\n\n"
        f"❤️ Health: {health}\n"
        f"💰 Gold Coins: {gold}\n"
        f"⚡ EXP: {exp}\n"
        f"📈 Level: {level}\n"
        f"🔮 Essence: {essence}"
    )

    await message.reply(profile_text)
