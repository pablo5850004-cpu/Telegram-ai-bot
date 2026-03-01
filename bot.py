import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ===== ВАШ DEEPSEEK КЛЮЧ (ПРЯМО В КОДЕ) =====
DEEPSEEK_API_KEY = "sk-9d4bb4d9a38f431f994f3b9d24f1094c"
# ============================================

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ОШИБКА: Нет BOT_TOKEN в переменных окружения!")
    exit()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище истории
user_conversations = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я DeepSeek в Telegram!\n"
        "Просто напиши мне что-нибудь!"
    )

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Простой запрос без истории (для начала)
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты полезный ассистент."},
                    {"role": "user", "content": message.text}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        
        if response.status_code == 402:
            await message.answer("❌ Ошибка 402: Не хватает баланса на DeepSeek API. Нужно пополнить счет.")
            return
            
        response.raise_for_status()
        result = response.json()
        reply = result['choices'][0]['message']['content']
        await message.answer(reply)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 402:
            await message.answer("❌ Ошибка 402: Недостаточно средств на счету DeepSeek")
        else:
            await message.answer(f"🌐 Ошибка API: {e.response.status_code}")
    except Exception as e:
        await message.answer(f"😔 Ошибка: {str(e)[:100]}")

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())