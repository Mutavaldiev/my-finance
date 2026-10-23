from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from dotenv import load_dotenv 
from service import *
from connection import *
import asyncio
import os

load_dotenv()

token = os.getenv("BOT_TOKEN")

bot = Bot(token=token)
dp = Dispatcher()



main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Profile")],
        [KeyboardButton(text="🆘 Help")],
        [KeyboardButton(text="🔄 History")],
        [KeyboardButton(text="💵 Balance")],
    ],
    resize_keyboard=True,
)



@dp.message(CommandStart())
async def start_bot(message: Message):
    user = message.from_user

    if not await get_user_by_id(user.id):
        await create_user(user.username, user.full_name, user.id)

    await message.answer(f"""
👋 Hello, {user.full_name}!
🤖 Welcome to My finance!
📚 Send /help to see commands
""", reply_markup=main_kb)


@dp.message(F.text == "🆘 Help")
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("""
💰 MY FINANCE — PERSONAL FINANCE BOT

🚀 /start - Start bot
📚 /help - Show commands
👤 /show_profile - Show my profile
💵 /balance - Show my balance
➕ /deposit Amount Description
➖ /withdraw Amount Description
📜 /history - Show transaction history
""")

@dp.message(F.text == "👤 Profile")
@dp.message(Command("show_profile"))
async def show_profile(message: Message):
    user = await get_user_by_id(message.from_user.id)

    if not user:
        await message.answer("❌ User not found!")
        return

    await message.answer(f"""
👤 MY FINANCE — YOUR PROFILE

🆔 Telegram ID: {message.from_user.id}
📛 Full Name: {user['full_name']}
🔗 Username: @{user['username'] or 'Not set'}
💰 Current Balance: {user['balance']} $
📅 Joined: {user['created_at']}
🟢 Account Status: {'Active' if user['is_active'] else 'Inactive'}
""")

@dp.message(F.text == "💵 Balance")
@dp.message(Command("balance"))
async def balance_handler(message: Message):
    user = await get_user_by_id(message.from_user.id)

    if not user:
        await message.answer("❌ User not found!")
        return

    await message.answer(f"💰 Your balance: {user['balance']} $")


@dp.message(Command("deposit"))
async def deposit_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("❗ Usage: /deposit Amount Description\nExample: /deposit 500 Salary")
        return

    parts = command.args.split(maxsplit=1)

    try:
        amount = float(parts[0])
    except ValueError:
        await message.answer("❌ Amount must be a valid number.")
        return

    success, result = await add_transaction(
        message.from_user.id, amount, "income", parts[1]
    )

    if not success:
        await message.answer(result)
        return

    await message.answer(f"""
➕ Deposit successful!
💰 Amount: {amount} $
📝 Description: {parts[1]}
💵 New Balance: {result} $
""")



@dp.message(Command("withdraw"))
async def withdraw_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("❗ Usage: /withdraw Amount Description\nExample: /withdraw 100 Food")
        return

    parts = command.args.split(maxsplit=1)


    try:
        amount = float(parts[0])
    except ValueError:
        await message.answer("❌ Amount must be a valid number.")
        return
    success, result = await add_transaction(
        message.from_user.id, amount, "expense", parts[1]
    )

    if not success:
        await message.answer(result)
        return

    await message.answer(f"""
➖ Withdrawal successful!
💰 Amount: {amount} $
📝 Description: {parts[1]}
💵 New Balance: {result} $
""")



@dp.message(F.text == "🔄 History")
@dp.message(Command("history"))
async def history_handler(message: Message):
    history = await get_user_history(message.from_user.id)

    if not history:
        await message.answer("📜 No transactions found.")
        return

    text = "📜 MY FINANCE — TRANSACTION HISTORY\n\n"

    for item in history:
        emoji = "➕" if item["operation_type"] == "income" else "➖"
        text += (f"""
{emoji} {item['amount']} $
📝 {item['description']}
📅 {item['created_at']}
        """)

    await message.answer(text)



async def main():
    await create_table()
    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
