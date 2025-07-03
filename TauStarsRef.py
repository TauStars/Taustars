import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart

# 🤖 Боттың токені мен админ ID
TOKEN = "8041043215:AAGYMVMwUTT_jVL5RJkHaCLkTRSudL-_Hwk"
ADMIN_ID = 6221618701

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📦 Уақытша жад (RAM)
users = {}  # user_id: {"ref_id": ..., "balance": 0, "referrals": []}

# 🔹 START командасы
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    ref_id = args[1] if len(args) > 1 else None

    if user_id not in users:
        users[user_id] = {
            "ref_id": int(ref_id) if ref_id and ref_id.isdigit() else None,
            "balance": 0,
            "referrals": []
        }
        if ref_id and ref_id.isdigit():
            ref_user = int(ref_id)
            if ref_user in users and user_id not in users[ref_user]["referrals"]:
                users[ref_user]["referrals"].append(user_id)

    # 🔘 Кнопкалар
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="👩‍💼 Біздің Менеджер", url="https://t.me/taustars")],
        [InlineKeyboardButton(text="💰 Реф ақша алу", url="https://t.me/Meng3456")]
    ])

    await message.answer(
        "Сәлеметсіз бе! Біз T A U Stars дүкені."
        "Біздің менежерден аласыз — товар бәрі сол жерде.",
        reply_markup=kb
    )

# 🔹 Профиль кнопкасы
@dp.callback_query(F.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = users.get(user_id, {"balance": 0, "referrals": [], "ref_id": None})
    ref_link = f"https://t.me/taustars_bot?start={user_id}"

    text = (
        f"👤 Пайдаланушы: @{callback.from_user.username or 'Аноним'}"
        f"👥 Рефералдар саны: {len(user['referrals'])}"
        f"💸 Табыс: {user['balance']} ₸"
        f"🔗 Реф. сілтеме:{ref_link}"
    )
    await callback.message.edit_text(text, reply_markup=callback.message.reply_markup)

# 🔹 /money командасы (ақша қосу)
@dp.message(Command("money"))
async def add_money(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 Сізге рұқсат жоқ.")

    parts = message.text.split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        return await message.answer("❗ Қате формат. Дұрыс үлгі: /money ID САН")

    user_id = int(parts[1])
    amount = int(parts[2])
    if user_id not in users:
        return await message.answer("❗ Пайдаланушы табылмады.")

    users[user_id]["balance"] += amount
    await message.answer(f"✅ {user_id} пайдаланушыға {amount} ₸ қосылды.")
    try:
        await bot.send_message(user_id, f"💸 Сізге TAU Stars тарапынан +{amount} ₸ қосылды!")
    except Exception:
        await message.answer("⚠️ Пайдаланушыға хабар жіберілмеді.")

# 🔹 /toney командасы (ақша шегеру)
@dp.message(Command("toney"))
async def remove_money(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 Сізге рұқсат жоқ.")

    parts = message.text.split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        return await message.answer("❗ Қате формат. Дұрыс үлгі: /toney ID САН")

    user_id = int(parts[1])
    amount = int(parts[2])
    if user_id not in users:
        return await message.answer("❗ Пайдаланушы табылмады.")

    users[user_id]["balance"] -= amount
    await message.answer(f"➖ {user_id} пайдаланушыдан {amount} ₸ шегерілді.")
    try:
        await bot.send_message(user_id, f"📤 Сіздің шотыңыздан -{amount} ₸ шегерілді. Ақша аударуға жіберілді.")
    except Exception:
        await message.answer("⚠️ Пайдаланушыға хабар жіберілмеді.")

# 🔹 /addreklama командасы (жарнама тарату)
@dp.message(Command("addreklama"))
async def broadcast_advert(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 Сізге рұқсат жоқ.")

    text = ""
    photo = None
    # Егер сурет + мәтін бірге команданың өзінде болса
    if message.photo:
        photo = message.photo[-1].file_id
        caption = message.caption or ""
        parts = caption.split(maxsplit=1)
        text = parts[1] if len(parts) > 1 else ""
    else:
        parts = message.text.split(maxsplit=1)
        text = parts[1] if len(parts) > 1 else ""
    # Реплайдан сурет алу
    if not photo and message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1].file_id

    if not text and not photo:
        return await message.answer(
            "❗ Мәтін немесе фото керек."
            "Қолдану:"
            "/addreklama <мәтін> (caption ретінде фото + мәтін)"
            "немесе реплайда суретпен `/addreklama`"
        )

    sent = 0
    for uid in users.keys():
        try:
            if photo:
                await bot.send_photo(chat_id=uid, photo=photo, caption=text or "")
            else:
                await bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception:
            continue

    await message.answer(f"✅ Жарнама {sent} пайдаланушыға жіберілді.")

# 🔹 Іске қосу
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
