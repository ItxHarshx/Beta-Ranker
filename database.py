import asyncpg
from datetime import datetime, timedelta

# Connect to PostgreSQL
async def connect_db():
    return await asyncpg.connect("postgresql://postgres:ZOfBatiHLaKonRFXSaycgkmxwSBEKffw@yamanote.proxy.rlwy.net:41047/railway")  # Change credentials!

# Create user if not exists
async def create_user_if_not_exists(user_id):
    conn = await connect_db()
    await conn.execute(
        """INSERT INTO users (user_id, health, gold_coins, exp, level, essence, last_message_time, last_checkin)
           VALUES ($1, 100, 0, 0, 1, 0, NOW(), NULL) 
           ON CONFLICT (user_id) DO NOTHING""",
        user_id
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
    conn = await asyncpg.connect("postgresql://postgres:ZOfBatiHLaKonRFXSaycgkmxwSBEKffw@yamanote.proxy.rlwy.net:41047/railway")
    query = f"SELECT user_id, first_name, {column} FROM users ORDER BY {column} DESC LIMIT 10"
    results = await conn.fetch(query)
    await conn.close()  # Close connection after fetching

    return [(row["user_id"], row["first_name"], row[column]) for row in results]  # ✅ Now returns first_name too
