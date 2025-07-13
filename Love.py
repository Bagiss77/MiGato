import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter
from aiogram.types import BotCommand

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль (для Render)
        logging.FileHandler('bot.log')  # Логи в файл
    ]
)
logger = logging.getLogger(__name__)

# Получение токена из переменной окружения
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения")
    raise ValueError("BOT_TOKEN не задан")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Пользовательский фильтр для текстовых сообщений
class TextMessageFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.content_type == 'text'

# Список фраз на 10 языках
love_phrases = [
    "I love you, Alena ❤️ (Английский)",
    "Я тебе кохаю, Олено ❤️ (Украинский)",
    "Te amo, Alena ❤️ (Испанский)",
    "Je t’aime, Alena ❤️ (Французский)",
    "Ich liebe dich, Alena ❤️ (Немецкий)",
    "Ti amo, Alena ❤️ (Итальянский)",
    "Eu te amo, Alena ❤️ (Португальский)",
    "Kocham cię, Alena ❤️ (Польский)",
    "愛してる、アレナ ❤️ (Японский)",
    "我爱你，阿莲娜 ❤️ (Китайский)"
]

# URL изображений (заменены на рабочие для примера)
YES_PHOTO_URL = "https://imgur.com/gallery/i-think-babies-are-enjoying-doggy-vacation-bit-too-much-Xuj0BOO#/t/happy_doggy_is_happy"  # Сердце
NO_PHOTO_URL = "https://imgur.com/gallery/shiro-siRX1Il#/t/cat"   # Грустный кот

# Установка команд для меню бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить опрос")
    ]
    await bot.set_my_commands(commands)

# Функция для отправки опроса
async def send_new_poll(chat_id: int):
    try:
        await bot.send_poll(
            chat_id=chat_id,
            question="Любит ли Кот Тимура?",
            options=["Да", "Нет"],
            is_anonymous=False,
            type="regular",
            allows_multiple_answers=False
        )
        logger.info(f"Опрос отправлен в чат {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке опроса: {e}")

# Обработчик текстовых сообщений
@dp.message(TextMessageFilter())
async def send_poll(message: types.Message):
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await send_new_poll(message.chat.id)

# Обработчик ответа на опрос
@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    chat_id = poll_answer.user.id
    option_id = poll_answer.option_ids[0] if poll_answer.option_ids else None
    logger.info(f"Получен ответ на опрос от {chat_id}: опция {option_id}")
    try:
        if option_id == 1:  # "Нет"
            await bot.send_message(chat_id, "Ответ не верный")
            await bot.send_photo(chat_id, photo=NO_PHOTO_URL)
        else:  # "Да"
            for phrase in love_phrases:
                await bot.send_message(chat_id, phrase)
            await bot.send_photo(chat_id, photo=YES_PHOTO_URL)
        await send_new_poll(chat_id)
    except Exception as e:
        logger.error(f"Ошибка при обработке ответа на опрос: {e}")
        await bot.send_message(chat_id, "Произошла ошибка, попробуйте позже.")

# Основная функция
async def main():
    try:
        await set_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка в основном цикле: {e}")

if __name__ == "__main__":
    asyncio.run(main())
