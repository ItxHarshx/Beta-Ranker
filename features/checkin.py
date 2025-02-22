from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime, timedelta
from database import get_last_checkin, update_checkin

router = Router()

@router.message(Command("daily"))
async def daily_checkin(message: types.Message):
    """Handles the /daily command for daily check-in rewards."""
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Get the last check-in time from the database
    last_checkin = await get_last_checkin(user_id)

    # If user has a check-in record, check if 24 hours have passed
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
            return

    # If eligible, update check-in time and reward user
    await update_checkin(user_id)
    await message.reply(
        f"✅ {first_name}, you have successfully checked in!\n"
        f"🎁 You received **75 Gold Coins** & **5 Essence**."
    )
