import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токены из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

# Системный промпт
SYSTEM_PROMPT = "Ты - полезный AI ассистент в Telegram."

# Хранилище
user_conversations = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Привет! Я AI бот. Просто напиши мне!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Показываем "печатает..."
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # История пользователя
        if user_id not in user_conversations:
            user_conversations[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        user_conversations[user_id].append(
            {"role": "user", "content": message.text}
        )
        
        # Запрос к OpenAI
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
        await message.answer("😔 Ошибка, попробуйте позже")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
