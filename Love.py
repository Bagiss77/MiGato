import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter, Command
from aiogram.types import BotCommand, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Получение токена и порта
API_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 8080))
BASE_URL = os.getenv('BASE_URL', 'https://migato-2.onrender.com')
WEBHOOK_URL = f"{BASE_URL}/webhook"
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

# Список фраз
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

# Пути к файлам (через FSInputFile)
YES_PHOTO_FILE = FSInputFile("static/images/yes.jpg")
YES_VIDEO_FILE = FSInputFile("static/videos/302786_tiny.mp4")
NO_PHOTO_FILE = FSInputFile("static/images/no.jpg")

# Установка команд
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

# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    logger.info(f"Получена команда /start от {message.from_user.id}")
    await message.answer("Добро пожаловать! Отправьте любое сообщение, чтобы начать опрос.")
    await send_new_poll(message.chat.id)

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
            await bot.send_photo(chat_id, photo=NO_PHOTO_FILE)
        else:  # "Да"
            for phrase in love_phrases:
                await bot.send_message(chat_id, phrase)
                await asyncio.sleep(0.5)
            await bot.send_photo(chat_id, photo=YES_PHOTO_FILE)
            await bot.send_video(chat_id, video=YES_VIDEO_FILE)
        await send_new_poll(chat_id)
    except Exception as e:
        logger.error(f"Ошибка при обработке ответа на опрос: {e}")
        await bot.send_message(chat_id, "Произошла ошибка, попробуйте позже.")

# Веб-сервер для Render и webhook
async def on_startup():
    await bot.delete_webhook()  # Удаляем старый webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен на {WEBHOOK_URL}")

async def on_shutdown():
    await bot.delete_webhook()
    logger.info("Webhook удалён")

async def handle(request):
    return web.Response(text="Bot is running")

async def static_handler(request):
    path = request.match_info['path']
    file_path = os.path.join('static', path)
    logger.info(f"Запрошен файл: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        raise web.HTTPNotFound()
    return web.FileResponse(file_path)

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    app.add_routes([web.get('/static/{path:.*}', static_handler)])
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path='/webhook')
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Веб-сервер запущен на порту {PORT}")

# Основная функция
async def main():
    try:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        await start_web_server()
        await asyncio.Event().wait()
    except Exception as e:
        logger.error(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
