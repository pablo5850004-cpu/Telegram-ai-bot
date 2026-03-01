import asyncio
import logging
import os
import base64
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ===== ЗАШИФРОВАННЫЙ OPENAI КЛЮЧ =====
ENCRYPTED_OPENAI_KEY = "c2stcHJvai16WDZnS1JhRTQ2cmlXZHJCa2xfVW53V0NYT1ZvZ0txT2UyZ1NyU3ctQWlvcGVneEJ5WE0tbjJ6czR0RG1tbkoyeThhWjJYVExEYVQzQmxsa0ZKSWZTeGZsNzJrRjQzdF9PckM2emRfZ2VDMlozMFRoY2xON09hV0FfRFR0b2N5TTFyNjFTczlVNk9vQXJqSDdUNzVlYjBxal9pb0E="

# Расшифровываем OpenAI ключ
OPENAI_API_KEY = base64.b64decode(ENCRYPTED_OPENAI_KEY).decode('utf-8')

# Токен бота берем из переменных окружения (как раньше)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Проверка токена бота
if not BOT_TOKEN:
    print("❌ ОШИБКА: Нет BOT_TOKEN в переменных окружения!")
    print("📝 На Bothost.ru добавьте переменную:")
    print("   BOT_TOKEN = ваш_токен_от_BotFather")
    exit()

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

print("✅ OpenAI ключ расшифрован из base64")
print("✅ Токен бота загружен из переменных окружения")

# Хранилище истории
user_conversations = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я AI бот!\n"
        "OpenAI ключ зашифрован в коде 🔐\n"
        "Токен бота в переменных окружения\n\n"
        "Просто напиши мне!"
    )

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]
    await message.answer("🧹 История очищена!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        if user_id not in user_conversations:
            user_conversations[user_id] = [
                {"role": "system", "content": "Ты полезный ассистент."}
            ]
        
        user_conversations[user_id].append(
            {"role": "user", "content": message.text}
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_conversations[user_id],
            max_tokens=1000
        )
        
        reply = response.choices[0].message.content
        
        user_conversations[user_id].append(
            {"role": "assistant", "content": reply}
        )
        
        await message.answer(reply)
        
    except Exception as e:
        await message.answer(f"😔 Ошибка: {str(e)[:100]}")

async def main():
    print("🚀 Бот запущен!")
    print(f"🔑 OpenAI ключ расшифрован: {OPENAI_API_KEY[:15]}...")
    print(f"🤖 Токен бота из env: {BOT_TOKEN[:15]}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())