import asyncpg
from datetime import datetime, timedelta

# Connect to PostgreSQL
async def connect_db():
    return await asyncpg.connect("postgresql://postgres:YDPmNVtPzHfYpwwznfXsPpuLvidailTt@hopper.proxy.rlwy.net:54588/railway")  # Change credentials!

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
