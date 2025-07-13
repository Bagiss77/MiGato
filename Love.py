
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter

# Вставьте ваш токен, полученный от @BotFather
API_TOKEN = '8076702747:AAGx0FiEGLF8Kh0FJH4N0xOzNjMCdhJWhdI'

# Пользовательский фильтр для текстовых сообщений
class TextMessageFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.content_type == 'text'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список фраз на 10 языках с указанием языка
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

# URL изображений
YES_PHOTO_URL = "https://imgur.com/gallery/i-think-babies-are-enjoying-doggy-vacation-bit-too-much-Xuj0BOO#/t/happy_doggy_is_happy"  # Сердце для ответа "Да"
NO_PHOTO_URL = "https://imgur.com/gallery/shiro-siRX1Il#/t/cat "   # Грустный кот для ответа "Нет"

# Функция для отправки опроса
async def send_new_poll(chat_id: int):
    await bot.send_poll(
        chat_id=chat_id,
        question="Любит ли Кот Тимура?",
        options=["Да", "Нет"],
        is_anonymous=False,
        type="regular",
        allows_multiple_answers=False
    )

# Обработчик любых текстовых сообщений
@dp.message(TextMessageFilter())
async def send_poll(message: types.Message):
    await send_new_poll(message.chat.id)

# Обработчик ответа на опрос
@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    chat_id = poll_answer.user.id
    option_id = poll_answer.option_ids[0] if poll_answer.option_ids else None
    if option_id == 1:  # "Нет"
        await bot.send_message(chat_id, "Ответ не верный")
        await bot.send_photo(chat_id, photo=NO_PHOTO_URL)
    else:  # "Да"
        for phrase in love_phrases:
            await bot.send_message(chat_id, phrase)
        await bot.send_photo(chat_id, photo=YES_PHOTO_URL)
    # Отправляем новый опрос
    await send_new_poll(chat_id)

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
