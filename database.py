import asyncpg
from datetime import datetime, timedelta

# Connect to PostgreSQL
async def connect_db():
    return await asyncpg.connect("postgresql://postgres:PvettOVPbAZRzvjkuuxPINApohmdekzV@mainline.proxy.rlwy.net:40917/railway")  # Change credentials!

# Create user if not exists
async def create_user_if_not_exists(user_id, first_name):
    conn = await connect_db()
    await conn.execute(
        """INSERT INTO users (user_id, first_name, health, gold_coins, exp, level, essence, last_message_time, last_checkin)
           VALUES ($1, $2, 100, 0, 0, 1, 0, NOW(), NULL) 
           ON CONFLICT (user_id) DO UPDATE SET first_name = EXCLUDED.first_name""",
        user_id, first_name
    )
    await conn.close()

# Fetch user data
async def get_user_data(user_id):
    conn = await connect_db()
    user = await conn.fetchrow("SELECT health, gold_coins, exp, level, essence FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return user  # Returns None if user not found

# Fetch last check-in time
async def get_last_checkin(user_id):
    conn = await connect_db()
    last_checkin = await conn.fetchval("SELECT last_checkin FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return last_checkin

# Function to update the check-in time and add rewards
async def update_checkin(user_id):
    conn = await connect_db()
    await conn.execute(
        "UPDATE users SET last_checkin = $1, gold_coins = gold_coins + 75, essence = essence + 5 WHERE user_id = $2",
        datetime.utcnow(), user_id
    )
    await conn.close()

async def get_top_users(category):
    """Fetch the top 10 users based on the selected category."""
    valid_columns = {
        "level": "level",
        "gold": "gold_coins",
        "essence": "essence"
    }

    column = valid_columns.get(category)
    if not column:
        return []

    # Connect to the database and fetch results
    conn = await asyncpg.connect("postgresql://postgres:PvettOVPbAZRzvjkuuxPINApohmdekzV@mainline.proxy.rlwy.net:40917/railway")
    query = f"SELECT user_id, first_name, {column} FROM users ORDER BY {column} DESC LIMIT 10"
    results = await conn.fetch(query)
    await conn.close()  # Close connection after fetching

    return [(row["user_id"], row["first_name"], row[column]) for row in results]  # ✅ Now returns first_name too

# ---------- Boosters Table -----------
async def create_boosters_table():
    conn = await connect_db()
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS boosters (
            user_id BIGINT PRIMARY KEY, 
            booster_name TEXT NOT NULL, 
            duration INTERVAL NOT NULL, 
            expiry TIMESTAMP NOT NULL
        )"""
    )
    await conn.close()

import datetime

# Function to check if the user has an active booster
async def get_active_booster(user_id):
    conn = await connect_db()
    booster = await conn.fetchrow("SELECT booster_name, expiry FROM boosters WHERE user_id = $1", user_id)
    await conn.close()
    
    if booster and booster["expiry"] > datetime.datetime.utcnow():
        return booster  # Return active booster details
    return None  # No active booster found

# Function to purchase a booster
async def purchase_booster(user_id, booster_name, duration, cost):
    conn = await connect_db()

    # Check if user has enough coins
    user = await conn.fetchrow("SELECT gold_coins FROM users WHERE user_id = $1", user_id)
    if not user or user["gold_coins"] < cost:
        await conn.close()
        return "not_enough_coins"

    # Check if user already has an active booster
    active_booster = await get_active_booster(user_id)
    if active_booster:
        await conn.close()
        return "booster_already_active"

    # Calculate expiry time
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)

    # Deduct coins and add booster
    async with conn.transaction():
        await conn.execute("UPDATE users SET gold_coins = gold_coins - $1 WHERE user_id = $2", cost, user_id)
        await conn.execute(
            """INSERT INTO boosters (user_id, booster_name, duration, expiry)
               VALUES ($1, $2, $3, $4)
               ON CONFLICT (user_id) DO UPDATE 
               SET booster_name = EXCLUDED.booster_name, duration = EXCLUDED.duration, expiry = EXCLUDED.expiry""",
            user_id, booster_name, duration, expiry_time
        )

    await conn.close()
    return "success"
