@dp.callback_query(F.data.startswith("buy_booster_"))
async def buy_booster(call: CallbackQuery):
    user_id = call.from_user.id
    booster_map = {
        "buy_booster_30m": ("2x Booster (30 min)", 30, 150),
        "buy_booster_1h": ("2x Booster (1 hour)", 60, 300),
        "buy_booster_24h": ("2x Booster (24 hours)", 1440, 3000),
    }
    
    booster_data = booster_map.get(call.data)
    if not booster_data:
        return  # Invalid data, ignore

    booster_name, duration, cost = booster_data
    result = await purchase_booster(user_id, booster_name, duration, cost)

    if result == "not_enough_coins":
        await call.answer("❌ You don’t have enough gold coins!", show_alert=True)
    elif result == "booster_already_active":
        await call.answer("⚠️ You already have an active booster!", show_alert=True)
    else:
        await call.answer(f"✅ {booster_name} activated! Enjoy your boosted rewards.", show_alert=True)
