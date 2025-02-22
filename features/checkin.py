from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime, timedelta
from database import get_last_checkin, update_checkin

import logging

router = Router()

@router.message(Command("daily"))
async def daily_checkin(message: types.Message):
    """Handles the /daily command for daily check-in rewards."""
    logging.info(f"Received /daily command from user {message.from_user.id}")  # Debug log

    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Get the last check-in time
    last_checkin = await get_last_checkin(user_id)
    logging.info(f"Last check-in for {user_id}: {last_checkin}")  # Debug log

    # Check if 24 hours have passed
    if last_checkin:
        next_checkin_time = last_checkin + timedelta(hours=24)
        remaining_time = next_checkin_time - datetime.utcnow()

        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)

            logging.info(f"User {user_id} must wait {int(hours)}h {int(minutes)}m.")  # Debug log
            await message.reply(
                f"⚠️ {first_name}, you've already claimed today's rewards!\n"
                f"⏳ You can check-in again in {int(hours)}h {int(minutes)}m."
            )
            return

    # Update check-in time and reward user
    await update_checkin(user_id)
    logging.info(f"User {user_id} received rewards.")  # Debug log

    await message.reply(
        f"✅ {first_name}, you have successfully checked in!\n"
        f"🎁 You received **75 Gold Coins** & **5 Essence**."
    )
