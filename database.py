import psycopg2

DB_URL = "postgresql://postgres:YDPmNVtPzHfYpwwznfXsPpuLvidailTt@hopper.proxy.rlwy.net:54588/railway"  # Replace with actual DB URL

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()
