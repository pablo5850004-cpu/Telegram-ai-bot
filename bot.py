import asyncio
import logging
import os
import base64
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ===== ЗАШИФРОВАННЫЙ DEEPSEEK КЛЮЧ =====
# Ваш ключ: sk-9d4bb4d9a38f431f994f3b9d24f1094c
ENCRYPTED_DEEPSEEK_KEY = "c2stOWQ0YmI0ZDlhMzhmNDMxZjk5NGYzYjlkMjRmMTA5NGM="
# ========================================

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Расшифровываем DeepSeek ключ
DEEPSEEK_API_KEY = base64.b64decode(ENCRYPTED_DEEPSEEK_KEY).decode('utf-8')

if not BOT_TOKEN:
    print("❌ ОШИБКА: Нет BOT_TOKEN в переменных окружения!")
    print("📝 На Bothost.ru добавьте переменную: BOT_TOKEN = ваш_токен_от_BotFather")
    exit()

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище истории диалогов
user_conversations = {}

async def get_deepseek_response(user_id, message_text):
    """Получение ответа от DeepSeek API"""
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Получаем историю пользователя
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {
                "role": "system", 
                "content": "Ты - DeepSeek, полезный AI ассистент. Ты дружелюбный, умный и помогаешь пользователям с любыми вопросами. Отвечай на том же языке, на котором спрашивают. Будь кратким но информативным."
            }
        ]
    
    # Добавляем сообщение пользователя
    user_conversations[user_id].append({
        "role": "user",
        "content": message_text
    })
    
    # Ограничиваем историю (последние 20 сообщений)
    if len(user_conversations[user_id]) > 21:
        user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-20:]
    
    # Данные для запроса
    data = {
        "model": "deepseek-chat",
        "messages": user_conversations[user_id],
        "temperature": 0.7,
        "max_tokens": 2000,
        "stream": False
    }
    
    try:
        # Отправляем запрос
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Получаем ответ
        reply = result['choices'][0]['message']['content']
        
        # Сохраняем ответ в историю
        user_conversations[user_id].append({
            "role": "assistant",
            "content": reply
        })
        
        return reply
        
    except requests.exceptions.Timeout:
        return "⏰ Превышено время ожидания. Попробуйте еще раз."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "❌ Ошибка авторизации DeepSeek API. Проверьте ключ!"
        else:
            return f"🌐 Ошибка API: {e.response.status_code}"
    except Exception as e:
        return f"😔 Ошибка: {str(e)[:100]}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я **DeepSeek** в Telegram!\n"
        "Тот самый ассистент, с которым ты общался!\n\n"
        "Задавай любые вопросы - я отвечу как обычно!\n\n"
        "Команды:\n"
        "/clear - забыть историю\n"
        "/stats - статистика"
    )

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        history_len = len(user_conversations[user_id]) - 1  # минус system
        await message.answer(f"📊 В истории {history_len} сообщений")
    else:
        await message.answer("📊 История пуста")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        # Очищаем историю, но оставляем system prompt
        user_conversations[user_id] = [user_conversations[user_id][0]]
    await message.answer("🧹 История диалога очищена! Начинаем с чистого листа.")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Показываем статус "печатает..."
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем ответ от DeepSeek
    reply = await get_deepseek_response(user_id, message.text)
    
    # Отправляем ответ (разбиваем если длинный)
    if len(reply) > 4096:
        for x in range(0, len(reply), 4096):
            await message.answer(reply[x:x+4096])
    else:
        await message.answer(reply)

async def main():
    print("🚀 Бот с DeepSeek API запущен!")
    print(f"🔑 DeepSeek ключ загружен: {DEEPSEEK_API_KEY[:15]}...")
    print(f"🔐 Зашифрованный ключ в коде: {ENCRYPTED_DEEPSEEK_KEY[:20]}...")
    print("🤖 Жду сообщения в Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())