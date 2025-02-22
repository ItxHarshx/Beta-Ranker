from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime, timedelta
import logging
from database import connect_db, create_user_if_not_exists, get_user_data

router = Router()

@router.message(Command("daily"))
async def daily_checkin(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    logging.info(f"/daily command received from {user_id}")

    try:
        await create_user_if_not_exists(user_id)
        
        conn = await connect_db()

async def get_last_checkin(user_id):
    conn = await connect_db()
    last_checkin = await conn.fetchval("SELECT last_checkin FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return last_checkin or datetime.min  # Avoids NoneType error
        

        # Check if 24 hours have passed
        if last_checkin:
            next_checkin_time = last_checkin + timedelta(hours=24)
            remaining_time = next_checkin_time - datetime.utcnow()

            if remaining_time.total_seconds() > 0:
                hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                await message.reply(
                    f"⚠️ {first_name}, you've already claimed today's rewards!\n"
                    f"⏳ You can check-in again in {int(hours)}h {int(minutes)}m."
                )
                await conn.close()
                return

        # Update check-in time and reward user
        await conn.execute(
            "UPDATE users SET last_checkin = $1, gold_coins = gold_coins + 75, essence = essence + 5 WHERE user_id = $2",
            datetime.utcnow(), user_id
        )
        await conn.close()

        await message.reply(
            f"✅ {first_name}, you've successfully checked in!\n"
            f"🎁 You received **75 Gold Coins** & **5 Essence**."
        )

    except Exception as e:
        logging.error(f"Error in /daily: {e}")
        await message.reply("❌ An error occurred. Please try again later.")
