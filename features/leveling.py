import random
import asyncpg
from aiogram import Router, types
from datetime import datetime, timedelta
from database import connect_db  # Import the existing DB connection function

router = Router()

# Leveling Configuration
EXP_PER_MESSAGE = 2
SPAM_LIMIT_SECONDS = 0.5  # Prevents spam (2 messages per second)

GROUP_ID = -1002361603406

# Leveling EXP Pattern
LEVEL_EXP_REQUIREMENTS = {
    1: 80,
    2: 120,
    3: 120,
    4: 150,
}  # After level 4, the pattern will increase dynamically.

def get_exp_required(level):
    """Get EXP required for the next level."""
    return LEVEL_EXP_REQUIREMENTS.get(level, 200 + (level - 5) * 50)  # Increasing pattern

# Function to get user data from `users` table
async def get_user_data(user_id):
    db = await connect_db()
    user = await db.fetchrow("SELECT exp, level, gold_coins, last_message_time FROM users WHERE user_id = $1", user_id)
    await db.close()
    
    if not user:
        return {"exp": 0, "level": 1, "gold_coins": 0, "last_message_time": None}
    return dict(user)

# Function to update EXP and handle leveling
async def update_user_exp(user_id, message: types.Message):
    db = await connect_db()
    user = await get_user_data(user_id)
    
    # Spam Prevention
    now = datetime.utcnow()
    if user["last_message_time"]:
        last_time = user["last_message_time"]
        if now - last_time < timedelta(seconds=SPAM_LIMIT_SECONDS):
            await message.reply("⚠️ You can't spam messages for EXP!")
            return

    new_exp = user["exp"] + EXP_PER_MESSAGE
    exp_required = get_exp_required(user["level"])
    
    # Level Up Check
    if new_exp >= exp_required:
        new_level = user["level"] + 1
        new_exp -= exp_required  # Carry over extra EXP
        coin_reward = random.randint(60, 120)
        new_coins = user["gold_coins"] + coin_reward

        # Update user data in `users` table
        await db.execute(
            "UPDATE users SET exp = $1, level = $2, gold_coins = $3, last_message_time = $4 WHERE user_id = $5",
            new_exp, new_level, new_coins, now, user_id
        )

        # Notify user
        await message.reply(
            f"🎉 <b>Level Up!</b>\n"
            f"✨ You reached <b>Level {new_level}</b>!\n"
            f"💰 You earned <b>{coin_reward} Coins</b>!"
        )
    else:
        # Update user EXP only
        await db.execute(
            "UPDATE users SET exp = $1, last_message_time = $2 WHERE user_id = $3",
            new_exp, now, user_id
        )

    await db.close()

# Message handler to track EXP in the target group
@router.message()
async def track_exp(message: types.Message):
    if message.chat.id == GROUP_ID:  # Ensures EXP tracking only in Kaisen World
        await update_user_exp(message.from_user.id, message)
