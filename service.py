
from connection import connection_db


async def get_user_by_id(telegram_id):
    conn = await connection_db()

    try:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            str(telegram_id)
        )
    finally:
        await conn.close()


async def create_user(username, full_name, telegram_id):
    conn = await connection_db()

    try:
        await conn.execute("""
            INSERT INTO users (username, full_name, telegram_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING
        """, username, full_name, str(telegram_id))
    finally:
        await conn.close()

async def add_transaction(telegram_id, amount, operation_type, description):
    conn = await connection_db()

    try:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1 FOR UPDATE",
                str(telegram_id)
            )

            if not user:
                return False, "❌ User not found!"

            current_balance = float(user["balance"])
            amount = round(float(amount), 2)

            if operation_type == "expense" and current_balance < amount:
                return False, "❌ Balance cant be debtor!"

            if operation_type == "income":
                balance = round(current_balance + amount, 2)
            else:
                balance = round(current_balance - amount, 2)

            await conn.execute(
                "UPDATE users SET balance = $1 WHERE user_id = $2",balance,user["user_id"])

            await conn.execute("""
                INSERT INTO history (user_id, amount, operation_type, description)
                VALUES ($1, $2, $3, $4)
            """,user["user_id"],amount,operation_type,description)

        return True, balance

    finally:
        await conn.close()


async def get_user_history(telegram_id):
    conn = await connection_db()

    try:
        return await conn.fetch("""
            SELECT h.* FROM history h
            JOIN users u ON u.user_id = h.user_id
            WHERE u.telegram_id = $1
            ORDER BY h.created_at DESC
            LIMIT 10
        """, str(telegram_id))
    finally:
        await conn.close()
