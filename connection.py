from dotenv import load_dotenv
import asyncpg
import os

load_dotenv()
pasw  = os.getenv("DATABASE_DB")


async def connection_db():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            database="my_finanace",
            password=pasw
        )
        return conn
    except Exception as Error:
        print(f"Connection Error: {Error}")

async def create_table():
    conn = await connection_db()

    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                full_name VARCHAR(100),
                telegram_id VARCHAR(200) UNIQUE NOT NULL,
                balance NUMERIC(12, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                history_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                amount NUMERIC(12, 2) NOT NULL,
                operation_type VARCHAR(10)
                    CHECK (operation_type IN ('income', 'expense')),
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        print("Tables created")

    finally:
        await conn.close()
